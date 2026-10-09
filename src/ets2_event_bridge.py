"""Consume JSON delivery events emitted by the native ETS2 telemetry plugin."""
from __future__ import annotations
import argparse, json, os, shutil, time
from pathlib import Path
from career import complete_delivery, load_state, save_state

def default_data_dir():
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("XDG_DATA_HOME")
    return Path(base) / "TruckRacingCareer" if base else Path.home()/".local"/"share"/"TruckRacingCareer"

def apply_delivery_event(event, save_path):
    if event.get("event") != "job.delivered":
        raise ValueError("Expected job.delivered telemetry event")
    job_id = str(event.get("job_id", "")).strip()
    state = load_state(save_path)
    applied = complete_delivery(state, job_id=job_id,
        cargo=str(event.get("cargo") or "ETS2 cargo delivery"),
        revenue_eur=float(event.get("revenue_eur", 0)),
        distance_km=float(event.get("distance_km", 0)))
    save_state(save_path, state)
    return {"applied": applied, "job_id": job_id, "state": state}

def process_event_file(path, save_path, archive):
    event = json.loads(path.read_text(encoding="utf-8"))
    result = apply_delivery_event(event, save_path)
    archive.mkdir(parents=True, exist_ok=True)
    shutil.move(str(path), str(archive/path.name))
    return result

def watch(inbox, save_path, archive, once=False, poll_seconds=.5):
    inbox.mkdir(parents=True, exist_ok=True)
    count = 0
    while True:
        for path in sorted(inbox.glob("*.json")):
            try:
                r = process_event_file(path, save_path, archive)
                print(("Applied" if r["applied"] else "Ignored duplicate")+f" ETS2 delivery {r['job_id']}")
                count += 1
            except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
                print(f"Could not process {path.name}: {exc}; file left in inbox")
        if once: return count
        time.sleep(max(.1, poll_seconds))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--inbox",type=Path,default=default_data_dir()/"inbox")
    p.add_argument("--archive",type=Path,default=default_data_dir()/"processed")
    p.add_argument("--save",type=Path,default=default_data_dir()/"career.json")
    p.add_argument("--once",action="store_true")
    a=p.parse_args(); watch(a.inbox,a.save,a.archive,a.once)
if __name__=="__main__": main()
