import time


class State:
    def __init__(self):
        self.happiness = 50
        self.energy = 100
        self.curiosity = 50
        self.social = 50
        self.activity = "idle"
        self.last_activity_change = time.time()
        self.last_interaction = time.time()

    def change_happiness(self, amount):
        self.happiness = max(0, min(100, self.happiness + amount))

    def change_energy(self, amount):
        self.energy = max(0, min(100, self.energy + amount))

    def change_curiosity(self, amount):
        self.curiosity = max(0, min(100, self.curiosity + amount))

    def change_social(self, amount):
        self.social = max(0, min(100, self.social + amount))

    def set_activity(self, activity):
        if self.activity != activity:
            self.last_activity_change = time.time()
        self.activity = activity

    def update_activity(self):
        elapsed = time.time() - self.last_activity_change

        if self.activity in {"talking", "thinking"} and elapsed >= 5:
            self.activity = "idle"
            self.last_activity_change = time.time()

    def get_activity_timer(self):
        if self.activity not in {"talking", "thinking"}:
            return 0

        elapsed = time.time() - self.last_activity_change
        remaining = 5 - elapsed
        return max(0, remaining)

    def apply_event(self, event):
        self.last_interaction = time.time()

        if event == "user_message":
            self.change_social(5)
            self.change_happiness(2)
            self.set_activity("talking")

        elif event == "compliment":
            self.change_happiness(10)
            self.change_social(5)
            self.set_activity("talking")

        elif event == "long_idle":
            self.change_social(-3)
            self.change_energy(-2)
            self.set_activity("idle")

        elif event == "interesting_topic":
            self.change_curiosity(10)
            self.set_activity("thinking")

        elif event == "silence":
            self.change_energy(-1)
            self.set_activity("idle")

    def get_mood(self):
        if self.energy < 20:
            return "tired"

        if self.happiness >= 75 and self.social >= 60:
            return "happy"

        if self.curiosity >= 75:
            return "curious"

        if self.social < 25:
            return "lonely"

        if self.happiness < 30:
            return "sad"

        return "calm"

    def get_behavior_profile(self):
        return {
            "mood": self.get_mood(),
            "activity": self.activity,
            "energy": self.energy,
            "curiosity": self.curiosity,
            "social": self.social,
            "happiness": self.happiness,
            "initiative": round(min(1.0, max(0.0, (self.curiosity + self.energy) / 200)), 2),
            "warmth": round(min(1.0, max(0.0, (self.social + self.happiness) / 200)), 2),
            "patience": round(min(1.0, max(0.0, (100 - self.energy + self.social) / 200)), 2),
        }

    def show_state(self):
        print("=== Mood State ===")
        print(f"Happiness : {self.happiness}")
        print(f"Energy    : {self.energy}")
        print(f"Curiosity : {self.curiosity}")
        print(f"Social    : {self.social}")
        print(f"Activity  : {self.activity}")
        print(f"Mood      : {self.get_mood()}")
        print(f"Activity Timer : {self.get_activity_timer():.1f}s")
