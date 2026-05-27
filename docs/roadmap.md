# Roadmap — Spotify Editorial Agentic Data Science

**Última actualización:** 2026-05-25
**Status:** Sprint 1 en progreso

---

## Contexto de negocio

**Quién:** Equipo editorial Spotify — curan playlists manualmente
**Problema:** Decisiones por intuición, resultados inconsistentes
**Objetivo:** Identificar señales tempranas de éxito ANTES de incluir canción en playlist
**Variable objetivo:** `streams`
**Métrica de éxito del proyecto:** El brief editorial producido es accionable y verificable con los datos reales

---

## Arquitectura del pipeline

```
TÚ defines (PM input)          LOS AGENTES ejecutan
──────────────────────         ───────────────────────────────────
problem-statement.md      →    steering wheel de todo el pipeline
Las 4 hipótesis (H1-H4)   →    Agente 3 prueba exactamente esas
Formato del brief         →    Agente 4 produce ESE brief

inputs/
  track_in_spotify_skill_academy.csv     (839 filas)
  track_in_competition_skill_academy.csv (953 filas)
         ↓
  Agente 1 — Data Recon
    → detecta tipos sucios, nulls, JOIN issues
    → output: reporte técnico + traducción LLM en lenguaje de negocio
         ↓
  Agente 2 — EDA Auto
    → ydata-profiling: reporte HTML completo
    → LLM resume los 3 hallazgos clave para PM
         ↓
  Agente 3 — Hypothesis Tester
    → prueba H1, H2, H3, H4 con pandas (determinístico)
    → LLM interpreta cada número en lenguaje editorial
         ↓
  Agente 4 — Business Translator
    → toma outputs de agentes 1+3
    → LLM produce brief editorial con señales ✓ y señales ✗
    → guarda outputs/editorial_brief.md
```

---

## Las 4 hipótesis (definidas por la PM)

| H | Señal | Variables |
|---|---|---|
| H1 | Más playlists = más streams | in_spotify_playlists, in_apple_playlists, in_deezer_playlists |
| H2 | Charts múltiples = más streams | in_spotify_charts, in_apple_charts, in_deezer_charts, in_shazam_charts |
| H3 | Canciones recientes en playlists rápido = más streams | released_year >= 2022 + playlists_count |
| H4 | Género/país/colaboradores predice streams | main_music_genre, main_country, artist_count |

---

## Control de calidad — anti-alucinación

**Agentes 1 y 3:** pandas calcula los números (determinístico). El LLM solo interpreta.
Cada output imprime: `stat calculado por pandas` + `interpretación del LLM` juntos.
Si el LLM dice "correlación alta" pero pandas dio r=0.12 → detectable a simple vista.

**Agente 2:** ydata-profiling genera HTML visual. La PM puede revisar el reporte directamente.

**Agente 4:** el brief cita las hipótesis específicas con sus números. Sin números = output inválido.

**Regla:** ningún agente toma decisiones de negocio. Solo produce evidencia. La PM decide.

---

## 3 modos de ejecución (comparativa para contenido)

| Modo | Dónde corre | LLM | Costo |
|---|---|---|---|
| **A — Local** | Windows `proyecto_labo/` | Bedrock Claude Sonnet 4.6 | ~$0.01 por run |
| **B — EC2** | `ubuntu@107.21.24.49:~/proyecto_spotify/` | Bedrock Claude Sonnet 4.6 | ~$0.01 por run |
| **C — EC2 Ollama** | mismo EC2 | qwen3-14b-32k local | $0 total |

Mismo código Python — solo cambia 1 línea en `get_llm()`.

---

## Escalabilidad

| Agente | 839 filas (ahora) | 1M filas (futuro) |
|---|---|---|
| Data Recon | ✅ | ✅ rápido |
| EDA Auto | ✅ | ⚠️ usar `minimal=True` o samplear 10% |
| Hypothesis | ✅ | ✅ pandas groupby/corr en segundos |
| Business Tx | ✅ | ✅ LLM solo recibe resumen, no datos crudos |

**Clave:** el LLM nunca ve datos crudos — solo stats. El cuello de botella es pandas, no el LLM.

---

## Portabilidad — otros datasets (no Spotify)

| Componente | Reutilizable sin cambios |
|---|---|
| Agente 1 — Data Recon | ✅ 100% — funciona con cualquier DataFrame |
| Agente 2 — EDA Auto | ✅ 100% — ydata-profiling es genérico |
| Agente 3 — Hypothesis | ⚠️ 20% — hipótesis son Spotify-específicas |
| Agente 4 — Business Tx | ⚠️ 30% — prompt editorial es específico |

Para otro dataset: redefinir problem-statement.md + hipótesis → agentes 1 y 2 funcionan solos.

---

## Documentación requerida (CRISP-DM)

| Archivo | Status | Contenido |
|---|---|---|
| `docs/problem-statement.md` | ⬜ pendiente | QUIÉN, QUÉ, POR QUÉ, MÉTRICA DE ÉXITO |
| `docs/roadmap.md` | ✅ este archivo | sprint plan + arquitectura |
| `docs/unit_00_setup_llm.md` | ✅ creado | spec módulo LLM compartido |
| `docs/unit_01_data_recon.md` | ✅ creado | spec Agente 1 |
| `docs/unit_02_eda_auto.md` | ✅ creado | spec Agente 2 |
| `docs/unit_03_hypothesis.md` | ✅ creado | spec Agente 3 |
| `docs/unit_04_business_tx.md` | ✅ creado | spec Agente 4 |

---

## Sprints

### Sprint 1 — Base (2026-05-25)

| # | Tarea | Status |
|---|---|---|
| 1.1 | Hook desbloqueado para `proyecto_labo/` | ✅ |
| 1.2 | `git init` + `.gitignore` + `.env.example` | ✅ |
| 1.3 | `requirements.txt` + `CLAUDE.md` actualizado | ✅ |
| 1.4 | Unit specs docs/ (4 agentes) | ✅ |
| 1.5 | EC2: carpeta `~/proyecto_spotify/` + deps instaladas | ✅ |
| 1.6 | SCP: subir CSVs Windows → EC2 | ⬜ pendiente |
| 1.7 | `.env` con Bedrock key en EC2 | ⬜ tú lo escribes |
| 1.8 | `agents/00_setup_llm.py` — LLM compartido | ⬜ |
| 1.9 | `agents/01_data_recon.py` — Agente 1 | ⬜ |
| 1.10 | `docs/problem-statement.md` — CRISP-DM formal | ⬜ tú lo validas |
| 1.11 | Push inicial a GitHub `klipso_data_1` | ⬜ |

### Sprint 2 — Agentes 2-4 + pipeline completo

| # | Tarea |
|---|---|
| 2.1 | `agents/02_eda_auto.py` |
| 2.2 | `agents/03_hypothesis.py` |
| 2.3 | `agents/04_business_tx.py` |
| 2.4 | `run_pipeline.py` — orquesta 4 agentes en secuencia |
| 2.5 | Modo A end-to-end (local Windows) |

### Sprint 3 — EC2 + comparativa Bedrock vs Ollama

| # | Tarea |
|---|---|
| 3.1 | Clonar repo en EC2 + configurar `.env` EC2 |
| 3.2 | Correr pipeline Modo B (EC2 + Bedrock) |
| 3.3 | Cambiar `get_llm()` → Ollama → Modo C |
| 3.4 | Documentar diferencias A vs B vs C (contenido) |

### Sprint 4 — Bedrock Agents (bonus)

| # | Tarea |
|---|---|
| 4.1 | Crear Bedrock Agent en consola AWS |
| 4.2 | Action group: llama al brief editorial como Lambda |
| 4.3 | "ChatBot editorial" para el equipo |
| 4.4 | Post/video: LangChain vs Bedrock Agents |

---

## Pendientes que requieren input de la PM

1. **problem-statement.md** — necesito que confirmes: QUIÉN / QUÉ / POR QUÉ / MÉTRICA DE ÉXITO
2. **Bedrock API key en EC2** — la escribes tú vía SSH (no la compartes en chat)
3. **AWS region** — confirmar si es `us-east-1` o cambiar en `.env`
4. **Validar brief editorial** — al final del Sprint 2, tú decides si el output es útil para un equipo real
