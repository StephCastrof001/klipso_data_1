# CLAUDE.md — proyecto_labo

## Contexto de negocio (CRISP-DM PASO 0)

**Quién:** Equipo editorial Spotify — curan playlists manualmente
**Problema:** Decisiones por intuición, resultados inconsistentes
**Objetivo:** Identificar señales tempranas de éxito ANTES de incluir canción en playlist
**Variable objetivo:** `streams`
**Pregunta central:** ¿Qué hace que una canción triunfe en MÚLTIPLES plataformas?

## Datos

| Archivo | Filas | Columnas clave |
|---|---|---|
| `inputs/track_in_spotify_skill_academy.csv` | 839 | track_id (int), track_name, artists_name, artist_count, main_music_genre, main_country, released_year/month/day, in_spotify_playlists, in_spotify_charts, streams (object — SUCIO) |
| `inputs/track_in_competition _skill_academy.csv` | 953 | track_id (object), in_apple_playlists, in_apple_charts, in_deezer_playlists (object), in_deezer_charts, in_shazam_charts (object) |

**JOIN key:** `track_id` — tipos distintos (int vs object), requiere normalización.
**Nota:** 839 vs 953 filas — tracks sin match = hallazgo de negocio, no error.

## Problemas de datos conocidos

- `streams` → object (string con comas) en vez de int
- `in_deezer_playlists` → object en vez de int
- `in_shazam_charts` → object en vez de int
- `track_id` → int en spotify, object en competition → JOIN roto sin normalización

## Las 4 hipótesis

| H | Señal | Variables |
|---|---|---|
| H1 | Más playlists = más streams | in_spotify_playlists, in_apple_playlists, in_deezer_playlists |
| H2 | Charts múltiples = más streams | in_spotify_charts, in_apple_charts, in_deezer_charts, in_shazam_charts |
| H3 | Canciones recientes en playlists rápido = más streams | released_year, released_month + playlists |
| H4 | Género/país/colaboradores = predictor | main_music_genre, main_country, artist_count |

## Stack técnico

- Python 3.9+
- LangChain + langchain-aws → Amazon Bedrock
- Modelo: `anthropic.claude-sonnet-4-5-20251001-v1:0` (Sonnet 4.6 en Bedrock)
- LangGraph: orquestación multi-agente
- ydata-profiling + sweetviz: AutoEDA
- pandas, numpy, matplotlib, seaborn, scikit-learn

## Autenticación Bedrock

```python
from langchain_aws import ChatBedrockConverse
from dotenv import load_dotenv
import os

load_dotenv()
llm = ChatBedrockConverse(
    model="anthropic.claude-sonnet-4-5-20251001-v1:0",
    api_key=os.getenv("BEDROCK_API_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
)
```

Variables en `.env` (no commitear):
- `BEDROCK_API_KEY` — Bedrock Console → API Keys → Create key
- `AWS_DEFAULT_REGION` — default: us-east-1

## Pipeline multi-agente

```
Agente 1 — agents/01_data_recon.py      → schema, nulls, tipos, JOIN issues
Agente 2 — agents/02_eda_auto.py        → ydata-profiling + sweetviz
Agente 3 — agents/03_hypothesis.py      → prueba H1, H2, H3, H4
Agente 4 — agents/04_business_tx.py     → traduce hallazgos → criterios editoriales
```

Referencia: `refs/ai-data-science-team/` — adaptar agentes con Bedrock en lugar de OpenAI.

## Estructura

```
proyecto_labo/
├── inputs/         # datos originales (NO modificar)
├── agents/         # scripts de agentes IA
├── notebooks/      # exploración manual
├── outputs/        # reportes HTML, gráficos
├── docs/           # documentación del caso
├── refs/           # repos de referencia (en .gitignore)
├── .env            # API keys (en .gitignore)
├── .env.example    # plantilla sin valores reales
├── requirements.txt
└── CLAUDE.md
```

## Reglas de trabajo

- No modificar archivos en `inputs/`
- `refs/` nunca va al repo (en .gitignore)
- `.env` nunca va al repo (en .gitignore)
- Cada agente tiene un output verificable (CSV, HTML, o print)
- Hallazgos se traducen a recomendación de negocio, no solo número
