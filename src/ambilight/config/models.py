"""Configuration data models."""

from __future__ import annotations

from dataclasses import dataclass

from ambilight.state.zone_state import ZoneRect


@dataclass(frozen=True)
class AppConfig:
    display_id: int
    zone: ZoneRect
    preview_interval_sec: float
    analysis_hz: float
    dark_threshold: float
    saturation_boost: float


@dataclass(frozen=True)
class Preset:
    name: str
    display_id: int
    zone: ZoneRect
    preview_interval_sec: float
    analysis_hz: float
    dark_threshold: float
    saturation_boost: float
