# BrainActive P3 High Ability - Content Coverage (v0.5-local)

Local development bank. 100 questions. Not production-approved.

## Total

- Questions: **1000**
- Visual / non-visual: **326** / **674**
- Verbal reasoning share: **16.0%** (target ~15-16%)

## By domain (vs revised blueprint)

| Domain | Count | Blueprint | Delta |
|---|---|---|---|
| numerical_reasoning | 180 | 18 | +162 |
| logical_reasoning | 180 | 18 | +162 |
| verbal_reasoning | 160 | 16 | +144 |
| visual_spatial | 160 | 16 | +144 |
| pattern_abstract | 200 | 20 | +180 |
| problem_solving | 120 | 12 | +108 |

## By level (vs blueprint target)

| Level | Count | Target | Delta |
|---|---|---|---|
| Explore | 215 | 30 | +185 |
| Think | 604 | 40 | +564 |
| Challenge | 113 | 22 | +91 |
| Master | 68 | 8 | +60 |

> Master tier is materially under the target (2 vs 8). See Gaps.

## By skill (skill_code)

| Skill | Count | Blueprint sub-target | Delta |
|---|---|---|---|
| 1.1 | 82 | 8 | +74 |
| 1.2 | 42 | 5 | +37 |
| 1.3 | 53 | 4 | +49 |
| 1.4 | 3 | 3 | +0 |
| 2.1 | 43 | 4 | +39 |
| 2.2 | 60 | 4 | +56 |
| 2.3 | 33 | 4 | +29 |
| 2.4 | 35 | 3 | +32 |
| 2.5 | 9 | 3 | +6 |
| 3.1 | 28 | 5 | +23 |
| 3.2 | 20 | 3 | +17 |
| 3.3 | 42 | 3 | +39 |
| 3.4 | 21 | 2 | +19 |
| 3.5 | 21 | 1 | +20 |
| 3.6 | 17 | 1 | +16 |
| 3.7 | 11 | 1 | +10 |
| 4.1 | 35 | 4 | +31 |
| 4.2 | 13 | 3 | +10 |
| 4.3 | 40 | 3 | +37 |
| 4.4 | 25 | 2 | +23 |
| 4.5 | 34 | 2 | +32 |
| 4.6 | 12 | 2 | +10 |
| 4.7 | 1 | - | - |
| 5.1 | 30 | 6 | +24 |
| 5.1+4.6 | 1 | - | - |
| 5.2 | 67 | 6 | +61 |
| 5.3 | 59 | 4 | +55 |
| 5.4 | 42 | 4 | +38 |
| 5.5 | 1 | - | - |
| 6.1 | 27 | 2 | +25 |
| 6.2 | 7 | 2 | +5 |
| 6.3 | 24 | 2 | +22 |
| 6.4 | 21 | 2 | +19 |
| 6.5 | 23 | 2 | +21 |
| 6.6 | 18 | 2 | +16 |

## Progression / source

- Baseline v0.4.1 (validated): **50** questions (qa_status=validated_baseline_v041).
- Verbal extension v0.5 (research-derived, AI-generated): **950** questions (qa_status=ai_generated_not_approved).
- New generated (this build): **0** questions (qa_status=ai_generated_not_approved).
- Full Skill-Practice progressions for the baseline 50 are documented in `revamp/report/v0.4.1_question_catalogue.md`; the verbal extension progressions in `revamp/curriculum/brainactive_verbal_pilot_plan.md`. The bank itself stores per-question skill_code + level so progressions can be rebuilt by the importer.

## Generator-friendly vs human-authored

- Deterministic / visual-spec driven (generator-friendly): **530**
- Text reasoning / authored (verbal, logical, problem-solving): **470**

## Remaining gaps against the first-100 blueprint

1. **Master tier shortfall**: 2 Master questions vs ~8 target. The baseline contributed 2 (BA_P3_0046, BA_P3_0050); this build added 0 new Master items. A dedicated Master-generation pass (items that require the child to *decide how to solve*) is recommended before AI1 QA.
2. **Numerical trimmed**: 18 vs original blueprint 20 (reduced by 2 so the total stays 100 after the revised verbal +2). If verbal is later set to 14, numerical can return to 20.
3. **Light sub-skills**: 4.5 (Position) is text-based (2 items, no diagram); 4.6 (Transform) has 1; 6.4 (Draw Diagram) and 6.5 (Make List) have 1 each. These are covered but thin.
4. **Verbal 3.7 (Sentence Completion)** intentionally capped at 1 (vocabulary + reasoning); do not expand without review.

## Drift guard

Run `python revamp/bank/validate_bank.py` after any edit. Current run: 100 questions, 0 structural issues, 0 duplicate IDs, 0 invalid answers, 34 visual assets present and valid SVG.