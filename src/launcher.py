"""Truck Racing Career companion for ETS2 telemetry and original Assetto Corsa."""
import json, os, subprocess, threading, time, tkinter as tk
from pathlib import Path
from tkinter import ttk, filedialog, messagebox
from career import RACE_EVENTS, complete_delivery, complete_race, load_state, save_state, fresh_state
from assetto_corsa import resolve_documents_root, run_race

def data_dir():
    root=os.environ.get("LOCALAPPDATA") or os.environ.get("XDG_DATA_HOME") or str(Path.home()/".local"/"share")
    return Path(root)/"TruckRacingCareer"
DATA=data_dir(); SAVE=DATA/"career.json"; INBOX=DATA/"inbox"; ARCHIVE=DATA/"processed"; CONFIG=DATA/"config.json"
def read_config():
    try:return json.loads(CONFIG.read_text(encoding="utf-8"))
    except (OSError,ValueError):return {}
def discover(root):
    root=Path(root); cars=root/"content"/"cars"; tracks=root/"content"/"tracks"
    cs=sorted(p.name for p in cars.iterdir() if p.is_dir()) if cars.is_dir() else []
    ts=[]
    if tracks.is_dir():
        for t in sorted(p for p in tracks.iterdir() if p.is_dir()):
            layouts=sorted(p.name for p in t.iterdir() if p.is_dir() and p.name not in {"ai","data"})
            ts.extend([t.name+"/"+x for x in layouts] if layouts else [t.name])
    return cs,ts
def process_events():
    INBOX.mkdir(parents=True,exist_ok=True)
    while True:
        for path in sorted(INBOX.glob("*.json")):
            try:
                event=json.loads(path.read_text(encoding="utf-8"))
                if event.get("event")!="job.delivered": raise ValueError("Unsupported event type")
                state=load_state(SAVE)
                complete_delivery(state,job_id=str(event.get("job_id","")),cargo=str(event.get("cargo") or "ETS2 cargo delivery"),revenue_eur=float(event.get("revenue_eur",0)),distance_km=float(event.get("distance_km",0)))
                save_state(SAVE,state); ARCHIVE.mkdir(parents=True,exist_ok=True); path.replace(ARCHIVE/path.name)
            except Exception as exc: print("Telemetry event left in inbox:",path.name,exc)
        time.sleep(.5)
class App:
 def __init__(self,root):
    self.root=root; root.title("Truck Racing Career"); root.geometry("740x520")
    DATA.mkdir(parents=True,exist_ok=True)
    if not SAVE.exists():save_state(SAVE,fresh_state())
    self.config=read_config(); self.ac=tk.StringVar(value=self.config.get("assetto_corsa_path","")); self.driver=tk.StringVar(value=self.config.get("driver_name","Career Driver"))
    self.car=tk.StringVar();self.track=tk.StringVar();self.event=tk.StringVar();self.status=tk.StringVar(value="Finish an ETS2 delivery to unlock racing.")
    f=ttk.Frame(root,padding=16);f.pack(fill="both",expand=True)
    ttk.Label(f,text="TRUCK RACING CAREER",font=("Segoe UI",18,"bold")).pack(anchor="w")
    ttk.Label(f,text="Deliver in Euro Truck Simulator 2. Race in your own Assetto Corsa installation.").pack(anchor="w",pady=6)
    self.stats=ttk.Label(f,text="");self.stats.pack(anchor="w",pady=8)
    g=ttk.LabelFrame(f,text="Assetto Corsa",padding=10);g.pack(fill="x",pady=8)
    ttk.Entry(g,textvariable=self.ac).grid(row=0,column=0,sticky="ew");ttk.Button(g,text="Browse",command=self.browse).grid(row=0,column=1,padx=5);ttk.Button(g,text="Scan",command=self.scan).grid(row=0,column=2)
    ttk.Label(g,text="Driver").grid(row=1,column=0,sticky="w",pady=5);ttk.Entry(g,textvariable=self.driver).grid(row=1,column=1,sticky="ew",pady=5)
    self.events=ttk.Combobox(g,textvariable=self.event,state="readonly");self.events.grid(row=2,column=0,columnspan=3,sticky="ew",pady=4)
    self.cars=ttk.Combobox(g,textvariable=self.car,state="readonly");self.cars.grid(row=3,column=0,sticky="ew",pady=4)
    self.tracks=ttk.Combobox(g,textvariable=self.track,state="readonly");self.tracks.grid(row=3,column=1,columnspan=2,sticky="ew",pady=4);g.columnconfigure(0,weight=1);g.columnconfigure(1,weight=1)
    ttk.Button(g,text="Launch race",command=self.race).grid(row=4,column=0,sticky="w",pady=8)
    ttk.Button(f,text="Start Euro Truck Simulator 2",command=self.ets2).pack(anchor="w",pady=5)
    ttk.Label(f,textvariable=self.status,wraplength=680).pack(anchor="w",pady=8)
    threading.Thread(target=process_events,daemon=True).start();self.scan();self.refresh()
 def browse(self):
    p=filedialog.askdirectory(title="Select Assetto Corsa folder containing acs.exe")
    if p:self.ac.set(p);self.scan()
 def scan(self):
    cars,tracks=discover(self.ac.get()) if self.ac.get() else ([],[])
    self.cars["values"]=cars;self.tracks["values"]=tracks
    if cars and self.car.get() not in cars:self.car.set(cars[0])
    if tracks and self.track.get() not in tracks:self.track.set(tracks[0])
 def refresh(self):
    try:
        s=load_state(SAVE);self.stats.configure(text=f"Money €{s['money_eur']:,.2f} | Trucking rep {s['trucking_reputation']} | Racing rep {s['racing_reputation']} | Deliveries {s['completed_deliveries']} | Races {s['completed_races']}")
        events=[e for e in RACE_EVENTS if e["id"] in s["unlocked_events"]]; values=[e["id"]+" — "+e["name"] for e in events];self.events["values"]=values
        if values and self.event.get() not in values:self.event.set(values[0])
        self.status.set("Ready. Complete a delivery in ETS2 to unlock the first race." if not events else "Career saved locally. Choose an unlocked event, installed car and track.")
    except Exception as e:self.status.set(str(e))
    self.root.after(1000,self.refresh)
 def ets2(self):
    try:os.startfile("steam://rungameid/227300")
    except Exception as e:messagebox.showerror("Truck Racing Career",str(e))
 def race(self):
    try:
        self.config.update({"assetto_corsa_path":self.ac.get(),"driver_name":self.driver.get()});CONFIG.write_text(json.dumps(self.config,indent=2),encoding="utf-8")
        event_id=self.event.get().split(" — ",1)[0];s=load_state(SAVE);event=next(e for e in RACE_EVENTS if e["id"]==event_id)
        if s["money_eur"]<event["entry_fee_eur"]:raise ValueError("Not enough career money for the entry fee")
        self.status.set("Assetto Corsa is running. Finish the race to import your result.");self.root.update_idletasks()
        result=run_race(game_root=Path(self.ac.get()),documents_root=resolve_documents_root(),car=self.car.get(),track=self.track.get(),driver_name=self.driver.get(),laps=3,ai_count=7,wait=True)
        if not result.get("completed"):raise ValueError(result.get("reason","No verified player finishing position in race_out.json; no reward recorded."))
        prize=max(0,(result["finishers"]-result["position"]+1)*100)
        award=complete_race(s,event_id=event_id,finish_position=result["position"],finishers=result["finishers"],prize_eur=prize);save_state(SAVE,s)
        self.status.set(f"Race recorded: P{result['position']}/{result['finishers']}. Prize €{prize}; racing reputation +{award}.")
    except Exception as e:messagebox.showerror("Truck Racing Career",str(e));self.status.set(str(e))
def main():
    root=tk.Tk();App(root);root.mainloop()
if __name__=="__main__":main()
