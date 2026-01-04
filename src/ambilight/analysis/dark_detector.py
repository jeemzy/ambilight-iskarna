"""Dark detection based on luminance threshold."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

RgbColor = Tuple[int, int, int]


@dataclass
class DarkDetector:
    """Detect dark scenes using a normalized luminance threshold."""

    threshold: float

    def is_dark(self, color: RgbColor) -> bool:
        r, g, b = color
        luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0
        return luminance <= self.threshold
