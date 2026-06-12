import os
import time
import json
import logging
import urllib.request
import urllib.error
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("00_github_data_fetcher")

GITHUB_USER = "StephCastrof001"
API_BASE = "https://api.github.com"
INPUTS_DIR = Path(__file__).parent.parent / "inputs"

def fetch_json(url: str, headers: dict = None) -> dict:
    """Realiza una peticion GET a la API de GitHub y maneja rate-limits."""
    req_headers = {"User-Agent": "Klipso-Auto-Fetcher"}
    if headers:
        req_headers.update(headers)
    
    req = urllib.request.Request(url, headers=req_headers)
    
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req) as response:
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

def download_file(url: str, save_path: Path):
    """Descarga un archivo crudo manejando errores."""
    logger.info(f"Downloading {url} to {save_path.name}")
    save_path.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, save_path)

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
                    file_name = Path(path).name
                    save_path = INPUTS_DIR / file_name
                    
                    if not save_path.exists():
                        download_file(raw_url, save_path)
                        stats["files_downloaded"] += 1
                        stats["files"].append(file_name)
                    else:
                        logger.info(f"File {file_name} ya existe. Saltando descarga.")
                        
    logger.info(f"Fetcher finalizado. Archivos descargados: {stats['files_downloaded']}")
    return stats

if __name__ == "__main__":
    run_fetcher()
