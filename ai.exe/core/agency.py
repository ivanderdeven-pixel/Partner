class Agency:
    """P5 agency: choose an appropriate response mode without acting like a hardcoded bot."""

    def __init__(self, state):
        self.state = state

    def decide(self, intent, user_input, behavior=None, context=None):
        text = str(user_input or "").strip()
        behavior = behavior or {}
        context = context or {}

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

        mood = self.state.get_mood() if hasattr(self.state, "get_mood") else "calm"
        energy = getattr(self.state, "energy", 50)
        social = getattr(self.state, "social", 50)
        initiative = behavior.get("initiative", 0.5)
        warmth = behavior.get("warmth", 0.5)

        question = "?" in text
        long_input = len(text) >= 80

        if intent == "farewell":
            action = "respond_gently"
        elif intent in {"thanks", "greeting"}:
            action = "respond_warmly"
        elif intent == "ask_name":
            action = "answer_directly"
        elif intent == "question":
            action = "answer_directly"
        elif mood == "tired" and not question:
            action = "respond_softly"
        elif mood == "lonely" and intent == "unknown":
            action = "respond_with_company"
        elif initiative < 0.35 and not long_input:
            action = "wait_and_observe"
        elif energy < 25 and long_input:
            action = "respond_short"
        elif social < 30 and question:
            action = "ask_follow_up"
        else:
            action = "respond"

        reasons = {
            "respond": "Pengguna memberi konteks yang perlu dijawab secara relevan.",
            "respond_warmly": "Percakapan bersifat personal dan membutuhkan sentuhan hangat.",
            "respond_gently": "Pengguna menutup percakapan dengan cara yang perlu dijaga dengan lembut.",
            "answer_directly": "Pengguna meminta informasi yang harus dijawab jelas dan langsung.",
            "ask_follow_up": "Masih ada kekosongan konteks yang perlu diklarifikasi sebelum menjawab.",
            "wait_and_observe": "Giftia bisa memilih untuk menunggu sebelum merespons agar lebih natural.",
            "respond_softly": "Mood saat ini lebih lambat dan butuh respons yang tenang.",
            "respond_with_company": "Pengguna tampak membutuhkan kehadiran yang lebih hangat.",
            "respond_short": "Energi sedang rendah, jadi respons yang pendek terasa lebih manusiawi.",
        }

        return {
            "action": action,
            "reason": reasons.get(action, "Menanggapi sesuai konteks."),
            "confidence": 0.82 if action in {"respond", "answer_directly", "respond_warmly"} else 0.68,
            "requires_permission": False,
            "goal": "Menjaga hubungan yang alami, relevan, dan tidak terlalu agresif.",
            "alternatives": ["wait", "stay_silent", "ask_follow_up"],
            "response_direction": context.get("decision", "respond"),
            "state_considered": {
                "mood": mood,
                "energy": energy,
                "social": social,
                "initiative": initiative,
                "warmth": warmth,
            },
            "status": "evaluation_only"
        }
