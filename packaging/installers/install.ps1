$ErrorActionPreference = "Stop"

$Prefix = if ($env:PREFIX) { $env:PREFIX } else { Join-Path $HOME ".panclaw" }
$BinDir = Join-Path $Prefix "bin"
$AppDir = Join-Path $Prefix "app"
$RootDir = Resolve-Path (Join-Path $PSScriptRoot "..\..")

New-Item -ItemType Directory -Force -Path $BinDir | Out-Null
New-Item -ItemType Directory -Force -Path $AppDir | Out-Null
Copy-Item -Recurse -Force (Join-Path $RootDir "src\panclaw") (Join-Path $AppDir "panclaw")

$Launcher = Join-Path $BinDir "panclaw.cmd"
Set-Content -Path $Launcher -Encoding ASCII -Value "@echo off`r`nset PYTHONPATH=$AppDir`r`npython -m panclaw %*`r`n"

Write-Host "PanClaw installed to $AppDir"
Write-Host "Add $BinDir to PATH if needed."

