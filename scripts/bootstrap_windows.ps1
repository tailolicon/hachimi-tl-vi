$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
  py -3.11 -m venv .venv
}
& .\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"

$master = Join-Path $env:USERPROFILE "AppData\LocalLow\Cygames\umamusume\master\master.mdb"
if (Test-Path $master) {
  Write-Host "Found master.mdb: $master"
  tlvi import-mdb $master
} else {
  Write-Warning "master.mdb not found at the default DMM location."
}

tlvi status
