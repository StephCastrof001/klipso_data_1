# Problem Statement — Spotify Editorial
## CRISP-DM Fase 0: Business Understanding

### QUIÉN
Equipo editorial de Spotify. Curan playlists manualmente.
Decisiones actuales: intuición del editor, sin respaldo de datos.

### QUÉ
Identificar señales tempranas de éxito de una canción ANTES de incluirla en una playlist.
Datos disponibles: presencia en plataformas (Spotify, Apple, Deezer, Shazam) + metadatos del track.

### POR QUÉ
- Resultados inconsistentes al curar playlists manualmente
- Canciones con alto potencial pasan desapercibidas por el equipo
- Canciones incluidas no siempre logran el engagement esperado
- El proceso actual no escala: hay más canciones que tiempo de revisión

### MÉTRICA DE ÉXITO DEL ANÁLISIS
- Al menos 3 señales verificables con los datos reales (no opinión del modelo)
- Las señales expresadas como criterios de inclusión/exclusión accionables
- El brief es legible por el equipo editorial sin conocimientos técnicos
- Cada señal tiene un número que la respalda (correlación, mediana, etc.)

### DATOS

| Archivo | Filas | Qué contiene |
|---|---|---|
| `track_in_spotify_skill_academy.csv` | 839 | Métricas Spotify + metadatos del track |
| `track_in_competition_skill_academy.csv` | 953 | Métricas Apple Music, Deezer, Shazam |

JOIN key: `track_id` — tipos distintos entre tablas (issue conocido, Agente 1 lo detecta).
Tracks sin match (839 vs 953): hallazgo de negocio, no error técnico.

### HIPÓTESIS A PROBAR

| H | Señal de negocio | Variables a analizar |
|---|---|---|
| H1 | Más playlists en múltiples plataformas = más streams | in_spotify_playlists, in_apple_playlists, in_deezer_playlists vs streams |
| H2 | Presencia en charts múltiples = más streams | in_spotify_charts, in_apple_charts, in_deezer_charts, in_shazam_charts vs streams |
| H3 | Canciones recientes que llegan a playlists rápido = más streams | released_year >= 2022 + tiempo_a_playlist (a calcular) |
| H4 | Género, país y número de artistas predicen streams | main_music_genre, main_country, artist_count |

### FUERA DE ALCANCE (este sprint)
- Modelo predictivo ML (siguiente fase, posiblemente EC2)
- Datos de audio features (no disponibles en este dataset)
- Comparación histórica multi-año
