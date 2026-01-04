"""Localhost-only control API."""

from __future__ import annotations

from dataclasses import asdict
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ambilight.config.json_store import AppConfig, JsonConfigStore, Preset
from ambilight.mjpeg.publisher import MjpegPreviewPublisher
from ambilight.services.sync_controller import SyncController
from ambilight.state.runtime_state import RuntimeState
from ambilight.state.zone_state import ZoneRect


class ZoneRectModel(BaseModel):
    x: int
    y: int
    width: int
    height: int


class AppConfigModel(BaseModel):
    display_id: int = Field(..., ge=1, le=2)
    zone: ZoneRectModel
    preview_interval_sec: float = Field(..., ge=0.5, le=2.0)
    analysis_hz: float
    dark_threshold: float = Field(..., ge=0.0, le=1.0)
    saturation_boost: float = Field(..., ge=0.0, le=1.0)


class PresetModel(BaseModel):
    name: str
    display_id: int = Field(..., ge=1, le=2)
    zone: ZoneRectModel
    preview_interval_sec: float
    analysis_hz: float
    dark_threshold: float
    saturation_boost: float


class DisplayInfo(BaseModel):
    id: int
    name: str
    width: int
    height: int


def _model_to_config(model: AppConfigModel) -> AppConfig:
    zone = ZoneRect(**model.zone.dict())
    return AppConfig(
        display_id=model.display_id,
        zone=zone,
        preview_interval_sec=model.preview_interval_sec,
        analysis_hz=model.analysis_hz,
        dark_threshold=model.dark_threshold,
        saturation_boost=model.saturation_boost,
    )


def _model_to_preset(model: PresetModel) -> Preset:
    zone = ZoneRect(**model.zone.dict())
    return Preset(
        name=model.name,
        display_id=model.display_id,
        zone=zone,
        preview_interval_sec=model.preview_interval_sec,
        analysis_hz=model.analysis_hz,
        dark_threshold=model.dark_threshold,
        saturation_boost=model.saturation_boost,
    )


class LocalApiServer:
    """Local API server binding to 127.0.0.1."""

    def __init__(
        self,
        config_store: JsonConfigStore,
        sync_controller: SyncController,
        runtime_state: RuntimeState,
        publisher: MjpegPreviewPublisher,
    ) -> None:
        self._config_store = config_store
        self._sync_controller = sync_controller
        self._runtime_state = runtime_state
        self._publisher = publisher
        self.app = FastAPI(title="Ambilight Local API")
        self._register_routes()

    def _register_routes(self) -> None:
        app = self.app

        @app.get("/api/status")
        async def get_status() -> dict:
            return {
                "sync_state": asdict(self._runtime_state.sync_state),
                "diagnostics": asdict(self._runtime_state.diagnostics),
            }

        @app.get("/api/displays", response_model=List[DisplayInfo])
        async def list_displays() -> List[DisplayInfo]:
            return [
                DisplayInfo(id=1, name="Display 1", width=0, height=0),
                DisplayInfo(id=2, name="Display 2", width=0, height=0),
            ]

        @app.get("/api/config", response_model=AppConfigModel)
        async def get_config() -> AppConfigModel:
            config = self._config_store.load_config(self._sync_controller.config)
            return AppConfigModel(**asdict(config))

        @app.put("/api/config", response_model=AppConfigModel)
        async def update_config(payload: AppConfigModel) -> AppConfigModel:
            config = _model_to_config(payload)
            self._config_store.save_config(config)
            self._sync_controller.config = config
            return AppConfigModel(**asdict(config))

        @app.get("/api/presets", response_model=List[PresetModel])
        async def list_presets() -> List[PresetModel]:
            presets = self._config_store.load_presets()
            return [PresetModel(**asdict(p)) for p in presets]

        @app.post("/api/presets", status_code=201)
        async def save_preset(payload: PresetModel) -> dict:
            preset = _model_to_preset(payload)
            self._config_store.save_preset(preset)
            return {"status": "saved"}

        @app.post("/api/presets/{name}/load", response_model=AppConfigModel)
        async def load_preset(name: str) -> AppConfigModel:
            presets = {p.name: p for p in self._config_store.load_presets()}
            if name not in presets:
                raise HTTPException(status_code=404, detail="Preset not found")
            preset = presets[name]
            config = AppConfig(
                display_id=preset.display_id,
                zone=preset.zone,
                preview_interval_sec=preset.preview_interval_sec,
                analysis_hz=preset.analysis_hz,
                dark_threshold=preset.dark_threshold,
                saturation_boost=preset.saturation_boost,
            )
            self._config_store.save_config(config)
            self._sync_controller.config = config
            return AppConfigModel(**asdict(config))

        @app.delete("/api/presets/{name}", status_code=204)
        async def delete_preset(name: str) -> None:
            self._config_store.delete_preset(name)

        @app.post("/api/sync/start")
        async def start_sync() -> dict:
            await self._sync_controller.start()
            return {"status": "started"}

        @app.post("/api/sync/pause")
        async def pause_sync() -> dict:
            await self._sync_controller.pause()
            return {"status": "paused"}

        @app.post("/api/sync/resume")
        async def resume_sync() -> dict:
            await self._sync_controller.resume()
            return {"status": "resumed"}

        @app.post("/api/sync/stop")
        async def stop_sync() -> dict:
            await self._sync_controller.stop()
            return {"status": "stopped"}

        @app.get("/api/preview/stream")
        async def preview_stream() -> StreamingResponse:
            return StreamingResponse(
                self._publisher.stream(),
                media_type="multipart/x-mixed-replace; boundary=frame",
            )
