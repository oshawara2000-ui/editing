"""Steps 2+3a: reuse srt/ cache, else transcribe LOCALLY (GPU) with word timestamps.

Default: Omar's transcribe.bat (Whisper large-v3). Fallback: faster-whisper here.
Result always ends in srt/<name>.srt + srt/<name>.words.json
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

from common import load_env, reel_paths, write_json, write_srt

DEFAULT_BAT = r"C:\Users\amrsh\Desktop\skills and textures and fonts\transcribe-tool\transcribe.bat"


def collect(p):
    """transcribe.bat may write next to the video: move results into srt/."""
    for ext in (".srt", ".words.json"):
        for cand in (p["video"].with_name(p["name"] + ext), p["video"].with_suffix(ext)):
            if cand.exists() and not (p["srt"] / (p["name"] + ext)).exists():
                shutil.move(str(cand), p["srt"] / (p["name"] + ext))


def main(folder):
    load_env()
    p = reel_paths(folder)
    if any((p["srt"] / f"{p['name']}{e}").exists() for e in (".words.json", ".srt")):
        print(f"CACHE HIT: transcript already in {p['srt']} -> skipping")
        return

    bat = os.environ.get("TRANSCRIBE_BAT", DEFAULT_BAT)
    if Path(bat).exists():
        print(f"Running {bat} ...")
        subprocess.run([bat, str(p["video"])], check=True)
        collect(p)
        if (p["srt"] / f"{p['name']}.srt").exists() or (p["srt"] / f"{p['name']}.words.json").exists():
            return
        print("transcribe.bat finished but no output found in srt/ -> using faster-whisper")

    from faster_whisper import WhisperModel

    model_name = os.environ.get("WHISPER_MODEL", "large-v3")
    try:
        model = WhisperModel(model_name, device="cuda", compute_type="float16")
    except Exception as e:
        print(f"GPU not available ({e}); CPU + medium model (slower)")
        model = WhisperModel("medium", device="cpu", compute_type="int8")
    segs, _ = model.transcribe(
        str(p["video"]), language="ar", word_timestamps=True, vad_filter=True,
        initial_prompt="فيديو عن الطباعة ثلاثية الأبعاد: PLA, PETG, nozzle, Bambu Lab, layer height",
    )
    out = []
    for i, s in enumerate(segs):
        out.append({"id": i, "start": round(s.start, 3), "end": round(s.end, 3), "text": s.text.strip(),
                    "words": [{"w": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)} for w in (s.words or [])]})
        print(f"[{s.start:7.2f}] {s.text.strip()}")
    write_json(p["srt"] / f"{p['name']}.words.json", {"source": "faster-whisper", "segments": out})
    write_srt(out, p["srt"] / f"{p['name']}.srt")


if __name__ == "__main__":
    main(sys.argv[1])
