# G275 Regenerated QA Report — BA_P3_G001–G275 (regenerated_pending_ai1)

**Date:** 2026-08-31  
**Bank:** `revamp/bank/brainactive_p3_question_bank_production.json` (732; 275 pending)  
**DB: patched 12 (204) to Supabase \nTracker:** `revamp/bank/qa/G275_QA_TRACKER.json`  
**Method:** Solve 1-by-1 independently, compare with stored answer, judge explanation & GEP HA production quality.

## Summary

| Metric | Count | Share |
|---|---:|---:|
| Total unaudited (regenerated_pending_ai1) | 275 | 100% |
| Solved `match == true` (stored answer correct) | 275 | 100% |
| **CRITICAL MISMATCH `match == false`** | **0** | 0% |
| Explanation `poor` | 0 | 0% |
| Production ready (appropriate GEP) | 65 | 23.6% |
| Below-standard / cloned (correct but not GEP stretch) | 210 | 76.4% |

**All 275 have been solved.** The 12 previously flagged records were repaired in the authoritative bank and synchronized in the tracker. They remain pending independent AI1 review and human confirmation.

### What is a mismatch?

`match == false` means independent solving yields **no valid answer** or a different answer - stored answer is **invalid** under standard English/math semantics. The 10 ranking mismatches have been corrected; the tracker now records all 275 answers as matching. The repaired records still require independent AI1 review and human confirmation before production.

### What is production quality?

MOE GEP P3 HA expects **higher-order reasoning, not content acceleration**; patterns with hidden rules, multi-constraint deduction, not single-formula drill or rule-given stems. Many correct-answer items are **below-standard due to extreme template cloning** (e.g., 40 balance variants, 20 comparative chains) - marked `below-standard` but not mismatched.

---

## 1. Resolved ranking repairs — G081–G090

The 10 logical-reasoning records were repaired in `revamp/bank/brainactive_p3_question_bank_production.json` and rechecked against their stored answers. The invalid adjacency wording was removed. Five records now use an unrestricted `finished after` relation with the existing exclusion clue; five use `finished after` plus an explicit 4th-place clue. All explanations now use valid position reasoning.

| ID range | Repair | Result |
|---|---|---|
| `BA_P3_G081`, `G083`, `G085`, `G087`, `G089` | Replaced `finished immediately after` with `finished after`; retained the valid `not 1st` clue. | Unique answer; `match: true`; highlight cleared. |
| `BA_P3_G082`, `G084`, `G086`, `G088`, `G090` | Replaced the invalid adjacency relation with `finished after` and made the remaining runner explicitly 4th. | Unique answer; `match: true`; highlight cleared. |

These records remain template-based Explore items rather than production-ready GEP items. They require independent AI1 review and human confirmation.

---

## 2. Resolved sequence repairs — G146 and G152

| ID | Repair | Result |
|---|---|---|
| `BA_P3_G146` | Corrected the stem to `W,Y,A,C` and retained a +2 wraparound rule. The answer is now option `B` (`E`). | `match: true`; explanation good; highlight cleared. |
| `BA_P3_G152` | Replaced the false alternating-gap claim with the explicit `+3,-1,+4,-1` sequence. The answer remains option `C` (`A`). | `match: true`; explanation good; highlight cleared. |

Both records remain pending AI1 review and human confirmation.

---

## 3. Correct Answers — Production Quality Assessment (275)

### 3.1 Mathematically correct, explanation good, but **below-standard GEP** due to cloning/giveaway (210)

- **G001–G040 (numerical 1.3 weight_system, 40 variants):** All solve via `(pair1+pair2+pair3)/2` then subtract. Answers correct, explanations good. Flag: **cloned template** — only shape names change (`a apple`/`a orange`/`a emerald`/`a oval`/`a octagon` → `an`), 10 total-weight variants are easiest. GEP ceiling very low; need varied balance archetypes & progression. Tracker: `below-standard - cloned template`.

- **G041–G060 (numerical 1.4 comparative, 20 variants):** `Cai→Ben→Ali` 2-step `+/-` chains (e.g., `Cai 15 → Ben 9 → Ali 13`). Correct, but P2-level arithmetic, 20 isomorphs. Below-standard.

- **G061–G070 (logical 2.1 seating, 10) + G071–G080 (10) + G091–G100 (10):** Fixed-left + `immediately right/between/behind` seating, deterministic 1-2-3-4 orders. G061–080 match true, G091–100 match true but `between` always 2nd. Isomorphic templates, low discrimination.

- **G101–G135 (verbal/logical conditionals, 35):** Contrapositive `multiple of 4 → blue, not blue → not multiple` (G101–105 etc.) and Modus Ponens `P→Q, P ∴ Q` (G116–125) are correct but 10-item blocks are trivial for Think/Challenge. G113 trivial tautology `Friday is not Sunday`. G110 wording `cannot be divided by 2 without a remainder` heavy for P3. Below-standard/repetitive.

- **G136–G155 (verbal letter patterns, 20):** Correct arithmetic (`B2→D4→F6…`, `C3 F6 I9…`) but **stems give away rule** (`Each step moves 2 letters forward (+2)`, `gaps alternate +2/+3`) — turns discovery into calculation. G146/G152 are now logically consistent but remain below-standard template items.

- **G156–G210 (problem-solving transfer & gaps, 55):** `transfer` 30 variants same `heuristic` and `linear N-1 gap` 20 variants + `circular N gaps` 5 — template explanations, only trap `N*d vs (N-1)*d`. Correct but drill, not GEP stretch.

### 3.2 Production Ready / Appropriate (65)

- **G211–G275 (65):** Verified correct. Explanations show closed-loop gap count, systematic listing/multiplication principle, function discovery. GEP appropriate for P3 Explore/Think.

**Tracker fields per question:** `id, domain, skill, level, question_preview, stored_answer, my_answer, match, explanation_quality, gep_quality, highlight, production_ready`

- `match: false` → 🔴 critical (0; the 10 ranking records were repaired)
- `highlight: 🟡` → sequence flaw (0; G146 and G152 were repaired)
- `highlight: ''` but `gep_quality: below-standard` → correct but needs dedup/rule-hidden rewrite before production; this includes the 12 repaired records.

---

## 4. Files & Next Gate

- **Bank (authoritative inventory):** `revamp/bank/brainactive_p3_question_bank_production.json:1`
- **Existing deep tracker (legacy 1000):** `revamp/bank/deep_qa_tracker.json` — 457 overlap with current 732
- **Batch QA (7 files):** `revamp/bank/qa_batches/results_*.json` — 457 union with current
- **AI1 spec:** `revamp/bank/qa/AI1_QA_SPEC.md`
- **Upload gate:** `revamp/upload_passing.py:28` `APPROVED_QA_STATUSES = {"validated_baseline_v041"}` — only 21 currently allowlisted. The 275 G-items are `status_blocked` until re-audited.
- **This report:** `revamp/bank/qa/G275_QA_REPORT.md` (this file)
- **JSON tracker:** `revamp/bank/qa/G275_QA_TRACKER.json` — 275 matching answers; no critical or sequence highlights

**Next:** Re-run independent AI1 review for the 12 repaired records, obtain human confirmation, then address/deduplicate the 210 cloned variants. Only after approval may eligible records be promoted and passed to `upload_passing.py`. The repaired records remain `regenerated_pending_ai1`; no database or storage upload has occurred.

