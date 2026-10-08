# build.ps1 — compile the first-run helper into a single Windows .exe.
# Run on the Windows build machine (not inside Emergent's Linux pod).
#
# Prereqs:
#   - Python 3.12 x64 on PATH
#   - cd into this folder before running
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\build.ps1

$ErrorActionPreference = "Stop"

Write-Host "[build] creating venv"
python -m venv .venv
. .\.venv\Scripts\Activate.ps1

Write-Host "[build] installing deps"
pip install --upgrade pip
pip install -r requirements.txt

Write-Host "[build] packing with PyInstaller"
pyinstaller `
    --onefile `
    --noconfirm `
    --name pvz_gw2_first_run `
    --console `
    --hidden-import winreg `
    main.py

Write-Host "[build] moving binary into mod bin/"
$outExe = ".\dist\pvz_gw2_first_run.exe"
if (-not (Test-Path $outExe)) {
    throw "build failed - $outExe not produced"
}
$modBin = Join-Path (Resolve-Path "..\..\pvz_gw2_kit\bin") "pvz_gw2_first_run.exe"
Copy-Item -Force $outExe $modBin

Write-Host "[build] done -> $modBin"
