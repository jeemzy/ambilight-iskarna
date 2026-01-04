"""Dominant color extraction using quantized palette."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from PIL import Image

RgbColor = Tuple[int, int, int]


@dataclass(frozen=True)
class DominantColorResult:
    rgb: RgbColor


def dominant_color_rgb(pixels: "Image.Image | list | tuple | object") -> RgbColor:
    """Return dominant color using palette quantization (no averaging)."""

    image = Image.fromarray(pixels).convert("RGB")
    quantized = image.quantize(colors=8, method=Image.MEDIANCUT)
    palette = quantized.getpalette()
    color_counts = quantized.getcolors()
    if not color_counts:
        return (0, 0, 0)
    dominant_index = max(color_counts, key=lambda item: item[0])[1]
    base = dominant_index * 3
    return (palette[base], palette[base + 1], palette[base + 2])
