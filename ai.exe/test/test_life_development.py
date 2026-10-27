import os
import tempfile
import unittest
from datetime import datetime, timezone

from core.life import LifeDevelopment


class LifeDevelopmentTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.temp_dir.name, "life.json")
        self.life = LifeDevelopment(self.path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_diary_persists_and_stays_separate(self):
        entry = self.life.add_diary_entry("Review today's choices.")
        reloaded = LifeDevelopment(self.path)
        self.assertEqual(reloaded.get_diary_entries()[0]["id"], entry["id"])
        self.assertEqual(reloaded.get_diary_entries()[0]["text"], "Review today's choices.")
        self.assertNotIn("conversation_history", reloaded.data)

    def test_empty_diary_entry_is_rejected(self):
        with self.assertRaises(ValueError):
            self.life.add_diary_entry("   ")

    def test_goal_status_transition(self):
        goal = self.life.add_goal("Finish P6", "2026-12-31")
        updated = self.life.update_goal_status(goal["id"], "completed")
        self.assertEqual(updated["status"], "completed")
        with self.assertRaises(ValueError):
            self.life.update_goal_status(goal["id"], "deleted")

    def test_invalid_target_date_is_rejected(self):
        with self.assertRaises(ValueError):
            self.life.add_goal("Goal", "not-a-date")

    def test_reflection_and_milestone(self):
        reflection = self.life.add_reflection("A test failed", "Add regression coverage", "Run tests")
        milestone = self.life.record_milestone("P6 started")
        self.assertEqual(self.life.get_reflections()[0]["id"], reflection["id"])
        self.assertEqual(milestone["title"], "P6 started")

    def test_time_context_and_elapsed_time(self):
        previous = datetime(2026, 10, 1, 8, 0, tzinfo=timezone.utc)
        current = datetime(2026, 10, 1, 9, 30, tzinfo=timezone.utc)
        self.life.mark_started(previous)
        context = self.life.get_time_context(current)
        self.assertEqual(context["seconds_since_last_seen"], 5400)
        self.assertEqual(context["daypart"], "morning")


if __name__ == "__main__":
    unittest.main()
