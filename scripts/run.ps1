$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
if (-not (Test-Path ".venv")) { py -m venv .venv }
& .\.venv\Scripts\Activate.ps1
python -m pip install -q -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
