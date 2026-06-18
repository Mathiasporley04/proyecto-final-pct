# Estado del proyecto — sesion 2026-06-18 (web FastAPI + pulido de UI)

## Resumen
La UI dejo de ser Streamlit y ahora es un **servidor web FastAPI** que sirve HTML
server-rendered (ver `docs/adr/004-fastapi-reemplaza-streamlit.md`). Toda la logica
de dominio (fuentes, metricas, modelos) se reutilizo sin cambios; solo cambio la capa
de presentacion. Esta sesion fue de **pulido visual y de marca** sobre esa base.

**Ubicacion canonica:** `C:\Users\mathi\Desktop\facultad\Programaciòn cientifica y tecnica\PROYECTO FINAL 2.0\`.
La aplicacion corre en `http://localhost:8000`.

## Stack (.venv, Python 3.14)
fastapi, uvicorn[standard], jinja2, pandas, numpy, pydantic, aiohttp, requests,
python-dateutil, yfinance. Dev: pytest, pytest-asyncio, ruff, mypy.

Se quitaron `streamlit` y `plotly`. Los graficos de linea usan **TradingView
Lightweight Charts** (JS self-hosted en `web/static/`, ~160 KB, no es dependencia
de Python).

## Comandos
```bash
.venv\Scripts\activate
# Servidor web en localhost:8000
.venv\Scripts\python.exe -m observatorio.web
# o, en desarrollo, con autorecarga al editar:
.venv\Scripts\python.exe -m uvicorn observatorio.web.app:app --reload
# Tests (55, corren offline)
.venv\Scripts\python.exe -m pytest tests -q
# Benchmark sync vs async
.venv\Scripts\python.exe scripts\benchmark_async.py
```

## Vistas
- `/` — **Panel central** (antes "Panorama"): snapshot de los 3 mercados (dolar UY,
  Bitcoin, S&P 500) + comparativa normalizada BTC vs S&P 500 + noticias.
- `/comparar` — tres bloques base 100: cripto vs cripto, S&P vs S&P, y un bloque
  mixto. El selector del bloque mixto esta dividido en dos paneles (Cripto | S&P),
  cada uno con scroll propio.
- `/salud` — healthcheck JSON.

## Cambios de esta sesion (2026-06-18)
1. **Selector mixto en dos paneles** (`comparar.html` + `.picker-split` en CSS):
   Cripto y S&P lado a lado, cada uno con scroll propio (antes las ~100 criptos
   tapaban el grupo S&P en una sola lista larga).
2. **Scrollbars finos y oscuros** (CSS global): reemplazan las barras blancas
   nativas de Windows, que desentonaban con el tema oscuro. Se elimino tambien el
   scroll horizontal espurio de los paneles (`overflow: hidden auto`).
3. **Correlacion eliminada**: se quito el heatmap del bloque mixto y su codigo de
   soporte (`heatmap_correlacion` en `web/graficos.py`, parametro `correlacion`).
   La metrica de dominio `matriz_correlacion` sigue en `metricas/` con sus tests.
4. **Sidebar neutro**: el token `--sidebar-primary` en modo oscuro paso de un azul
   saturado a gris neutro, para entrar en la paleta gris del resto del tema.
5. **Rebrand**:
   - Logo: emoji 📊 -> icono SVG de velas (candlestick), tambien en el favicon.
   - "Panorama" -> "Panel central" (nav, titulo, breadcrumb, h1). Identificadores
     internos (`vista='panorama'`, nombres de funcion, ids) sin tocar.
   - Se quito "LATAM" de la marca, los titulos de pestana y el `title` de FastAPI.
   - Marca estatica: sin el chevron, sin el chip de fondo del logo y sin hover
     (la marca no es clickeable, no debe parecer un control).

## Estructura actual
```
src/observatorio/
├── core/        (Activo, FuenteDatos, Mercado, tipos)
├── activos/     (Cripto, AccionUSA, Divisa)
├── fuentes/     (CoinGecko, Yahoo, DolarApi UY + cache + registro + esquemas)
├── metricas/    (6 funciones puras: rendimiento, volatilidad, correlacion, ...)
├── normalizadores/ (regex: tickers, fechas, validadores)
└── web/         (FastAPI: app, datos, graficos, noticias, sp500, glosario,
                  templates/ Jinja2, static/ CSS + Lightweight Charts)
tests/   (55 tests)
scripts/ (benchmark_async.py)
docs/    (etica, glosario, decisiones, adr/, portafolio/, peer-review/)
```
La migracion a FastAPI elimino los modulos que ya no se usan: `ui/` (Streamlit),
`persistencia/`, `core/portfolio.py`, `activos/accion_arg.py`, `fuentes/data912.py`
y sus tests (de ahi que el conteo bajara de 76 a 55).

## Decisiones de dominio que siguen vigentes
- Idioma del dominio: espanol.
- Yahoo se mantiene sync (yfinance bloqueante); corre en thread cuando se llama async.
- CoinGecko free tier devuelve 429 con varias cripto en paralelo: aislado via
  `FuenteIndisponible` por simbolo.
- Cero `print()` en codigo de aplicacion; cada metrica es funcion pura (sin estado/red).

## Tests
**55 pasando, 0 fallos** (~0.6s, sin red). Cubren metricas, normalizadores, fuentes
(DTOs Pydantic), activos (polimorfismo) y mercado.

## Pendientes no criticos
- Tasa ARS real (MEP) — quedo fuera del alcance de la version web actual.
- Integrar `validar_cotizacion` (Pydantic) desde las fuentes (hoy construyen
  `Cotizacion` directo).
- Vista "Acerca de" (mencionada en `docs/etica.md` como "en construccion").
- Tests de integracion contra APIs reales (skip en CI).

## Como retomar
1. `cd "C:\Users\mathi\Desktop\facultad\Programaciòn cientifica y tecnica\PROYECTO FINAL 2.0"`.
2. `.\.venv\Scripts\activate`.
3. Levantar: `.\.venv\Scripts\python.exe -m observatorio.web` y abrir `http://localhost:8000`.
4. Si el puerto 8000 esta ocupado, matar el `python.exe` que lo escucha
   (`Get-NetTCPConnection -LocalPort 8000 | % { Stop-Process -Id $_.OwningProcess -Force }`).
5. Tests: `.\.venv\Scripts\python.exe -m pytest tests -q` (debe dar 55 passed).
