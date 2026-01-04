# Configuration Compatibility

## JSON Config and Presets

- JSON config/presets must remain backward compatible.
- New fields should be optional with defaults.
- Removing or renaming fields requires a documented migration note here.

## .env Schema

- Environment variables `HA_BASE_URL`, `HA_TOKEN`, and `HA_ENTITY_ID` are required.
- Any changes to required env vars must include explicit migration guidance.
