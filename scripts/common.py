"""Shared helpers: find the video, folders, .env loading, Gemini client."""
import json
import os
import sys
from pathlib import Path

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".m4v"}
ROOT = Path(__file__).resolve().parent.parent


def load_env():
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def reel_paths(folder):
    folder = Path(folder).resolve()
    if not folder.is_dir():
        sys.exit(f"Folder not found: {folder}")
    # CLAUDE.md layout: originals in source/ (fallback: project root). Never modified.
    src = folder / "source" if (folder / "source").is_dir() else folder
    videos = sorted(p for p in src.iterdir() if p.suffix.lower() in VIDEO_EXT)
    if not videos:
        sys.exit(f"No video found in {src}")
    video = max(videos, key=lambda p: p.stat().st_size)  # biggest = main take
    d = {"folder": folder, "video": video, "name": video.stem}
    for key, sub in (("srt", "srt"), ("work", "_claude_preview"), ("output", "export")):
        d[key] = folder / sub
        d[key].mkdir(exist_ok=True)
    return d


def load_words(srt_dir, name):
    """Load transcript in our normalized form, whatever produced it
    (our transcribe.py, Omar's transcribe.bat, or a plain .srt)."""
    wj, sp = Path(srt_dir) / f"{name}.words.json", Path(srt_dir) / f"{name}.srt"
    if wj.exists():
        data = read_json(wj)
        if isinstance(data, dict) and "segments" in data:
            segs = data["segments"]
        elif isinstance(data, list) and data and "words" in data[0]:
            segs = data
        elif isinstance(data, list):  # flat word list -> one segment per ~sentence gap
            segs, cur = [], []
            for w in data:
                if cur and float(w["start"]) - float(cur[-1]["end"]) > 0.6:
                    segs.append(cur); cur = []
                cur.append(w)
            if cur:
                segs.append(cur)
            segs = [{"words": c} for c in segs]
        else:
            sys.exit(f"Unknown words.json format: {wj}")
        out = []
        for i, s in enumerate(segs):
            words = [{"w": (w.get("w") or w.get("word") or w.get("text") or "").strip(),
                      "start": float(w["start"]), "end": float(w["end"])} for w in s.get("words", [])]
            start = float(s.get("start", words[0]["start"] if words else 0))
            end = float(s.get("end", words[-1]["end"] if words else 0))
            text = (s.get("text") or " ".join(w["w"] for w in words)).strip()
            out.append(dict(s, id=i, start=start, end=end, text=text, words=words))
        meta = data if isinstance(data, dict) else {}
        return {**{k: v for k, v in meta.items() if k != "segments"}, "segments": out}
    if sp.exists():
        return {"source": "srt", "segments": parse_srt(sp)}
    sys.exit(f"No transcript for {name} in {srt_dir}")


def parse_srt(path):
    def t(x):
        h, m, rest = x.strip().replace(".", ",").split(":")
        s, ms = rest.split(",")
        return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
    segs = []
    for block in Path(path).read_text(encoding="utf-8-sig").strip().split("\n\n"):
        lines = block.strip().splitlines()
        if len(lines) >= 3 and "-->" in lines[1]:
            a, b = lines[1].split("-->")
            segs.append({"id": len(segs), "start": t(a), "end": t(b), "text": " ".join(lines[2:]), "words": []})
    return segs


def read_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def write_json(p, data):
    Path(p).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def gemini_json(prompt):
    """Send TEXT only (never video) to Gemini, get JSON back.
    Uses GEMINI_API_KEY (Google AI Studio) if set, else OPENROUTER_API_KEY."""
    load_env()
    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-pro")
    if os.environ.get("GEMINI_API_KEY"):
        from google import genai
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        resp = client.models.generate_content(
            model=model, contents=prompt,
            config={"response_mime_type": "application/json", "temperature": 0.2},
        )
        text = resp.text
    elif os.environ.get("OPENROUTER_API_KEY"):
        import requests
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
            json={"model": os.environ.get("OPENROUTER_MODEL", f"google/{model}"),
                  "messages": [{"role": "user", "content": prompt}],
                  "response_format": {"type": "json_object"}, "temperature": 0.2},
            timeout=180,
        )
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"]
    else:
        sys.exit("Put GEMINI_API_KEY (or OPENROUTER_API_KEY) in .env")
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
    return json.loads(text)


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def write_srt(segments, path):
    lines = []
    for i, s in enumerate(segments, 1):
        lines += [str(i), f"{srt_time(s['start'])} --> {srt_time(s['end'])}", s["text"].strip(), ""]
    Path(path).write_text("\n".join(lines), encoding="utf-8")
