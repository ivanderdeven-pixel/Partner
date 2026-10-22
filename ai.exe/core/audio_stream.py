
import queue
import threading
import time

import numpy as np
import sounddevice as sd


class AudioStream:
    """
    Continuous microphone capture with a bounded audio queue.

    Audio is captured continuously while the stream is running.
    Speech detection and transcription are handled by other components.
    """

    def __init__(
        self,
        input_device=1,
        sample_rate=None,
        channels=1,
        block_size=1024,
        queue_capacity=100,
    ):
        self.input_device = input_device
        self.channels = channels
        self.block_size = block_size

        device_info = sd.query_devices(input_device, "input")
        self.sample_rate = int(
            sample_rate or device_info["default_samplerate"]
        )

        self._queue = queue.Queue(maxsize=queue_capacity)
        self._stream = None
        self._running = False
        self._lock = threading.Lock()
        self._dropped_blocks = 0
        self._last_error = None

    @property
    def is_running(self):
        return self._running

    @property
    def dropped_blocks(self):
        return self._dropped_blocks

    @property
    def last_error(self):
        return self._last_error

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            self._last_error = str(status)

        if not self._running:
            return

        # Copy the audio: PortAudio owns the callback's input buffer.
        block = np.array(indata, dtype=np.float32, copy=True)

        try:
            self._queue.put_nowait(block)
        except queue.Full:
            # Keep the newest audio instead of growing memory indefinitely.
            try:
                self._queue.get_nowait()
            except queue.Empty:
                pass

            self._dropped_blocks += 1

            try:
                self._queue.put_nowait(block)
            except queue.Full:
                self._dropped_blocks += 1

    def start(self):
        with self._lock:
            if self._running:
                return

            self._last_error = None
            self._running = True

            try:
                self._stream = sd.InputStream(
                    device=self.input_device,
                    samplerate=self.sample_rate,
                    channels=self.channels,
                    dtype="float32",
                    blocksize=self.block_size,
                    callback=self._audio_callback,
                )
                self._stream.start()

            except Exception:
                self._running = False

                if self._stream is not None:
                    try:
                        self._stream.close()
                    except Exception:
                        pass

                self._stream = None
                raise

    def read(self, timeout=1.0):
        """
        Return the next audio block as a float32 NumPy array.
        Return None if no block arrives before timeout.
        """
        if not self._running:
            raise RuntimeError("AudioStream belum berjalan.")

        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def clear_buffer(self):
        """Discard queued audio, for example when beginning a new session."""
        while True:
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break

    def stop(self):
        with self._lock:
            self._running = False
            stream = self._stream
            self._stream = None

        if stream is not None:
            try:
                stream.stop()
            finally:
                stream.close()

        self.clear_buffer()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
