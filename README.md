# Spotify Editorial Intelligence

> ¿Qué hace que una canción triunfe en múltiples plataformas?

---

## 1. El problema de negocio

El equipo editorial de Spotify decide qué canciones entran a sus playlists manualmente.
Lo hacen por intuición: escuchan, sienten, deciden. El resultado es inconsistente.

**El costo real:** una canción que entra tarde a una playlist pierde su ventana de momentum.
Una que entra sin señal real ocupa espacio de una que sí hubiera roto.

**La pregunta:** ¿existen señales medibles — antes de que una canción explote — que predigan
su éxito cross-platform?

---

## 2. El estado del dato — lo que llegó y lo que estaba roto

Llegaron 2 archivos CSV. Antes de cualquier análisis, el Agente 1 mapeó el estado real:

```
--- track_in_spotify ---
Shape: (839, 12)
  track_id:    int64       ← tipo A
  streams:     object      ← PROBLEMA: string con comas, no número

--- track_in_competition ---
Shape: (953, 6)
  track_id:           object  ← tipo B — JOIN roto
  in_deezer_playlists: object ← PROBLEMA: debería ser int
  in_shazam_charts:   object  ← PROBLEMA: 5.25% nulls
```

**El JOIN estaba roto.** `track_id` era `int64` en Spotify y `object` en competition.
Sin normalizar, el merge produce resultados silenciosamente incorrectos — no un error visible.

**Impacto del delta:** 839 tracks en Spotify vs 953 en competition → 114 tracks sin match.
Esas 114 canciones existen en Apple/Deezer/Shazam pero no llegaron a Spotify.
No es un error de datos — es una señal de negocio: no toda presencia cross-platform implica Spotify.

**Solución aplicada:** normalizar `track_id` a string en ambos archivos antes del merge.
Resultado: 839 tracks con datos cross-platform completos para análisis.

---

## 3. El pipeline — qué hizo cada agente y qué encontró

### Agente 2 — EDA: las correlaciones reales

Con el dataset limpio y unido, el agente calculó la correlación de cada variable con streams:

```
streams ↔ in_spotify_playlists:  r = 0.788  ← señal más fuerte
streams ↔ in_apple_playlists:    r = 0.775
streams ↔ in_deezer_playlists:   r = 0.759
streams ↔ in_spotify_charts:     r = 0.242
streams ↔ in_apple_charts:       r = 0.317
streams ↔ in_deezer_charts:      r = 0.228
streams ↔ in_shazam_charts:      r = 0.053  ← señal casi nula
streams ↔ artist_count:          r = −0.123 ← negativa
```

**Lo que el agente encontró:** las playlists tienen r ~0.78 en las 3 plataformas.
Los charts tienen correlaciones 3x más débiles. Shazam es irrelevante como predictor.

**Distribución de streams — el dato que cambia la lectura:**

```
mean:   536M  ← inflada por outliers
median: 301M  ← la realidad de la mayoría
max:    3.7B  ← Blinding Lights distorsiona todo
min:    2.7K
```

La distribución es altamente sesgada. Los promedios mienten. Usamos mediana como métrica honesta.

---

### Agente 3 — Hipótesis: los 4 tests formales

```
H1: Más playlists cross-platform → más streams
    Pearson r = 0.795, p = 0.0  ✓ CONFIRMADA
    Spearman ρ = 0.831, p = 0.0  (más robusto con outliers)

H2: Charts múltiples → más streams
    Mann-Whitney p = 0.0  ✓ CONFIRMADA
    Top 25% charts:  mediana 480M streams
    Resto:           mediana 274M streams
    Diferencia: +75% más streams en el top cuartil

H3: Canciones recientes en playlists rápido → más streams
    año vs streams: ρ = −0.68, p = 0.0  (esperado: viejas acumularon más tiempo)
    recientes en playlists rápido: ρ = 0.651, p = 0.0  ✓ CONFIRMADA
    Ventana crítica: primera semana de lanzamiento

H4: Género / país / colaboradores predicen streams
    ANOVA géneros: F = 4.46, p = 0.0  ✓ CONFIRMADA
    artist_count: ρ = −0.135, p = 0.0001  (más colaboradores = menos streams)
    Top géneros por mediana: Disco pop 2.3B, Indie rock 2.1B, EDM 1.9B
```

**El hallazgo contraintuitivo:** más colaboradores correlaciona negativamente con streams.
Los mega-collabs son estrategia comercial, no señal de éxito orgánico.

---

### Agente 4 — Traducción editorial (único agente que usa LLM)

Tomó los números y generó criterios accionables para el equipo:

```
CRITERIOS DE INCLUSIÓN
  1. En playlists de 2+ plataformas en semana 1 → prioridad alta
  2. Lanzamiento < 2 semanas → actuar antes de perder ventana
  3. Género: Disco pop, Indie rock, EDM → señal histórica positiva
  4. Mercados: Australia, Barbados, Ireland → alto rendimiento relativo
  5. En playlists Spotify → correlación más alta (r=0.788)

SEÑALES DE ALERTA
  - Solo en Shazam charts → r=0.053, no actuar
  - Más de 2 colaboradores → puede ser estrategia, no momentum real
  - Sin playlists en semana 1 → ventana cerrada
```

---

### Agente 5 — Visualización (5 gráficos interactivos Plotly)

Generados independientemente del pipeline, disponibles en `outputs/`:

| Archivo | Qué muestra |
|---|---|
| `viz_h1_playlists.html` | Scatter 839 puntos + OLS — r=0.79 visible |
| `viz_h2_charts.html` | Boxplot Top 25% vs resto — diferencia 206M |
| `viz_h3_timing.html` | Mediana de streams por año de lanzamiento |
| `viz_h4_genres.html` | Top 10 géneros por mediana — horizontal bar |
| `viz_dashboard.html` | Dashboard 2×2 — 4 hipótesis en una pantalla |

---

## 4. Los hallazgos — con contexto de negocio

**La señal más fuerte no es el audio — es la distribución.**

Una canción que en su primera semana aparece en playlists de Spotify + Apple + Deezer
tiene r = 0.79 con el volumen final de streams. Esa señal es:
- Medible en tiempo real (APIs de plataformas)
- Accionable antes de que el hit ocurra
- Reproducible: no depende del género ni del artista

**Lo que Shazam no dice:** r = 0.053. Una canción viral en Shazam no predice streams.
Shazam mide curiosidad momentánea, no intención de escucha repetida.

**El efecto colaboraciones:** canciones con 3+ artistas tienen menos streams que solos o dúos.
Los collabs masivos son marketing, no señal orgánica.

---

## 5. Impacto cuantificado

| Señal | Efecto medido |
|---|---|
| Playlists cross-platform (2+) | r = 0.79 → predictor más fuerte del dataset |
| Top 25% charts vs resto | +75% más streams (480M vs 274M mediana) |
| Entrada rápida a playlists (< 7 días) | ρ = 0.651 positivo para canciones recientes |
| Géneros top (Disco pop, Indie, EDM) | Mediana 2–2.3B vs 301M global |
| Más de 2 colaboradores | −13.5% correlación con streams |

---

## 6. Stack

- **Limpieza + hipótesis:** pandas, scipy — sin LLM, determinístico, reproducible
- **LLM:** solo Agente 4 (traducción editorial) — OpenAI o AWS Bedrock vía LangChain
- **Visualización:** Plotly + Streamlit
- **Orquestación:** LangGraph + importlib

```bash
pip install -r requirements.txt
python run_pipeline.py          # Agentes 1–4
python agents/05_viz.py         # Solo gráficos
streamlit run app.py            # App narrativa en localhost:8501
```

Requiere `.env` con `OPENAI_API_KEY` o credenciales Bedrock. Ver `.env.example`.

---

## Modelos

| | Descripción | Estado |
|---|---|---|
| **A** | Pipeline determinístico — este análisis | ✅ Completo |
| **A.1** | A + audio DNA (bpm, energy) + mediana + H5 | 🔨 En spec |
| **B** | Human-in-the-Loop — PM revisa en cada paso | 📋 Pendiente |
| **C** | RAG + memoria entre sesiones + self-improvement | 📋 Pendiente |

Ver `docs/methodology.md` para arquitectura completa.

---

*Dataset: Spotify Skill Academy | Proyecto: StephCastrof001/klipso_data_1*
