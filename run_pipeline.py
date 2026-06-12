"""Pipeline completo — ejecuta los agentes Spotify en secuencia con maxima robustez."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import importlib.util
import time
import logging
import traceback
from pathlib import Path

# Configurar logging robusto
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler("pipeline_execution.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("Orchestrator")

AGENTS_DIR = Path(__file__).parent / "agents"
INPUTS_DIR = Path(__file__).parent / "inputs"

def _load_agent(filename: str):
    """Carga un modulo con nombre numerico."""
    path = AGENTS_DIR / filename
    spec = importlib.util.spec_from_file_location(filename.replace(".", "_"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run_pipeline() -> dict:
    logger.info("=" * 60)
    logger.info("PIPELINE SPOTIFY EDITORIAL — INICIO ROBUSTO")
    logger.info("=" * 60)

    # --- Pre-check: Ingestión Autónoma (Agente 00) ---
    if not INPUTS_DIR.exists() or not any(INPUTS_DIR.iterdir()):
        logger.warning("Carpeta inputs/ vacia o no existe. Iniciando Agente 00 (Data Fetcher)...")
        try:
            agent00 = _load_agent("00_github_data_fetcher.py")
            fetch_stats = agent00.run_fetcher()
            logger.info(f"Agente 00 completado. Stats: {fetch_stats}")
        except Exception as e:
            logger.error(f"Fallo el Agente 00: {e}")
            logger.debug(traceback.format_exc())
            # Continúa, pero el pipeline fallará después si no hay datos

    results = {}

    # --- Agente 1: Data Recon ---
    logger.info("\n[1/4] DATA RECON")
    t0 = time.time()
    try:
        agent01 = _load_agent("01_data_recon.py")
        results["recon"] = agent01.run_recon()
        logger.info(f"Agente 1 completado en {time.time() - t0:.1f}s")
    except Exception as e:
        logger.error(f"Error critico en Agente 1: {e}")
        logger.debug(traceback.format_exc())
        return results

    # --- Agente 2: EDA Auto ---
    logger.info("\n[2/4] EDA AUTO")
    t0 = time.time()
    try:
        agent02 = _load_agent("02_eda_auto.py")
        results["eda"] = agent02.run_eda()
        logger.info(f"Agente 2 completado en {time.time() - t0:.1f}s")
    except Exception as e:
        logger.error(f"Error en Agente 2: {e}")
        logger.debug(traceback.format_exc())
        # El EDA a veces no bloquea el hypothesis testing si no es dependiente directo
        # Pero segun la logica, el Agente 3 necesita df_merged del EDA.
        return results

    # --- Agente 3: Hypothesis Testing ---
    logger.info("\n[3/4] HYPOTHESIS TESTING")
    t0 = time.time()
    try:
        agent03 = _load_agent("03_hypothesis.py")
        results["hypothesis"] = agent03.run_hypothesis(
            df_merged=results["eda"].get("df_merged")
        )
        logger.info(f"Agente 3 completado en {time.time() - t0:.1f}s")
    except Exception as e:
        logger.error(f"Error en Agente 3: {e}")
        logger.debug(traceback.format_exc())
        results["hypothesis"] = {}

    # --- Agente 4: Business Translation ---
    logger.info("\n[4/4] BUSINESS TRANSLATION")
    t0 = time.time()
    try:
        agent04 = _load_agent("04_business_tx.py")
        results["brief"] = agent04.run_business_tx(
            recon_result=results.get("recon", {}),
            eda_result=results.get("eda", {}),
            hypothesis_result=results.get("hypothesis", {}),
        )
        logger.info(f"Agente 4 completado en {time.time() - t0:.1f}s")
    except Exception as e:
        logger.error(f"Error en Agente 4: {e}")
        logger.debug(traceback.format_exc())
        results["brief"] = ""

    logger.info("=" * 60)
    logger.info("PIPELINE CORE COMPLETADO")
    
    # --- Evaluaciones (Capa 5) ---
    logger.info("Invocando Capa 5 (Evaluaciones)...")
    try:
        import eval_pipeline
        eval_stats = eval_pipeline.run_evaluations(results)
        logger.info(f"Evals completados: {eval_stats['timestamp']}")
    except Exception as e:
        logger.error(f"Fallo en la Capa de Evals: {e}")
        logger.debug(traceback.format_exc())

    logger.info("FIN DEL PROCESO.")
    return results

if __name__ == "__main__":
    run_pipeline()
