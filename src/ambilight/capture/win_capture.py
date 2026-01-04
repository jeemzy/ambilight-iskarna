"""Windows capture provider using dxcam (DXGI)."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

import dxcam
import numpy as np
from PIL import Image

from ambilight.capture.frame_provider import Frame, FrameProvider


class WinCaptureFrameProvider(FrameProvider):
    """Capture frames from a Windows display using dxcam."""

    def __init__(self, scale: float = 1.0) -> None:
        self._camera: Optional[dxcam.DXCamera] = None
        self._scale = scale
        self._display_id: Optional[int] = None

    def start(self, display_id: int) -> None:
        if display_id not in (1, 2):
            raise ValueError("display_id must be 1 or 2")
        self._display_id = display_id
        output_idx = display_id - 1
        self._camera = dxcam.create(output_idx=output_idx)
        if self._camera is None:
            raise RuntimeError("Failed to initialize dxcam")
        self._camera.start(target_fps=30, video_mode=True)

    def stop(self) -> None:
        if self._camera is not None:
            self._camera.stop()
        self._camera = None

    def get_frame(self) -> Frame | None:
        if self._camera is None:
            return None
        frame = self._camera.get_latest_frame()
        if frame is None:
            return None
        pixels = self._downscale(frame)
        return Frame(pixels=pixels, timestamp=datetime.utcnow())

    def _downscale(self, frame: np.ndarray) -> np.ndarray:
        if self._scale >= 1.0:
            return frame
        width = max(1, int(frame.shape[1] * self._scale))
        height = max(1, int(frame.shape[0] * self._scale))
        image = Image.fromarray(frame)
        resized = image.resize((width, height), resample=Image.BILINEAR)
        return np.asarray(resized)
