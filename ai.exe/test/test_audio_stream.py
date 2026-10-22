
import time
import traceback

from core.audio_stream import AudioStream


def main():
    stream = None

    try:
        print("=== AudioStream Diagnostic Test ===")
        print("Menyiapkan mikrofon...")

        stream = AudioStream(input_device=1)

        print(f"Sample rate: {stream.sample_rate} Hz")
        print("Memulai stream...")

        stream.start()

        print("AudioStream aktif.")
        print("Tes berlangsung selama 10 detik.")
        print("Diam sebentar, bicara normal, lalu diam lagi.")
        print("-" * 45)

        start_time = time.monotonic()
        blocks_read = 0
        samples_read = 0
        last_report = start_time

        while time.monotonic() - start_time < 10:
            block = stream.read(timeout=1.0)

            if block is None:
                print("[WARNING] Tidak ada blok audio selama 1 detik.")
                continue

            blocks_read += 1
            samples_read += len(block)

            peak = float(abs(block).max())
            rms = float((block ** 2).mean() ** 0.5)

            now = time.monotonic()

            if now - last_report >= 0.5:
                elapsed = now - start_time

                print(
                    f"[{elapsed:5.2f}s] "
                    f"Blok: {blocks_read:4d} | "
                    f"Peak: {peak:.6f} | "
                    f"RMS: {rms:.6f}"
                )

                last_report = now

        print("-" * 45)
        print("=== Hasil Tes ===")
        print(f"Durasi: {time.monotonic() - start_time:.2f} detik")
        print(f"Total blok diterima: {blocks_read}")
        print(f"Total sampel: {samples_read}")
        print(f"Blok terbuang: {stream.dropped_blocks}")
        print(f"Status terakhir: {stream.last_error}")

        if blocks_read == 0:
            print("[HASIL] Tidak ada blok audio yang diterima.")
        elif samples_read == 0:
            print("[HASIL] Blok diterima, tetapi tidak berisi sampel.")
        else:
            print("[HASIL] Data audio berhasil diterima.")

    except KeyboardInterrupt:
        print("\n[INTERRUPT] Tes dihentikan melalui interupsi.")

    except Exception as error:
        print(f"\n[ERROR] {type(error).__name__}: {error}")
        traceback.print_exc()

    finally:
        if stream is not None:
            try:
                stream.stop()
                print("AudioStream berhenti dengan aman.")
            except Exception as error:
                print(
                    f"[ERROR saat menghentikan stream] "
                    f"{type(error).__name__}: {error}"
                )


if __name__ == "__main__":
    main()
