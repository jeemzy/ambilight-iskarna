"""Home Assistant REST client with backoff and throttling."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Tuple

import httpx

RgbColor = Tuple[int, int, int]


@dataclass
class HomeAssistantClient:
    base_url: str
    token: str
    entity_id: str
    min_interval_ms: int = 100
    _client: httpx.AsyncClient = field(init=False)
    _last_send: Optional[datetime] = None
    _backoff_seconds: float = 1.0
    _max_backoff: float = 30.0

    def __post_init__(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=5.0,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def set_color(self, color: RgbColor, brightness: int = 255) -> bool:
        await self._throttle()
        payload = {
            "entity_id": self.entity_id,
            "rgb_color": list(color),
            "brightness": brightness,
        }
        return await self._post("/api/services/light/turn_on", payload)

    async def turn_off(self) -> bool:
        await self._throttle()
        payload = {"entity_id": self.entity_id}
        return await self._post("/api/services/light/turn_off", payload)

    async def _post(self, path: str, payload: dict) -> bool:
        try:
            response = await self._client.post(path, json=payload)
            response.raise_for_status()
            self._backoff_seconds = 1.0
            return True
        except httpx.HTTPError:
            await asyncio.sleep(self._backoff_seconds)
            self._backoff_seconds = min(self._max_backoff, self._backoff_seconds * 2)
            return False

    async def _throttle(self) -> None:
        if self._last_send is None:
            self._last_send = datetime.utcnow()
            return
        delta = datetime.utcnow() - self._last_send
        min_interval = timedelta(milliseconds=self.min_interval_ms)
        if delta < min_interval:
            await asyncio.sleep((min_interval - delta).total_seconds())
        self._last_send = datetime.utcnow()
