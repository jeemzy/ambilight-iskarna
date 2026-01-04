"""Frame provider abstraction."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

import numpy as np


@dataclass(frozen=True)
class Frame:
    pixels: np.ndarray
    timestamp: datetime


class FrameProvider(Protocol):
    """Interface for frame providers."""

    def start(self, display_id: int) -> None:
        """Start capture for a display."""

    def stop(self) -> None:
        """Stop capture."""

    def get_frame(self) -> Frame | None:
        """Fetch the latest frame or None if unavailable."""
