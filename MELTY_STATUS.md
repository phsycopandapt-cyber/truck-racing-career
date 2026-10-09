# Melty release status — Truck Racing Career

**Status: installable Windows build created; live-game verification still required. Do not claim a fully verified one-click gameplay release yet.**

## Work completed
- Native Windows x64 ETS2 SCS Telemetry SDK plugin listens for the real `job.delivered` gameplay event and writes a local JSON event.
- Companion consumes delivery events, ignores duplicate job IDs, and persists career progress.
- Desktop companion discovers installed AC cars/tracks, prepares a race, launches original Assetto Corsa and reads a fresh `race_out.json` result.
- Windows CI downloads the official SDK during build, compiles the companion EXE and telemetry DLL, and packages a ZIP with an installer.
- Installer copies the telemetry plugin into the ETS2 game folder and creates a desktop shortcut for the companion.

## Verification completed
- Windows GitHub Actions build: **SUCCESS**.
- Windows automated tests: **10 passed**.
- Companion executable: built successfully as x64 Windows GUI executable.
- Native telemetry plugin: built successfully as x64 Windows DLL.
- Required exports `scs_telemetry_init` and `scs_telemetry_shutdown`: confirmed in the built DLL.
- Package ZIP: uploaded as artifact `TruckRacingCareer-Windows-x64` and archive integrity checked.

Build run: https://github.com/phsycopandapt-cyber/truck-racing-career/actions/runs/37974338331

## Still required on a real PC
1. Install on Windows with ETS2 and original Assetto Corsa installed.
2. Verify the DLL loads in ETS2 and a real delivery is credited once.
3. Verify an unlocked race starts in AC and the actual finishing position is imported.
4. If either integration fails, collect logs and fix the issue before calling it fully playable.
5. Melty package inspection/one-click check, genuine gameplay screenshot, and license/remix permission confirmation remain outstanding.

The build is ready for hands-on testing, but the games were not available in the build environment, so the live gameplay loop is not yet certified.
