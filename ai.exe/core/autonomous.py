"""Bounded scheduler for self-initiated conversation.

Only produces local terminal messages. It does not contact external services,
inspect private diary entries, or perform actions outside the application.
"""
import time
from datetime import datetime


class AutonomousResponse:
    def __init__(
        self,
        enabled=True,
        idle_seconds=180,
        cooldown_seconds=900,
        max_per_session=3,
        clock=None,
    ):
        self.enabled = bool(enabled)
        self.idle_seconds = max(30, int(idle_seconds))
        self.cooldown_seconds = max(60, int(cooldown_seconds))
        self.max_per_session = max(0, int(max_per_session))
        self._clock = clock or time.monotonic
        self.last_user_activity = self._clock()
        self.last_initiative = None
        self.sent_this_session = 0
        self.last_reason = None

    def user_interacted(self):
        self.last_user_activity = self._clock()

    def set_enabled(self, enabled):
        self.enabled = bool(enabled)

    def evaluate(self, state, recent_history, active_goals=None, force=False):
        """Return a small trigger description or None; never generates speech itself."""
        if not self.enabled and not force:
            return None
        if self.sent_this_session >= self.max_per_session and not force:
            return None

        now = self._clock()
        idle_for = max(0, now - self.last_user_activity)
        if not force and idle_for < self.idle_seconds:
            return None
        if (
            not force
            and self.last_initiative is not None
            and now - self.last_initiative < self.cooldown_seconds
        ):
            return None

        state = state or {}
        history = recent_history or []
        goals = [
            goal for goal in (active_goals or [])
            if isinstance(goal, dict) and goal.get("status", "active") == "active"
        ]

        # Avoid repeatedly interrupting when the user is likely done or the
        # internal state suggests rest. These are transparent heuristics.
        mood = state.get("mood", "calm")
        energy = state.get("energy", 100)
        social = state.get("social", 50)
        curiosity = state.get("curiosity", 50)
        if not force and (mood == "tired" or energy < 20):
            return None

        last_user_text = ""
        last_assistant_text = ""
        if history:
            last = history[-1]
            if isinstance(last, dict):
                last_user_text = str(last.get("user", ""))[:300]
                last_assistant_text = str(last.get("ai", last.get("assistant", "")))[:300]

        reason = "scheduled_idle"
        if curiosity >= 70:
            reason = "curiosity"
        elif social < 30:
            reason = "social_state"
        elif goals:
            reason = "active_goal"
        elif last_user_text:
            reason = "conversation_followup"

        self.last_reason = reason
        return {
            "reason": reason,
            "idle_seconds": int(idle_for),
            "state": {
                "mood": mood,
                "energy": energy,
                "social": social,
                "curiosity": curiosity,
            },
            "last_user_text": last_user_text,
            "last_assistant_text": last_assistant_text,
            "active_goals": [str(goal.get("title", ""))[:120] for goal in goals[:3]],
            "local_time": datetime.now().astimezone().isoformat(timespec="minutes"),
            "forced": bool(force),
        }

    def mark_sent(self):
        now = self._clock()
        self.last_initiative = now
        self.last_user_activity = now
        self.sent_this_session += 1
