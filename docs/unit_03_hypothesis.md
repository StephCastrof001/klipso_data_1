# TASK: agente-03-hypothesis

GOAL: Agente que prueba las 4 hipótesis editoriales de Spotify con correlaciones y el LLM interpreta
FILES: agents/03_hypothesis.py
CONTRACT: def run_hypothesis(df: pd.DataFrame) -> dict
DONE WHEN: grep -q "run_hypothesis" agents/03_hypothesis.py && grep -q "H1\|H2\|H3\|H4" agents/03_hypothesis.py
ROLLBACK: git revert HEAD

# Contexto
- Importar LLM desde agents/00_setup_llm.py
- Recibir DataFrame limpio+joinado (o leer outputs/clean_data.csv)
- Las 4 hipótesis a probar:
  * H1: correlación in_spotify_playlists + in_apple_playlists + in_deezer_playlists vs streams
  * H2: correlación in_spotify_charts + in_apple_charts + in_deezer_charts + in_shazam_charts vs streams
  * H3: canciones recientes (released_year >= 2022) en playlists rápido tienen más streams?
  * H4: agrupar por main_music_genre y main_country → cuál tiene más streams median?
- Para cada hipótesis: calcular con pandas (.corr(), .groupby(), etc.)
- Pasar resultados numéricos al LLM para que interprete en lenguaje editorial
- Return: dict con keys H1, H2, H3, H4 — cada uno con keys: stat (float/dict), verdict (str del LLM)
- Imprimir tabla resumen con los 4 veredictos
