"""Validation helpers for configuration data."""

from __future__ import annotations

from ambilight.config.models import AppConfig
from ambilight.state.zone_state import ZoneRect


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def validate_zone(zone: ZoneRect) -> None:
    if not zone.is_valid():
        raise ValueError("zone width/height must be > 0")


def validate_config(config: AppConfig) -> AppConfig:
    if config.display_id not in (1, 2):
        raise ValueError("display_id must be 1 or 2")
    validate_zone(config.zone)
    if not 0.5 <= config.preview_interval_sec <= 2.0:
        raise ValueError("preview_interval_sec out of bounds")
    dark = clamp(config.dark_threshold, 0.0, 1.0)
    sat = clamp(config.saturation_boost, 0.0, 1.0)
    return AppConfig(
        display_id=config.display_id,
        zone=config.zone,
        preview_interval_sec=config.preview_interval_sec,
        analysis_hz=config.analysis_hz,
        dark_threshold=dark,
        saturation_boost=sat,
    )
