"""Mechanical QA gate for isolated BrainActive gap-fill candidates."""
import json
import os
import re
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK_DIR = os.path.join(ROOT, "bank")
SOURCE = os.path.join(BANK_DIR, "brainactive_p3_question_bank.json")
PRODUCTION = os.path.join(BANK_DIR, "brainactive_p3_question_bank_production.json")
CANDIDATE = os.path.join(BANK_DIR, "gapfill_candidates.json")
RESULTS = os.path.join(BANK_DIR, "gapfill_qa_results.json")
IMAGE_DIR = os.path.join(BANK_DIR, "gapfill_images")
DOMAIN_OF_SKILL = {
    "1.1": "numerical_reasoning", "1.2": "numerical_reasoning", "1.3": "numerical_reasoning", "1.4": "numerical_reasoning",
    "3.1": "verbal_reasoning", "3.2": "verbal_reasoning", "3.3": "verbal_reasoning", "3.4": "verbal_reasoning", "3.5": "verbal_reasoning",
    "5.1": "pattern_abstract", "5.2": "pattern_abstract", "5.3": "pattern_abstract", "5.4": "pattern_abstract",
    "6.1": "problem_solving", "6.2": "problem_solving", "6.3": "problem_solving", "6.6": "problem_solving",
}
LEVEL_DIFFICULTY = {"Explore": "easy", "Think": "medium", "Challenge": "hard", "Master": "expert"}


def load(path, encoding="utf-8"):
    return json.load(open(path, encoding=encoding))


def main():
    source = load(SOURCE, "cp1252")["questions"]
    production = load(PRODUCTION)["questions"]
    candidates = load(CANDIDATE)["questions"]
    existing = source + production
    existing_ids = {q["id"] for q in existing}
    existing_fingerprints = {
        (q.get("question", "").strip().lower(), str(q.get("answer", "")).strip().lower())
        for q in existing
    }
    failures = []
    results = []
    seen_ids = set()
    seen_fingerprints = set()
    expected_prefix = "BA_P3_ADD_"
    for q in candidates:
        qid = q.get("id", "")
        checks = []
        if not re.fullmatch(r"BA_P3_ADD_\d{4}", qid):
            checks.append("invalid_id")
        if qid in existing_ids or qid in seen_ids:
            checks.append("duplicate_id")
        seen_ids.add(qid)
        fingerprint = (q.get("question", "").strip().lower(), str(q.get("answer", "")).strip().lower())
        if fingerprint in existing_fingerprints or fingerprint in seen_fingerprints:
            checks.append("duplicate_question_answer")
        seen_fingerprints.add(fingerprint)
        skill = q.get("skill")
        if skill not in DOMAIN_OF_SKILL or q.get("domain") != DOMAIN_OF_SKILL[skill]:
            checks.append("skill_domain_mismatch")
        level = q.get("level")
        if level not in LEVEL_DIFFICULTY or q.get("difficulty") != LEVEL_DIFFICULTY[level]:
            checks.append("difficulty_level_mismatch")
        options = q.get("options")
        option_ids = [o.get("id") for o in options] if isinstance(options, list) else []
        option_text = [o.get("text") for o in options] if isinstance(options, list) else []
        if option_ids != ["A", "B", "C", "D"] or len(set(option_text)) != 4 or any(not text for text in option_text):
            checks.append("invalid_options")
        if q.get("answer") not in {"A", "B", "C", "D"}:
            checks.append("invalid_answer")
        answer_text = next((o.get("text") for o in options if o.get("id") == q.get("answer")), None) if isinstance(options, list) else None
        if not q.get("question") or not q.get("explanation") or not answer_text:
            checks.append("missing_core_text")
        if q.get("qa_status") != "gapfill_pending_qa":
            checks.append("unexpected_qa_status")
        if not q.get("provenance", {}).get("original"):
            checks.append("missing_original_provenance")
        if q.get("visual_required"):
            if not q.get("visual_spec") or q.get("image_path") != f"p3/{qid}.svg":
                checks.append("invalid_visual_metadata")
            svg_path = os.path.join(IMAGE_DIR, f"{qid}.svg")
            png_path = os.path.join(IMAGE_DIR, f"{qid}.png")
            if not os.path.exists(svg_path) or not os.path.exists(png_path):
                checks.append("missing_rendered_asset")
            else:
                try:
                    ET.parse(svg_path)
                except ET.ParseError:
                    checks.append("invalid_svg")
        elif q.get("image_path"):
            checks.append("nonvisual_image_path")
        if checks:
            failures.append({"id": qid, "checks": checks})
        results.append({"id": qid, "verdict": "FAIL" if checks else "PASS", "checks": checks})

    counts = {}
    for q in candidates:
        key = q.get("skill")
        counts[key] = counts.get(key, 0) + 1
    output = {
        "status": "PASS" if not failures else "FAIL",
        "candidate_count": len(candidates),
        "passed": len(candidates) - len(failures),
        "failed": len(failures),
        "skill_counts": counts,
        "results": results,
    }
    json.dump(output, open(RESULTS, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({k: output[k] for k in ("status", "candidate_count", "passed", "failed", "skill_counts")}, indent=2, sort_keys=True))
    if failures:
        print("Failures:", json.dumps(failures[:20], indent=2))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
