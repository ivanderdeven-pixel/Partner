
import time

import numpy as np
import sounddevice as sd
import scipy.signal
import noisereduce as nr
import whisper


class Hearing:
    def __init__(self, model_size="base"):
        self.model = whisper.load_model(model_size)

    @staticmethod
    def _measure(audio):
        if audio.size == 0:
            return {"peak": 0.0, "rms": 0.0}

        return {
            "peak": float(np.max(np.abs(audio))),
            "rms": float(np.sqrt(np.mean(audio ** 2)))
        }

    @staticmethod
    def _detect_speech(audio, sample_rate=16000):
        """Energy-based VAD: memperkirakan rentang ucapan dari energi audio."""
        frame_size = int(sample_rate * 0.03)  # frame 30 ms

        if len(audio) < frame_size:
            return audio, False

        frame_count = len(audio) // frame_size
        frames = audio[:frame_count * frame_size].reshape(
            frame_count, frame_size
        )

        frame_rms = np.sqrt(np.mean(frames ** 2, axis=1))

        # Ambang adaptif dengan batas minimum dan maksimum.
        noise_estimate = float(np.percentile(frame_rms, 20))
        threshold = max(0.0015, min(0.015, noise_estimate * 1.5))

        active = frame_rms > threshold

        if not np.any(active):
            return audio, False

        # Pertahankan jeda pendek agar awal/akhir kata tidak terpotong.
        active_indices = np.flatnonzero(active)
        padding = int(0.20 / 0.03)

        first = max(0, active_indices[0] - padding)
        last = min(frame_count - 1, active_indices[-1] + padding)

        start = first * frame_size
        end = min(len(audio), (last + 1) * frame_size)

        return audio[start:end], True

    @staticmethod
    def _normalize_audio(audio, target_rms=0.04, max_gain=8.0):
        """Normalisasi terbatas; tidak menaikkan volume tanpa batas."""
        stats = Hearing._measure(audio)
        current_rms = stats["rms"]

        if current_rms < 1e-7:
            return audio

        gain = min(target_rms / current_rms, max_gain)
        normalized = audio * gain

        # Hindari clipping.
        peak = float(np.max(np.abs(normalized)))

        if peak > 0.95:
            normalized = normalized * (0.95 / peak)

        return normalized.astype(np.float32)

    def listen_and_transcribe(self, duration=5, input_device=1):
        try:
            target_rate = 16000
            device_info = sd.query_devices(input_device, "input")
            source_rate = int(device_info["default_samplerate"])

            print(f"Mendengarkan selama {duration} detik...")

            capture_start = time.perf_counter()

            audio = sd.rec(
                int(duration * source_rate),
                samplerate=source_rate,
                channels=1,
                dtype="float32",
                device=input_device
            )
            sd.wait()

            capture_seconds = time.perf_counter() - capture_start
            audio = np.asarray(audio, dtype=np.float32).flatten()

            if audio.size == 0:
                raise ValueError("Audio kosong.")

            before = self._measure(audio)

            if before["peak"] < 0.005:
                raise ValueError(
                    "Audio terlalu pelan atau mikrofon tidak menangkap suara."
                )

            # 1. Resampling ke 16 kHz.
            if source_rate != target_rate:
                divisor = np.gcd(source_rate, target_rate)

                audio = scipy.signal.resample_poly(
                    audio,
                    target_rate // divisor,
                    source_rate // divisor
                ).astype(np.float32)

            # 2. High-pass filter ringan untuk mengurangi dengung frekuensi rendah.
            sos = scipy.signal.butter(
                3,
                80,
                btype="highpass",
                fs=target_rate,
                output="sos"
            )
            audio = scipy.signal.sosfiltfilt(sos, audio).astype(np.float32)

            # 3. Noise suppression.
            suppression_start = time.perf_counter()

            audio = nr.reduce_noise(
                y=audio,
                sr=target_rate,
                stationary=False,
                prop_decrease=0.65
            ).astype(np.float32)

            suppression_seconds = time.perf_counter() - suppression_start
            after_suppression = self._measure(audio)

            # 4. Deteksi rentang ucapan.
            speech_audio, has_speech = self._detect_speech(
                audio,
                target_rate
            )

            if not has_speech:
                raise ValueError(
                    "Ucapan tidak terdeteksi. Coba bicara lebih jelas "
                    "atau periksa noise suppression."
                )

            # 5. Normalisasi level setelah noise suppression.
            audio = self._normalize_audio(speech_audio)

            after = self._measure(audio)

            # 6. Transkripsi Whisper.
            transcription_start = time.perf_counter()

            result = self.model.transcribe(
                audio,
                language="id",
                fp16=False,
                beam_size=5,
                condition_on_previous_text=False
            )

            transcription_seconds = (
                time.perf_counter() - transcription_start
            )

            text = result["text"].strip()

            print(
                f"[Audio] Sample rate: {source_rate} Hz "
                f"→ {target_rate} Hz"
            )
            print(f"[Audio] Durasi rekam: {capture_seconds:.2f} detik")
            print(
                f"[Level sebelum] Peak: {before['peak']:.4f} | "
                f"RMS: {before['rms']:.4f}"
            )
            print(
                f"[Setelah noise suppression] "
                f"Peak: {after_suppression['peak']:.4f} | "
                f"RMS: {after_suppression['rms']:.4f}"
            )
            print(
                f"[Level untuk Whisper] Peak: {after['peak']:.4f} | "
                f"RMS: {after['rms']:.4f}"
            )
            print(
                f"[DSP] Waktu noise suppression: "
                f"{suppression_seconds:.2f} detik"
            )
            print(
                f"[Whisper] Waktu transkripsi: "
                f"{transcription_seconds:.2f} detik"
            )
            print(f"[Transkripsi] {text or '(kosong)'}")

            return {
                "success": bool(text),
                "text": text,
                "audio_seconds": round(capture_seconds, 2),
                "suppression_seconds": round(suppression_seconds, 2),
                "transcription_seconds": round(transcription_seconds, 2),
                "sample_rate": source_rate,
                "peak": round(after["peak"], 4),
                "rms": round(after["rms"], 4),
                "error": None if text else "Ucapan tidak berhasil dikenali."
            }

        except Exception as e:
            return {
                "success": False,
                "text": "",
                "error": str(e)
            }
