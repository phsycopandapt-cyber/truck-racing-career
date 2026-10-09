# Truck Racing Career — source-only prototype

**Status: source-only / not yet a playable ETS2–Assetto Corsa mashup.**

A single-player career built around two real games:
- **Primary: Euro Truck Simulator 2** — ordinary cargo deliveries, European roads and the player's own truck.
- **Companion: Assetto Corsa** — actual installed cars, tracks and racing physics for career events.

The opening loop is: finish an ordinary ETS2 delivery → earn money and trucking reputation → unlock the first AC race → record race results and racing reputation → continue trucking to fund the racing career. Career state persists locally.

## Important integration boundary

The current prototype implements and tests the career rules, save format and Assetto Corsa installation discovery. It does **not** yet receive live ETS2 delivery-completion events, launch Assetto Corsa through Melty, or install into either game. It must not be presented as playable or published yet. This environment cannot access the Windows game installations or Melty's API, and the Melty endpoint could not be resolved from this session.

The intended ETS2 bridge is the official SCS Telemetry SDK; its events must be verified against a running ETS2 install before the career awards money. Assetto Corsa content must be enumerated from the player's own `content/cars` and `content/tracks` directories. No game assets are included.

## Run the rules tests

```sh
python -m unittest discover -s tests -v
```

## Try the local career rules (development only)

```sh
python src/career.py new --save career.json
python src/career.py delivery --save career.json --job-id demo-001 --cargo "Machine parts" --revenue 1250 --distance-km 240
python src/career.py status --save career.json
```

The delivery command is a development harness, not a live ETS2 integration.
