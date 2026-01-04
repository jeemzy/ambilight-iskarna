"""Logging helpers with structured context."""

from __future__ import annotations

import logging
from typing import Any


def configure_logging(level: int = logging.INFO) -> None:
    """Configure root logging with a structured-friendly format."""

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


class ContextLoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that appends structured context to messages."""

    def process(self, msg: str, kwargs: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        if self.extra:
            context = " ".join(f"{k}={v}" for k, v in self.extra.items())
            msg = f"{msg} {context}".strip()
        return msg, kwargs


def get_logger(name: str, **context: Any) -> ContextLoggerAdapter:
    """Return a logger with attached structured context."""

    logger = logging.getLogger(name)
    return ContextLoggerAdapter(logger, context)
