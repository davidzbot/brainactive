"""Generate isolated, original BrainActive high-ability gap-fill candidates.

This script never rewrites the existing source or production bank. Candidates remain
pending QA until qa_gapfill.py passes them and a human approves the result.
"""
import builtins
import importlib.util
import json
import os
import random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK_DIR = os.path.join(ROOT, "bank")
SOURCE = os.path.join(BANK_DIR, "brainactive_p3_question_bank.json")
PRODUCTION = os.path.join(BANK_DIR, "brainactive_p3_question_bank_production.json")
OUTPUT = os.path.join(BANK_DIR, "gapfill_candidates.json")


def load_generator():
    path = os.path.join(BANK_DIR, "generate_1000.py")
    original_open = builtins.open

    def encoding_open(file, mode="r", *args, **kwargs):
        if os.path.abspath(str(file)) == os.path.abspath(SOURCE) and "b" not in mode:
            kwargs.setdefault("encoding", "cp1252")
        return original_open(file, mode, *args, **kwargs)

    builtins.open = encoding_open
    try:
        spec = importlib.util.spec_from_file_location("brainactive_generator", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        builtins.open = original_open


def safe_num_chain(generator, rng):
    names = rng.sample(["Ali", "Ben", "Cai", "Dan", "Ela", "Fox"], 3)
    a, b, c = names
    base = rng.randint(8, 14)
    off1 = rng.randint(2, 5)
    off2 = rng.randint(2, 5)
    values = {c: base, b: base - off2, a: base - off2 + off1}
    top = max(values, key=values.get)
    question = f"{a} has {off1} more marbles than {b}. {b} has {off2} fewer than {c}. {c} has {base}. Who has the most?"
    distractors = generator.decoys([name for name in names if name != top], top, 3, rng)
    explanation = (
        f"{c} has {base}. {b} has {base} - {off2} = {values[b]}. "
        f"{a} has {values[b]} + {off1} = {values[a]}. {top} has the most."
    )
    return generator.mk(
        "numerical_reasoning", "1.4", "Think", question, top, distractors,
        explanation, "Chaining several comparisons into a full order.",
        ["p3", "high_ability", "numerical", "logic"], "Original gap-fill generator 1.4.", rng,
    )


def level_factory(factory, level):
    def create(rng):
        for _ in range(30):
            question = factory(rng)
            if isinstance(question, dict) and question.get("level") == level:
                return question
        return None
    return create


def main():
    generator = load_generator()
    source = json.load(open(SOURCE, encoding="cp1252"))
    production = json.load(open(PRODUCTION, encoding="utf-8"))["questions"]
    existing_ids = {q["id"] for q in source["questions"]} | {q["id"] for q in production}
    existing_fingerprints = {
        (q.get("question", "").strip().lower(), str(q.get("answer", "")).strip().lower())
        for q in source["questions"] + production
    }

    targets = [
        ("1.1", generator.g_num_seq, 5),
        ("1.2", generator.g_num_analogy, 5),
        ("1.3", generator.g_num_system, 5),
        ("1.4", lambda rng: safe_num_chain(generator, rng), 5),
        ("3.1", generator.g_ver_analogy, 5),
        ("3.2", generator.g_ver_class, 5),
        ("3.4", generator.g_ver_wordmanip, 5),
        ("3.5", generator.g_ver_sentlogic, 5),
        ("5.1", generator.g_pat_countseq, 5),
        ("5.2", generator.g_pat_matrix2, 5),
        ("5.3", generator.g_pat_odd, 5),
        ("5.4", generator.g_pat_analogy, 5),
        ("6.1", generator.g_ps_wb, 5),
        ("6.2", generator.g_ps_gc, 5),
        ("6.3", generator.g_ps_ba, 5),
        ("6.6", generator.g_ps_patternapp, 5),
        ("1.1", generator.g_num_master, 3),
        ("3.3", generator.g_ver_master, 3),
        ("6.1", generator.g_ps_master, 2),
        ("5.2", level_factory(generator.g_pat_matrix3, "Challenge"), 3),
        ("6.1", level_factory(generator.g_ps_wb, "Challenge"), 2),
    ]

    rng = random.Random(20260830)
    candidates = []
    skill_counts = {}
    serial = 1
    for skill, factory, target in targets:
        made = 0
        attempts = 0
        while made < target and attempts < target * 20:
            attempts += 1
            try:
                question = factory(rng)
            except Exception as error:
                print(f"SKIP generator error for {skill}: {error}")
                continue
            if not isinstance(question, dict):
                print(f"SKIP invalid generator output for {skill}: {question!r}")
                continue
            fingerprint = (
                question.get("question", "").strip().lower(),
                str(question.get("answer", "")).strip().lower(),
            )
            if fingerprint in existing_fingerprints:
                continue
            qid = f"BA_P3_ADD_{serial:04d}"
            serial += 1
            for option in question.get("options", []):
                option["text"] = str(option.get("text", ""))
            option_texts = [option.get("text", "") for option in question.get("options", [])]
            if len(option_texts) != 4 or len(set(option_texts)) != 4:
                continue
            question["id"] = qid
            question["image_path"] = f"p3/{qid}.svg" if question.get("visual_required") else None
            question["qa_status"] = "gapfill_pending_qa"
            question.setdefault("provenance", {})
            question["provenance"].update({
                "source_inspiration": "Original item based on BrainActive GEP/HAL skill framework",
                "original": True,
                "gapfill_skill": skill,
                "generation_seed": 20260830,
            })
            candidates.append(question)
            existing_ids.add(qid)
            existing_fingerprints.add(fingerprint)
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
            made += 1
        if made != target:
            raise RuntimeError(f"Could not generate {target} unique candidates for {skill}; made {made}")

    json.dump({
        "dataset": {
            "name": "BrainActive P3 high-ability gap-fill candidates",
            "status": "pending_qa",
            "original_only": True,
            "generation_seed": 20260830,
            "basis": "BrainActive curriculum research and MOE-described enriched reasoning goals",
        },
        "questions": candidates,
    }, open(OUTPUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"Generated candidates: {len(candidates)}")
    print("Skill counts:", json.dumps(skill_counts, sort_keys=True))
    print("Visual candidates:", sum(1 for q in candidates if q.get("visual_required")))
    print("Levels:", json.dumps({level: sum(1 for q in candidates if q.get("level") == level) for level in ("Explore", "Think", "Challenge", "Master")}, sort_keys=True))
    print("Output:", OUTPUT)


if __name__ == "__main__":
    main()
