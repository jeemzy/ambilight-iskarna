"""Simple async scheduler helpers."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta


async def run_periodic(
    interval_sec: float, callback: Callable[[], Awaitable[None]]
) -> None:
    """Run an async callback at a fixed interval."""

    while True:
        start = datetime.utcnow()
        await callback()
        elapsed = (datetime.utcnow() - start).total_seconds()
        sleep_for = max(0.0, interval_sec - elapsed)
        await asyncio.sleep(sleep_for)
