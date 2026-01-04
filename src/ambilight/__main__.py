"""Module entrypoint for python -m ambilight."""

from __future__ import annotations

import asyncio

from ambilight.main import main


if __name__ == "__main__":
    asyncio.run(main())
