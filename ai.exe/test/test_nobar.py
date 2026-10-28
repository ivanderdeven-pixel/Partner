import unittest
from unittest.mock import patch

from core.nobar import ScreenNobar


class NobarTests(unittest.TestCase):
    def test_starts_off_and_status_is_read_only(self):
        nobar = ScreenNobar(model="test-vision", interval=4)
        status = nobar.status()
        self.assertEqual(status["state"], "off")
        self.assertEqual(status["model"], "test-vision")
        self.assertEqual(status["interval_seconds"], 4.0)
        self.assertEqual(status["last_observation"], "")

    def test_pause_resume_and_stop_transitions(self):
        nobar = ScreenNobar(model="test-vision")
        with patch.object(nobar, "_watch_loop", side_effect=lambda: None):
            self.assertTrue(nobar.start())
            self.assertEqual(nobar.state, "watching")
            self.assertTrue(nobar.pause())
            self.assertEqual(nobar.state, "paused")
            self.assertTrue(nobar.resume())
            self.assertEqual(nobar.state, "watching")
            nobar.stop()
            self.assertEqual(nobar.state, "off")

    def test_cannot_pause_when_off_or_resume_when_not_paused(self):
        nobar = ScreenNobar(model="test-vision")
        self.assertFalse(nobar.pause())
        self.assertFalse(nobar.resume())


if __name__ == "__main__":
    unittest.main()
