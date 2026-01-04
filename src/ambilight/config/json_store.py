"""JSON configuration and preset storage."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List

from ambilight.config.validators import validate_config
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



def _config_from_dict(data: dict) -> AppConfig:
    zone = ZoneRect(**data["zone"])
    return validate_config(
        AppConfig(
            display_id=int(data["display_id"]),
            zone=zone,
            preview_interval_sec=float(data["preview_interval_sec"]),
            analysis_hz=float(data["analysis_hz"]),
            dark_threshold=float(data["dark_threshold"]),
            saturation_boost=float(data["saturation_boost"]),
        )
    )


def _preset_from_dict(data: dict) -> Preset:
    zone = ZoneRect(**data["zone"])
    if not data.get("name"):
        raise ValueError("preset name is required")
    return Preset(
        name=str(data["name"]),
        display_id=int(data["display_id"]),
        zone=zone,
        preview_interval_sec=float(data["preview_interval_sec"]),
        analysis_hz=float(data["analysis_hz"]),
        dark_threshold=float(data["dark_threshold"]),
        saturation_boost=float(data["saturation_boost"]),
    )


class JsonConfigStore:
    """Persist non-secret configuration and presets to JSON files."""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.config_path = self.base_dir / "config.json"
        self.presets_path = self.base_dir / "presets.json"

    def load_config(self, default: AppConfig) -> AppConfig:
        if not self.config_path.exists():
        return validate_config(default)
        data = json.loads(self.config_path.read_text(encoding="utf-8"))
        return _config_from_dict(data)

    def save_config(self, config: AppConfig) -> None:
        validated = validate_config(config)
        self.config_path.write_text(
            json.dumps(asdict(validated), indent=2), encoding="utf-8"
        )

    def load_presets(self) -> List[Preset]:
        if not self.presets_path.exists():
            return []
        data = json.loads(self.presets_path.read_text(encoding="utf-8"))
        return [_preset_from_dict(item) for item in data]

    def save_presets(self, presets: Iterable[Preset]) -> None:
        unique = {}
        for preset in presets:
            unique[preset.name] = preset
        payload = [asdict(preset) for preset in unique.values()]
        self.presets_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def save_preset(self, preset: Preset) -> None:
        presets = self.load_presets()
        presets = [p for p in presets if p.name != preset.name]
        presets.append(preset)
        self.save_presets(presets)

    def delete_preset(self, name: str) -> None:
        presets = [p for p in self.load_presets() if p.name != name]
        self.save_presets(presets)
