"""Step 4: Gemini reads the transcript (text only) and proposes the edit -> _claude_preview/plan.json

--mode locked : CLAUDE.md 1.3 Locked Edit (client talking-heads). Only trims dead air at the
                head/tail; hook = the real opening line. No reordering, no cuts inside speech.
--mode reel   : Fekra Craft own reels. Hook (~3 s) may be lifted from later and played first,
                and Gemini may drop false starts / repeated takes BETWEEN sentences.
"""
import argparse

from common import gemini_json, load_words, read_json, reel_paths, write_json

RULES = {
    "locked": """LOCKED EDIT: keep every word, its order, pauses and repetitions. Do NOT cut inside the
speech, do NOT reorder, do NOT lift a hook from later. Only trim dead air before the first word and
after the last word. "hook" = the first ~3 s as they are, "keep" = one segment from first to last word.""",
    "reel": """REEL MODE: 1) hook: pick the single strongest line (2-4 s) that stops the scroll (surprising
result, question, bold claim). It will be played FIRST, then the reel starts. It must be a complete
phrase, cut at word boundaries, and must stay true to what is said later (no fake promise).
2) keep: segments in the ORIGINAL order, cut only at sentence/word boundaries (use the word times),
dropping silences > 0.4 s, false starts and repeated takes (keep the best take). Never reorder
sentences and never cut a word in half. Leave ~0.08 s of air before and after each segment.""",
}

PROMPT = """You are a short-form editor for Fekra Craft (3D printing, Egyptian Arabic).
Raw take: {duration}s. Target reel: about {target}s.
{rules}
Use only times that exist in the transcript. Never invent words. Return JSON exactly:
{{"hook":{{"start":0.0,"end":0.0,"text":"","why":""}},
  "keep":[{{"start":0.0,"end":0.0,"text":""}}],
  "remove":[{{"start":0.0,"end":0.0,"reason":""}}],
  "estimated_length_s":0}}

Transcript, one line per segment: start-end | text | word times
{lines}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--target", type=int, default=45)
    ap.add_argument("--mode", choices=RULES, default="reel")
    a = ap.parse_args()
    p = reel_paths(a.folder)
    fixed = p["srt"] / f"{p['name']}.fixed.words.json"
    data = load_words(p["srt"], f"{p['name']}.fixed" if fixed.exists() else p["name"])
    probe = read_json(p["work"] / "probe.json")
    lines = "\n".join(
        f"{s['start']:.2f}-{s['end']:.2f} | {s['text']} | " + " ".join(f"{w['w']}@{w['start']:.2f}" for w in s["words"])
        for s in data["segments"]
    )
    plan = gemini_json(PROMPT.format(duration=probe["duration_s"], target=a.target, rules=RULES[a.mode], lines=lines))
    plan.update(mode=a.mode, approved=False)
    if a.mode == "locked":  # the hook is just the opening, don't play it twice
        plan["hook"]["play_first"] = False
    write_json(p["work"] / "plan.json", plan)
    h = plan["hook"]
    print(f"MODE {a.mode}\nHOOK [{h['start']:.2f}-{h['end']:.2f}] {h['text']}  ({h.get('why','')})")
    for k in plan["keep"]:
        print(f"KEEP [{k['start']:.2f}-{k['end']:.2f}] {k.get('text', '')[:70]}")
    print(f"~{plan.get('estimated_length_s')}s, {len(plan.get('remove', []))} removals")


if __name__ == "__main__":
    main()
