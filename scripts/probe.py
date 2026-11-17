"""Step 1: inspect the video with ffprobe -> work/probe.json (small summary)."""
import json
import subprocess
import sys

from common import reel_paths, write_json


def main(folder):
    p = reel_paths(folder)
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(p["video"])],
        capture_output=True, text=True, check=True,
    ).stdout
    info = json.loads(out)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), {})
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), {})
    num, den = (v.get("r_frame_rate", "0/1").split("/") + ["1"])[:2]
    rotate = int((v.get("tags") or {}).get("rotate", 0) or 0)
    for sd in v.get("side_data_list", []):
        rotate = int(sd.get("rotation", rotate) or rotate)
    w, h = v.get("width"), v.get("height")
    if abs(rotate) in (90, 270):
        w, h = h, w
    summary = {
        "video": p["video"].name,
        "duration_s": round(float(info["format"].get("duration", 0)), 2),
        "width": w, "height": h,
        "vertical": bool(w and h and h > w),
        "fps": round(int(num) / max(int(den), 1), 3),
        "video_codec": v.get("codec_name"),
        "audio_codec": a.get("codec_name"),
        "audio_rate": a.get("sample_rate"),
        "audio_channels": a.get("channels"),
        "size_mb": round(int(info["format"].get("size", 0)) / 1e6, 1),
    }
    write_json(p["work"] / "probe.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(sys.argv[1])
