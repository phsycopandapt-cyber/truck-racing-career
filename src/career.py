#!/usr/bin/env python3
"""Rules prototype for Truck Racing Career; not yet connected to live game telemetry."""
from __future__ import annotations
import argparse, json
from pathlib import Path

SCHEMA_VERSION = 1
RACE_EVENTS = json.loads((Path(__file__).resolve().parents[1] / "sheets" / "race_events.json").read_text(encoding="utf-8"))["events"]


def fresh_state():
    return {"schema_version": SCHEMA_VERSION, "money_eur": 0.0, "trucking_reputation": 0,
            "racing_reputation": 0, "completed_deliveries": 0, "completed_races": 0,
            "processed_job_ids": [], "unlocked_events": []}


def load_state(path: Path):
    if not path.exists():
        return fresh_state()
    state = json.loads(path.read_text(encoding="utf-8"))
    if state.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Unsupported career save schema")
    for key in fresh_state():
        if key not in state:
            raise ValueError(f"Save is missing required field: {key}")
    return state


def save_state(path: Path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(path)


def refresh_unlocks(state):
    for event in RACE_EVENTS:
        if (state["completed_deliveries"] >= event["required_deliveries"]
                and state["trucking_reputation"] >= event["minimum_trucking_reputation"]
                and event["id"] not in state["unlocked_events"]):
            state["unlocked_events"].append(event["id"])


def complete_delivery(state, *, job_id, cargo, revenue_eur, distance_km):
    if not job_id or not cargo.strip():
        raise ValueError("job_id and cargo are required")
    if job_id in state["processed_job_ids"]:
        return False
    if revenue_eur < 0 or distance_km <= 0:
        raise ValueError("revenue must be non-negative and distance must be positive")
    reputation = max(1, int(distance_km // 100))
    state["money_eur"] = round(state["money_eur"] + revenue_eur, 2)
    state["trucking_reputation"] += reputation
    state["completed_deliveries"] += 1
    state["processed_job_ids"].append(job_id)
    refresh_unlocks(state)
    return True


def complete_race(state, *, event_id, finish_position, finishers, prize_eur):
    event = next((e for e in RACE_EVENTS if e["id"] == event_id), None)
    if event is None:
        raise ValueError("Unknown race event")
    if event_id not in state["unlocked_events"]:
        raise ValueError("Race event is not unlocked")
    if not (1 <= finish_position <= finishers) or finishers < 1 or prize_eur < 0:
        raise ValueError("Invalid race result")
    if state["money_eur"] < event["entry_fee_eur"]:
        raise ValueError("Not enough money to pay the race entry fee")
    state["money_eur"] = round(state["money_eur"] - event["entry_fee_eur"] + prize_eur, 2)
    # Finishing position determines reputation; podium gets a meaningful bonus.
    award = max(1, finishers - finish_position + 1)
    if finish_position == 1:
        award += 5
    state["racing_reputation"] += award
    state["completed_races"] += 1
    return award


def discover_assetto_corsa(game_root: Path):
    """Return actual installed car/track folder names; never invent content."""
    content = game_root / "content"
    cars = sorted(p.name for p in (content / "cars").iterdir() if p.is_dir()) if (content / "cars").is_dir() else []
    tracks = sorted(p.name for p in (content / "tracks").iterdir() if p.is_dir()) if (content / "tracks").is_dir() else []
    return {"cars": cars, "tracks": tracks}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for cmd in ("new", "status"):
        p = sub.add_parser(cmd); p.add_argument("--save", type=Path, required=True)
    p = sub.add_parser("delivery"); p.add_argument("--save", type=Path, required=True); p.add_argument("--job-id", required=True); p.add_argument("--cargo", required=True); p.add_argument("--revenue", type=float, required=True); p.add_argument("--distance-km", type=float, required=True)
    p = sub.add_parser("discover-ac"); p.add_argument("--game-root", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "discover-ac":
        print(json.dumps(discover_assetto_corsa(args.game_root), indent=2)); return
    state = fresh_state() if args.command == "new" else load_state(args.save)
    if args.command == "delivery":
        applied = complete_delivery(state, job_id=args.job_id, cargo=args.cargo, revenue_eur=args.revenue, distance_km=args.distance_km)
        print("Delivery applied" if applied else "Duplicate delivery ignored")
    save_state(args.save, state)
    print(json.dumps(state, indent=2))

if __name__ == "__main__": main()
