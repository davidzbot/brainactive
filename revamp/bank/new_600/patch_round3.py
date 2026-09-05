"""Round 3: reframe VIS_001/002/009 with compass-story context."""
import json, os, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))

REPL = {
    "NEW_VIS_001": {
        "question": "A weather-vane arrow points north. A gust of wind turns it 90 degrees clockwise. Which compass direction does it point now?",
        "options": [{"id": "A", "text": "North"}, {"id": "B", "text": "East"},
                    {"id": "C", "text": "South"}, {"id": "D", "text": "West"}],
        "answer": "B",
        "explanation": "A quarter-turn clockwise moves north \u2192 east. The vane points east.",
    },
    "NEW_VIS_002": {
        "question": "A signpost arrow points east. It is spun 90 degrees clockwise once. Which compass direction does it point now?",
        "options": [{"id": "A", "text": "North"}, {"id": "B", "text": "East"},
                    {"id": "C", "text": "South"}, {"id": "D", "text": "West"}],
        "answer": "C",
        "explanation": "A quarter-turn clockwise moves east \u2192 south.",
    },
    "NEW_VIS_009": {
        "question": "A compass needle points north. It swings 90 degrees clockwise, then 90 degrees more, then 90 degrees more. Which compass direction is it pointing at the end?",
        "options": [{"id": "A", "text": "North"}, {"id": "B", "text": "East"},
                    {"id": "C", "text": "South"}, {"id": "D", "text": "West"}],
        "answer": "D",
        "explanation": "Three quarter-turns clockwise: north \u2192 east \u2192 south \u2192 west.",
    },
}

for fn in ("new_visual_p1.json", "new_visual_p1b.json"):
    p = os.path.join(HERE, fn)
    qs = json.load(open(p, encoding="utf-8"))
    dirty = False
    for q in qs:
        if q.get("id") in REPL:
            r = REPL[q["id"]]
            q["question"] = r["question"]
            q["options"] = r["options"]
            q["answer"] = r["answer"]
            q["explanation"] = r["explanation"]
            dirty = True
    if dirty:
        json.dump(qs, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("patched", fn)
