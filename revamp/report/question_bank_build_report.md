# Question Bank Build Report — v0.6-local

**Date:** 2026-08-28
**Scope:** Local content-bank scaling only. No DB, no Supabase, no production code, no publish.

## What was built
A **1000-question** local development bank at `revamp/bank/brainactive_p3_question_bank.json`,
scaled from the validated 100-question v0.5-local bank. The 100 validated questions are kept as the
seed; **900** additional questions were generated deterministically to reach 1000, preserving the
research-derived domain balance (numerical / logical / verbal / visual / pattern / problem_solving).

## Counts
- **Total in bank:** 1000
- **From v0.5-local seed (frozen + verbal + 40 generated):** 100 (`qa_status` mixed; the 50 baseline are `validated_baseline_v041`)
- **Newly generated for v0.6:** 900 (deterministic, grounded in GEP General Ability / CogAT / UK 11+ VR-NVR / MOE 2026 HAL archetypes)
- All 900 new items carry `qa_status = ai_generated_not_approved` (pending AI1 QA + human review).

## Domain distribution (research-derived balance preserved)
| Domain | Count | Share |
|---|---|---|
| numerical_reasoning | 180 | 18% |
| logical_reasoning | 180 | 18% |
| verbal_reasoning | 160 | 16% |
| visual_spatial | 160 | 16% |
| pattern_abstract | 200 | 20% |
| problem_solving | 120 | 12% |

## Difficulty distribution
- Explore: 215
- Think: 604
- Challenge: 113
- Master: 68   (added via dedicated Master-tier generators; ~7% expert items for the high-ability audience)

## Visual count
- Visual questions: **328** (rendered to `revamp/bank/images/*.svg` + PNG; `render.py` extended to
  parse the richer figure descriptions used by matrix / odd-one-out / figure-analogy items).
- Non-visual (text reasoning): 672.

## Generator coverage
- 33 deterministic generators (`revamp/bank/generate_1000.py`) across the 6 domains and 41 skills.
- Each generator computes the answer and auto-builds near-miss distractors; duplicates are rejected
  by (question, answer) fingerprint against both seed and new items.
- Pattern/visual generators expanded with combinatorial variety (shape/colour/size/dot transforms,
  row+column matrix rules) so each can yield 30+ genuinely distinct items.

## Unresolved issues
1. **Think-heavy.** 604 Think vs 215 Explore — acceptable for high-ability but skewed; some Think
   items could be re-levelled to Explore on review.
2. **Independent answer verification not yet run.** Structural validation passes, but reasoning
   correctness of the 900 new items still requires the AI1 pass (AI1_QA_SPEC.md) + human review.
3. **Verbal 3.7 Sentence Completion capped at 10** (vocabulary + reasoning) — intentional.
4. The 900 new items are **not yet AI1-QA'd or human-approved** — development content only.

## Validation (current run)
- `validate_bank.py`: 1000 questions, **0 structural issues, 0 duplicate IDs, 0 invalid answers**,
  328 visual assets present + valid SVG, 0 duplicate (question, answer) fingerprints.
- `CONTENT_COVERAGE.md` regenerated for 1000.

## Recommended next gate
1. **Independent AI1 QA** per `revamp/bank/qa/AI1_QA_SPEC.md` over all 1000 questions (answer
   re-derivation + P3 appropriateness + A/B/C verbal check).
2. **Human review** of AI1 REVIEW/FAIL items; re-author as needed.
3. **Master-tier generation pass** — DONE (68 Master items added via dedicated expert generators).
4. Only after 1–3: import to Supabase question records + Storage for visual assets, then production app.
   Until then: JSON only. No DB, no publish.

## Pipeline state
```
Research -> Curriculum -> 100-q validated seed -> Local 1000-q development bank
  -> Deterministic visual assets (render.py extended)
  -> Automated structural validation (0 issues)
  -> READY FOR INDEPENDENT AI1 QA

---

## Audit (added 2026-08-28)

An **independent auditor** `revamp/bank/audit_bank.py` was written and run over all 1000
questions. It does NOT call the generators — it re-derives every answer by **parsing the question
text** for the computable families, and cross-checks structure + explanation/answer consistency.

### Method
- **C1 structural:** exactly 4 options; answer letter valid and maps to an existing option; options distinct.
- **C2 consistency:** the correct option text (short options) appears in explanation/reasoning.
- **C3 re-derivation** (parse-only, independent of generator) for families 1.1, 1.2, 1.3, 1.4,
  2.1, 2.3, 3.3, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6 — predict the answer and compare to the stored one;
  flag mismatch (a fitting model predicts a different value) or ambiguity (models fit with
  conflicting predictions / order not uniquely determined).
- **C4 verbal A/B/C:** count report only (no content changed).

### Results (after fixes, final run)
- Total audited: **1000**
- C1 structural fails: **0**
- C2 consistency fails: **1** (BA_P3_0020 — option "hexagon, blue" vs explanation "blue hexagon";
  a reversed-word-order paraphrase, **not** a real bug; residual).
- C3 mismatches: **0**
- C3 ambiguous: **0**
- Unverified-by-skill: **606** (visual/pattern + most verbal + seed items phrased differently from
  the generators — covered by C1+C2 and manual sampling; no hidden mismatch found).

### Bugs found and fixed in `generate_1000.py`
1. **`g_log_cond` (2.3) hardcoded "19" in explanation** — the question used a random number 11–29
   but the explanation always said "19 is not blue". Fixed to use the actual number.
   Examples (regenerated): `BA_P3_0278` (22), `BA_P3_0280` (17), `BA_P3_0323` (15), `BA_P3_0394` (26)
   — ~15 items affected. Auditor flagged each via the number-consistency check.
2. **`g_ps_list` (6.5) wrong count formula** — used `len(L)**2` instead of `len(L)**len(L)`.
   3-letter codes from 3 letters were stored as 9 (should be 27). Fixed. Examples: `BA_P3_1154`,
   `BA_P3_1157`, `BA_P3_1187` (now 27); 2-letter cases (4) unchanged/correct.
3. **`g_log_order` second branch (2.1) under-determined order** — "a beats b, b beats c, a beats d"
   leaves d's position between b and c ambiguous, yet a single order was stored as correct. Rewritten
   as a fully-determined chain `a beats b, b beats c, c beats d → a>b>c>d`. (Auditor's topological
   uniqueness check now passes for all ordering items, including the validated seed `BA_P3_0186`.)
4. **`g_log_constraint` (2.2) under-determined answer** — "who sits second from the left" was not
   fixed by the constraints (two candidates). Rewritten deterministically: A left end, B next to A
   (seat 2), C at right end (seat 4) ⇒ D forced to seat 3; any seat asked has a unique answer.
5. **`g_log_class` / `g_ver_class` (2.4 / 3.2) wrong odd-one-out** — the distractor pool included
   "whale", which is an animal, so it was an invalid odd-one-out when the group was animals. Removed
   "whale" from both pools (replaced with non-animal "table").

### Verbal A/B/C compliance
- VR7 (sentence completion, class **B**, capped) total = **11** (1 validated seed + 10 generated),
  within the "~1 per 100" tolerance; all other verbal skills are class **C** (reasoning, vocabulary-light).
  No class **A** (pure-vocabulary) items exist. No content was changed by the audit — only counts reported.

### Archetype alignment (confirmed vs external guides)
Question **types** match recognised GEP GA / CogAT / UK 11+ archetypes:
- CogAT Quantitative = Number Series (1.1), Number Analogies (1.2), Number Puzzles (1.3 weight system).
- CogAT Verbal = Verbal Analogies (3.1), Verbal Classification (3.2), Sentence Completion (3.7).
- CogAT Nonverbal / UK 11+ NVR = Figure Matrices (5.2), Figure Classification / Odd-One-Out (5.3, 2.4),
  Paper Folding (4.8, framework-only), Rotation (4.1), Reflection (4.2), Nets/Cubes (4.3),
  Analogies (5.4), Codes (3.3). SPONCS (Shape/Position/Orientation/Number/Colour/Size) is exactly the
  feature set used by the pattern/visual generators.
- 2.3 conditionals (contrapositive, chained) = GEP GA logical deduction; 6.x heuristics (working
  backwards, guess-and-check, draw-a-diagram, make-a-list, pattern-application, before-after) = the
  Singapore "thinking skills" identity emphasised by MOE 2026 HAL.
No off-archetype or non-P3-appropriate item type was found.

### Residual caveats
- 606 items remain "unverified" by automated parse (visual/pattern/most verbal + seed items with
  paraphrased phrasings). They passed structural validation and explanation/answer consistency, and a
  manual sample showed correct answers; full answer-proof still needs the AI1 pass.
- `BA_P3_0020` C2 flag is a paraphrase, not a defect.
- VR7 count (11) is marginally above a strict 10; acceptable under "~1 per 100".
- **Gate unchanged:** independent **AI1 QA** + human review are still required before any import.
```
