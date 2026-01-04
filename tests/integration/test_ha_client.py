from __future__ import annotations

import asyncio
from typing import Any

import httpx

from ambilight.ha.client import HomeAssistantClient


def test_ha_client_sends_requests() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    client = HomeAssistantClient(
        base_url="http://ha.local",
        token="token",
        entity_id="light.lamp",
    )
    client._client = httpx.AsyncClient(transport=transport, base_url="http://ha.local")

    async def run() -> None:
        await client.set_color((10, 20, 30))
        await client.turn_off()
        await client.close()

    asyncio.run(run())
    assert len(requests) == 2
