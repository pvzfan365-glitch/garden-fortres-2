# pack_vpk.ps1 — assemble pvz_gw2_kit into a Valve VPK.
# Runs on the Windows build machine. Requires TF2 installed (uses its vpk.exe).
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\pack_vpk.ps1
#
# Output: ..\dist\pvz_gw2_kit.vpk ready to drop into:
#   {Steam}\steamapps\common\Team Fortress 2\tf\custom\pvz_gw2_kit.vpk
# (TF2 reads either a folder OR a .vpk under tf/custom/; this script makes the .vpk.)

$ErrorActionPreference = "Stop"

$Here      = Split-Path -Parent $MyInvocation.MyCommand.Path
$ModRoot   = Resolve-Path (Join-Path $Here "..\pvz_gw2_kit")
$ModParent = Resolve-Path (Join-Path $Here "..")
$DistDir   = Join-Path $ModParent "dist"
$VpkOut    = Join-Path $DistDir "pvz_gw2_kit.vpk"

# ----- 1. locate vpk.exe (ships with TF2) -----
$Tf2Exe = $null
$SteamRoot = (Get-ItemProperty -Path "HKCU:\SOFTWARE\Valve\Steam" -ErrorAction SilentlyContinue).SteamPath
if (-not $SteamRoot) { $SteamRoot = "C:\Program Files (x86)\Steam" }
$Tf2VpkCandidates = @(
    (Join-Path $SteamRoot "steamapps\common\Team Fortress 2\bin\vpk.exe"),
    (Join-Path $SteamRoot "steamapps\common\Team Fortress 2\bin\x64\vpk.exe")
)
$VpkExe = $Tf2VpkCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $VpkExe) {
    throw "vpk.exe not found. Install TF2 or set `$env:VPK_EXE to the full path."
}
Write-Host "[pack] using vpk.exe = $VpkExe"

# ----- 2. UTF-16 LE BOM encode tf_english.txt (TF2 requires it) -----
$EnglishTxt = Join-Path $ModRoot "resource\tf_english.txt"
if (Test-Path $EnglishTxt) {
    Write-Host "[pack] re-encoding tf_english.txt as UTF-16 LE"
    $raw = Get-Content $EnglishTxt -Raw -Encoding UTF8
    [System.IO.File]::WriteAllText($EnglishTxt, $raw, [System.Text.UnicodeEncoding]::new($false, $true))
}

# ----- 3. make sure the sound/cache placeholder exists so the folder packs -----
$CacheDir = Join-Path $ModRoot "sound\cache"
if (-not (Test-Path $CacheDir)) { New-Item -ItemType Directory -Force -Path $CacheDir | Out-Null }
if (-not (Test-Path (Join-Path $CacheDir ".gitkeep"))) {
    "placeholder - populated by pvz_gw2_first_run.exe" | Out-File (Join-Path $CacheDir "README.txt")
}

# ----- 4. clean previous build -----
if (Test-Path $DistDir) { Remove-Item -Recurse -Force $DistDir }
New-Item -ItemType Directory -Force -Path $DistDir | Out-Null

# ----- 5. pack -----
Write-Host "[pack] packing $ModRoot -> $VpkOut"
& "$VpkExe" "$ModRoot"
if ($LASTEXITCODE -ne 0) { throw "vpk.exe exited $LASTEXITCODE" }
# vpk.exe writes <ModRoot>.vpk next to the folder; move it to dist/
$ProducedVpk = "$ModRoot.vpk"
if (-not (Test-Path $ProducedVpk)) { throw "expected $ProducedVpk but it wasn't produced" }
Move-Item -Force $ProducedVpk $VpkOut

Write-Host "[pack] done -> $VpkOut"
Write-Host "[pack] drop this file at: {Steam}\steamapps\common\Team Fortress 2\tf\custom\pvz_gw2_kit.vpk"
