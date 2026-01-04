"""LAN-facing UI server with minimal bridge."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
import httpx
from fastapi.staticfiles import StaticFiles

from ambilight.web.bridge import Bridge


class LanUiServer:
    """Serve static UI over LAN and forward allowed actions to localhost API."""

    def __init__(self, bridge: Bridge, static_dir: Path) -> None:
        self._bridge = bridge
        self._static_dir = static_dir
        self.app = FastAPI(title="Ambilight LAN UI")
        self._register_routes()

    def _register_routes(self) -> None:
        app = self.app
        app.mount("/static", StaticFiles(directory=self._static_dir), name="static")

        @app.get("/")
        async def index() -> FileResponse:
            index_path = self._static_dir / "index.html"
            if not index_path.exists():
                raise HTTPException(status_code=404, detail="Missing index.html")
            return FileResponse(index_path)

        @app.post("/bridge")
        async def bridge_request(payload: dict[str, Any]) -> JSONResponse:
            path = payload.get("path")
            method = payload.get("method", "GET").upper()
            data = payload.get("data")
            if not path:
                raise HTTPException(status_code=400, detail="Missing path")
            response = await self._bridge.forward(path, method=method, json=data)
            return JSONResponse(status_code=response.status_code, content=response.json())

        @app.get("/preview")
        async def preview_stream() -> StreamingResponse:
            async def _iter_stream() -> bytes:
                async with httpx.AsyncClient(base_url=self._bridge.local_api_base) as client:
                    async with client.stream("GET", "/api/preview/stream") as response:
                        async for chunk in response.aiter_bytes():
                            yield chunk

            return StreamingResponse(
                _iter_stream(),
                media_type="multipart/x-mixed-replace; boundary=frame",
            )
