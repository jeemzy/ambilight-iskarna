from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from ambilight.config.json_store import JsonConfigStore
from ambilight.config.models import AppConfig
from ambilight.mjpeg.publisher import MjpegPreviewPublisher
from ambilight.state.runtime_state import RuntimeState
from ambilight.state.zone_state import ZoneRect
from ambilight.web.local_api import LocalApiServer


class StubSyncController:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    async def start(self) -> None:
        return None

    async def pause(self) -> None:
        return None

    async def resume(self) -> None:
        return None

    async def stop(self) -> None:
        return None


def _make_app() -> TestClient:
    store = JsonConfigStore(Path("tests/.config"))
    config = AppConfig(
        display_id=1,
        zone=ZoneRect(x=0, y=0, width=10, height=10),
        preview_interval_sec=1.0,
        analysis_hz=25.0,
        dark_threshold=0.1,
        saturation_boost=0.2,
    )
    controller = StubSyncController(config)
    runtime = RuntimeState()
    publisher = MjpegPreviewPublisher()
    server = LocalApiServer(store, controller, runtime, publisher)
    return TestClient(server.app)


def test_status_endpoint() -> None:
    client = _make_app()
    response = client.get("/api/status")
    assert response.status_code == 200
    payload = response.json()
    assert "sync_state" in payload
    assert "diagnostics" in payload


def test_displays_endpoint() -> None:
    client = _make_app()
    response = client.get("/api/displays")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_config_round_trip() -> None:
    client = _make_app()
    response = client.get("/api/config")
    assert response.status_code == 200
    payload = response.json()
    payload["preview_interval_sec"] = 1.5
    updated = client.put("/api/config", json=payload)
    assert updated.status_code == 200
    assert updated.json()["preview_interval_sec"] == 1.5


def test_sync_controls() -> None:
    client = _make_app()
    assert client.post("/api/sync/start").status_code == 200
    assert client.post("/api/sync/pause").status_code == 200
    assert client.post("/api/sync/resume").status_code == 200
    assert client.post("/api/sync/stop").status_code == 200
