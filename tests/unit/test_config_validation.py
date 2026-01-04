from __future__ import annotations

import pytest

from ambilight.config.models import AppConfig
from ambilight.config.validators import validate_config, validate_zone
from ambilight.state.zone_state import ZoneRect


def test_validate_zone_rejects_zero_size() -> None:
    with pytest.raises(ValueError):
        validate_zone(ZoneRect(x=0, y=0, width=0, height=10))


def test_validate_config_clamps_ranges() -> None:
    config = AppConfig(
        display_id=1,
        zone=ZoneRect(x=0, y=0, width=10, height=10),
        preview_interval_sec=1.0,
        analysis_hz=25.0,
        dark_threshold=2.0,
        saturation_boost=-1.0,
    )
    validated = validate_config(config)
    assert validated.dark_threshold == 1.0
    assert validated.saturation_boost == 0.0
