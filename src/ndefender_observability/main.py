"""FastAPI entrypoint for observability service."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response

from .config import AppConfig, load_config
from .health.compute import compute_deep_health, compute_status_snapshot
from .metrics.registry import init_metrics, render_metrics
from .state import ObservabilityState
from .version import GIT_SHA, VERSION


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_metrics(VERSION, GIT_SHA)
    app.state.config = load_config()
    app.state.store = ObservabilityState()
    yield


app = FastAPI(title="N-Defender Observability", version=VERSION, lifespan=lifespan)


@app.get("/api/v1/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.get("/api/v1/health/detail")
def health_detail() -> JSONResponse:
    store: ObservabilityState = app.state.store
    data = compute_deep_health(store)
    data["status"] = "ok"
    return JSONResponse(data)


@app.get("/api/v1/status")
def status() -> JSONResponse:
    store: ObservabilityState = app.state.store
    data = compute_status_snapshot(store)
    return JSONResponse(data)


@app.get("/api/v1/version")
def version() -> JSONResponse:
    return JSONResponse({"version": VERSION, "git_sha": GIT_SHA})


@app.get("/api/v1/config")
def config() -> JSONResponse:
    cfg: AppConfig = app.state.config
    return JSONResponse(cfg.sanitized())


@app.get("/metrics")
def metrics() -> Response:
    data = render_metrics()
    return Response(content=data, media_type="text/plain; version=0.0.4")
