"""Assetto Corsa content discovery, race config and result parser."""
import json, os, shutil, subprocess, time
from pathlib import Path

def discover_assetto_corsa(game_root):
    root=Path(game_root)/"content"; cars=root/"cars"; tracks=root/"tracks"
    cs=sorted(p.name for p in cars.iterdir() if p.is_dir()) if cars.is_dir() else []
    ts=[]
    if tracks.is_dir():
        for t in sorted(p for p in tracks.iterdir() if p.is_dir()):
            layouts=sorted(p.name for p in t.iterdir() if p.is_dir() and p.name not in {"ai","data"})
            ts.extend([t.name+"/"+x for x in layouts] if layouts else [t.name])
    return {"cars":cs,"tracks":ts}

def resolve_documents_root(explicit=None):
    if explicit:return Path(explicit)
    home=Path.home()
    for p in [home/"Documents"/"Assetto Corsa",home/"OneDrive"/"Documents"/"Assetto Corsa"]:
        if p.exists():return p
    return home/"Documents"/"Assetto Corsa"

def build_race_ini(*,car,track,driver_name,laps=3,ai_count=7,skins=None):
    if not car or any(c in car for c in "\\/\r\n"):raise ValueError("car must be a single installed car folder name")
    if not track or "\\" in track or "\r" in track or "\n" in track:raise ValueError("invalid track")
    if not 1<=laps<=99 or not 0<=ai_count<=19:raise ValueError("laps must be 1–99 and AI count 0–19")
    skins=skins or [""]; skin=skins[0]; folder,_,layout=track.partition("/")
    lines=["[RACE]",f"TRACK={folder}",f"CONFIG_TRACK={layout}",f"MODEL={car}","MODEL_CONFIG=",f"SKIN={skin}","PENALTIES=1","FIXED_SETUP=0","DRIFT_MODE=0",f"RACE_LAPS={laps}",f"CARS={ai_count+1}","AI_LEVEL=80","JUMP_START_PENALTY=0","WEATHER_0=3_clear","","[DRIVE]",f"MODEL={car}",f"SKIN={skin}","MODEL_CONFIG=","AI_LEVEL=","AI_AGGRESSION=0","SETUP=","FIXED_SETUP=0","VIRTUAL_MIRROR=0",f"DRIVER_NAME={driver_name}","NATIONALITY=","","[HEADER]","VERSION=2","","[SESSION_0]","NAME=RACE","TYPE=3","SPAWN_SET=START",f"LAPS={laps}","DURATION_MINUTES=0","","[GROOVE]","VIRTUAL_LAPS=10","MAX_LAPS=30","STARTING_LAPS=0",""]
    lines += ["[CAR_0]","SETUP=",f"SKIN={skin}","MODEL=-","MODEL_CONFIG=","BALLAST=0","RESTRICTOR=0",f"DRIVER_NAME={driver_name}","NATIONALITY=",""]
    for i in range(1,ai_count+1):
        lines += [f"[CAR_{i}]",f"MODEL={car}",f"SKIN={skins[i%len(skins)]}","MODEL_CONFIG=",f"DRIVER_NAME=Truck Racing AI {i:02d}","NATION_CODE=ITA","AI_LEVEL=80","AI_AGGRESSION=20","SETUP=","BALLAST=0","RESTRICTOR=0",""]
    return "\n".join(lines)

def parse_race_result(data,driver_name):
    players=data.get("players") or []; sessions=data.get("sessions") or []
    if not players or not sessions:return None
    race=next((s for s in reversed(sessions) if s.get("type")==3 or str(s.get("name","")).upper()=="RACE"),None)
    if not race:return None
    order=race.get("raceResult") or []
    if not order:return None
    for pos,index in enumerate(order,1):
        if isinstance(index,int) and 0<=index<len(players) and str(players[index].get("name","")).strip().casefold()==driver_name.strip().casefold():
            return {"position":pos,"finishers":len([i for i in order if isinstance(i,int) and 0<=i<len(players)])}
    return None

def run_race(*,game_root,documents_root,car,track,driver_name,laps=3,ai_count=7,wait=True):
    root=Path(game_root); exe=root/"acs.exe"; content=discover_assetto_corsa(root)
    if car not in content["cars"]:raise ValueError(f"Car '{car}' not found in Assetto Corsa")
    if track not in content["tracks"]:raise ValueError(f"Track '{track}' not found in Assetto Corsa")
    if not exe.is_file():raise FileNotFoundError(f"acs.exe not found: {exe}")
    docs=Path(documents_root); cfg=docs/"cfg"; out=docs/"out"/"race_out.json"; cfg.mkdir(parents=True,exist_ok=True);out.parent.mkdir(parents=True,exist_ok=True)
    skinsdir=root/"content"/"cars"/car/"skins"; skins=sorted(p.name for p in skinsdir.iterdir() if p.is_dir()) if skinsdir.is_dir() else [""]
    raceini=cfg/"race.ini";raceini.write_text(build_race_ini(car=car,track=track,driver_name=driver_name,laps=laps,ai_count=ai_count,skins=skins),encoding="utf-8")
    old=cfg/"launcher.ini"; lines=old.read_text(encoding="utf-8",errors="replace").splitlines() if old.exists() else []
    replacements={"DRIVE":"race","TRACK":track.split("/",1)[0]};seen=set();patched=[]
    for line in lines:
        key=line.split("=",1)[0].strip().upper() if "=" in line else ""
        if key in replacements:patched.append(key+"="+replacements[key]);seen.add(key)
        else:patched.append(line)
    for k,v in replacements.items():
        if k not in seen:patched.append(k+"="+v)
    old.write_text("\n".join(patched)+"\n",encoding="utf-8")
    backup=None
    if out.exists():
        backupdir=Path(os.environ.get("LOCALAPPDATA",str(Path.home())))/"TruckRacingCareer"/"previous-ac-results";backupdir.mkdir(parents=True,exist_ok=True)
        backup=backupdir/f"race_out_before_{int(time.time()*1000)}.json";shutil.copy2(out,backup);out.unlink()
    proc=subprocess.Popen([str(exe)],cwd=str(root))
    if not wait:return {"started":True,"pid":proc.pid,"race_ini":str(raceini)}
    proc.wait()
    if not out.exists():return {"started":True,"completed":False,"reason":"Assetto Corsa did not write a fresh race_out.json; no career reward was recorded.","previous_result_backup":str(backup) if backup else None}
    try:data=json.loads(out.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as exc:return {"started":True,"completed":False,"reason":f"Could not read race_out.json: {exc}"}
    result=parse_race_result(data,driver_name)
    return {"started":True,"completed":True,**result,"race_out":str(out)} if result else {"started":True,"completed":False,"reason":"Could not verify player's finishing position; no reward was recorded."}
