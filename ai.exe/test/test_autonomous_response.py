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
            idle_grace_seconds=10,
            evaluation_interval_seconds=5,
            clock=self.clock,
        )
        self.state = {
            "mood": "calm",
            "energy": 80,
            "social": 50,
            "curiosity": 50,
        }

    def test_waits_for_short_interaction_grace(self):
        self.clock.advance(9)
        self.assertIsNone(self.agent.evaluate(self.state, []))
        self.clock.advance(1)
        self.assertIsNotNone(self.agent.evaluate(self.state, []))

    def test_user_interaction_resets_idle_grace(self):
        self.clock.advance(9)
        self.agent.user_interacted()
        self.clock.advance(9)
        self.assertIsNone(self.agent.evaluate(self.state, []))

    def test_evaluation_interval_is_technical_not_speech_cooldown(self):
        self.clock.advance(10)
        self.assertIsNotNone(self.agent.evaluate(self.state, []))
        self.agent.mark_evaluated()
        self.agent.mark_spoken()
        self.assertIsNone(self.agent.evaluate(self.state, []))
        self.clock.advance(5)
        # A new decision cycle may happen even though the agent recently spoke.
        self.assertIsNotNone(self.agent.evaluate(self.state, []))

    def test_disabled_suppresses_automatic_but_force_requests_evaluation(self):
        self.agent.set_enabled(False)
        self.clock.advance(20)
        self.assertIsNone(self.agent.evaluate(self.state, []))
        self.assertIsNotNone(self.agent.evaluate(self.state, [], force=True))

    def test_tired_state_is_passed_to_decision_layer_not_silently_blocked(self):
        self.clock.advance(10)
        tired = dict(self.state, mood="tired", energy=10)
        trigger = self.agent.evaluate(tired, [])
        self.assertIsNotNone(trigger)
        self.assertEqual(trigger["state"]["mood"], "tired")
        self.assertEqual(trigger["state"]["energy"], 10)

    def test_decision_layer_can_set_context_dependent_recheck(self):
        self.clock.advance(10)
        self.agent.evaluate(self.state, [])
        self.agent.mark_evaluated()
        self.agent.schedule_next_evaluation(120)
        self.clock.advance(60)
        self.assertIsNone(self.agent.evaluate(self.state, []))
        self.clock.advance(60)
        self.assertIsNotNone(self.agent.evaluate(self.state, []))

    def test_no_session_message_cap(self):
        self.clock.advance(10)
        self.agent.evaluate(self.state, [])
        for _ in range(10):
            self.agent.mark_spoken()
        self.clock.advance(5)
        self.assertIsNotNone(self.agent.evaluate(self.state, []))


if __name__ == "__main__":
    unittest.main()
