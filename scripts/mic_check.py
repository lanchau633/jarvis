"""Measure input level on each candidate microphone so you can tell which one
actually hears you. Run it, talk normally for the countdown, and pick the
device with a clearly higher level than the others.

    .conda-env\\python.exe scripts\\mic_check.py
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import numpy as np
import sounddevice as sd

SECONDS = 4
SAMPLE_RATE = 16000


def candidates():
    seen = set()
    out = []
    for idx, dev in enumerate(sd.query_devices()):
        if dev["max_input_channels"] <= 0:
            continue
        name = dev["name"].strip()
        # Skip the aggregate/loopback entries; they aren't real capture devices.
        if any(s in name.lower() for s in ("sound mapper", "primary sound", "stereo mix", "speaker", "output")):
            continue
        if name in seen:
            continue
        seen.add(name)
        out.append((idx, name))
    return out


def measure(index: int) -> tuple[float, float]:
    rec = sd.rec(
        int(SECONDS * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        device=index,
    )
    sd.wait()
    audio = np.nan_to_num(rec.flatten(), nan=0.0, posinf=0.0, neginf=0.0)
    audio = np.clip(audio.astype(np.float64), -1.0, 1.0)
    return float(np.sqrt(np.mean(audio**2))), float(np.max(np.abs(audio)))


def main() -> None:
    devices = candidates()
    print(f"Testing {len(devices)} input device(s), {SECONDS}s each.")
    print("TALK CONTINUOUSLY while each one is being tested.\n")

    results = []
    for index, name in devices:
        print(f"  [{index}] {name[:52]:<52} ", end="", flush=True)
        for n in (3, 2, 1):
            print(f"{n}.", end="", flush=True)
            time.sleep(0.4)
        try:
            rms, peak = measure(index)
        except Exception as exc:
            print(f" FAILED ({type(exc).__name__})")
            continue
        bar = "#" * min(40, int(min(rms, 1.0) * 400))
        if peak >= 0.99:
            verdict = "CLIPPING"
        elif rms < 0.002:
            verdict = "SILENT"
        elif rms < 0.01:
            verdict = "quiet"
        else:
            verdict = "GOOD"
        print(f" rms={rms:.4f} peak={peak:.3f} {verdict:<8} {bar}")
        results.append((rms, index, name))

    if not results:
        print("\nNo device produced a reading.")
        return

    results.sort(reverse=True)
    best_rms, best_idx, best_name = results[0]
    print("\n" + "=" * 60)
    if best_rms < 0.002:
        print("Every device read as silent - check Windows mic privacy settings")
        print("and that the mic isn't muted in hardware.")
    else:
        print(f"LOUDEST: [{best_idx}] {best_name}  (rms={best_rms:.4f})")
        print("\nTo use it, add this to C:\\Users\\<you>\\.config\\jarvis\\config.json:")
        print(f'    "voice_device": {best_idx}')


if __name__ == "__main__":
    main()
