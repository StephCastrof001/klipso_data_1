# TASK: agente-01-data-recon

GOAL: Agente que audita el schema, tipos, nulls y problemas de JOIN de los dos CSVs de Spotify
FILES: agents/01_data_recon.py
CONTRACT: def run_recon(spotify_path: str, competition_path: str) -> dict
DONE WHEN: grep -q "run_recon" agents/01_data_recon.py && grep -q "track_id" agents/01_data_recon.py
ROLLBACK: git revert HEAD

# Contexto
- Importar LLM desde agents/00_setup_llm.py
- Leer dos CSVs con pandas
- Detectar y reportar: tipos de datos por columna, nulls, columnas con object donde se espera int
- Detectar problema JOIN: track_id es int en spotify, object en competition
- El agente usa el LLM para traducir hallazgos técnicos a lenguaje de negocio
- Output: imprimir reporte + return dict con keys: schema_issues, null_counts, join_warning
- Problemas conocidos a detectar:
  * streams → object (string con comas) en vez de int
  * in_deezer_playlists → object en vez de int  
  * in_shazam_charts → object en vez de int
  * track_id type mismatch entre tablas
- Usar langchain/langgraph para llamar al LLM con el reporte técnico
- MODEL: anthropic.claude-sonnet-4-5-20251001-v1:0
