"""Servidor web (FastAPI) del Observatorio Financiero LATAM.

Sirve HTML server-rendered. Los graficos de lineas se dibujan con TradingView
Lightweight Charts y la correlacion con una tabla-heatmap (sin librerias
pesadas). Las fuentes se consultan en paralelo. Ver ADR-004.

Ejecutar:
    python -m observatorio.web
    # o, con autoreload en desarrollo:
    uvicorn observatorio.web.app:app --reload
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from observatorio.metricas import (
    calcular_drawdown_maximo,
    calcular_rendimiento_porcentual,
    calcular_volatilidad,
    clasificar_volatilidad,
)
from observatorio.web.datos import (
    PERIODOS_COMPARAR,
    PERIODOS_PANORAMA,
    cotizaciones_panorama,
    iniciar_precalentamiento,
    series_en_paralelo,
    universo_disponible,
)
from observatorio.web.glosario import GLOSARIO
from observatorio.web.graficos import heatmap_correlacion, serie_payload

_AQUI = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(_AQUI / "templates"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Mantener el cache caliente desde el arranque (evita el lag inicial de 2-3s).
    iniciar_precalentamiento()
    yield


app = FastAPI(title="Observatorio Financiero LATAM", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(_AQUI / "static")), name="static")

# Series fijas que dibuja el panorama (comparativa rapida cripto vs bolsa USA).
_SERIES_PANORAMA: dict[str, tuple[str, str]] = {
    "BTC": ("cripto", "BTC"),
    "S&P 500": ("usa", "^GSPC"),
}

_DISCLAIMER = (
    "Producto informativo y educativo. No constituye asesoramiento financiero. "
    "Rendimientos pasados no garantizan rendimientos futuros."
)


@app.get("/", response_class=HTMLResponse)
def panorama(request: Request, dias: int = 30):
    """Snapshot de los cuatro mercados + comparativa normalizada."""
    if dias not in PERIODOS_PANORAMA.values():
        dias = 30

    tarjetas = cotizaciones_panorama()
    items = [(nombre, clave, simbolo) for nombre, (clave, simbolo) in _SERIES_PANORAMA.items()]
    series_fechas, series_precios, errores = series_en_paralelo(items, dias)
    chart = serie_payload(series_fechas, series_precios) if series_precios else None

    return templates.TemplateResponse(
        request,
        "panorama.html",
        {
            "vista": "panorama",
            "tarjetas": tarjetas,
            "periodos": PERIODOS_PANORAMA,
            "dias": dias,
            "chart": chart,
            "errores": errores,
            "disclaimer": _DISCLAIMER,
        },
    )


@app.get("/comparar", response_class=HTMLResponse)
def comparar(
    request: Request,
    activos: list[str] | None = Query(default=None),
    dias: int = 90,
):
    """Comparacion profunda: evolucion, metricas y correlacion entre activos."""
    if dias not in PERIODOS_COMPARAR.values():
        dias = 90

    universo = universo_disponible()
    INDICE = "usa:^GSPC"
    MAX_ADICIONALES = 4
    # El indice S&P 500 va fijo como base; el usuario agrega hasta 4 activos mas.
    agregados = [v for v in (activos or []) if v in universo and v != INDICE][:MAX_ADICIONALES]
    seleccion = ([INDICE] if INDICE in universo else []) + agregados

    # Listas para el selector (sin el indice, que va fijo), por precio descendente.
    cripto = sorted(
        [(v, it) for v, it in universo.items() if it["grupo"] == "cripto"],
        key=lambda kv: kv[1]["precio"] or 0.0,
        reverse=True,
    )
    sp500 = sorted(
        [(v, it) for v, it in universo.items()
         if it["grupo"] == "sp500" and it["simbolo"] != "^GSPC"],
        key=lambda kv: kv[1]["precio"] if kv[1]["precio"] is not None else -1.0,
        reverse=True,
    )

    items = [(universo[v]["corto"], universo[v]["clave"], universo[v]["simbolo"]) for v in seleccion]
    series_fechas, series_precios, errores = series_en_paralelo(items, dias)

    filas = []
    for label, precios in series_precios.items():
        vol = calcular_volatilidad(precios)
        filas.append(
            {
                "activo": label,
                "rendimiento": round(calcular_rendimiento_porcentual(precios[0], precios[-1]), 2),
                "volatilidad": round(vol, 3),
                "clasificacion": clasificar_volatilidad(vol),
                "peor_caida": round(calcular_drawdown_maximo(precios) * 100, 2),
            }
        )

    chart = serie_payload(series_fechas, series_precios) if series_precios else None
    heatmap = heatmap_correlacion(series_precios) if len(series_precios) >= 2 else None

    return templates.TemplateResponse(
        request,
        "comparar.html",
        {
            "vista": "comparar",
            "cripto": cripto,
            "sp500": sp500,
            "agregados": agregados,
            "max_adic": MAX_ADICIONALES,
            "periodos": PERIODOS_COMPARAR,
            "dias": dias,
            "filas": filas,
            "chart": chart,
            "heatmap": heatmap,
            "errores": errores,
            "glosario": GLOSARIO,
            "disclaimer": _DISCLAIMER,
        },
    )


@app.get("/salud")
def salud():
    """Healthcheck simple."""
    return JSONResponse({"estado": "ok"})


def main() -> None:
    """Punto de entrada para `python -m observatorio.web`."""
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
