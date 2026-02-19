"""FastAPI entrypoint for observability service."""

import asyncio
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response

from .collectors.aggregator_http import AggregatorHttpCollector
from .collectors.jsonl_tail import JsonlTailCollector
from .collectors.pi_stats import PiStatsCollector
from .collectors.system_controller_http import SystemControllerHttpCollector
from .config import AppConfig, load_config
from .diagnostics import DiagnosticsOptions, create_bundle
from .health.compute import compute_deep_health, compute_status_snapshot
from .metrics.registry import init_metrics, render_metrics, update_subsystem_metrics
from .state import ObservabilityState
from .utils.http import RateLimiter, get_client_key
from .version import GIT_SHA, VERSION


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_metrics(VERSION, GIT_SHA)
    app.state.config = load_config()
    app.state.store = ObservabilityState()
    app.state.pi_collector = PiStatsCollector()
    app.state.tasks = []
    app.state.rate_limiter = RateLimiter(
        app.state.config.rate_limit.max_requests,
        app.state.config.rate_limit.window_s,
    )
    app.state.diag_last_ts_ms = 0

    disable_collectors = os.getenv("NDEFENDER_OBS_DISABLE_COLLECTORS") == "1"
    if "PYTEST_CURRENT_TEST" in os.environ:
        disable_collectors = True

    if not disable_collectors:
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

        antsdr_collector = JsonlTailCollector(
            subsystem="antsdr",
            path=app.state.config.jsonl.antsdr_path,
            event_types=["RF_CONTACT_NEW", "RF_CONTACT_UPDATE", "RF_CONTACT_LOST"],
            interval_s=app.state.config.polling.antsdr_jsonl_s,
            stale_after_s=app.state.config.thresholds.stale_after_s.antsdr,
        )
        app.state.antsdr_collector = antsdr_collector
        app.state.tasks.append(asyncio.create_task(antsdr_collector.run(app.state.store)))

        remoteid_collector = JsonlTailCollector(
            subsystem="remoteid",
            path=app.state.config.jsonl.remoteid_path,
            event_types=[
                "CONTACT_NEW",
                "CONTACT_UPDATE",
                "CONTACT_LOST",
                "TELEMETRY_UPDATE",
                "REPLAY_STATE",
            ],
            interval_s=app.state.config.polling.remoteid_jsonl_s,
            stale_after_s=app.state.config.thresholds.stale_after_s.remoteid,
        )
        app.state.remoteid_collector = remoteid_collector
        app.state.tasks.append(asyncio.create_task(remoteid_collector.run(app.state.store)))
    yield
    if not disable_collectors:
        agg_collector.stop()
        system_collector.stop()
        antsdr_collector.stop()
        remoteid_collector.stop()
    for task in app.state.tasks:
        task.cancel()
    await asyncio.gather(*app.state.tasks, return_exceptions=True)


app = FastAPI(title="N-Defender Observability", version=VERSION, lifespan=lifespan)


def _require_api_key(request: Request, config: AppConfig) -> None:
    if not config.auth.enabled:
        return
    key = request.headers.get("x-api-key") or request.query_params.get("api_key")
    if not key or key != config.auth.api_key:
        raise HTTPException(status_code=401, detail="unauthorized")


def _require_rate_limit(request: Request, config: AppConfig) -> None:
    if not config.rate_limit.enabled:
        return
    limiter: RateLimiter = request.app.state.rate_limiter
    key = get_client_key(request)
    if not limiter.allow(key):
        raise HTTPException(status_code=429, detail="rate limit exceeded")


def _guarded(request: Request) -> None:
    config: AppConfig = request.app.state.config
    _require_api_key(request, config)
    _require_rate_limit(request, config)


def _require_local(request: Request) -> None:
    client = request.client
    host = client.host if client else ""
    if host == "::1" or host.startswith("127."):
        return
    raise HTTPException(status_code=403, detail="local only")


@app.get("/api/v1/health")
def health(request: Request) -> JSONResponse:
    _guarded(request)
    return JSONResponse({"status": "ok"})


@app.get("/api/v1/health/detail")
def health_detail(request: Request) -> JSONResponse:
    _guarded(request)
    store: ObservabilityState = app.state.store
    data = compute_deep_health(store)
    data["status"] = "ok"
    return JSONResponse(data)


@app.get("/api/v1/status")
def status(request: Request) -> JSONResponse:
    _guarded(request)
    store: ObservabilityState = app.state.store
    data = compute_status_snapshot(store)
    return JSONResponse(data)


@app.get("/api/v1/version")
def version(request: Request) -> JSONResponse:
    _guarded(request)
    return JSONResponse({"version": VERSION, "git_sha": GIT_SHA})


@app.get("/api/v1/config")
def config(request: Request) -> JSONResponse:
    _guarded(request)
    cfg: AppConfig = app.state.config
    return JSONResponse(cfg.sanitized())


@app.get("/metrics")
def metrics(request: Request) -> Response:
    _guarded(request)
    collector: PiStatsCollector = app.state.pi_collector
    try:
        collector.collect()
    except Exception:
        pass
    update_subsystem_metrics(app.state.store)
    data = render_metrics()
    return Response(content=data, media_type="text/plain; version=0.0.4")


@app.post("/api/v1/diag/bundle")
def diag_bundle(request: Request) -> JSONResponse:
    _guarded(request)
    _require_local(request)
    cooldown_ms = 60_000
    now_ms = int(time.time() * 1000)
    last_ts = request.app.state.diag_last_ts_ms or 0
    if now_ms - last_ts < cooldown_ms:
        raise HTTPException(status_code=429, detail="cooldown active")
    request.app.state.diag_last_ts_ms = now_ms
    config: AppConfig = request.app.state.config
    base_url = f"http://127.0.0.1:{config.service.port}"
    api_key = config.auth.api_key if config.auth.enabled else None
    options = DiagnosticsOptions(base_url=base_url, api_key=api_key)
    try:
        result = create_bundle(options)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return JSONResponse(
        {"path": result.path, "size_bytes": result.size_bytes, "created_ts": result.created_ts}
    )
