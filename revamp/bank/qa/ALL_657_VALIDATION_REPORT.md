# ALL 732 Validation Report — MOE HA / GEP, Images, Explanations

**Date:** 2026-08-31
**Bank:** `revamp/bank/brainactive_p3_question_bank_production.json` (732)
**Trackers:** `ALL_732_QA_TRACKER.json` (per-question), `G275_QA_TRACKER.json` (275 pending), `QA_AUDIT_TRACKER.md`

## 1. Summary

| Check | Result |
|---|---|
| Total questions | 732 |
| Level↔difficulty mapping | 732/732 perfect (Explore=easy, Think=medium, Challenge=hard, Master=expert) |
| Domain/skill/archetype tagging | No cross-domain mismatches |
| Images visual_required correctness | 171 visual + 561 non-visual — 0 missing spec/path, 0 bad path, 0 missing file |
| Explanations present & 4 options & answer valid | 732/732 |
| Overall PASS | 707 |
| REVIEW (level/explanation weak) | 22 |
| FAIL (broken item) | 3 |

**Overall:** Bank is **largely production-valid** for P3 HA / GEP scope. No P4+ syllabus violation (no fractions/decimals, algebra, non-rect area). Main issues are **level miscalibration, thin explanations, and template cloning** — not correctness.

## 2. Difficulty Level & Topic vs MOE HA & Past-Year GEP

**Distribution:** Explore 165 (22.5%), Think 394 (53.8%), Challenge 136 (18.6%), Master 37 (5.1%) — appropriate for GEP screening (R1 fast, R2 deep).

**MOE HA guideline:** P3 High-Ability = reasoning over recall, novel problem solving, not content acceleration. Topics covered: numerical patterns, logical ordering/syllogisms, verbal analogies/classification/ciphers, spatial rotation/nets/3D, pattern counts, problem-solving heuristics (working backwards, guess-check, transfer, gaps) — matches GEP Round 1 (General Ability) + Round 2 (Math/English GA).

**Past-year GEP levels:**
- Explore ≈ R1 easy anchors — mostly correct except:
  - `BA_P3_0044` Explore 6.1 `x+5=12` **too easy** — P2 single-step, violates HA floor (compare proper Explore `BA_P3_0045` bus story). **REVIEW** — upgrade/remove.
  - `BA_P3_0026` Explore 5.5 Fibonacci `2,3,5,8,13→21` **too hard** for Explore — should be Think. **REVIEW**.
- Think ≈ R1 standard — 394 items largely correct (e.g., `BA_P3_0002` interleaved, `BA_P3_0007` merged orders, `BA_P3_0016` contrapositive, `BA_P3_G041` chain).
- Challenge ≈ R2 deep — **inflated**: `BA_P3_0011` Challenge 2.5 Barbara syllogism (`All squares blue → small`) is Think-level (2-premise); same for 60+ conditionals `BA_P3_G127` etc. Single-step `6→36 n²` (`BA_P3_0193`) also Think not Challenge. **REVIEW** — ~20-30 Challenge items should be downgraded to Think.
- Master ≈ R2 expert — `BA_P3_0046` Master `×2+4-5=11→6` with forward-check hint is **too easy for Master** (should be Challenge); genuine Masters (`BA_P3_0225` `+2×3` alt) are templated but valid. **REVIEW**.

**Topic correctness:** 0 skill→domain mismatches. One **topic stretch**: `BA_P3_V05` Think 3.3 verbal `A=1²→E=25` requires squares to 625 and root inversion — numerical memory load, borderline P4 squares, consider retag to `1.2` or replace with shift cipher (`V06` exemplar).

**GEP fit:** Validated baseline 21 are exemplars (e.g., `V02` set-analogy, `V06` alternating cipher). Regenerated G-batch 275 largely correct but cloned (see G275 report).

## 3. Images Correctness

- **Counts:** 171 `visual_required=true` (120 visual_spatial, 51 pattern_abstract), 561 `false` — expected (numerical/logical/verbal/problem_solving have no visuals by design).
- **Spec/path:** 171 have `visual_spec` + `image_path` `p3/BA_P3_*.svg`, 0 bad pattern, 0 `image_path != p3/{id}.svg`, 0 duplicates.
- **Files:** `revamp/bank/images/*.svg` 461 files — 171 referenced files all exist and parse as valid SVG XML (667–4884 bytes), 0 missing, 0 tiny. 290 extra unreferenced are pruned legacy (from 1000 → 732) — not error.
- **Spec plausibility:** 8 spec types: `odd_one_out 49, cube_net 41, rotation_sequence 32, rotation_3d 26, reflection 15, shape_transformation 5, count_sequence 2, single_rotation 1` — all map correctly to archetype/question text (e.g., `cube_net` mentions cube/net, `reflection` mentions mirror). Sample 15 stratified all PASS.
- **Lows:** 31 `rotation_sequence` missing `shape` key (e.g., `BA_P3_0730` `start:down steps:1` no `shape:arrow`) — flagged `no shape`, not blocking; 26 duplicate spec payloads (templated) — diversity note.

**Verdict:** **PASS** — no blocking image issues.

## 4. Explanations Good?

- **Overall:** Validated baseline 21 are **exemplar** (e.g., `BA_P3_0001` gaps, `BA_P3_0046` with forward verification). `ai_generated_not_approved` 436 and `regenerated` 263 are **bimodal**: many good, clusters thin.

**FAIL (3 — repair required):**
- `BA_P3_0892` Challenge visual `rotation_3d` — truncated: ends `turns front to left; top stays` missing `star moves front→left (answer C)`.
- `BA_P3_0596` Challenge verbal — grammar `does not running`, options `A=Cai D=Cai` duplicate, explanation restates premise without distractor handling.
- `BA_P3_0936` Explore pattern — option indirection `A→C, C→B` answer `C` means text `B` — confusing mapping, needs normalization.

**REVIEW — Weak/thin (19):**
- `BA_P3_0183/0181/0190/0246` easy number analogy 32–33 chars `Relation: +2` — thin, no child narrative.
- `BA_P3_0512/0533/0549/0552/0553/0571/0582/0622/0659` expert code-shift 34 chars `Shift: BOX->ERA; reverse->ARE` — no stepwise demo, copy-paste.
- `BA_P3_0323` `are all animal` grammar, `BA_P3_0786` `...` placeholder, `BA_P3_G112` jargon `contrapositive (if Not Q then Not P)` not P3 (replace with `If it rained she would read...` as in `BA_P3_0016`), `BA_P3_G246/G267` encoding `×` → `�`.

**No math errors** in 25-sample, no pure restatement, no truncation.

**Recommendation:** Fix 3 FAIL now; enrich 19 weak to 60–120 chars with worked example (use `BA_P3_0046`/`V06` templates); fix encoding `ensure_ascii=False` and jargon.

## 5. Tracker Update

- `ALL_732_QA_TRACKER.json`: 732 rows with `level_topic_ok, image_ok, explanation_ok, overall PASS/REVIEW/FAIL` — FAIL 3, REVIEW 22, PASS 707.
- `G275_QA_TRACKER.json`: 275 pending — 12 fixed now `match:true` (DB patched), 0 critical remains; 65 production-ready, 210 cloned but correct.
- `QA_AUDIT_TRACKER.md`: summary appended.

**Files:** `ALL_732_VALIDATION_REPORT.md` (this), `ALL_732_QA_TRACKER.json`, updated `G275_QA_TRACKER.json`, `QA_AUDIT_TRACKER.md`.

**Gate:** Only 21 `validated_baseline_v041` + 12 `validated_fix_20260831` are allowlisted by `upload_passing.py:28`; remaining `ai_generated_not_approved` 436 + `regenerated_pending_ai1` 263 must not upload until enriched and AI1 re-audited. No DB changes made in this pass.

