"""LAN UI bridge to localhost control API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import httpx


@dataclass
class Bridge:
    local_api_base: str
    allowed_paths: Iterable[str]
    allowed_prefixes: Iterable[str] = ()

    async def forward(self, path: str, method: str = "GET", json: dict | None = None) -> httpx.Response:
        if not self._is_allowed(path):
            raise ValueError("Bridge path not allowed")
        async with httpx.AsyncClient(base_url=self.local_api_base, timeout=5.0) as client:
            response = await client.request(method, path, json=json)
            response.raise_for_status()
            return response

    def _is_allowed(self, path: str) -> bool:
        if path in self.allowed_paths:
            return True
        return any(path.startswith(prefix) for prefix in self.allowed_prefixes)
