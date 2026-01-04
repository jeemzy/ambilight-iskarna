"""Load Home Assistant secrets from .env."""

from __future__ import annotations

from dataclasses import dataclass
import os
from urllib.parse import urlparse

from dotenv import load_dotenv


@dataclass(frozen=True)
class EnvConfig:
    ha_base_url: str
    ha_token: str
    ha_entity_id: str


def _validate_base_url(value: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("HA_BASE_URL must be a valid http/https URL")


def load_env_config() -> EnvConfig:
    """Load Home Assistant connection config from environment."""

    load_dotenv()
    base_url = os.getenv("HA_BASE_URL", "").strip()
    token = os.getenv("HA_TOKEN", "").strip()
    entity_id = os.getenv("HA_ENTITY_ID", "").strip()

    if not base_url or not token or not entity_id:
        raise ValueError("Missing HA_BASE_URL, HA_TOKEN, or HA_ENTITY_ID")
    _validate_base_url(base_url)
    if "." not in entity_id:
        raise ValueError("HA_ENTITY_ID must use domain.object_id format")

    return EnvConfig(ha_base_url=base_url, ha_token=token, ha_entity_id=entity_id)
