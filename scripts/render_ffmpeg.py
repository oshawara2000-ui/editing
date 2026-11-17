"""Step 6 (ffmpeg path): hook first (reel mode), then kept segments, 9:16, source fps.

  --draft : _claude_preview/draft_720p_30fps.mp4 (fast, for review)        [CLAUDE.md 1.4]
  (none)  : export/edited_video_4k_30fps.mp4 2160x3840, needs "approved": true in plan.json

GPU (NVENC) when available, else CPU. Voice loudness -16 LUFS / -1.5 dBTP. Original never touched.
"""
import argparse
import subprocess
import sys

from common import read_json, reel_paths


def has_nvenc():
    r = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True)
    return "h264_nvenc" in r.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--rotate", choices=["cw", "ccw", "180"], help="fix a sideways camera clip")
    a = ap.parse_args()
    p = reel_paths(a.folder)
    plan = read_json(p["work"] / "plan.json")
    probe = read_json(p["work"] / "probe.json")
    if not a.draft and not plan.get("approved"):
        sys.exit('Final needs approval: set "approved": true in plan.json (render --draft first)')

    rot = {"cw": "transpose=1,", "ccw": "transpose=2,", "180": "hflip,vflip,", None: ""}[a.rotate]
    W, H = (720, 1280) if a.draft else (2160, 3840)
    fps = probe.get("fps") or 30
    clips = ([plan["hook"]] if plan["hook"].get("play_first", True) else []) + plan["keep"]
    parts, labels = [], ""
    for i, c in enumerate(clips):
        s, e = float(c["start"]), float(c["end"])
        parts.append(
            f"[0:v]trim={s}:{e},setpts=PTS-STARTPTS,{rot}"
            f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},setsar=1[v{i}];"
            f"[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={max(e-s-0.03,0)}:d=0.03[a{i}];"
        )
        labels += f"[v{i}][a{i}]"
    graph = "".join(parts) + f"{labels}concat=n={len(clips)}:v=1:a=1[v][a];[a]loudnorm=I=-16:TP=-1.5:LRA=11[ao]"

    if a.draft:
        out = p["work"] / "draft_720p_30fps.mp4"
        gpu, cpu = ["-c:v", "h264_nvenc", "-preset", "p1", "-cq", "28"], ["-c:v", "libx264", "-preset", "ultrafast", "-crf", "28"]
    else:
        out = p["output"] / "edited_video_4k_30fps.mp4"
        gpu = ["-c:v", "h264_nvenc", "-preset", "p6", "-tune", "hq", "-rc", "vbr", "-cq", "17", "-b:v", "0", "-profile:v", "high"]
        cpu = ["-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high"]
        if (probe.get("height") or 0) < 3840 and (probe.get("width") or 0) < 3840:
            print("NOTE: source is below 4K -> final is UPSCALED, not native 4K")
    for enc in ([gpu, cpu] if has_nvenc() else [cpu]):
        cmd = ["ffmpeg", "-y", "-v", "error", "-stats", "-i", str(p["video"]), "-filter_complex", graph,
               "-map", "[v]", "-map", "[ao]", *enc, "-pix_fmt", "yuv420p", "-r", str(fps),
               "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(out)]
        if subprocess.run(cmd).returncode == 0:
            break
        print("GPU encode failed, falling back to CPU")
    else:
        sys.exit("ffmpeg failed")
    print(f"Done: {out}")


if __name__ == "__main__":
    main()
