import platform
import time
import threading
import os
import sounddevice as sd
from datetime import datetime


class Perception:

    def __init__(self, state):
        self.state = state
        self.previous_snapshot = None
        self.events = []

        self.running = True

        self.thread = threading.Thread(
            target=self._observer_loop,
            daemon=True
        )

        self.thread.start()

    # =========================
    # P4.1 TIME AWARENESS
    # =========================

    def perceive_time(self):
        now = datetime.now()

        hour = now.hour

        if 5 <= hour < 11:
            period = "morning"

        elif 11 <= hour < 15:
            period = "afternoon"

        elif 15 <= hour < 18:
            period = "evening"

        else:
            period = "night"

        return {
            "timestamp": now.isoformat(),
            "date": now.date().isoformat(),
            "time": now.strftime("%H:%M:%S"),
            "day": now.strftime("%A"),
            "hour": hour,
            "period": period
        }

    # =========================
    # P4.2 ACTIVITY PERCEPTION
    # =========================

    def perceive_activity(self):
        return {
            "activity": self.state.activity,
            "activity_timer": round(
                self.state.get_activity_timer(),
                2
            )
        }

    # =========================
    # P4.3 ENVIRONMENT AWARENESS
    # =========================

    def perceive_environment(self):
        return {
            "platform": platform.system(),
            "platform_version": platform.release(),
            "python_version": platform.python_version()
        }

    # =========================
    # P4.4 EVENT DETECTION
    # =========================

    def detect_events(self, snapshot):
        events = []

        previous = self.previous_snapshot

        if previous is not None:

            previous_activity = (
                previous["activity"]["activity"]
            )

            current_activity = (
                snapshot["activity"]["activity"]
            )

            if (
                previous_activity
                != current_activity
            ):
                events.append({
                    "type": "activity_changed",
                    "from": previous_activity,
                    "to": current_activity,
                    "timestamp": snapshot[
                        "time"
                    ]["timestamp"]
                })

            previous_period = (
                previous["time"]["period"]
            )

            current_period = (
                snapshot["time"]["period"]
            )

            if (
                previous_period
                != current_period
            ):
                events.append({
                    "type": "period_changed",
                    "from": previous_period,
                    "to": current_period,
                    "timestamp": snapshot[
                        "time"
                    ]["timestamp"]
                })

        self.previous_snapshot = snapshot

        return events

    def _observer_loop(self):
        while self.running:
            snapshot = {
                "time": self.perceive_time(),
                "activity": self.perceive_activity(),
                "environment": self.perceive_environment()
            }

            detected_events = self.detect_events(snapshot)

            if detected_events:
                self.events.extend(detected_events)

            time.sleep(1)

    def get_events(self):
        events = self.events.copy()
        self.events.clear()
        return events

    
    def perceive_hearing(self, audio_input=None):
        try:
            devices = sd.query_devices()

            input_devices = [
            device
            for device in devices
            if device["max_input_channels"] > 0
        ]

            return {
            "available": len(input_devices) > 0,
            "device_count": len(input_devices),
            "devices": [
                {
                    "name": device["name"],
                    "channels": device["max_input_channels"]
                }
                for device in input_devices
            ],
            "input": audio_input
        }

        except Exception:
            return {
            "available": False,
            "device_count": 0,
            "devices": [],
            "input": audio_input
        }

    def listen(self, duration=1):
        try:
            sample_rate = 16000

            audio = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype="float32"
            )

            sd.wait()

            return {
                "success": True,
                "sample_rate": sample_rate,
                "duration": duration,
                "samples": len(audio)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def perceive_vision(self, visual_input=None):
        if visual_input is None:
            return {
                "available": False,
                "input": None
            }

        return {
            "available": True,
            "input": visual_input
        }


    def build_context(self, snapshot):
        time_data = snapshot["time"]
        activity_data = snapshot["activity"]
        computer_data = snapshot["computer"]

        return {
            "time": {
                "period": time_data["period"],
                "day": time_data["day"]
            },

            "activity": activity_data["activity"],

            "environment": snapshot["environment"],

            "computer": {
                "hostname": computer_data["hostname"],
                "processor": computer_data["processor"],
                "architecture": computer_data["architecture"],
                "cpu_count": computer_data["cpu_count"]
            },

            "hearing_available": (
                snapshot["hearing"]["available"]
            ),

            "vision_available": (
                snapshot["vision"]["available"]
            ),

            "events": snapshot["events"]
        }

    # =========================
    # FULL PERCEPTION
    # =========================

    def perceive(self):
        snapshot = {
            "time": self.perceive_time(),
            "activity": self.perceive_activity(),
            "environment": self.perceive_environment(),
            "computer": self.perceive_computer(),
            "hearing": self.perceive_hearing(),
            "vision": self.perceive_vision()
        }

        snapshot["events"] = self.get_events()

        snapshot["context"] = self.build_context(
            snapshot
        )

        return snapshot


    def perceive_computer(self):
        return {
            "hostname": platform.node(),
            "processor": platform.processor(),
            "architecture": platform.machine(),
            "cpu_count": os.cpu_count()
        }