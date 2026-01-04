"""Sync pipeline orchestrating capture, analysis, and HA updates."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import colorsys
import numpy as np

from ambilight.analysis.dark_detector import DarkDetector
from ambilight.analysis.dominant_color import dominant_color_rgb
from ambilight.analysis.smoothing import SmoothingFilter150ms
from ambilight.capture.frame_provider import FrameProvider
from ambilight.config.json_store import AppConfig
from ambilight.ha.client import HomeAssistantClient
from ambilight.mjpeg.publisher import MjpegPreviewPublisher
from ambilight.state.runtime_state import RuntimeState, SyncStatus
from ambilight.state.zone_state import DisplayBounds, ZoneRect
from ambilight.utils.logging import get_logger


@dataclass
class SyncController:
    frame_provider: FrameProvider
    ha_client: HomeAssistantClient
    publisher: MjpegPreviewPublisher
    runtime_state: RuntimeState
    config: AppConfig

    _analysis_task: Optional[asyncio.Task] = None
    _preview_task: Optional[asyncio.Task] = None
    _running: bool = False

    def __post_init__(self) -> None:
        self._smoothing = SmoothingFilter150ms()
        self._logger = get_logger("ambilight.sync")

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self.runtime_state.sync_state.status = SyncStatus.RUNNING
        self.frame_provider.start(self.config.display_id)
        self.runtime_state.diagnostics.selected_display = self.config.display_id
        self._analysis_task = asyncio.create_task(self._analysis_loop())
        self._preview_task = asyncio.create_task(self._preview_loop())

    async def pause(self) -> None:
        if not self._running:
            return
        self.runtime_state.sync_state.status = SyncStatus.PAUSED
        await self.ha_client.turn_off()

    async def resume(self) -> None:
        if not self._running:
            return
        self.runtime_state.sync_state.status = SyncStatus.RUNNING

    async def stop(self) -> None:
        self._running = False
        self.runtime_state.sync_state.status = SyncStatus.STOPPED
        await self.ha_client.turn_off()
        self.frame_provider.stop()
        if self._analysis_task:
            self._analysis_task.cancel()
        if self._preview_task:
            self._preview_task.cancel()

    async def _preview_loop(self) -> None:
        while self._running:
            frame = self.frame_provider.get_frame()
            if frame is None:
                self.runtime_state.diagnostics.capture_status = "disconnected"
                await asyncio.sleep(self.config.preview_interval_sec)
                continue
            self.runtime_state.diagnostics.capture_status = "connected"
            self.publisher.update_frame(frame.pixels)
            self.runtime_state.diagnostics.preview_fps = 1.0 / self.config.preview_interval_sec
            await asyncio.sleep(self.config.preview_interval_sec)

    async def _analysis_loop(self) -> None:
        interval = 1.0 / max(1.0, self.config.analysis_hz)
        dark_detector = DarkDetector(self.config.dark_threshold)
        while self._running:
            if self.runtime_state.sync_state.status != SyncStatus.RUNNING:
                await asyncio.sleep(interval)
                continue
            frame = self.frame_provider.get_frame()
            if frame is None:
                self.runtime_state.diagnostics.capture_status = "disconnected"
                await asyncio.sleep(interval)
                continue
            self.runtime_state.diagnostics.capture_status = "connected"
            zone = self._clamp_zone(self.config.zone, frame.pixels)
            self.runtime_state.diagnostics.zone = zone
            cropped = frame.pixels[zone.y : zone.y + zone.height, zone.x : zone.x + zone.width]
            color = dominant_color_rgb(cropped)
            boosted = self._boost_saturation(color, self.config.saturation_boost)
            smoothed = self._smoothing.update(boosted, frame.timestamp)
            self.runtime_state.diagnostics.analysis_hz = self.config.analysis_hz
            self.runtime_state.diagnostics.latency_ms = (
                datetime.utcnow() - frame.timestamp
            ).total_seconds() * 1000.0
            self.runtime_state.sync_state.last_color_rgb = smoothed
            self.runtime_state.sync_state.last_update_ts = frame.timestamp
            hsv = colorsys.rgb_to_hsv(smoothed[0] / 255.0, smoothed[1] / 255.0, smoothed[2] / 255.0)
            self.runtime_state.diagnostics.current_color_rgb = smoothed
            self.runtime_state.diagnostics.current_color_hsv = (hsv[0], hsv[1], hsv[2])
            if dark_detector.is_dark(smoothed):
                success = await self.ha_client.turn_off()
                self.runtime_state.diagnostics.ha_status = "connected" if success else "disconnected"
            else:
                success = await self.ha_client.set_color(smoothed)
                self.runtime_state.diagnostics.ha_status = "connected" if success else "disconnected"
            await asyncio.sleep(interval)

    def _clamp_zone(self, zone: ZoneRect, pixels: np.ndarray) -> ZoneRect:
        bounds = DisplayBounds(width=pixels.shape[1], height=pixels.shape[0])
        return zone.clamp_to_bounds(bounds)

    def _boost_saturation(self, color: tuple[int, int, int], boost: float) -> tuple[int, int, int]:
        r, g, b = color
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        s = min(1.0, s + boost)
        r2, g2, b2 = colorsys.hsv_to_rgb(h, s, v)
        return (int(r2 * 255), int(g2 * 255), int(b2 * 255))
