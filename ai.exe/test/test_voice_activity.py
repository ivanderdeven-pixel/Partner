
import time

from core.audio_stream import AudioStream


def main():
    stream = AudioStream(input_device=1)

    try:
        stream.start()

        print("=== Kalibrasi Noise ===")
        print("Durasi: 20 detik")
        print("0–5 detik   : diam sebisa mungkin")
        print("5–10 detik  : biarkan suara lingkungan terdengar")
        print("10–15 detik : bicara dengan suara normal jika memungkinkan")
        print("15–20 detik : diam kembali")
        print("")

        measurements = {
            "quiet": [],
            "environment": [],
            "speech": [],
            "quiet_end": [],
        }

        start = time.monotonic()
        last_report = start

        while True:
            elapsed = time.monotonic() - start

            if elapsed >= 20:
                break

            block = stream.read(timeout=1.0)

            if block is None:
                print("[WARNING] Tidak menerima blok audio.")
                continue

            rms = float((block ** 2).mean() ** 0.5)
            peak = float(abs(block).max())

            if elapsed < 5:
                phase = "quiet"
            elif elapsed < 10:
                phase = "environment"
            elif elapsed < 15:
                phase = "speech"
            else:
                phase = "quiet_end"

            measurements[phase].append((rms, peak))

            now = time.monotonic()
            if now - last_report >= 1:
                print(
                    f"[{elapsed:5.1f}s] "
                    f"Kondisi: {phase} | "
                    f"RMS: {rms:.6f} | "
                    f"Peak: {peak:.6f}"
                )
                last_report = now

        print("\n=== Ringkasan ===")

        for phase, values in measurements.items():
            if not values:
                print(f"{phase}: tidak ada data")
                continue

            rms_values = sorted(v[0] for v in values)
            peak_values = sorted(v[1] for v in values)

            middle = len(values) // 2

            print(
                f"{phase}: "
                f"median RMS={rms_values[middle]:.6f} | "
                f"median Peak={peak_values[middle]:.6f} | "
                f"blok={len(values)}"
            )

    except KeyboardInterrupt:
        print("\nKalibrasi dihentikan.")

    finally:
        stream.stop()
        print("AudioStream berhenti.")


if __name__ == "__main__":
    main()
