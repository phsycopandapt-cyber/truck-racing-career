import json, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import career
import assetto_corsa
import ets2_event_bridge

class CareerTests(unittest.TestCase):
    def test_delivery_earns_money_reputation_and_unlocks_first_race(self):
        state=career.fresh_state()
        self.assertTrue(career.complete_delivery(state,job_id="job-1",cargo="Machine parts",revenue_eur=1250,distance_km=240))
        self.assertEqual(state["money_eur"],1250)
        self.assertEqual(state["trucking_reputation"],2)
        self.assertIn("club_sprint_01",state["unlocked_events"])
    def test_duplicate_delivery_is_idempotent(self):
        state=career.fresh_state(); kwargs=dict(job_id="job-1",cargo="Food",revenue_eur=500,distance_km=120)
        self.assertTrue(career.complete_delivery(state,**kwargs));self.assertFalse(career.complete_delivery(state,**kwargs))
        self.assertEqual(state["money_eur"],500);self.assertEqual(state["completed_deliveries"],1)
    def test_race_spends_entry_fee_and_adds_reputation(self):
        state=career.fresh_state();career.complete_delivery(state,job_id="job-1",cargo="Parts",revenue_eur=1000,distance_km=200)
        award=career.complete_race(state,event_id="club_sprint_01",finish_position=1,finishers=8,prize_eur=600)
        self.assertEqual(state["money_eur"],1450);self.assertEqual(state["racing_reputation"],award);self.assertEqual(state["completed_races"],1)
    def test_locked_race_and_overspending_are_rejected(self):
        state=career.fresh_state()
        with self.assertRaisesRegex(ValueError,"not unlocked"):career.complete_race(state,event_id="club_sprint_01",finish_position=1,finishers=8,prize_eur=600)
        career.complete_delivery(state,job_id="job-1",cargo="Parts",revenue_eur=100,distance_km=100)
        with self.assertRaisesRegex(ValueError,"Not enough money"):career.complete_race(state,event_id="club_sprint_01",finish_position=1,finishers=8,prize_eur=600)
    def test_save_persists_state(self):
        state=career.fresh_state();career.complete_delivery(state,job_id="job-1",cargo="Parts",revenue_eur=500,distance_km=120)
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"career.json";career.save_state(p,state);self.assertEqual(career.load_state(p),state)
    def test_assetto_content_discovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/"content/cars/car_a/skins/default").mkdir(parents=True);(root/"content/tracks/track_a/layout1").mkdir(parents=True)
            found=assetto_corsa.discover_assetto_corsa(root)
            self.assertEqual(found,{"cars":["car_a"],"tracks":["track_a/layout1"]})
    def test_race_ini_has_player_and_ai_entries(self):
        ini=assetto_corsa.build_race_ini(car="car_a",track="track_a/layout1",driver_name="Test Driver",laps=4,ai_count=3,skins=["default","red"])
        self.assertIn("CONFIG_TRACK=layout1",ini);self.assertIn("RACE_LAPS=4",ini);self.assertIn("[CAR_0]",ini);self.assertIn("MODEL=-",ini);self.assertIn("[CAR_3]",ini)
    def test_parse_realistic_race_out_result(self):
        data={"players":[{"name":"Test Driver","car":"car_a"},{"name":"AI","car":"car_a"}],"sessions":[{"type":3,"name":"RACE","raceResult":[1,0]}]}
        self.assertEqual(assetto_corsa.parse_race_result(data,"Test Driver"),{"position":2,"finishers":2})
    def test_parser_rejects_missing_player(self):
        self.assertIsNone(assetto_corsa.parse_race_result({"players":[{"name":"AI"}],"sessions":[{"type":3,"raceResult":[0]}]},"Test Driver"))
    def test_ets2_event_requires_valid_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            save=Path(tmp)/"career.json"
            event={"event":"job.delivered","job_id":"job-a","cargo":"Parts","revenue_eur":1200,"distance_km":250}
            result=ets2_event_bridge.apply_delivery_event(event,save)
            self.assertTrue(result["applied"]);self.assertEqual(result["state"]["money_eur"],1200)
            again=ets2_event_bridge.apply_delivery_event(event,save)
            self.assertFalse(again["applied"]);self.assertEqual(again["state"]["completed_deliveries"],1)

if __name__=="__main__":unittest.main()
