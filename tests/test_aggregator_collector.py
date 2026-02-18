import asyncio

from ndefender_observability.collectors.aggregator_http import AggregatorHttpCollector
from ndefender_observability.health.model import HealthState
from ndefender_observability.state import ObservabilityState


class ResponseStub:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class ClientStub:
    def __init__(self, responses: dict[str, ResponseStub]):
        self._responses = responses

    async def get(self, endpoint: str):
        if endpoint not in self._responses:
            raise RuntimeError("missing stub")
        return self._responses[endpoint]


def test_aggregator_ok() -> None:
    store = ObservabilityState()
    collector = AggregatorHttpCollector("http://localhost:8000")
    client = ClientStub(
        {
            "/api/v1/health": ResponseStub(200, {"status": "ok"}),
            "/api/v1/status": ResponseStub(200, {"ok": True}),
        }
    )
    asyncio.run(collector._poll_once(store, client))
    state = store.get("aggregator")
    assert state.state == HealthState.OK


def test_aggregator_degraded() -> None:
    store = ObservabilityState()
    collector = AggregatorHttpCollector("http://localhost:8000")
    client = ClientStub(
        {
            "/api/v1/health": ResponseStub(200, {"status": "ok"}),
            "/api/v1/status": ResponseStub(500, {}),
        }
    )
    asyncio.run(collector._poll_once(store, client))
    state = store.get("aggregator")
    assert state.state == HealthState.DEGRADED


def test_aggregator_offline() -> None:
    store = ObservabilityState()
    collector = AggregatorHttpCollector("http://localhost:8000")
    client = ClientStub(
        {
            "/api/v1/health": ResponseStub(503, {}),
            "/api/v1/status": ResponseStub(503, {}),
        }
    )
    asyncio.run(collector._poll_once(store, client))
    state = store.get("aggregator")
    assert state.state == HealthState.OFFLINE
