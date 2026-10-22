import json
import os


HISTORY_FILE = "data/conversation_history.json"


class ConversationHistory:

    def __init__(self):
        self.history = self.load()

    def load(self):
        if not os.path.exists(HISTORY_FILE):
            return []

        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    def save(self):
        os.makedirs("data", exist_ok=True)

        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(
                self.history,
                file,
                indent=4,
                ensure_ascii=False
            )

    def add(self, user_message, ai_message):
        self.history.append({
            "user": user_message,
            "ai": ai_message
        })
        self.history = self.history[-300:]
        self.save()

    def get_recent(self, amount=20):
        return self.history[-amount:]