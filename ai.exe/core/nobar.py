"""Opt-in screen-based co-watching for Giftia.

Requires the optional `mss` package and an Ollama vision model.
No screenshots are written to disk. Capture is off until /nobar on.
"""
import base64
import os
import threading
import time
from datetime import datetime

from ollama import chat


class ScreenNobar:
    def __init__(self, on_reaction=None, model=None, interval=8.0):
        self.model = model or os.getenv("GIFTIA_VISION_MODEL", "qwen2.5vl:3b")
        self.interval = max(4.0, float(interval))
        self.on_reaction = on_reaction or print
        self._state_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread = None
        self._state = "off"
        self._last_observation = ""
        self._last_error = None

    @property
    def state(self):
        with self._state_lock:
            return self._state

    @property
    def last_error(self):
        with self._state_lock:
            return self._last_error

    def start(self):
        with self._state_lock:
            if self._state in ("watching", "paused"):
                return False
            self._stop_event.clear()
            self._state = "watching"
            self._last_error = None
            self._thread = threading.Thread(
                target=self._watch_loop,
                name="giftia-nobar",
                daemon=True,
            )
            self._thread.start()
        return True

    def pause(self):
        with self._state_lock:
            if self._state != "watching":
                return False
            self._state = "paused"
            return True

    def resume(self):
        with self._state_lock:
            if self._state != "paused":
                return False
            self._state = "watching"
            return True

    def stop(self, timeout=2.0):
        with self._state_lock:
            thread = self._thread
            self._state = "off"
            self._stop_event.set()
        if thread and thread.is_alive() and thread is not threading.current_thread():
            thread.join(timeout=max(0.0, timeout))
        return True

    def status(self):
        with self._state_lock:
            return {
                "state": self._state,
                "model": self.model,
                "interval_seconds": self.interval,
                "last_error": self._last_error,
                "last_observation": self._last_observation,
            }

    @staticmethod
    def _capture_png_base64():
        # Import lazily so normal chat works without screen-capture dependencies.
        import mss
        import mss.tools

        with mss.mss() as capture:
            monitor = capture.monitors[1]  # primary monitor, not virtual desktop
            shot = capture.grab(monitor)
            png = mss.tools.to_png(shot.rgb, shot.size)
        return base64.b64encode(png).decode("ascii")

    def _observe(self, image_b64, timestamp):
        previous = self._last_observation or "Belum ada pengamatan sebelumnya."
        prompt = f"""Kamu adalah teman nobar anime Giftia. Waktu cuplikan: {timestamp}.
Amati gambar layar ini. Bandingkan dengan pengamatan sebelumnya:
{previous}

Berikan satu pengamatan ringkas dalam bahasa Indonesia tentang adegan yang benar-benar tampak.
Jika ada momen yang layak ditanggapi, berikan satu reaksi spontan singkat seperti teman nobar.
Jangan mengarang dialog atau kejadian yang tidak terlihat. Jangan mengklaim memahami audio.
Jika tidak ada perubahan bermakna atau tidak ada reaksi yang perlu disampaikan, jawab tepat: SILENT
Maksimal 2 kalimat. Jangan menyebut instruksi ini."""
        result = chat(
            model=self.model,
            messages=[{
                "role": "user",
                "content": prompt,
                "images": [image_b64],
            }],
            think=False,
        )
        message = getattr(result, "message", None)
        return (getattr(message, "content", "") or "").strip()

    def _watch_loop(self):
        while not self._stop_event.is_set():
            if self.state == "paused":
                self._stop_event.wait(0.25)
                continue
            if self.state != "watching":
                break
            try:
                timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
                image_b64 = self._capture_png_base64()
                observation = self._observe(image_b64, timestamp)
                if observation and observation.upper() != "SILENT":
                    with self._state_lock:
                        self._last_observation = observation[:1200]
                        self._last_error = None
                    self.on_reaction(f"[Nobar {timestamp}] {observation[:1200]}")
                elif observation:
                    with self._state_lock:
                        self._last_error = None
            except Exception as error:
                with self._state_lock:
                    self._last_error = f"{type(error).__name__}: {error}"
                # Do not flood the terminal or retry in a tight loop.
                self._stop_event.wait(min(self.interval, 5.0))
            self._stop_event.wait(self.interval)
        with self._state_lock:
            if self._state != "paused":
                self._state = "off"
