"""Decision-cycle scheduler for self-initiated conversation.

The scheduler decides when to ask the cognition layer for an evaluation; it
does not decide that the AI must speak. Timing values are resource/interaction
guards, not personality rules. This module performs no external actions.
"""
import time
from datetime import datetime


class AutonomousResponse:
    def __init__(
        self,
        enabled=True,
        idle_grace_seconds=60,
        evaluation_interval_seconds=30,
        clock=None,
    ):
        self.enabled = bool(enabled)
        self.idle_grace_seconds = max(1, int(idle_grace_seconds))
        self.evaluation_interval_seconds = max(1, int(evaluation_interval_seconds))
        self._clock = clock or time.monotonic
        self.last_user_activity = self._clock()
        self.last_evaluation = None
        self.next_evaluation_at = None
        self.last_initiative = None
        self.evaluations_this_session = 0
        self.initiatives_this_session = 0

    def user_interacted(self):
        self.last_user_activity = self._clock()

    def set_enabled(self, enabled):
        self.enabled = bool(enabled)

    def evaluate(
        self,
        state,
        recent_history,
        active_goals=None,
        preferences=None,
        self_model=None,
        force=False,
    ):
        """Return a context snapshot when a decision cycle is due, else None.

        `force=True` requests a decision cycle now; it does not force speech.
        """
        if not self.enabled and not force:
            return None

        now = self._clock()
        idle_for = max(0, now - self.last_user_activity)
        if not force and idle_for < self.idle_grace_seconds:
            return None
        if not force and self.next_evaluation_at is not None and now < self.next_evaluation_at:
            return None
        if (
            not force
            and self.next_evaluation_at is None
            and self.last_evaluation is not None
            and now - self.last_evaluation < self.evaluation_interval_seconds
        ):
            return None

        state = state if isinstance(state, dict) else {}
        history = recent_history if isinstance(recent_history, list) else []
        goals = [
            goal for goal in (active_goals or [])
            if isinstance(goal, dict) and goal.get("status", "active") == "active"
        ]

        last_user_text = ""
        last_assistant_text = ""
        if history and isinstance(history[-1], dict):
            last_user_text = str(history[-1].get("user", ""))[:500]
            last_assistant_text = str(
                history[-1].get("ai", history[-1].get("assistant", ""))
            )[:500]

        return {
            "idle_seconds": int(idle_for),
            "state": {
                key: state.get(key)
                for key in ("mood", "energy", "social", "curiosity", "activity")
                if key in state
            },
            "last_user_text": last_user_text,
            "last_assistant_text": last_assistant_text,
            "active_goals": [
                {"title": str(goal.get("title", ""))[:160],
                 "target_date": goal.get("target_date")}
                for goal in goals[:10]
            ],
            "preferences": preferences if isinstance(preferences, dict) else {},
            "self_model": self_model if isinstance(self_model, dict) else {},
            "recent_history": history[-8:],
            "local_time": datetime.now().astimezone().isoformat(timespec="minutes"),
            "forced_evaluation": bool(force),
            "last_initiative_seconds_ago": (
                None if self.last_initiative is None
                else max(0, int(now - self.last_initiative))
            ),
        }

    def mark_evaluated(self):
        self.last_evaluation = self._clock()
        self.evaluations_this_session += 1

    def schedule_next_evaluation(self, seconds):
        """Set a context-dependent recheck time suggested by the decision layer."""
        delay = max(30, min(600, int(seconds)))
        self.next_evaluation_at = self._clock() + delay

    def mark_spoken(self):
        """Record speech for context and duplicate-awareness, not as a cooldown."""
        self.last_initiative = self._clock()
        self.initiatives_this_session += 1
