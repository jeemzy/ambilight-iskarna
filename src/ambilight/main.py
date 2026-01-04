"""Application entrypoint."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

import uvicorn

from ambilight.config.env_loader import load_env_config
from ambilight.config.json_store import JsonConfigStore
from ambilight.config.models import AppConfig
from ambilight.ha.client import HomeAssistantClient
from ambilight.mjpeg.publisher import MjpegPreviewPublisher
from ambilight.services.sync_controller import SyncController
from ambilight.state.runtime_state import RuntimeState
from ambilight.state.zone_state import ZoneRect
from ambilight.utils.logging import configure_logging
from ambilight.web.bridge import Bridge
from ambilight.web.lan_ui_server import LanUiServer
from ambilight.web.local_api import LocalApiServer
from ambilight.capture.win_capture import WinCaptureFrameProvider


async def _serve(app, host: str, port: int) -> None:
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def main() -> None:
    configure_logging()
    env = load_env_config()
    config_dir = Path.cwd() / "config"
    store = JsonConfigStore(config_dir)
    default = AppConfig(
        display_id=1,
        zone=ZoneRect(x=0, y=0, width=100, height=100),
        preview_interval_sec=1.0,
        analysis_hz=25.0,
        dark_threshold=0.1,
        saturation_boost=0.2,
    )
    config = store.load_config(default)

    ha_client = HomeAssistantClient(
        base_url=env.ha_base_url, token=env.ha_token, entity_id=env.ha_entity_id
    )
    frame_provider = WinCaptureFrameProvider(scale=0.5)
    publisher = MjpegPreviewPublisher()
    runtime_state = RuntimeState()
    controller = SyncController(
        frame_provider=frame_provider,
        ha_client=ha_client,
        publisher=publisher,
        runtime_state=runtime_state,
        config=config,
    )

    local_api = LocalApiServer(store, controller, runtime_state, publisher)
    bridge = Bridge(
        local_api_base="http://127.0.0.1:8765",
        allowed_paths={
            "/api/status",
            "/api/displays",
            "/api/config",
            "/api/presets",
            "/api/sync/start",
            "/api/sync/pause",
            "/api/sync/resume",
            "/api/sync/stop",
        },
        allowed_prefixes=(
            "/api/presets/",
        ),
    )
    ui_server = LanUiServer(bridge, Path(__file__).parent / "web" / "static")

    local_port = int(os.getenv("LOCAL_API_PORT", "8765"))
    ui_port = int(os.getenv("LAN_UI_PORT", "8080"))

    try:
        await asyncio.gather(
            _serve(local_api.app, "127.0.0.1", local_port),
            _serve(ui_server.app, "0.0.0.0", ui_port),
        )
    finally:
        await controller.stop()
        await ha_client.turn_off()
        await ha_client.close()


if __name__ == "__main__":
    asyncio.run(main())
