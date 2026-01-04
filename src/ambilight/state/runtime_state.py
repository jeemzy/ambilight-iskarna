"""Runtime state and diagnostics tracking."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Tuple

from ambilight.state.zone_state import ZoneRect

RgbColor = Tuple[int, int, int]
HsvColor = Tuple[float, float, float]


class SyncStatus(str, Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"


@dataclass
class SyncState:
    status: SyncStatus = SyncStatus.STOPPED
    last_color_rgb: Optional[RgbColor] = None
    last_update_ts: Optional[datetime] = None


@dataclass
class Diagnostics:
    analysis_hz: Optional[float] = None
    latency_ms: Optional[float] = None
    preview_fps: Optional[float] = None
    selected_display: Optional[int] = None
    zone: Optional[ZoneRect] = None
    current_color_rgb: Optional[RgbColor] = None
    current_color_hsv: Optional[HsvColor] = None
    ha_status: str = "disconnected"
    capture_status: str = "disconnected"


@dataclass
class RuntimeState:
    sync_state: SyncState = field(default_factory=SyncState)
    diagnostics: Diagnostics = field(default_factory=Diagnostics)
