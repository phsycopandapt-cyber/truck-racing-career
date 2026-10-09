# Melty release status — Truck Racing Career

**NOT READY TO PUBLISH. Keep the Melty listing as a draft.**

## Source implementation added

- Native Windows x64 SCS telemetry plugin listens for ETS2's `job.delivered` gameplay event and emits local JSON events.
- Python career consumer applies each delivery once and persists career progress.
- Desktop companion discovers the player's installed Assetto Corsa cars/tracks, configures a race, launches the original game and attempts to import the real `race_out.json` finishing order.
- Windows CI workflow downloads the official SDK during build, compiles the plugin and packages a companion executable.

## Verification status

- Earlier Python tests for career rules and the integration code passed locally (14 tests).
- Python syntax compilation passed locally.
- Windows DLL build: pending workflow execution.
- Real ETS2 delivery event: not tested in the running game.
- Real AC race launch and result import: not tested in the running game.
- Melty package inspection, recipe validation, one-click check, real gameplay screenshot and publication: not performed. The Melty endpoint was unreachable from this environment.
- Project license/remix permission: undecided.

## Release gates

1. Get a successful Windows CI artifact.
2. Install it on a Windows PC with both games installed.
3. Confirm the plugin loads in ETS2 and one real delivery is credited exactly once.
4. Confirm an unlocked event launches AC and the real finishing position updates the save.
5. Run Melty's own inspection and one-click checks and capture a genuine in-game screenshot.
6. Confirm license and remix permissions.

Until all six gates pass, label the project as an integration prototype rather than a playable mashup.
