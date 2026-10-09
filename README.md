# Truck Racing Career

A single-player career companion linking **Euro Truck Simulator 2** delivery progress with races in the player's own **original Assetto Corsa** installation.

## Career loop

1. Start the Truck Racing Career companion.
2. Start ETS2 and complete an ordinary delivery.
3. The native SCS telemetry plugin detects the real `job.delivered` event and writes it to the local event inbox.
4. The companion applies the delivery once, awards career money/reputation and unlocks racing events.
5. Select an installed AC car and track, launch the race, and finish it.
6. The companion reads Assetto Corsa's fresh `race_out.json` result and awards the career prize/reputation.

## Windows install

1. Download `TruckRacingCareer-Windows-x64.zip` from the successful build artifact linked on the repository's **Actions** page.
2. Extract the ZIP to a normal folder.
3. Right-click `install.ps1` and choose **Run with PowerShell**. If Windows blocks scripts, open PowerShell in the extracted folder and run `powershell -ExecutionPolicy Bypass -File .\install.ps1`.
4. When prompted, enter the ETS2 game folder — the folder containing `eurotrucks2.exe` (usually under `Steam\steamapps\common\Euro Truck Simulator 2`).
5. Start **Truck Racing Career** from the desktop shortcut.
6. Start ETS2 from the companion, complete a delivery, then return to the companion. The first delivery unlocks the first race.
7. In the companion, select the Assetto Corsa folder containing `acs.exe`, scan installed content, and choose an unlocked event, car and track.

Requirements: Windows 10/11 x64, Steam, ETS2 and the original Assetto Corsa (not Competizione). Cars/tracks are not bundled; the companion uses the player's installed content. Career data is stored under `%LOCALAPPDATA%\TruckRacingCareer`.

## Troubleshooting

- **No delivery credit:** ensure the DLL is at `<ETS2 game folder>\bin\win_x64\plugins\TruckRacingCareer.dll`. The companion must be running when the delivery event is emitted. Restart ETS2 after installing/updating the DLL.
- **No cars/tracks found:** choose the AC installation directory containing `acs.exe`, then click Scan.
- **Race result not imported:** ensure the player name in the companion matches the driver name written into the AC race config. The companion will not award a result it cannot verify.
- **Melty one-click validation:** not yet run; a genuine live-game test is still required.

## Source and verification

- `src/career.py`: career rules and save format.
- `src/ets2_event_bridge.py`: event inbox consumer and duplicate protection.
- `src/assetto_corsa.py`: content discovery, race configuration and result import.
- `src/launcher.py`: Windows companion UI.
- `integrations/ets2-telemetry-plugin/`: native ETS2 telemetry DLL source.
- `.github/workflows/build-windows.yml`: Windows build and artifact packaging.

The automated tests exercise career logic and integration helpers; they do not substitute for testing with ETS2 and Assetto Corsa actually running. The Windows CI build must pass before the ZIP artifact is considered installable, and the first real delivery/race still needs to be verified on a PC with both games installed.

## Third-party software and licensing

The plugin uses the official SCS Telemetry SDK headers fetched at build time. No game assets are included. Assetto Corsa and ETS2 remain separate products. The repository's project license/remix permissions have not yet been decided.
