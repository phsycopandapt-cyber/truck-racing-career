# Truck Racing Career

**Status: integration prototype — not yet verified in the actual games.**

Truck Racing Career is a single-player career companion for **Euro Truck Simulator 2** and the original **Assetto Corsa**.

## Intended player loop

1. Launch ETS2 and complete an ordinary delivery.
2. The native SCS telemetry plugin listens for ETS2's official `job.delivered` gameplay event and writes a local JSON event.
3. The companion processes that event once, rewards trucking money/reputation, and unlocks racing events.
4. Choose an installed AC car and track in the companion. It writes a single-player `race.ini`, launches `acs.exe`, and imports the session's `race_out.json` finishing order.
5. Race rewards and reputation are saved locally.

## Repository contents

- `src/career.py`: persistent career rules, delivery rewards, race unlocks and race rewards.
- `src/launcher.py`: Windows desktop companion, telemetry watcher, AC content discovery, race launch and result import.
- `src/ets2_event_bridge.py`: command-line delivery-event consumer useful for diagnostics.
- `integrations/ets2-telemetry-plugin/`: native Windows x64 SCS telemetry plugin source and CMake project.
- `.github/workflows/build-windows.yml`: Windows CI workflow to download the official SCS SDK, build the plugin and package a companion executable.

## Important: not a playable release yet

Python rule/integration tests pass in the development environment, but **the native Windows build and both live-game integrations have not been verified here**. The workflow must build successfully, and the resulting ZIP must be installed and tested on a Windows PC with ETS2 and Assetto Corsa. Do not call this a verified one-click mod or publish it as ready until the DLL loads in ETS2, a real delivery unlocks a race, and a real AC race result is imported correctly.

## Requirements for live testing

- Windows 10/11 x64
- Euro Truck Simulator 2 and original Assetto Corsa installed
- Steam
- At least one AC car and track installed

No game assets are included. Cars and tracks are discovered from the player's own AC installation.

## Local tests

```sh
python -m unittest discover -s tests -v
python -m py_compile src/*.py
```

These tests do not replace live-game testing.

## Credits and license

ETS2 telemetry API: [official SCS Telemetry SDK documentation](https://modding.scssoft.com/wiki/Documentation/Engine/SDK/Telemetry). The build workflow downloads the SDK from SCS; SDK headers are not bundled here. Assetto Corsa is developed by Kunos Simulazioni; the project does not redistribute game content.

**Project license and remix permission are not yet decided.** Confirm them before public distribution.
