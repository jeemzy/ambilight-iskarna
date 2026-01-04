from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np

from ambilight.analysis.dominant_color import dominant_color_rgb
from ambilight.analysis.smoothing import SmoothingFilter150ms


def test_dominant_color_from_synthetic_frame() -> None:
    frame = np.zeros((10, 10, 3), dtype=np.uint8)
    frame[:, :] = [255, 0, 0]
    frame[0:2, 0:2] = [0, 0, 255]
    dominant = dominant_color_rgb(frame)
    assert dominant == (255, 0, 0)


def test_smoothing_window_keeps_recent_samples() -> None:
    filt = SmoothingFilter150ms()
    now = datetime.utcnow()
    filt.update((0, 0, 0), now - timedelta(milliseconds=200))
    smoothed = filt.update((255, 0, 0), now)
    assert smoothed == (255, 0, 0)
