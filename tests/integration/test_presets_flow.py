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


def test_preset_save_load_roundtrip() -> None:
    store = JsonConfigStore(Path("tests/.config_flow"))
    config = AppConfig(
        display_id=2,
        zone=ZoneRect(x=5, y=6, width=7, height=8),
        preview_interval_sec=1.0,
        analysis_hz=25.0,
        dark_threshold=0.2,
        saturation_boost=0.3,
    )
    controller = StubSyncController(config)
    runtime = RuntimeState()
    publisher = MjpegPreviewPublisher()
    server = LocalApiServer(store, controller, runtime, publisher)
    client = TestClient(server.app)

    preset = {
        "name": "roundtrip",
        "display_id": 2,
        "zone": {"x": 5, "y": 6, "width": 7, "height": 8},
        "preview_interval_sec": 1.0,
        "analysis_hz": 25.0,
        "dark_threshold": 0.2,
        "saturation_boost": 0.3,
    }
    client.post("/api/presets", json=preset)
    loaded = client.post("/api/presets/roundtrip/load").json()
    assert loaded["display_id"] == 2
    assert loaded["zone"]["width"] == 7
