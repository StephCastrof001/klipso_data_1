import os
import time
import json
import logging
import urllib.request
import urllib.error
import hashlib
import tempfile
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("00_github_data_fetcher")

GITHUB_USER = "StephCastrof001"
API_BASE = "https://api.github.com"
INPUTS_DIR = Path(__file__).parent.parent / "inputs"

def _auth_headers() -> dict:
    """Genera headers de autenticación con token si existe."""
    headers = {"User-Agent": "Klipso-Auto-Fetcher"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
        logger.info("Usando token de autenticación GitHub")
    else:
        logger.warning("Sin GITHUB_TOKEN en entorno. Límite de 60 req/h activo.")
    return headers

def fetch_json(url: str, headers: dict = None) -> dict:
    """Realiza una petición GET a la API de GitHub y maneja rate-limits."""
    req_headers = _auth_headers()
    if headers:
        req_headers.update(headers)
    
    req = urllib.request.Request(url, headers=req_headers)
    
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                reset_time = int(e.headers.get("X-RateLimit-Reset", time.time() + 60))
                sleep_time = max(reset_time - time.time(), 10)
                logger.warning(f"Rate limit hit. Sleeping for {sleep_time:.0f} seconds...")
                time.sleep(sleep_time)
            else:
                logger.error(f"HTTPError {e.code}: {e.reason} para la url {url}")
                raise
        except Exception as e:
            logger.error(f"Error desconocido: {e}")
            time.sleep(5)
    raise Exception("Max retries exceeded")

def download_if_changed(raw_url: str, save_path: Path) -> str:
    """
    Descarga un archivo crudo manejando errores con idempotencia por hash.
    
    Args:
        raw_url: URL del archivo a descargar
        save_path: Ruta donde guardar el archivo
        
    Returns:
        "downloaded" | "updated" | "unchanged" | "error"
    """
    try:
        # Calcular hash del archivo existente si existe
        existing_hash = None
        if save_path.exists():
            with open(save_path, "rb") as f:
                existing_hash = hashlib.sha256(f.read()).hexdigest()
        
        # Descargar a archivo temporal
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = Path(tmp.name)
            logger.info(f"Downloading {raw_url} to {save_path.name}")
            urllib.request.urlretrieve(raw_url, tmp_path)
            
            # Calcular hash del nuevo archivo
            with open(tmp_path, "rb") as f:
                new_hash = hashlib.sha256(f.read()).hexdigest()
        
        # Comparar hashes
        if existing_hash is None:
            # No existe archivo previo
            save_path.write_bytes(tmp_path.read_bytes())
            logger.info(f"Nuevo archivo: {save_path.name}")
            return "downloaded"
        elif existing_hash == new_hash:
            # Hashes iguales, no se necesita actualizar
            logger.info(f"Archivo {save_path.name} no ha cambiado (hash idéntico)")
            return "unchanged"
        else:
            # Hashes diferentes, actualizar
            save_path.write_bytes(tmp_path.read_bytes())
            logger.info(f"Archivo {save_path.name} actualizado (hash diferente)")
            return "updated"
            
    except Exception as e:
        logger.error(f"Error al descargar {raw_url}: {e}")
        return "error"

def run_fetcher() -> dict:
    """Agente 00: Busca autonomamente repositorios del usuario y descarga excels/csvs."""
    logger.info(f"Iniciando busqueda autonoma para el usuario: {GITHUB_USER}")
    stats = {"repos_scanned": 0, "files_downloaded": 0, "files": []}
    
    # 1. Obtener repos del usuario
    repos_url = f"{API_BASE}/users/{GITHUB_USER}/repos?per_page=100"
    try:
        repos = fetch_json(repos_url)
    except Exception as e:
        logger.error(f"Error fetching repos: {e}")
        return stats
        
    stats["repos_scanned"] = len(repos)
    logger.info(f"Encontrados {len(repos)} repositorios para {GITHUB_USER}")
    
    for repo in repos:
        repo_name = repo["name"]
        default_branch = repo["default_branch"]
        tree_url = f"{API_BASE}/repos/{GITHUB_USER}/{repo_name}/git/trees/{default_branch}?recursive=1"
        
        try:
            tree = fetch_json(tree_url)
        except Exception as e:
            logger.warning(f"No se pudo leer el arbol de {repo_name}: {e}")
            continue
            
        for item in tree.get("tree", []):
            if item["type"] == "blob":
                path = item["path"]
                if path.endswith(".csv") or path.endswith(".xlsx"):
                    raw_url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{repo_name}/{default_branch}/{path}"
                    # Anti-colision: guardar como {repo_name}__{filename}
                    file_name = f"{repo_name}__{Path(path).name}"
                    save_path = INPUTS_DIR / file_name
                    
                    result = download_if_changed(raw_url, save_path)
                    if result != "error":
                        stats["files_downloaded"] += 1
                        stats["files"].append(file_name)
                    else:
                        logger.warning(f"Error descargando {file_name}")
                        
    logger.info(f"Fetcher finalizado. Archivos descargados: {stats['files_downloaded']}")
    return stats

if __name__ == "__main__":
    run_fetcher()
