"""Step 3b: Gemini Pro fixes what Whisper MISHEARD (text only). Timings stay from Whisper.

Never overwrites the Whisper files: writes srt/<name>.fixed.words.json + srt/<name>.fixed.srt
and srt/<name>.fixes.txt (what changed, for a quick human check).
"""
import json
import sys

from common import gemini_json, load_words, reel_paths, write_json, write_srt

PROMPT = """You are proof-listening an automatic Whisper transcript of an Egyptian Arabic video about
3D printing (brand: Fekra Craft). Fix ONLY words that were clearly misheard.
Rules: keep the Egyptian dialect exactly as spoken (never convert to formal Arabic), never rephrase,
never remove repetitions or filler that was actually said, write technical terms / brands / units in
English (PLA, PETG, nozzle, bed, layer height, infill, Bambu Lab, mm...), keep numbers as digits.
Do not merge, split, add or drop segments. Return JSON: {"segments":[{"id":0,"text":"..."}]}

Segments:
"""


def respread(seg, text):
    words = text.split()
    if len(words) == len(seg["words"]):
        return [dict(w, w=nw) for w, nw in zip(seg["words"], words)]
    total = sum(len(w) for w in words) or 1  # word count changed: spread by length
    t, dur, out = seg["start"], seg["end"] - seg["start"], []
    for w in words:
        d = dur * len(w) / total
        out.append({"w": w, "start": round(t, 3), "end": round(t + d, 3)})
        t += d
    return out


def main(folder):
    p = reel_paths(folder)
    fixed_json = p["srt"] / f"{p['name']}.fixed.words.json"
    if fixed_json.exists():
        print("CACHE HIT: already corrected -> skipping")
        return
    data = load_words(p["srt"], p["name"])
    payload = [{"id": s["id"], "text": s["text"]} for s in data["segments"]]
    fixed = {int(s["id"]): s["text"] for s in gemini_json(PROMPT + json.dumps(payload, ensure_ascii=False))["segments"]}
    log = []
    for s in data["segments"]:
        new = fixed.get(s["id"], s["text"]).strip()
        if new and new != s["text"]:
            log.append(f"[{s['start']:.2f}] {s['text']}\n      -> {new}")
            s["text_whisper"], s["text"] = s["text"], new
            if s["words"]:
                s["words"] = respread(s, new)
    data["corrected_by"] = "gemini"
    write_json(fixed_json, data)
    write_srt(data["segments"], p["srt"] / f"{p['name']}.fixed.srt")
    (p["srt"] / f"{p['name']}.fixes.txt").write_text("\n".join(log) or "no changes", encoding="utf-8")
    print(f"Gemini corrected {len(log)}/{len(data['segments'])} segments (see {p['name']}.fixes.txt)")


if __name__ == "__main__":
    main(sys.argv[1])
