"""P6 life-development storage for private diary, goals, reflections, milestones, and time awareness.

Private diary entries are kept separate from chat history and are not automatically
included in LLM prompts. This module performs no autonomous external actions.
"""
import json
import os
from datetime import datetime
from typing import Optional


class LifeDevelopment:
    def __init__(self, file_path: str = "data/life.json", max_entries: int = 500):
        self.file_path = file_path
        self.max_entries = max(1, int(max_entries))
        self.data = self._load()
        for key in ("diary", "goals", "reflections", "milestones"):
            if not isinstance(self.data.get(key), list):
                self.data[key] = []
        self.data.setdefault("last_seen_at", None)

    @staticmethod
    def _now() -> datetime:
        return datetime.now().astimezone()

    @classmethod
    def _timestamp(cls) -> str:
        return cls._now().isoformat(timespec="seconds")

    def _load(self) -> dict:
        if not os.path.exists(self.file_path):
            return {"diary": [], "goals": [], "reflections": [], "milestones": [], "last_seen_at": None}
        with open(self.file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, dict):
            raise ValueError("Life-development data must be a JSON object.")
        return data

    def save(self) -> None:
        directory = os.path.dirname(self.file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        temporary_path = self.file_path + ".tmp"
        with open(temporary_path, "w", encoding="utf-8") as file:
            json.dump(self.data, file, indent=4, ensure_ascii=False)
        os.replace(temporary_path, self.file_path)

    def _next_id(self, collection: str) -> str:
        prefix = collection + "-"
        highest = 0
        for item in self.data.get(collection, []):
            value = str(item.get("id", ""))
            if value.startswith(prefix):
                try:
                    highest = max(highest, int(value[len(prefix):]))
                except ValueError:
                    continue
        return f"{collection}-{highest + 1:04d}"

    def add_diary_entry(self, text: str) -> dict:
        text = str(text or "").strip()
        if not text:
            raise ValueError("Diary entry cannot be empty.")
        entry = {"id": self._next_id("diary"), "created_at": self._timestamp(), "text": text}
        self.data["diary"].append(entry)
        self.data["diary"] = self.data["diary"][-self.max_entries:]
        self.save()
        return entry.copy()

    def get_diary_entries(self, limit: int = 10) -> list[dict]:
        limit = max(0, int(limit))
        return [item.copy() for item in self.data["diary"][-limit:]][::-1] if limit else []

    def add_goal(self, title: str, target_date: Optional[str] = None) -> dict:
        title = str(title or "").strip()
        if not title:
            raise ValueError("Goal title cannot be empty.")
        if target_date:
            target_date = str(target_date).strip()
            datetime.strptime(target_date, "%Y-%m-%d")
        goal = {
            "id": self._next_id("goals"),
            "title": title,
            "created_at": self._timestamp(),
            "target_date": target_date or None,
            "status": "active",
        }
        self.data["goals"].append(goal)
        self.data["goals"] = self.data["goals"][-self.max_entries:]
        self.save()
        return goal.copy()

    def get_goals(self, status: Optional[str] = None) -> list[dict]:
        goals = self.data["goals"]
        if status is not None:
            goals = [goal for goal in goals if goal.get("status") == status]
        return [goal.copy() for goal in goals]

    def update_goal_status(self, goal_id: str, status: str) -> dict:
        if status not in {"active", "paused", "completed"}:
            raise ValueError("Status must be active, paused, or completed.")
        for goal in self.data["goals"]:
            if goal.get("id") == goal_id:
                goal["status"] = status
                goal["updated_at"] = self._timestamp()
                self.save()
                return goal.copy()
        raise KeyError(f"Goal not found: {goal_id}")

    def add_reflection(self, observation: str, lesson: str = "", next_step: str = "") -> dict:
        observation = str(observation or "").strip()
        if not observation:
            raise ValueError("Reflection observation cannot be empty.")
        reflection = {
            "id": self._next_id("reflections"),
            "created_at": self._timestamp(),
            "observation": observation,
            "lesson": str(lesson or "").strip(),
            "next_step": str(next_step or "").strip(),
        }
        self.data["reflections"].append(reflection)
        self.data["reflections"] = self.data["reflections"][-self.max_entries:]
        self.save()
        return reflection.copy()

    def get_reflections(self, limit: int = 10) -> list[dict]:
        limit = max(0, int(limit))
        return [item.copy() for item in self.data["reflections"][-limit:]][::-1] if limit else []

    def record_milestone(self, title: str, detail: str = "") -> dict:
        title = str(title or "").strip()
        if not title:
            raise ValueError("Milestone title cannot be empty.")
        milestone = {
            "id": self._next_id("milestones"),
            "created_at": self._timestamp(),
            "title": title,
            "detail": str(detail or "").strip(),
        }
        self.data["milestones"].append(milestone)
        self.data["milestones"] = self.data["milestones"][-self.max_entries:]
        self.save()
        return milestone.copy()

    def get_time_context(self, now: Optional[datetime] = None) -> dict:
        current = now or self._now()
        if current.tzinfo is None:
            current = current.astimezone()
        hour = current.hour
        if 5 <= hour < 11:
            daypart = "morning"
        elif 11 <= hour < 15:
            daypart = "midday"
        elif 15 <= hour < 18:
            daypart = "afternoon"
        elif 18 <= hour < 22:
            daypart = "evening"
        else:
            daypart = "night"

        gap_seconds = None
        previous = self.data.get("last_seen_at")
        if previous:
            try:
                previous_dt = datetime.fromisoformat(previous)
                if previous_dt.tzinfo is None:
                    previous_dt = previous_dt.astimezone()
                gap_seconds = max(0, int((current - previous_dt).total_seconds()))
            except (TypeError, ValueError):
                pass
        return {
            "now": current.isoformat(timespec="seconds"),
            "local_date": current.date().isoformat(),
            "daypart": daypart,
            "seconds_since_last_seen": gap_seconds,
        }

    def mark_started(self, now: Optional[datetime] = None) -> dict:
        current = now or self._now()
        self.data["last_seen_at"] = current.isoformat(timespec="seconds")
        self.save()
        return self.get_time_context(current)
