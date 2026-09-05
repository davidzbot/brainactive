"""Replace 4 duplicated/near-duplicate numerical questions with fresh items."""
import json, io, sys, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = {
    "domain": "numerical_reasoning",
    "topic": "Numerical Thinking",
    "skill": "1.1",
    "archetype": "number_sequence",
    "question_type": "multiple_choice",
    "tags": ["p3", "high_ability", "numerical", "sequence"],
    "visual_required": False,
    "visual_spec": None,
    "image_path": None,
    "is_active": True,
    "created_at": "2026-09-05T00:00:00+00:00",
    "updated_at": "2026-09-05T00:00:00+00:00",
    "qa_status": "new_draft_20260905",
}

FRESH = {
    "NEW_NUM_002": dict(BASE, **{
        "id": "NEW_NUM_002", "level": "Explore", "difficulty": "easy",
        "question": "A lily pad doubles every day: 1 pad, 2 pads, 4 pads, 8 pads. How many pads on the next day?",
        "options": [{"id": "A", "text": "12"}, {"id": "B", "text": "14"},
                    {"id": "C", "text": "16"}, {"id": "D", "text": "10"}],
        "answer": "C",
        "explanation": "Each day the pads double: 1 × 2 = 2, 2 × 2 = 4, 4 × 2 = 8, so 8 × 2 = 16.",
        "reasoning": "Spotting doubling in a story context.",
    }),
    "NEW_NUM_006": dict(BASE, **{
        "id": "NEW_NUM_006", "level": "Explore", "difficulty": "easy",
        "question": "Find the next number: 1, 9, 25, 49, ___? (Hint: 1×1, 3×3, 5×5, 7×7.)",
        "options": [{"id": "A", "text": "64"}, {"id": "B", "text": "72"},
                    {"id": "C", "text": "81"}, {"id": "D", "text": "100"}],
        "answer": "C",
        "explanation": "These are odd squares: 1×1 = 1, 3×3 = 9, 5×5 = 25, 7×7 = 49, so 9×9 = 81.",
        "reasoning": "Recognising odd square numbers.",
    }),
    "NEW_NUM_017": dict(BASE, **{
        "id": "NEW_NUM_017", "level": "Think", "difficulty": "medium",
        "question": "Find the next number: 1, 3, 9, 27, ___?",
        "options": [{"id": "A", "text": "72"}, {"id": "B", "text": "81"},
                    {"id": "C", "text": "90"}, {"id": "D", "text": "108"}],
        "answer": "B",
        "explanation": "Each number triples: 1 × 3 = 3, 3 × 3 = 9, 9 × 3 = 27, so 27 × 3 = 81.",
        "reasoning": "Spotting tripling.",
    }),
    "NEW_NUM_023": dict(BASE, **{
        "id": "NEW_NUM_023", "level": "Think", "difficulty": "medium",
        "question": "Find the next number: 2, 5, 9, 14, 20, ___?",
        "options": [{"id": "A", "text": "25"}, {"id": "B", "text": "26"},
                    {"id": "C", "text": "27"}, {"id": "D", "text": "28"}],
        "answer": "C",
        "explanation": "Gaps: +3, +4, +5, +6. The next gap is +7: 20 + 7 = 27.",
        "reasoning": "Spotting growing differences.",
    }),
}

FILES = ["new_numerical_p1.json", "new_numerical_p2.json"]
for fn in FILES:
    p = os.path.join(HERE, fn)
    qs = json.load(open(p, encoding="utf-8"))
    changed = 0
    for i, q in enumerate(qs):
        if q.get("id") in FRESH:
            qs[i] = FRESH[q["id"]]
            changed += 1
    if changed:
        json.dump(qs, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(fn, "replaced", changed)
print("done")
