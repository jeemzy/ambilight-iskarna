"""Zone state and geometry helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DisplayBounds:
    """Display bounds in pixels."""

    width: int
    height: int


@dataclass(frozen=True)
class ZoneRect:
    """Rectangle defining the capture zone in display coordinates."""

    x: int
    y: int
    width: int
    height: int

    def is_valid(self) -> bool:
        return self.width > 0 and self.height > 0

    def clamp_to_bounds(self, bounds: DisplayBounds) -> "ZoneRect":
        x = max(0, min(self.x, bounds.width - 1))
        y = max(0, min(self.y, bounds.height - 1))
        width = max(1, min(self.width, bounds.width - x))
        height = max(1, min(self.height, bounds.height - y))
        return ZoneRect(x=x, y=y, width=width, height=height)


def full_screen(bounds: DisplayBounds) -> ZoneRect:
    return ZoneRect(x=0, y=0, width=bounds.width, height=bounds.height)


def centered(bounds: DisplayBounds, width: int, height: int) -> ZoneRect:
    x = max(0, (bounds.width - width) // 2)
    y = max(0, (bounds.height - height) // 2)
    return ZoneRect(x=x, y=y, width=width, height=height).clamp_to_bounds(bounds)


def top(bounds: DisplayBounds, height: int) -> ZoneRect:
    return ZoneRect(x=0, y=0, width=bounds.width, height=height).clamp_to_bounds(bounds)


def bottom(bounds: DisplayBounds, height: int) -> ZoneRect:
    y = max(0, bounds.height - height)
    return ZoneRect(x=0, y=y, width=bounds.width, height=height).clamp_to_bounds(bounds)


def left(bounds: DisplayBounds, width: int) -> ZoneRect:
    return ZoneRect(x=0, y=0, width=width, height=bounds.height).clamp_to_bounds(bounds)


def right(bounds: DisplayBounds, width: int) -> ZoneRect:
    x = max(0, bounds.width - width)
    return ZoneRect(x=x, y=0, width=width, height=bounds.height).clamp_to_bounds(bounds)
