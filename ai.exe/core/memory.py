import json
import os


MEMORY_FILE = "data/memory.json"


class Memory:

    def __init__(self):
        self.memory = self.load()
        if "preferences" not in self.memory:
            self.memory["preferences"] = {}
            self.save()

    def load(self):
        if not os.path.exists(MEMORY_FILE):
            return {}

        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    def save(self):
        os.makedirs("data", exist_ok=True)

        with open(MEMORY_FILE, "w", encoding="utf-8") as file:
            json.dump(
                self.memory,
                file,
                indent=4,
                ensure_ascii=False
            )

    def get(self, key, default=None):
        return self.memory.get(key, default)

    def set(self, key, value):
        self.memory[key] = value
        self.save()

    def remember(self, key, value):
        self.memory[key] = value
        self.save()

    def remember_preference(self, preference_type, value):
        if "preferences" not in self.memory:
            self.memory["preferences"] = {}

        if preference_type not in self.memory["preferences"]:
            self.memory["preferences"][preference_type] = []

        if value not in self.memory["preferences"][preference_type]:
            self.memory["preferences"][preference_type].append(value)

        self.save()