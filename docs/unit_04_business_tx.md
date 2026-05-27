# TASK: agente-04-business-translator

GOAL: Agente que toma los resultados de los 3 agentes anteriores y produce criterios editoriales accionables
FILES: agents/04_business_tx.py
CONTRACT: def run_business_translation(recon_results: dict, hypothesis_results: dict) -> str
DONE WHEN: grep -q "run_business_translation" agents/04_business_tx.py && grep -q "criterios\|editorial\|playlist" agents/04_business_tx.py
ROLLBACK: git revert HEAD

# Contexto
- Importar LLM desde agents/00_setup_llm.py
- Recibir recon_results (de agente 1) y hypothesis_results (de agente 3)
- Usar LLM con prompt específico para equipo editorial Spotify
- El prompt debe pedir al LLM que produzca:
  1. Top 3 señales tempranas para incluir en playlist (basadas en hipótesis confirmadas)
  2. Top 3 señales de alerta (tracks a evitar)
  3. Recomendación de flujo de trabajo para el equipo editorial
- Formato de output: Markdown con secciones claras para PM no-técnica
- Return: string Markdown
- Guardar en outputs/editorial_brief.md
- Imprimir el brief completo
