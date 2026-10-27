import unittest

from core.autonomous import AutonomousResponse


class FakeClock:
    def __init__(self):
        self.value = 1000.0

    def __call__(self):
        return self.value

    def advance(self, seconds):
        self.value += seconds


class AutonomousResponseTests(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.agent = AutonomousResponse(
            enabled=True,
            idle_seconds=30,
            cooldown_seconds=60,
            max_per_session=2,
            clock=self.clock,
        )
        self.state = {
            "mood": "calm",
            "energy": 80,
            "social": 50,
            "curiosity": 50,
        }

    def test_waits_until_idle_threshold(self):
        self.clock.advance(29)
        self.assertIsNone(self.agent.evaluate(self.state, []))
        self.clock.advance(1)
        self.assertIsNotNone(self.agent.evaluate(self.state, []))

    def test_user_interaction_resets_idle_clock(self):
        self.clock.advance(29)
        self.agent.user_interacted()
        self.clock.advance(29)
        self.assertIsNone(self.agent.evaluate(self.state, []))

    def test_tired_state_suppresses_automatic_initiative(self):
        self.clock.advance(60)
        tired = dict(self.state, mood="tired", energy=10)
        self.assertIsNone(self.agent.evaluate(tired, []))

    def test_disabled_suppresses_automatic_but_force_can_run(self):
        self.agent.set_enabled(False)
        self.clock.advance(60)
        self.assertIsNone(self.agent.evaluate(self.state, []))
        self.assertIsNotNone(self.agent.evaluate(self.state, [], force=True))

    def test_cooldown_and_session_limit(self):
        self.clock.advance(60)
        self.assertIsNotNone(self.agent.evaluate(self.state, []))
        self.agent.mark_sent()
        self.assertIsNone(self.agent.evaluate(self.state, []))
        self.clock.advance(61)
        self.assertIsNotNone(self.agent.evaluate(self.state, []))
        self.agent.mark_sent()
        self.clock.advance(61)
        self.assertIsNone(self.agent.evaluate(self.state, []))


if __name__ == "__main__":
    unittest.main()
