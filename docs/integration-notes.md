# Integration notes

## ETS2 → career

The native plugin registers for the official SCS Telemetry SDK configuration and gameplay events. It remembers the current job metadata and responds to the `job.delivered` event. It writes an atomic JSON file to `%LOCALAPPDATA%/TruckRacingCareer/inbox/`; it does not edit ETS2 saves.

Example event:

```json
{
  "schema_version": 1,
  "event": "job.delivered",
  "job_id": "ets2-unique-event-id",
  "cargo": "cargo name",
  "source_city": "source",
  "destination_city": "destination",
  "revenue_eur": 1250.0,
  "distance_km": 240.0,
  "earned_xp": 15,
  "cargo_damage": 0.0
}
```

The companion applies a delivery only once per unique `job_id`. Malformed files remain in the inbox for inspection.

## Career → Assetto Corsa

The companion discovers content under the player's own AC installation: `content/cars` and `content/tracks`. It writes `Documents/Assetto Corsa/cfg/race.ini`, updates the relevant keys in `launcher.ini`, launches `acs.exe`, then reads `Documents/Assetto Corsa/out/race_out.json`. It awards no race result if it cannot identify the player in the race finishing order.

The companion targets the original Assetto Corsa (Steam app 244210), not Assetto Corsa Competizione. The current direct launch and result parsing still require a real Windows/game test.

## Package build

The Windows workflow fetches the official SCS Telemetry SDK at build time, builds the x64 DLL with MSVC/CMake and uses PyInstaller to package the desktop companion. Intended package layout:

- `TruckRacingCareer.exe` → ETS2 game root
- `bin/win_x64/plugins/TruckRacingCareer.dll` → ETS2 game root

No game assets or SDK headers are redistributed in the package.

## Verification

Python unit tests and syntax compilation have passed in the development environment. Windows build, live ETS2 telemetry, AC launch/result import, Melty package validation and one-click check are pending. Do not publish as a ready-to-play one-click mod until those checks pass.
