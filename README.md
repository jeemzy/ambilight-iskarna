# ambilight-iskarna

Ambilight-style lighting controller for an IKEA ISKARNA lamp via Home Assistant.
It captures a single user-defined zone from Display 1 or Display 2, computes a
dominant color with a fixed 150 ms smoothing window, and sends rate-limited
updates to Home Assistant.

## Features

- Single zone only (drag/resized in the UI)
- Dominant-color extraction (no averaging)
- Fixed 150 ms temporal smoothing
- Adjustable dark threshold and saturation boost
- LAN UI on port 8080, localhost control API on port 8765
- Presets stored as local JSON (non-secret config)
- Home Assistant secrets loaded from `.env`

## Requirements

- Windows 10/11 machine with Display 1 and Display 2 available
- Python 3.11+
- Home Assistant on the same LAN

## Setup

1. Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Create a `.env` file in the repository root:

```text
HA_BASE_URL=http://<home-assistant-host>:8123
HA_TOKEN=<long-lived-access-token>
HA_ENTITY_ID=light.<your_entity_id>
```

## Run

```powershell
python -m ambilight.main
```

The LAN UI is available at:

```text
http://<laptop-ip>:8080
```

## Notes

- The UI binds to `0.0.0.0` for LAN access; the control API binds to `127.0.0.1`.
- Configuration and presets are stored in `config/` as JSON.
- Secrets are loaded only from `.env`.
