
import numpy as np


class VoiceActivityDetector:
    """
    Energy-based VAD.
    Mendeteksi aktivitas akustik, bukan memastikan bahwa suara
    tersebut adalah ucapan manusia.
    """

    def __init__(
        self,
        sample_rate=44100,
        frame_ms=30,
        threshold_floor=0.0003,
        threshold_multiplier=3.0,
        noise_alpha=0.05,
        min_speech_ms=90,
        min_silence_ms=450,
    ):
        self.sample_rate = sample_rate
        self.frame_size = max(
            1, int(sample_rate * frame_ms / 1000)
        )

        self.threshold_floor = threshold_floor
        self.threshold_multiplier = threshold_multiplier
        self.noise_alpha = noise_alpha

        self.min_speech_frames = max(
            1, round(min_speech_ms / frame_ms)
        )
        self.min_silence_frames = max(
            1, round(min_silence_ms / frame_ms)
        )

        self.noise_rms = threshold_floor
        self._speech_frames = 0
        self._silence_frames = 0
        self._active = False

    @property
    def is_active(self):
        return self._active

    def reset(self):
        self.noise_rms = self.threshold_floor
        self._speech_frames = 0
        self._silence_frames = 0
        self._active = False

    def process(self, audio_block):
        """
        Menerima satu blok audio float32.
        Mengembalikan statistik dan status aktivitas suara.
        """
        audio = np.asarray(audio_block, dtype=np.float32).reshape(-1)

        if audio.size == 0:
            return {
                "rms": 0.0,
                "threshold": self.threshold_floor,
                "active": self._active,
                "event": None,
            }

        rms = float(np.sqrt(np.mean(audio ** 2)))
        threshold = max(
            self.threshold_floor,
            self.noise_rms * self.threshold_multiplier,
        )

        detected = rms > threshold
        event = None

        if not self._active:
            if detected:
                self._speech_frames += max(
                    1, round(
                        audio.size / self.frame_size
                    )
                )

                if self._speech_frames >= self.min_speech_frames:
                    self._active = True
                    self._silence_frames = 0
                    event = "speech_start"
            else:
                self._speech_frames = 0

                # Perbarui perkiraan noise hanya ketika tidak aktif.
                self.noise_rms = (
                    (1 - self.noise_alpha) * self.noise_rms
                    + self.noise_alpha * rms
                )

        else:
            if detected:
                self._silence_frames = 0
            else:
                self._silence_frames += max(
                    1, round(
                        audio.size / self.frame_size
                    )
                )

                if self._silence_frames >= self.min_silence_frames:
                    self._active = False
                    self._speech_frames = 0
                    self._silence_frames = 0
                    event = "speech_end"

        return {
            "rms": rms,
            "threshold": threshold,
            "active": self._active,
            "event": event,
        }
