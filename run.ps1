# HackMysore 1.0 — one-command local launcher
$ErrorActionPreference = 'Stop'
if (-not (Test-Path '.\venv\Scripts\python.exe')) {
  Write-Host 'Virtual environment not found. Create it with:' -ForegroundColor Yellow
  Write-Host 'python -m venv venv' -ForegroundColor Cyan
  exit 1
}
& .\venv\Scripts\python.exe -m uvicorn backend.main:app --reload
