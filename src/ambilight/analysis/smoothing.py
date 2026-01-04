"""Temporal smoothing with a fixed 150 ms window."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Deque, Tuple

RgbColor = Tuple[int, int, int]


@dataclass
class SmoothingFilter150ms:
    """Fixed temporal smoothing filter with a 150 ms window."""

    window_ms: int = 150
    _samples: Deque[tuple[datetime, RgbColor]] = field(default_factory=deque)

    def update(self, color: RgbColor, timestamp: datetime) -> RgbColor:
        self._samples.append((timestamp, color))
        cutoff = timestamp - timedelta(milliseconds=self.window_ms)
        while self._samples and self._samples[0][0] < cutoff:
            self._samples.popleft()
        return self._average()

    def _average(self) -> RgbColor:
        if not self._samples:
            return (0, 0, 0)
        total = [0, 0, 0]
        for _, color in self._samples:
            total[0] += color[0]
            total[1] += color[1]
            total[2] += color[2]
        count = len(self._samples)
        return (total[0] // count, total[1] // count, total[2] // count)
