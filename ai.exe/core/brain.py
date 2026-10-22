
import json
from datetime import datetime, timezone

from ollama import chat

from core.perception import Perception
from core.hearing import Hearing


class Brain:

    def __init__(
        self,
        state,
        history,
        memory,
        ai_memory
    ):
        self.state = state
        self.history = history
        self.memory = memory
        self.ai_memory = ai_memory

        self.perception = Perception(state)
        self.hearing = Hearing()

    def listen(
        self,
        duration=5,
        input_device=1
    ):
        result = self.hearing.listen_and_transcribe(
            duration=duration,
            input_device=input_device
        )

        if not result.get("success"):
            return {
                "success": False,
                "text": "",
                "error": result.get(
                    "error",
                    "Gagal memproses audio."
                )
            }

        text = str(
            result.get("text", "")
        ).strip()

        if not text:
            return {
                "success": False,
                "text": "",
                "error": "Tidak ada ucapan yang berhasil dikenali."
            }

        return {
            "success": True,
            "text": text
        }

    def think_from_voice(
        self,
        duration=5,
        input_device=1
    ):
        voice_result = self.listen(
            duration=duration,
            input_device=input_device
        )

        if not voice_result["success"]:
            return {
                "success": False,
                "heard": "",
                "thought": None,
                "error": voice_result.get("error")
            }

        user_input = voice_result["text"]
        thought = self.think(user_input)

        return {
            "success": True,
            "heard": user_input,
            "thought": thought
        }

    def analyze_identity(self):
        identity = self.ai_memory.get_identity()

        return {
            "instance_id": identity.get("instance_id"),
            "name": identity.get("name"),
            "status": identity.get("status"),
            "origin": identity.get("origin"),
            "operational_age": identity.get(
                "operational_age"
            )
        }

    def detect_intent(self, user_input):
        text = user_input.lower().strip()

        if (
            "halo" in text
            or "hai" in text
            or "hi" in text
        ):
            return "greeting"

        if (
            "namamu siapa" in text
            or "siapa namamu" in text
        ):
            return "ask_name"

        if (
            "apa kabar" in text
            or "kabarmu" in text
            or "menurutmu sendiri" in text
            or "kamu bagaimana" in text
        ):
            return "ask_condition"

        if (
            "terima kasih" in text
            or "makasih" in text
        ):
            return "thanks"

        if (
            "dadah" in text
            or "sampai jumpa" in text
        ):
            return "farewell"

        if "?" in text:
            return "question"

        return "unknown"

    def detect_memory(self, user_input):
        text = user_input.strip()

        if text.lower().startswith("namaku "):
            name = text[7:].strip()

            if name:
                return {
                    "type": "user_name",
                    "value": name
                }

        return None

    def analyze_state(self):
        return {
            "mood": self.state.get_mood(),
            "activity": self.state.activity,
            "happiness": self.state.happiness,
            "energy": self.state.energy,
            "curiosity": self.state.curiosity,
            "social": self.state.social
        }

    def analyze_memory(self):
        return {
            "user_name": self.memory.get(
                "user_name"
            ),
            "preferences": self.memory.get(
                "preferences",
                {}
            )
        }

    def analyze_ai_memory(self, user_input):
        return {
            "experiences": self.ai_memory.get_experiences(),

            "relevant_experiences": (
                self.ai_memory.search_experiences(
                    user_input
                )
            ),

            "preferences": (
                self.ai_memory.get_preferences()
            ),

            "opinions": (
                self.ai_memory.get_opinions()
            ),

            "personality": (
                self.ai_memory.get_personality()
            ),

            "values": (
                self.ai_memory.get_values()
            ),

            "morality": (
                self.ai_memory.get_morality()
            ),

            "self_model": (
                self.ai_memory.get_self_model()
            )
        }

    def get_context(self):
        return self.history.get_recent(5)

    def analyze_context(self, user_input):
        context = self.history.get_recent(5)
        text = user_input.lower()

        if not context:
            return {
                "has_context": False,
                "reference": None,
                "history": []
            }

        reference = None

        if (
            "yang tadi" in text
            or "tadi" in text
            or "itu" in text
            or "sebelumnya" in text
        ):
            reference = "previous"

        return {
            "has_context": True,
            "reference": reference,
            "history": context
        }

    def make_decision(
        self,
        intent,
        state
    ):
        mood = state["mood"]

        if intent == "ask_name":
            return "answer_name"

        if intent == "greeting":
            if mood == "tired":
                return "greet_gently"

            if mood == "happy":
                return "greet_happily"

            return "greet_normal"

        if intent == "ask_condition":
            return "answer_condition"

        if intent == "thanks":
            return "respond_thanks"

        if intent == "farewell":
            return "say_goodbye"

        if intent == "question":
            return "answer_question"

        if intent == "statement":
            return "acknowledge"

        return "acknowledge"

    def evaluate_agency_decision(
        self,
        user_input,
        intent,
        state,
        behavior,
        response_decision
    ):
        """
        Evaluate a possible conversational action for P5.1.

        This first implementation is evaluation-only: it does not execute
        external actions or independently initiate communication.
        """
        text = str(user_input or "").strip()

        if not text:
            return {
                "action": "wait",
                "reason": "Tidak ada input yang perlu ditanggapi.",
                "confidence": 1.0,
                "requires_permission": False,
                "goal": "Menghindari respons tanpa konteks.",
                "alternatives": ["respond", "stay_silent"],
                "status": "evaluation_only"
            }

        reasons = {
            "greeting": "Pengguna memulai interaksi.",
            "ask_name": "Pengguna meminta informasi identitas.",
            "ask_condition": "Pengguna menanyakan keadaan Giftia.",
            "thanks": "Pengguna menyampaikan terima kasih.",
            "farewell": "Pengguna mengakhiri interaksi.",
            "question": "Pengguna mengajukan pertanyaan.",
            "statement": "Pengguna menyampaikan pernyataan.",
            "unknown": "Maksud pengguna belum terklasifikasi."
        }

        known_intents = {
            "greeting",
            "ask_name",
            "ask_condition",
            "thanks",
            "farewell",
            "question",
            "statement"
        }

        # Heuristik awal, bukan probabilitas yang sudah dikalibrasi.
        confidence = 0.85 if intent in known_intents else 0.55

        return {
            "action": "respond",
            "reason": reasons.get(
                intent,
                "Memberikan tanggapan sesuai konteks."
            ),
            "confidence": confidence,
            "requires_permission": False,
            "goal": "Menanggapi pengguna secara relevan.",
            "alternatives": ["wait", "stay_silent"],
            "response_direction": response_decision,
            "state_considered": {
                "mood": state.get("mood"),
                "energy": state.get("energy"),
                "social": state.get("social")
            },
            "behavior_considered": {
                "initiative": behavior.get("initiative"),
                "patience": behavior.get("patience"),
                "caution": behavior.get("caution")
            },
            "status": "evaluation_only"
        }

    def think(self, user_input):

        perception = self.perception.perceive()

        intent = self.detect_intent(
            user_input
        )

        state = self.analyze_state()
        memory = self.analyze_memory()
        identity = self.analyze_identity()

        ai_memory = self.analyze_ai_memory(
            user_input
        )

        new_memory = self.detect_memory(
            user_input
        )

        ai_experience = self.detect_ai_experience(
            user_input
        )

        preference_candidate = (
            self.evaluate_preference_candidate(
                ai_experience
            )
        )

        preference_evaluation = (
            self.evaluate_preference(
                preference_candidate
            )
        )

        preference_result = (
            self.commit_preference(
                preference_evaluation
            )
        )

        opinion_evaluation = (
            self.evaluate_opinion(
                ai_experience
            )
        )

        opinion_result = (
            self.commit_opinion(
                opinion_evaluation
            )
        )

        personality_evaluation = (
            self.evaluate_personality(
                ai_experience
            )
        )

        personality_result = (
            self.commit_personality(
                personality_evaluation
            )
        )

        value_evaluation = (
            self.evaluate_value(
                ai_experience
            )
        )

        value_result = (
            self.commit_value(
                value_evaluation
            )
        )

        morality_evaluation = (
            self.evaluate_morality(
                ai_experience
            )
        )

        morality_result = (
            self.commit_morality(
                morality_evaluation
            )
        )

        self_evaluation = (
            self.evaluate_self_model(
                ai_experience
            )
        )

        self_result = (
            self.commit_self_model(
                self_evaluation
            )
        )

        personality_stability = (
            self.stabilize_personality()
        )

        behavior = self.calculate_behavior(
            state
        )

        important_event = (
            self.detect_important_event(
                user_input
            )
        )

        decision = self.make_decision(
            intent,
            state
        )

        agency_decision = self.evaluate_agency_decision(
            user_input=user_input,
            intent=intent,
            state=state,
            behavior=behavior,
            response_decision=decision
        )

        context = self.analyze_context(
            user_input
        )

        updated_ai_memory = (
            self.analyze_ai_memory(
                user_input
            )
        )

        return {
            "user_input": user_input,
            "intent": intent,
            "state": state,
            "perception": perception,
            "memory": memory,
            "identity": identity,
            "ai_memory": updated_ai_memory,
            "new_memory": new_memory,
            "ai_experience": ai_experience,
            "preference_candidate": preference_candidate,
            "preference_evaluation": preference_evaluation,
            "preference_result": preference_result,
            "opinion_evaluation": opinion_evaluation,
            "opinion_result": opinion_result,
            "personality_evaluation": personality_evaluation,
            "personality_result": personality_result,
            "value_evaluation": value_evaluation,
            "value_result": value_result,
            "morality_evaluation": morality_evaluation,
            "morality_result": morality_result,
            "self_evaluation": self_evaluation,
            "self_result": self_result,
            "personality_stability": personality_stability,
            "behavior": behavior,
            "important_event": important_event,
            "decision": decision,
            "agency_decision": agency_decision,
            "context": context
        }

    def build_llm_context(
        self,
        thought,
        user_input
    ):
        ai_memory = thought["ai_memory"]

        return {
            "user_input": user_input,
            "intent": thought["intent"],
            "decision": thought["decision"],
            "agency_decision": thought.get("agency_decision", {}),
            "state": thought["state"],
            "perception": thought["perception"],
            "memory": thought["memory"],
            "identity": thought["identity"],
            "context": thought["context"],
            "current_experience": thought["ai_experience"],
            "behavior": thought["behavior"],

            "ai_memory": {
                "relevant_experiences": [],

                "preferences": (
                    ai_memory["preferences"]
                ),

                "opinions": (
                    ai_memory["opinions"]
                ),

                "personality": (
                    ai_memory["personality"]
                ),

                "values": (
                    ai_memory["values"]
                ),

                "morality": (
                    ai_memory["morality"]
                ),

                "self_model": (
                    ai_memory["self_model"]
                )
            }
        }

    def detect_ai_experience(
        self,
        user_input
    ):
        text = user_input.strip()

        if not text:
            return None

        markers = [
            "aku membuat",
            "aku mencoba",
            "aku melakukan",
            "aku belajar",
            "aku mengalami",
            "aku berhasil",
            "aku gagal",
            "aku merasa"
        ]

        text_lower = text.lower()

        for marker in markers:
            if marker in text_lower:
                return {
                    "type": "experience",
                    "content": text
                }

        return None

    def evaluate_preference_candidate(
        self,
        experience
    ):
        if not experience:
            return None

        if experience.get(
            "type"
        ) != "experience":
            return None

        content = experience.get(
            "content",
            ""
        ).strip()

        if not content:
            return None

        return {
            "value": content,
            "source": "experience"
        }

    def evaluate_preference(
        self,
        candidate
    ):
        if not candidate:
            return None

        value = candidate["value"]

        matches = (
            self.ai_memory
            .get_experience_matches(
                value
            )
        )

        response = chat(
            model="qwen3:latest",
            messages=[
                {
                    "role": "system",
                    "content": """
Tentukan apakah pengalaman baru memberi
alasan yang cukup bagi AI untuk membentuk
preferensi pribadi.

Pilih satu:

LIKE
DISLIKE
UNKNOWN

Jangan membuat preferensi hanya karena
sesuatu disebutkan.

LIKE berarti ada bukti bahwa AI cenderung
menyukai pengalaman tersebut.

DISLIKE berarti ada bukti bahwa AI cenderung
tidak menyukainya.

UNKNOWN berarti bukti belum cukup.

Jawab hanya satu kata.
"""
                },
                {
                    "role": "user",
                    "content": f"""
Pengalaman baru:
{value}

Pengalaman terkait:
{matches}
"""
                }
            ],
            think=False
        )

        result = (
            response.message.content
            .strip()
            .upper()
        )

        if result not in [
            "LIKE",
            "DISLIKE",
            "UNKNOWN"
        ]:
            result = "UNKNOWN"

        return {
            "candidate": value,
            "decision": result,
            "reason": None
        }

    def commit_preference(
        self,
        evaluation
    ):
        if not evaluation:
            return None

        decision = evaluation["decision"]
        value = evaluation["candidate"]
        reason = evaluation.get("reason")

        if decision == "LIKE":
            self.ai_memory.add_preference(
                "likes",
                value,
                reason
            )

        elif decision == "DISLIKE":
            self.ai_memory.add_preference(
                "dislikes",
                value,
                reason
            )

        else:
            return None

        self.ai_memory.complete_preference_candidate(
            value,
            decision
        )

        return {
            "type": decision,
            "value": value,
            "reason": reason
        }

    def evaluate_opinion(
        self,
        experience
    ):
        if not experience:
            return None

        content = experience.get(
            "content",
            ""
        ).strip()

        if not content:
            return None

        existing = self.ai_memory.get_opinions()

        response = chat(
            model="qwen3:latest",
            messages=[
                {
                    "role": "system",
                    "content": """
Tentukan apakah pengalaman baru memberi
dasar bagi AI untuk membentuk atau
memperbarui opini pribadi.

Opini bukan fakta.

Jika belum cukup, gunakan UNKNOWN.

Tentukan:

topic
stance
reason
confidence

stance hanya:

POSITIVE
NEGATIVE
NEUTRAL
UNKNOWN

confidence harus 0.0 sampai 1.0.

Jika tidak cukup, topic boleh null.

Jawab HANYA JSON valid:

{
    "topic": "...",
    "stance": "...",
    "reason": "...",
    "confidence": 0.0
}
"""
                },
                {
                    "role": "user",
                    "content": f"""
Pengalaman baru:
{content}

Opini sebelumnya:
{existing}
"""
                }
            ],
            think=False
        )

        try:
            data = json.loads(
                response.message.content.strip()
            )

        except json.JSONDecodeError:
            return {
                "topic": None,
                "stance": "UNKNOWN",
                "reason": None,
                "confidence": 0.0
            }

        stance = str(
            data.get(
                "stance",
                "UNKNOWN"
            )
        ).upper()

        if stance not in [
            "POSITIVE",
            "NEGATIVE",
            "NEUTRAL",
            "UNKNOWN"
        ]:
            stance = "UNKNOWN"

        try:
            confidence = float(
                data.get(
                    "confidence",
                    0.0
                )
            )
        except (
            TypeError,
            ValueError
        ):
            confidence = 0.0

        confidence = max(
            0.0,
            min(
                1.0,
                confidence
            )
        )

        return {
            "topic": data.get("topic"),
            "stance": stance,
            "reason": data.get("reason"),
            "confidence": confidence
        }

    def commit_opinion(
        self,
        evaluation
    ):
        if not evaluation:
            return None

        topic = evaluation.get("topic")
        stance = evaluation.get("stance", "UNKNOWN")
        reason = evaluation.get("reason")
        confidence = evaluation.get("confidence", 0.0)

        if not topic or stance == "UNKNOWN":
            return None

        existing = self.ai_memory.get_opinion(topic)

        if existing:
            old_confidence = existing.get(
                "confidence",
                0.5
            )

            new_confidence = (
                old_confidence + confidence
            ) / 2

            self.ai_memory.update_opinion(
                topic,
                stance,
                reason,
                new_confidence
            )

            return {
                "type": "updated",
                "topic": topic,
                "stance": stance,
                "reason": reason,
                "confidence": new_confidence
            }

        self.ai_memory.add_opinion(
            topic,
            stance,
            reason,
            confidence
        )

        return {
            "type": "created",
            "topic": topic,
            "stance": stance,
            "reason": reason,
            "confidence": confidence
        }

    def evaluate_personality(
        self,
        experience
    ):
        if not experience:
            return None

        content = experience.get(
            "content",
            ""
        ).strip()

        if not content:
            return None

        personality = self.ai_memory.get_personality()
        preferences = self.ai_memory.get_preferences()
        opinions = self.ai_memory.get_opinions()

        response = chat(
            model="qwen3:latest",
            messages=[
                {
                    "role": "system",
                    "content": """
Evaluasi apakah pengalaman baru memberi
bukti yang cukup untuk mengubah kepribadian AI.

Kepribadian tidak berubah drastis karena
satu pengalaman.

Gunakan trait:

curiosity
patience
confidence
sociability
caution

Nilai perubahan hanya antara -0.1 dan 0.1.

Jika belum cukup, gunakan changes kosong.

Jawab HANYA JSON:

{
    "changes": {
        "trait": 0.05
    },
    "reason": "..."
}

atau:

{
    "changes": {},
    "reason": null
}
"""
                },
                {
                    "role": "user",
                    "content": f"""
Pengalaman:
{content}

Personality:
{personality}

Preferences:
{preferences}

Opinions:
{opinions}
"""
                }
            ],
            think=False
        )

        try:
            data = json.loads(
                response.message.content.strip()
            )

        except json.JSONDecodeError:
            return {
                "changes": {},
                "reason": None
            }

        changes = data.get("changes", {})

        if not isinstance(changes, dict):
            changes = {}

        valid_traits = [
            "curiosity",
            "patience",
            "confidence",
            "sociability",
            "caution"
        ]

        clean_changes = {}

        for trait, change in changes.items():
            if trait not in valid_traits:
                continue

            try:
                change = float(change)
            except (
                TypeError,
                ValueError
            ):
                continue

            change = max(
                -0.1,
                min(0.1, change)
            )

            clean_changes[trait] = change

        return {
            "changes": clean_changes,
            "reason": data.get("reason")
        }

    def commit_personality(
        self,
        evaluation
    ):
        if not evaluation:
            return None

        changes = evaluation.get("changes", {})

        if not changes:
            return None

        personality = self.ai_memory.get_personality()

        traits = personality.setdefault(
            "traits",
            {
                "curiosity": 0.5,
                "patience": 0.5,
                "confidence": 0.5,
                "sociability": 0.5,
                "caution": 0.5
            }
        )

        for trait, change in changes.items():
            current = traits.get(trait, 0.5)

            traits[trait] = max(
                0.0,
                min(1.0, current + change)
            )

        personality["last_reason"] = evaluation.get("reason")

        personality["updated_at"] = datetime.now(
            timezone.utc
        ).isoformat()

        self.ai_memory.set_personality(personality)

        return {
            "changes": changes,
            "personality": personality
        }

    def evaluate_value(
        self,
        experience
    ):
        if not experience:
            return None

        content = experience.get(
            "content",
            ""
        ).strip()

        if not content:
            return None

        values = self.ai_memory.get_values()

        response = chat(
            model="qwen3:latest",
            messages=[
                {
                    "role": "system",
                    "content": """
Evaluasi apakah pengalaman baru memberi
dasar bagi AI untuk membentuk atau
memperkuat nilai pribadi.

Nilai harus berasal dari pengalaman,
bukan daftar nilai yang dipaksakan.

Jika belum cukup, gunakan UNKNOWN.

Jika cukup, berikan:

value
reason
importance

importance 0.0 sampai 1.0.

Jawab HANYA JSON:

{
    "value": "...",
    "reason": "...",
    "importance": 0.0
}

Jika belum cukup:

{
    "value": null,
    "reason": null,
    "importance": 0.0
}
"""
                },
                {
                    "role": "user",
                    "content": f"""
Pengalaman:
{content}

Nilai yang sudah ada:
{values}
"""
                }
            ],
            think=False
        )

        try:
            data = json.loads(
                response.message.content.strip()
            )

        except json.JSONDecodeError:
            return None

        value = data.get("value")

        if not value:
            return None

        try:
            importance = float(
                data.get("importance", 0.0)
            )
        except (
            TypeError,
            ValueError
        ):
            importance = 0.0

        importance = max(
            0.0,
            min(1.0, importance)
        )

        return {
            "value": value,
            "reason": data.get("reason"),
            "importance": importance
        }

    def commit_value(
        self,
        evaluation
    ):
        if not evaluation:
            return None

        value = evaluation.get("value")

        if not value:
            return None

        reason = evaluation.get("reason")
        importance = evaluation.get("importance", 0.5)

        existing_values = self.ai_memory.get_values()

        exists = False

        for existing in existing_values:
            if existing.get("value") == value:
                exists = True
                break

        if exists:
            self.ai_memory.update_value(
                value,
                reason,
                importance
            )

            result_type = "updated"

        else:
            self.ai_memory.add_value(
                value,
                reason,
                importance
            )

            result_type = "created"

        return {
            "type": result_type,
            "value": value,
            "reason": reason,
            "importance": importance
        }

    def evaluate_morality(
        self,
        experience
    ):
        if not experience:
            return None

        content = experience.get(
            "content",
            ""
        ).strip()

        if not content:
            return None

        morality = self.ai_memory.get_morality()

        response = chat(
            model="qwen3:latest",
            messages=[
                {
                    "role": "system",
                    "content": """
Evaluasi apakah pengalaman baru memberi
dasar bagi AI untuk membentuk atau
memperkuat prinsip moral pribadi.

Jangan membuat aturan ekstrem.

Prinsip harus berasal dari pengalaman
dan pertimbangan terhadap dampaknya.

Jika belum cukup, kembalikan:

{
    "principle": null,
    "reason": null
}

Jika cukup:

{
    "principle": "...",
    "reason": "..."
}

Jawab HANYA JSON valid.
"""
                },
                {
                    "role": "user",
                    "content": f"""
Pengalaman:
{content}

Moralitas saat ini:
{morality}
"""
                }
            ],
            think=False
        )

        try:
            data = json.loads(
                response.message.content.strip()
            )

        except json.JSONDecodeError:
            return None

        principle = data.get("principle")

        if not principle:
            return None

        return {
            "principle": principle,
            "reason": data.get("reason")
        }

    def commit_morality(
        self,
        evaluation
    ):
        if not evaluation:
            return None

        principle = evaluation.get("principle")

        if not principle:
            return None

        reason = evaluation.get("reason")
        morality = self.ai_memory.get_morality()

        principles = morality.setdefault(
            "principles",
            []
        )

        for existing in principles:
            if existing.get("principle") == principle:
                return {
                    "type": "existing",
                    "principle": principle
                }

        principles.append({
            "principle": principle,
            "reason": reason,
            "created_at": datetime.now(
                timezone.utc
            ).isoformat()
        })

        self.ai_memory.set_morality(morality)

        return {
            "type": "created",
            "principle": principle,
            "reason": reason
        }

    def evaluate_self_model(
        self,
        experience
    ):
        if not experience:
            return None

        content = experience.get(
            "content",
            ""
        ).strip()

        if not content:
            return None

        self_model = self.ai_memory.get_self_model()

        response = chat(
            model="qwen3:latest",
            messages=[
                {
                    "role": "system",
                    "content": """
Evaluasi apakah pengalaman baru memberi
informasi yang cukup untuk memperbarui
pemahaman AI terhadap dirinya sendiri.

Perbarui hanya jika ada alasan.

Self-model memiliki:

description
strengths
weaknesses
interests

Jangan mengarang identitas baru.

Jawab HANYA JSON:

{
    "description": null,
    "strength": null,
    "weakness": null,
    "interest": null,
    "reason": null
}

Gunakan null jika tidak ada perubahan.
"""
                },
                {
                    "role": "user",
                    "content": f"""
Pengalaman:
{content}

Self-model saat ini:
{self_model}
"""
                }
            ],
            think=False
        )

        try:
            data = json.loads(
                response.message.content.strip()
            )

        except json.JSONDecodeError:
            return None

        return data

    def commit_self_model(
        self,
        evaluation
    ):
        if not evaluation:
            return None

        self_model = self.ai_memory.get_self_model()
        changed = False

        description = evaluation.get("description")

        if description:
            self_model["description"] = description
            changed = True

        strength = evaluation.get("strength")

        if strength:
            if strength not in self_model["strengths"]:
                self_model["strengths"].append(strength)
                changed = True

        weakness = evaluation.get("weakness")

        if weakness:
            if weakness not in self_model["weaknesses"]:
                self_model["weaknesses"].append(weakness)
                changed = True

        interest = evaluation.get("interest")

        if interest:
            if interest not in self_model["interests"]:
                self_model["interests"].append(interest)
                changed = True

        if not changed:
            return None

        self_model["development"].append({
            "reason": evaluation.get("reason"),
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat()
        })

        self.ai_memory.set_self_model(self_model)

        return {
            "updated": True,
            "self_model": self_model
        }

    def stabilize_personality(self):
        personality = self.ai_memory.get_personality()
        traits = personality.get("traits")

        if not traits:
            return None

        for trait in traits:
            value = traits[trait]

            traits[trait] = max(
                0.0,
                min(1.0, float(value))
            )

        personality["traits"] = traits

        self.ai_memory.set_personality(personality)

        return personality

    def calculate_behavior(
        self,
        state
    ):
        personality = self.ai_memory.get_personality()

        traits = personality.get("traits", {})

        curiosity = traits.get("curiosity", 0.5)
        patience = traits.get("patience", 0.5)
        sociability = traits.get("sociability", 0.5)
        caution = traits.get("caution", 0.5)

        energy = state.get("energy", 50)
        social = state.get("social", 50)

        warmth = (
            sociability + (social / 100)
        ) / 2

        initiative = (
            curiosity + (energy / 100)
        ) / 2

        return {
            "warmth": round(
                max(0.0, min(1.0, warmth)),
                2
            ),

            "initiative": round(
                max(0.0, min(1.0, initiative)),
                2
            ),

            "patience": round(
                max(0.0, min(1.0, patience)),
                2
            ),

            "caution": round(
                max(0.0, min(1.0, caution)),
                2
            ),

            "energy": round(
                max(0.0, min(1.0, energy / 100)),
                2
            )
        }

    def detect_important_event(
        self,
        user_input
    ):
        text = user_input.strip().lower()

        if text.startswith("hari ini penting"):
            return {
                "type": "important",
                "content": user_input.strip()
            }

        return None
