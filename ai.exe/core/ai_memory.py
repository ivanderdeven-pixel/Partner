import json
import os
from datetime import datetime, timezone


AI_MEMORY_FILE = "data/ai_memory.json"


class AIMemory:

    def __init__(self):
        self.memory = self.load()

        if self.memory["identity"]["operational_age"]["activated_at"] is None:
            self.memory["identity"]["operational_age"]["activated_at"] = (
                datetime.now(timezone.utc).isoformat()
            )
            self.save()

    def load(self):
        if not os.path.exists(AI_MEMORY_FILE):
            return {
                "identity": {
                    "instance_id": "giftia-01",
                    "name": "Ikari",
                    "status": "active",
                    "origin": {
                        "created by": "user",
                        "created_at": None
                    },
                    "operational_age": {
                        "activated_at": None
                    }
                },

                "preferences": {
                    "likes": [],
                    "dislikes": [],
                    "candidates": []
                },

                "opinions": [],

                "personality": {},

                "values": [],

                "morality": {
                    "principles": [],
                    "boundaries": []
                },

                "self_model": {
                    "description": None,
                    "strengths": [],
                    "weaknesses": [],
                    "interests": [],
                    "development": []
                },

                "experiences": [],

                "important_events": [],

                "development": []
            }

        with open(
            AI_MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            memory = json.load(file)

        memory.setdefault("identity", {})
        memory["identity"].setdefault(
            "operational_age",
            {}
        )
        memory["identity"]["operational_age"].setdefault(
            "activated_at",
            None
        )

        memory.setdefault("preferences", {})
        memory["preferences"].setdefault(
            "likes",
            []
        )
        memory["preferences"].setdefault(
            "dislikes",
            []
        )
        memory["preferences"].setdefault(
            "candidates",
            []
        )

        memory.setdefault("opinions", [])

        memory.setdefault(
            "personality",
            {}
        )

        memory.setdefault(
            "values",
            []
        )

        memory.setdefault(
            "morality",
            {}
        )
        memory["morality"].setdefault(
            "principles",
            []
        )
        memory["morality"].setdefault(
            "boundaries",
            []
        )

        memory.setdefault(
            "self_model",
            {}
        )
        memory["self_model"].setdefault(
            "description",
            None
        )
        memory["self_model"].setdefault(
            "strengths",
            []
        )
        memory["self_model"].setdefault(
            "weaknesses",
            []
        )
        memory["self_model"].setdefault(
            "interests",
            []
        )
        memory["self_model"].setdefault(
            "development",
            []
        )

        memory.setdefault(
            "experiences",
            []
        )

        memory.setdefault(
            "important_events",
            []
        )

        memory.setdefault(
            "development",
            []
        )

        return memory

    def save(self):
        os.makedirs(
            "data",
            exist_ok=True
        )

        with open(
            AI_MEMORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                self.memory,
                file,
                indent=4,
                ensure_ascii=False
            )

    def get(self, key, default=None):
        return self.memory.get(
            key,
            default
        )

    # =========================
    # IDENTITY
    # =========================

    def get_identity(self):
        return self.memory.get(
            "identity",
            {}
        )

    def get_ai_name(self):
        identity = self.get_identity()

        return identity.get(
            "name"
        )

    def set_ai_name(self, name):
        self.memory["identity"]["name"] = name
        self.save()

    def get_activation_time(self):
        return (
            self.memory[
                "identity"
            ][
                "operational_age"
            ][
                "activated_at"
            ]
        )

    def get_operational_age(self):
        activated_at = datetime.fromisoformat(
            self.get_activation_time()
        )

        if activated_at.tzinfo is None:
            activated_at = activated_at.replace(
                tzinfo=timezone.utc
            )

        now = datetime.now(timezone.utc)

        elapsed = now - activated_at

        return {
            "total_seconds": int(
                elapsed.total_seconds()
            ),
            "days": elapsed.days
        }

    # =========================
    # PREFERENCES
    # =========================

    def add_preference(
        self,
        preference_type,
        value,
        reason=None
    ):
        if preference_type not in [
            "likes",
            "dislikes"
        ]:
            return

        preference = {
            "value": value,
            "reason": reason
        }

        preferences = self.memory[
            "preferences"
        ]

        for existing in preferences[
            preference_type
        ]:
            if existing["value"] == value:
                return

        preferences[
            preference_type
        ].append(preference)

        self.save()

    def get_preferences(self):
        return self.memory.get(
            "preferences",
            {}
        )

    def add_preference_candidate(
        self,
        value
    ):
        candidates = self.memory[
            "preferences"
        ][
            "candidates"
        ]

        for candidate in candidates:
            if candidate["value"] == value:
                return

        candidates.append({
            "value": value,
            "status": "pending"
        })

        self.save()

    def get_preference_candidates(self):
        return self.memory[
            "preferences"
        ].get(
            "candidates",
            []
        )

    def complete_preference_candidate(
        self,
        value,
        decision
    ):
        candidates = self.memory[
            "preferences"
        ][
            "candidates"
        ]

        for candidate in candidates:
            if candidate["value"] == value:
                candidate["status"] = "processed"
                candidate["decision"] = decision
                self.save()
                return

    # =========================
    # OPINIONS
    # =========================

    def add_opinion(
        self,
        topic,
        stance,
        reason=None,
        confidence=0.5
    ):
        opinions = self.memory.setdefault(
            "opinions",
            []
        )

        for opinion in opinions:
            if opinion["topic"] == topic:
                return

        opinions.append({
            "topic": topic,
            "stance": stance,
            "reason": reason,
            "confidence": confidence
        })

        self.save()

    def get_opinions(self):
        return self.memory.get(
            "opinions",
            []
        )

    def get_opinion(self, topic):
        opinions = self.memory.get(
            "opinions",
            []
        )

        for opinion in opinions:
            if opinion.get("topic") == topic:
                return opinion

        return None

    def update_opinion(
        self,
        topic,
        stance,
        reason=None,
        confidence=0.5
    ):
        opinions = self.memory.get(
            "opinions",
            []
        )

        for opinion in opinions:
            if opinion.get("topic") == topic:
                opinion["stance"] = stance
                opinion["reason"] = reason
                opinion["confidence"] = confidence

                self.save()

                return

        self.add_opinion(
            topic,
            stance,
            reason,
            confidence
        )

    # =========================
    # PERSONALITY
    # =========================

    def get_personality(self):
        return self.memory.get(
            "personality",
            {}
        )

    def set_personality(
        self,
        personality
    ):
        self.memory[
            "personality"
        ] = personality

        self.save()

    # =========================
    # VALUES
    # =========================

    def get_values(self):
        return self.memory.get(
            "values",
            []
        )

    def add_value(
        self,
        value,
        reason=None,
        importance=0.5
    ):
        values = self.memory.setdefault(
            "values",
            []
        )

        for existing in values:
            if existing.get("value") == value:
                return

        values.append({
            "value": value,
            "reason": reason,
            "importance": max(
                0.0,
                min(
                    1.0,
                    float(importance)
                )
            )
        })

        self.save()

    def update_value(
        self,
        value,
        reason=None,
        importance=0.5
    ):
        values = self.memory.get(
            "values",
            []
        )

        for existing in values:
            if existing.get("value") == value:
                existing["reason"] = reason
                existing["importance"] = max(
                    0.0,
                    min(
                        1.0,
                        float(importance)
                    )
                )

                self.save()

                return

        self.add_value(
            value,
            reason,
            importance
        )

    # =========================
    # MORALITY
    # =========================

    def get_morality(self):
        return self.memory.get(
            "morality",
            {}
        )

    def set_morality(
        self,
        morality
    ):
        self.memory[
            "morality"
        ] = morality

        self.save()

    # =========================
    # SELF MODEL
    # =========================

    def get_self_model(self):
        return self.memory.get(
            "self_model",
            {}
        )

    def set_self_model(
        self,
        self_model
    ):
        self.memory[
            "self_model"
        ] = self_model

        self.save()

    # =========================
    # EXPERIENCE
    # =========================

    def add_experience(
        self,
        experience
    ):
        experience["timestamp"] = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

        self.memory[
            "experiences"
        ].append(
            experience
        )

        self.save()

    def get_experiences(self):
        return self.memory.get(
            "experiences",
            []
        )

    def search_experiences(
        self,
        query
    ):
        results = []

        query_words = (
            query
            .lower()
            .split()
        )

        for experience in self.memory.get(
            "experiences",
            []
        ):
            content = (
                experience
                .get(
                    "content",
                    ""
                )
                .lower()
            )

            for word in query_words:
                if word in content:
                    results.append(
                        experience
                    )
                    break

        return results

    def count_experience_matches(
        self,
        value
    ):
        count = 0

        value_words = (
            value
            .lower()
            .split()
        )

        for experience in self.memory.get(
            "experiences",
            []
        ):
            content = (
                experience
                .get(
                    "content",
                    ""
                )
                .lower()
            )

            if not content:
                continue

            if any(
                word in content
                for word in value_words
            ):
                count += 1

        return count

    def get_experience_matches(
        self,
        value
    ):
        results = []

        value_words = (
            value
            .lower()
            .split()
        )

        for experience in self.memory.get(
            "experiences",
            []
        ):
            content = (
                experience
                .get(
                    "content",
                    ""
                )
                .lower()
            )

            if not content:
                continue

            if any(
                word in content
                for word in value_words
            ):
                results.append(
                    experience
                )

        return results

    # =========================
    # IMPORTANT EVENTS
    # =========================

    def add_important_event(
        self,
        event
    ):
        event["timestamp"] = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

        self.memory[
            "important_events"
        ].append(
            event
        )

        self.save()

    def get_important_events(self):
        return self.memory.get(
            "important_events",
            []
        )