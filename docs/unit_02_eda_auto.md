# TASK: agente-02-eda-auto

GOAL: Agente que genera reporte AutoEDA con ydata-profiling sobre los datos limpios y joinados
FILES: agents/02_eda_auto.py
CONTRACT: def run_eda(df: pd.DataFrame, output_path: str = "outputs/eda_report.html") -> str
DONE WHEN: grep -q "run_eda" agents/02_eda_auto.py && grep -q "ProfileReport" agents/02_eda_auto.py
ROLLBACK: git revert HEAD

# Contexto
- Importar LLM desde agents/00_setup_llm.py
- Recibir DataFrame ya limpio y joinado (o leer desde outputs/clean_data.csv si existe)
- Generar reporte con ydata_profiling.ProfileReport (minimal=True para velocidad)
- Guardar HTML en output_path
- Usar LLM para generar 3 bullet points de hallazgos clave del reporte
- Return: path del HTML generado
- Imprimir: "EDA report saved to {output_path}" + los 3 bullets del LLM
- Dependencia: pip install ydata-profiling
