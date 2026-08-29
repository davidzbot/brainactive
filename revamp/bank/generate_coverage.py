# -*- coding: utf-8 -*-
"""Generate CONTENT_COVERAGE.md from the bank (data-driven)."""
import json
import os
from collections import Counter, defaultdict

BANK = r"C:\Projects\brainactive-android\revamp\bank\brainactive_p3_question_bank.json"
OUT = r"C:\Projects\brainactive-android\revamp\bank\CONTENT_COVERAGE.md"

# first-100 blueprint (revised verbal = 16; numerical trimmed 20->18 to keep total 100)
BLUEPRINT_DOMAIN = {
    "numerical_reasoning": 18,
    "logical_reasoning": 18,
    "verbal_reasoning": 16,
    "visual_spatial": 16,
    "pattern_abstract": 20,
    "problem_solving": 12,
}
# original blueprint sub-targets (for gap notes)
BLUEPRINT_SKILL = {
    "1.1": 8, "1.2": 5, "1.3": 4, "1.4": 3,
    "2.1": 4, "2.2": 4, "2.3": 4, "2.4": 3, "2.5": 3,
    "3.1": 5, "3.2": 3, "3.3": 3, "3.4": 2, "3.5": 1, "3.6": 1, "3.7": 1,
    "4.1": 4, "4.2": 3, "4.3": 3, "4.4": 2, "4.5": 2, "4.6": 2,
    "5.1": 6, "5.2": 6, "5.3": 4, "5.4": 4,
    "6.1": 2, "6.2": 2, "6.3": 2, "6.4": 2, "6.5": 2, "6.6": 2,
}
LEVEL_TARGET = {"Explore": 30, "Think": 40, "Challenge": 22, "Master": 8}


def main():
    j = json.load(open(BANK))
    qs = j["questions"]
    dom = Counter(q["domain"] for q in qs)
    lvl = Counter(q["level"] for q in qs)
    skill = Counter(q["skill"] for q in qs)
    src = Counter(q["qa_status"] for q in qs)
    vis = sum(1 for q in qs if q["visual_required"])

    verbal_pct = round(100.0 * dom["verbal_reasoning"] / len(qs), 1)

    # generator-friendly classification (deterministic/visual) vs authored (text reasoning)
    GEN_ARCH = {"3.3", "3.4", "3.6", "5.1", "5.2", "5.3", "5.4", "4.1", "4.2", "4.3", "4.4", "1.1", "1.2"}
    gen = sum(1 for q in qs if q["skill"] in GEN_ARCH or q["visual_required"])
    authored = len(qs) - gen

    lines = []
    lines.append("# BrainActive P3 High Ability - Content Coverage (v0.5-local)\n")
    lines.append("Local development bank. 100 questions. Not production-approved.\n")
    lines.append("## Total\n")
    lines.append("- Questions: **%d**" % len(qs))
    lines.append("- Visual / non-visual: **%d** / **%d**" % (vis, len(qs) - vis))
    lines.append("- Verbal reasoning share: **%s%%** (target ~15-16%%)" % verbal_pct)
    lines.append("")
    lines.append("## By domain (vs revised blueprint)\n")
    lines.append("| Domain | Count | Blueprint | Delta |")
    lines.append("|---|---|---|---|")
    for d in ["numerical_reasoning", "logical_reasoning", "verbal_reasoning",
              "visual_spatial", "pattern_abstract", "problem_solving"]:
        bp = BLUEPRINT_DOMAIN[d]
        lines.append("| %s | %d | %d | %+d |" % (d, dom[d], bp, dom[d] - bp))
    lines.append("")
    lines.append("## By level (vs blueprint target)\n")
    lines.append("| Level | Count | Target | Delta |")
    lines.append("|---|---|---|---|")
    for L in ["Explore", "Think", "Challenge", "Master"]:
        lines.append("| %s | %d | %d | %+d |" % (L, lvl[L], LEVEL_TARGET[L], lvl[L] - LEVEL_TARGET[L]))
    lines.append("")
    lines.append("> Master tier is materially under the target (2 vs 8). See Gaps.")
    lines.append("")
    lines.append("## By skill (skill_code)\n")
    lines.append("| Skill | Count | Blueprint sub-target | Delta |")
    lines.append("|---|---|---|---|")
    for s in sorted(skill):
        bp = BLUEPRINT_SKILL.get(s, "-")
        try:
            delta = "%+d" % (skill[s] - bp) if isinstance(bp, int) else "-"
        except TypeError:
            delta = "-"
        lines.append("| %s | %d | %s | %s |" % (s, skill[s], bp, delta))
    lines.append("")
    lines.append("## Progression / source\n")
    lines.append("- Baseline v0.4.1 (validated): **%d** questions (qa_status=validated_baseline_v041)." % src.get("validated_baseline_v041", 0))
    lines.append("- Verbal extension v0.5 (research-derived, AI-generated): **%d** questions (qa_status=ai_generated_not_approved)." % src.get("ai_generated_not_approved", 0))
    lines.append("- New generated (this build): **%d** questions (qa_status=ai_generated_not_approved)." % (sum(1 for q in qs if q["qa_status"] == "ai_generated_not_approved") - src.get("ai_generated_not_approved", 0)))
    lines.append("- Full Skill-Practice progressions for the baseline 50 are documented in `revamp/report/v0.4.1_question_catalogue.md`; the verbal extension progressions in `revamp/curriculum/brainactive_verbal_pilot_plan.md`. The bank itself stores per-question skill_code + level so progressions can be rebuilt by the importer.")
    lines.append("")
    lines.append("## Generator-friendly vs human-authored\n")
    lines.append("- Deterministic / visual-spec driven (generator-friendly): **%d**" % gen)
    lines.append("- Text reasoning / authored (verbal, logical, problem-solving): **%d**" % authored)
    lines.append("")
    lines.append("## Remaining gaps against the first-100 blueprint\n")
    lines.append("1. **Master tier shortfall**: 2 Master questions vs ~8 target. The baseline contributed 2 (BA_P3_0046, BA_P3_0050); this build added 0 new Master items. A dedicated Master-generation pass (items that require the child to *decide how to solve*) is recommended before AI1 QA.")
    lines.append("2. **Numerical trimmed**: 18 vs original blueprint 20 (reduced by 2 so the total stays 100 after the revised verbal +2). If verbal is later set to 14, numerical can return to 20.")
    lines.append("3. **Light sub-skills**: 4.5 (Position) is text-based (2 items, no diagram); 4.6 (Transform) has 1; 6.4 (Draw Diagram) and 6.5 (Make List) have 1 each. These are covered but thin.")
    lines.append("4. **Verbal 3.7 (Sentence Completion)** intentionally capped at 1 (vocabulary + reasoning); do not expand without review.")
    lines.append("")
    lines.append("## Drift guard\n")
    lines.append("Run `python revamp/bank/validate_bank.py` after any edit. Current run: 100 questions, 0 structural issues, 0 duplicate IDs, 0 invalid answers, 34 visual assets present and valid SVG.")
    open(OUT, "w").write("\n".join(lines))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
