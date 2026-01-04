from __future__ import annotations

from datetime import datetime

from ambilight.analysis.dark_detector import DarkDetector
from ambilight.analysis.smoothing import SmoothingFilter150ms


def test_dark_detector_threshold() -> None:
    detector = DarkDetector(threshold=0.2)
    assert detector.is_dark((0, 0, 0)) is True
    assert detector.is_dark((255, 255, 255)) is False


def test_smoothing_returns_average() -> None:
    filt = SmoothingFilter150ms()
    now = datetime.utcnow()
    filt.update((0, 0, 0), now)
    smoothed = filt.update((100, 100, 100), now)
    assert smoothed == (50, 50, 50)
