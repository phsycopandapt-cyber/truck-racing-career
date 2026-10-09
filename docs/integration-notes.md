# Integration notes

## Roles
- ETS2 is `primary`: Melty installs the career bridge into the ETS2 experience and starts it.
- Assetto Corsa is `companion`: its own installation provides car and track content, and the actual game provides race physics.
- The recipe will need `together` only if the finished design requires both games to stay running at once. The intended first version can hand off from ETS2 to AC between career activities, so do not force simultaneous execution unless the implementation proves it necessary.

## Required work before this is a real mashup
1. On the target Windows PC, find both installed game roots and versions.
2. Read the installed official SCS Telemetry SDK and implement a minimal plugin/bridge that reports a completed delivery from the live game. Do not award rewards from user-entered test data in release mode.
3. Validate actual event timing and duplicate-delivery protection against the live ETS2 version.
4. Discover actual AC cars/tracks from the companion game folder and build a launch flow that selects a real installed car and track, then returns the race result to the persistent career. No bundled or look-alike game content.
5. Use only loaders/install paths Melty itself supports; check its one-click validator before any listing.
6. Run both games on the target PC, capture genuine gameplay showing a real ETS2 delivery and the AC race transition, and test persistence across restarts.

## Publishing metadata — draft only
- Proposed title: Truck Racing Career
- Tagline: Haul cargo across Europe. Earn your seat on the grid.
- Description: Build two reputations in one connected career. Complete ordinary Euro Truck Simulator 2 deliveries to earn money and trucking reputation, then unlock racing events using cars, tracks and driving physics from your own Assetto Corsa installation. Progress is saved locally. Single-player.
- Credits: SCS Software for ETS2 and its telemetry SDK; Kunos Simulazioni for Assetto Corsa; third-party code and assets to be credited only after their exact dependencies and licenses are established.
- License/remixing: UNDECIDED — must be confirmed before publication. Do not imply permission to remix or redistribute third-party code/assets.
