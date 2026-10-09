import json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import career

class CareerTests(unittest.TestCase):
    def test_delivery_earns_money_reputation_and_unlocks_first_race(self):
        state = career.fresh_state()
        self.assertTrue(career.complete_delivery(state, job_id="job-1", cargo="Machine parts", revenue_eur=1250, distance_km=240))
        self.assertEqual(state["money_eur"], 1250)
        self.assertEqual(state["trucking_reputation"], 2)
        self.assertIn("club_sprint_01", state["unlocked_events"])

    def test_duplicate_delivery_is_idempotent(self):
        state = career.fresh_state()
        kwargs = dict(job_id="job-1", cargo="Food", revenue_eur=500, distance_km=120)
        self.assertTrue(career.complete_delivery(state, **kwargs))
        self.assertFalse(career.complete_delivery(state, **kwargs))
        self.assertEqual(state["money_eur"], 500)
        self.assertEqual(state["completed_deliveries"], 1)

    def test_race_spends_entry_fee_and_adds_racing_reputation(self):
        state = career.fresh_state()
        career.complete_delivery(state, job_id="job-1", cargo="Parts", revenue_eur=1000, distance_km=200)
        award = career.complete_race(state, event_id="club_sprint_01", finish_position=1, finishers=8, prize_eur=600)
        self.assertEqual(state["money_eur"], 1450)
        self.assertEqual(state["racing_reputation"], award)
        self.assertEqual(state["completed_races"], 1)

    def test_cannot_enter_locked_race_or_overspend(self):
        state = career.fresh_state()
        with self.assertRaisesRegex(ValueError, "not unlocked"):
            career.complete_race(state, event_id="club_sprint_01", finish_position=1, finishers=8, prize_eur=600)
        career.complete_delivery(state, job_id="job-1", cargo="Parts", revenue_eur=100, distance_km=100)
        with self.assertRaisesRegex(ValueError, "Not enough money"):
            career.complete_race(state, event_id="club_sprint_01", finish_position=1, finishers=8, prize_eur=600)

    def test_save_persists_state(self):
        state = career.fresh_state()
        career.complete_delivery(state, job_id="job-1", cargo="Parts", revenue_eur=500, distance_km=120)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "career.json"
            career.save_state(path, state)
            loaded = career.load_state(path)
            self.assertEqual(loaded, state)

    def test_assetto_content_discovery_reads_real_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / "content/cars/ks_abarth500").mkdir(parents=True); (root / "content/tracks/monza").mkdir(parents=True)
            found = career.discover_assetto_corsa(root)
            self.assertEqual(found, {"cars": ["ks_abarth500"], "tracks": ["monza"]})

if __name__ == "__main__": unittest.main()
