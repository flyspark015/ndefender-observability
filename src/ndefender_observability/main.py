"""FastAPI entrypoint for observability service."""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response

from .collectors.aggregator_http import AggregatorHttpCollector
from .collectors.pi_stats import PiStatsCollector
from .collectors.system_controller_http import SystemControllerHttpCollector
from .config import AppConfig, load_config
from .health.compute import compute_deep_health, compute_status_snapshot
from .metrics.registry import init_metrics, render_metrics, update_subsystem_metrics
from .state import ObservabilityState
from .version import GIT_SHA, VERSION


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_metrics(VERSION, GIT_SHA)
    app.state.config = load_config()
    app.state.store = ObservabilityState()
    app.state.pi_collector = PiStatsCollector()
    app.state.tasks = []

    agg_collector = AggregatorHttpCollector(
        app.state.config.backend_aggregator.base_url,
        interval_s=app.state.config.polling.aggregator_s,
    )
    app.state.aggregator_collector = agg_collector
    app.state.tasks.append(asyncio.create_task(agg_collector.run(app.state.store)))

    system_collector = SystemControllerHttpCollector(
        app.state.config.system_controller.base_url,
        interval_s=app.state.config.polling.system_controller_s,
    )
    app.state.system_controller_collector = system_collector
    app.state.tasks.append(asyncio.create_task(system_collector.run(app.state.store)))
    yield
    agg_collector.stop()
    system_collector.stop()
    for task in app.state.tasks:
        task.cancel()
    await asyncio.gather(*app.state.tasks, return_exceptions=True)


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
    collector: PiStatsCollector = app.state.pi_collector
    try:
        collector.collect()
    except Exception:
        pass
    update_subsystem_metrics(app.state.store)
    data = render_metrics()
    return Response(content=data, media_type="text/plain; version=0.0.4")
