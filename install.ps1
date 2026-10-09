$ErrorActionPreference = 'Stop'
$pluginSource = Join-Path $PSScriptRoot 'bin\win_x64\plugins\TruckRacingCareer.dll'
$appSource = Join-Path $PSScriptRoot 'TruckRacingCareer.exe'
if (-not (Test-Path $pluginSource)) { throw "Plugin DLL missing: $pluginSource" }
if (-not (Test-Path $appSource)) { throw "Companion executable missing: $appSource" }
$ets2 = Read-Host 'Enter the Euro Truck Simulator 2 game folder (the folder containing eurotrucks2.exe)'
if (-not (Test-Path (Join-Path $ets2 'eurotrucks2.exe'))) {
  throw "Could not find eurotrucks2.exe in '$ets2'. Choose the actual ETS2 game folder, not the Steam folder."
}
$pluginDir = Join-Path $ets2 'bin\win_x64\plugins'
New-Item -ItemType Directory -Force -Path $pluginDir | Out-Null
Copy-Item -LiteralPath $pluginSource -Destination (Join-Path $pluginDir 'TruckRacingCareer.dll') -Force
$appDir = Join-Path $env:LOCALAPPDATA 'Programs\Truck Racing Career'
New-Item -ItemType Directory -Force -Path $appDir | Out-Null
$appPath = Join-Path $appDir 'TruckRacingCareer.exe'
Copy-Item -LiteralPath $appSource -Destination $appPath -Force
$desktop = [Environment]::GetFolderPath('Desktop')
$shortcutPath = Join-Path $desktop 'Truck Racing Career.lnk'
$ws = New-Object -ComObject WScript.Shell
$shortcut = $ws.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $appPath
$shortcut.WorkingDirectory = $appDir
$shortcut.Description = 'Truck Racing Career companion for ETS2 and Assetto Corsa'
$shortcut.Save()
Write-Host ''
Write-Host 'Installation complete.' -ForegroundColor Green
Write-Host "ETS2 telemetry plugin: $pluginDir\TruckRacingCareer.dll"
Write-Host "Career companion: $appPath"
Write-Host 'Start Truck Racing Career from the desktop shortcut before launching ETS2.'
Write-Host 'The first delivery unlocks the first race. Assetto Corsa must be installed separately.'
Pause
