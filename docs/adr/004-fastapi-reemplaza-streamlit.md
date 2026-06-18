# ADR-004: FastAPI reemplaza a Streamlit como capa de UI

**Estado:** aceptado (2026-06). Supera a [ADR-001](001-streamlit-vs-fastapi.md).

## Contexto
ADR-001 eligio Streamlit por su bajo costo de desarrollo. Mas adelante se decidio
servir la aplicacion como un servidor web "normal" (HTML sobre HTTP en localhost),
en lugar de la app Streamlit, para tener control total sobre el layout, las URLs y
la presentacion, sin el chrome propio de Streamlit.

## Decision
Reemplazar la UI de Streamlit por **FastAPI + Jinja2 + Plotly.js**.

- Backend: FastAPI servido con uvicorn, en `src/observatorio/web/`.
- Vistas server-rendered con Jinja2: `/` (Panorama) y `/comparar`.
- Graficos de lineas: **TradingView Lightweight Charts** (Apache-2.0, ~160 KB,
  self-hosted en `web/static/`). Dan crosshair, escala de precios con ultimo valor,
  zoom/pan y area con degradado, con un peso minimo. El backend solo envia el payload
  (series normalizadas) como JSON.
- Correlacion: tabla-heatmap en HTML/CSS (color por celda calculado en Python), sin
  ninguna libreria de graficos.
- Se descarto Plotly (bundle de ~4.8 MB) por costo de carga/render; ver "Consecuencias".
- Las fuentes se consultan en paralelo (thread pool) para reducir la latencia total.
- Controles (periodo, seleccion de activos) son formularios HTML `GET` estandar.

## Razones
- Servidor web estandar HTTP en `localhost:8000`; URLs y HTML bajo nuestro control.
- Reutiliza el 100% de la logica de dominio (fuentes, metricas, modelos) sin cambios.
- FastAPI ya estaba evaluado como alternativa en ADR-001.

## Consecuencias
- Se quitan las dependencias `streamlit` y `plotly`; se agregan `fastapi`, `uvicorn`,
  `jinja2`. Lightweight Charts es JS self-hosted (no es dependencia de Python).
- El caching de UI de Streamlit (`st.cache_data` / `st.cache_resource`) se reemplaza
  por el cache TTL que las fuentes ya implementaban (`@cache_ttl`) mas un singleton
  de fuentes (`functools.lru_cache`).
- Aparece codigo de presentacion propio (templates Jinja2 + CSS) que antes resolvia
  Streamlit; a cambio se gana control fino del layout.
- La documentacion de portafolio anterior que menciona Streamlit queda como registro
  historico del proceso (no se reescribe).

## Actualizacion (2026-06-18)
- Se **removio** la tabla-heatmap de correlacion del bloque mixto (y su codigo de
  soporte `heatmap_correlacion`/`_color_correlacion`). La metrica de dominio
  `matriz_correlacion` sigue en `metricas/`; solo se quito de la UI. El bloque mixto
  queda como comparativa base 100.
- Pulido de UI/marca: selector mixto en dos paneles (Cripto | S&P), scrollbars propios
  del tema, sidebar neutro (sin el azul saturado), logo candlestick, "Panorama" ->
  "Panel central" y se quito "LATAM" de la marca. Detalle en
  `docs/portafolio/etapa-8-web.md`.
