from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from ambilight.config.json_store import AppConfig, JsonConfigStore
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


def _make_client() -> TestClient:
    store = JsonConfigStore(Path("tests/.config_presets"))
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


def test_presets_crud() -> None:
    client = _make_client()
    preset = {
        "name": "test",
        "display_id": 1,
        "zone": {"x": 0, "y": 0, "width": 10, "height": 10},
        "preview_interval_sec": 1.0,
        "analysis_hz": 25.0,
        "dark_threshold": 0.1,
        "saturation_boost": 0.2,
    }
    assert client.post("/api/presets", json=preset).status_code == 201
    presets = client.get("/api/presets").json()
    assert any(p["name"] == "test" for p in presets)
    loaded = client.post("/api/presets/test/load").json()
    assert loaded["display_id"] == 1
    assert client.delete("/api/presets/test").status_code == 204
