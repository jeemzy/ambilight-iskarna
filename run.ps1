param(
    [int]$UiPort = 8080,
    [int]$ApiPort = 8765
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

. .\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
pip install -e .

$env:LAN_UI_PORT = $UiPort
$env:LOCAL_API_PORT = $ApiPort

python -m ambilight
