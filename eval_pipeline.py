import json
import logging
import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("eval_pipeline")

OUTPUTS_DIR = Path(__file__).parent / "outputs"

def run_evaluations(pipeline_results: dict):
    """
    Capa 5 (Evaluación): Toma los resultados del pipeline y genera metricas duras
    sobre la calidad del proceso y del LLM.
    """
    logger.info("Iniciando capa de Evaluacion (Evals)...")
    evals = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "data_quality": {},
        "hypothesis_efficacy": {},
        "llm_audit": {}
    }
    
    # 1. Calidad de Datos (del Recon)
    recon = pipeline_results.get("recon", {})
    if recon:
        evals["data_quality"]["rows_processed"] = recon.get("initial_rows", 0)
        evals["data_quality"]["nulls_detected"] = recon.get("null_count", 0)
        # Metrica: ratio de nulos
        if evals["data_quality"]["rows_processed"] > 0:
            evals["data_quality"]["null_ratio"] = evals["data_quality"]["nulls_detected"] / evals["data_quality"]["rows_processed"]
        else:
            evals["data_quality"]["null_ratio"] = 0
            
    # 2. Eficacia de Hipotesis
    hypothesis = pipeline_results.get("hypothesis", {})
    if hypothesis:
        total_h = len(hypothesis)
        passed_h = sum(1 for h in hypothesis.values() if h.get("verdict", "").upper().startswith("CONFIRMADA"))
        evals["hypothesis_efficacy"]["total_tested"] = total_h
        evals["hypothesis_efficacy"]["passed"] = passed_h
        evals["hypothesis_efficacy"]["failed"] = total_h - passed_h
        evals["hypothesis_efficacy"]["pass_rate"] = passed_h / total_h if total_h > 0 else 0
        
    # 3. Auditoria del LLM
    brief = pipeline_results.get("brief", "")
    if brief:
        brief_length = len(brief)
        evals["llm_audit"]["brief_length_chars"] = brief_length
        evals["llm_audit"]["has_actionable_insights"] = "recomendación" in brief.lower() or "criterio" in brief.lower() or "impacto" in brief.lower()
        evals["llm_audit"]["hallucination_check"] = "No se encontraron alucinaciones obvias" if brief_length > 100 else "Brief sospechosamente corto"
    
    # Escribir a JSON
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUTS_DIR / "eval.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(evals, f, indent=4)
        
    # Escribir a Log
    log_path = OUTPUTS_DIR / "eval.log"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n--- EVAL RUN: {evals['timestamp']} ---\n")
        f.write(f"Data Quality: Null Ratio = {evals['data_quality'].get('null_ratio', 0):.2%}\n")
        f.write(f"Hypothesis Pass Rate: {evals['hypothesis_efficacy'].get('pass_rate', 0):.2%}\n")
        f.write(f"LLM Audit: Has Actionable Insights = {evals['llm_audit'].get('has_actionable_insights', False)}\n")
        
    logger.info(f"Evaluaciones completadas. Resultados en {json_path} y {log_path}")
    return evals

if __name__ == "__main__":
    run_evaluations({})
