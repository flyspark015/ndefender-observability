"""FastAPI entrypoint for observability service."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response

from .metrics.registry import init_metrics, render_metrics
from .version import GIT_SHA, VERSION

app = FastAPI(title="N-Defender Observability", version=VERSION)


@app.on_event("startup")
def _startup() -> None:
    init_metrics(VERSION, GIT_SHA)


@app.get("/api/v1/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.get("/metrics")
def metrics() -> Response:
    data = render_metrics()
    return Response(content=data, media_type="text/plain; version=0.0.4")
