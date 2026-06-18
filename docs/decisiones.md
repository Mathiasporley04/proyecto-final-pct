# Bitacora de decisiones tecnicas

## Stack
- **FastAPI + uvicorn + Jinja2** para la UI web: HTML server-rendered en `localhost:8000`. Reemplazo a Streamlit (ver ADR-004); da control total del layout, URLs y presentacion. (Antes fue Streamlit por su bajo costo de desarrollo.)
- **TradingView Lightweight Charts** (JS self-hosted, ~160 KB) para los graficos de linea: crosshair, escala con ultimo valor, zoom/pan. Reemplazo a Plotly (bundle ~4.8 MB) por costo de carga/render.
- **Pydantic v2** para validacion de datos en frontera con APIs externas (planeado, pendiente de aplicarse a respuestas concretas).
- **aiohttp** + **asyncio.gather** para paralelismo de fuentes. Yahoo se ejecuta en thread porque `yfinance` es sincrono.
- **cryptography (Fernet)** para portfolio: AES-128-CBC + HMAC-SHA256 en formato versionado. (La feature de portfolio se removio en la migracion web; ver ADR-004.)

## Hallazgos descubiertos durante el desarrollo
- **CoinGecko free tier** devuelve 429 cuando se hacen 3+ requests cripto en paralelo. Manejado con `FuenteIndisponible` por simbolo, sin tumbar las otras fuentes. Mitigacion futura: serializar las cripto o reducir la frecuencia.
- **DolarApi UY**: endpoint `https://uy.dolarapi.com/v1/cotizaciones`. La cotizacion BROU se extrae filtrando por nombre.

## Convenciones reforzadas
- Idioma del dominio en espanol.
- Cero `print()` en codigo de aplicacion.
- Cada metrica es funcion pura, sin acceso a estado, sin red.
- No `except Exception` salvo en bordes externos.

## Capa web y marca (post ADR-004, 2026-06)
- **Cache de UI** de Streamlit (`st.cache_data`) reemplazado por el cache TTL que las
  fuentes ya tenian (`@cache_ttl`) + un hilo de precalentamiento al arranque.
- **Correlacion removida** de la UI: el heatmap del bloque mixto se quito junto con su
  codigo de soporte. La metrica `matriz_correlacion` se conserva en `metricas/`. El
  bloque mixto queda como comparativa base 100.
- **Marca neutra**: la paleta es grayscale (shadcn neutral). Se quito el unico color
  saturado (el azul del sidebar en modo oscuro) para que el item activo y el logo
  entren en la misma paleta gris.
- **Selector mixto en dos columnas** (Cripto | S&P) con scroll independiente: con ~100
  criptos en una sola lista, el grupo S&P quedaba enterrado.
- **Scrollbars** finos y tematizados (no los nativos blancos de Windows).
- **Naming**: "Panorama" -> "Panel central" y se quito "LATAM" de la marca/titulos
  (solo texto visible; los identificadores internos no se tocaron).
