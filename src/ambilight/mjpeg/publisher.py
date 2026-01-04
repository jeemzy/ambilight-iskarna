"""MJPEG preview publisher."""

from __future__ import annotations

from io import BytesIO
from typing import Generator, Optional

import numpy as np
from PIL import Image

from ambilight.utils.bounded_queue import BoundedQueue


class MjpegPreviewPublisher:
    """Publish MJPEG frames from the latest available snapshot."""

    def __init__(self, max_frames: int = 2) -> None:
        self._frames = BoundedQueue[bytes](maxlen=max_frames)

    def update_frame(self, pixels: np.ndarray) -> None:
        image = Image.fromarray(pixels).convert("RGB")
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=80)
        self._frames.put(buffer.getvalue())

    def stream(self) -> Generator[bytes, None, None]:
        boundary = b"--frame"
        while True:
            frame = self._frames.get_latest()
            if frame is None:
                yield b""
                continue
            yield boundary + b"\r\n"
            yield b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
