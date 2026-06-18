# Etapa 8 — Capa web (FastAPI) y pulido de UI

Continuacion despues de las etapas 1-7 (con Streamlit). La UI se reescribio como
servidor web; ver `docs/adr/004-fastapi-reemplaza-streamlit.md`. Las etapas 4-7 de
este portafolio quedan como **registro historico** del proceso con Streamlit.

## Migracion a FastAPI
- Backend FastAPI + uvicorn; vistas server-rendered con Jinja2 (`src/observatorio/web/`).
- Graficos de linea con **TradingView Lightweight Charts** (self-hosted, ~160 KB) en
  lugar de Plotly: el backend solo envia el payload de series como JSON.
- Se reutilizo el 100% del dominio (fuentes, metricas, modelos) sin cambios.
- Se quitaron los modulos que ya no se usan: `ui/` (Streamlit), `persistencia/`,
  `core/portfolio.py`, `activos/accion_arg.py`, `fuentes/data912.py` y sus tests
  (el conteo de tests bajo de 76 a 55).

## Pulido de UI (2026-06-18)
- Selector del bloque mixto dividido en dos paneles (Cripto | S&P) con scroll propio,
  para que las ~100 criptos no tapen el grupo S&P.
- Scrollbars finos y acordes al tema oscuro (en vez de las barras blancas nativas de
  Windows); se elimino el scroll horizontal espurio.
- Se removio la tabla-heatmap de correlacion del bloque mixto (la metrica de dominio
  `matriz_correlacion` se conserva en `metricas/`).
- Sidebar con paleta neutra: se quito el azul saturado del item activo y del logo.
- Rebrand: logo candlestick (SVG, tambien favicon), "Panorama" -> "Panel central", y
  se quito "LATAM" de la marca y los titulos.

## Que se aprendio
- Separar **dominio** de **presentacion** permitio cambiar toda la UI (Streamlit ->
  FastAPI) sin tocar fuentes ni metricas: la inversion en funciones puras y modelos
  rindio al momento de migrar.
- Server-rendered + una libreria de grafico liviana (Lightweight Charts) da control
  fino del layout con un peso muy por debajo de un bundle tipo Plotly.

## Tests
55 tests, 0 fallos (corren offline, ~0.6s).
