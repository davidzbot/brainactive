# BrainActive P3 High Ability — Research & Pilot Report

## 1. What we learned from research
- Singapore high-ability identification is **reasoning-first**. Historically GEP used a two-round
  Screening (English+Math) then Selection (+ General Ability). **From 2026 MOE moves to a single
  stage emphasising reasoning, language and problem-solving**, not syllabus drilling.
- HAL (High Ability Learners) school programmes (E2K, MEW, etc.) reward the *same thinking habits*.
- The General Ability paper is IQ-like: ~30–40 items / ~75 min, split into **verbal** (analogies,
  anagrams, decoding, logic) and **non-verbal** (patterns, odd-one-out, spatial rotation/reflection/
  3D nets, logic). SPONCS is the standard visual-analysis heuristic.
- High-ability P3 items are **non-routine**: the bottleneck is reasoning, not arithmetic.

## 2. Recommended BrainActive positioning
**"BrainActive — High-Ability Thinking Practice for Primary 3."**
Frame as *reasoning-skill development*, explicitly **not** an MOE/GEP test or a predictor of
selection. This is accurate, covers both GEP and HAL audiences, and avoids official-claim risk.
(Target audience and store copy confirmed: kids high-ability only, English-first.)

## 3. Recommended taxonomy
Five families, ~30 archetypes (see `brainactive_question_taxonomy.md`):
- **A Numerical** (sequence, interleaved, analogy, missing-number, comparative, cryptarithm)
- **B Logical** (ordering, odd-one-out, conditional, classification, constraint, syllogism)
- **C Pattern/Sequence** (rotation seq, 2x2 analogy, odd-one-out shapes, shape analogy, count seq, matrix)
- **D Verbal** (function analogy, place analogy, odd-word, anagram, cipher, sentence logic)
- **E Visual/Spatial** (single rotation, reflection, cube net, transformation, position, 3D rotation)

## 4. Strongest question types for the product
Rule-based, high-generative types that scale cheaply and feel "puzzle-like": number sequences
(A1–A4), figure rotation/reflection/transformation (C1, C4, C5, E1, E2, E4, E5), count/matrix
patterns (C3, C6), and ciphers (D5). These map directly to a deterministic generator.

## 5. Types hard to generate reliably
Hand-crafted / quality-critical: conditional deduction (B3), syllogisms (B6), verbal analogies
(D1–D3), sentence logic (D6). These need careful authoring and human review; do not auto-generate
unchecked. Constraint and 3D-net items (B5, E3, E6) need small curated pools.

## 6. Types that should use deterministic visual generators
All `visual_spatial` and most `pattern_sequence` items: drive an **SVG/Canvas generator** from
`visual_spec` (rotation angle, reflection axis, grid coords, SPONCS attributes, net layout).
**No raster images** — keeps rendering exact and answer-unambiguous.

## 7. Quality issues found during self-QA
- One typo fixed: a `question:` key in BA_P3_0004 (now `question`).
- All 30 re-solved independently; every answer verified present in its 4 options; explanations
  restate the rule and prove the answer; difficulty re-checked against a strong-P3 bar.
- 0 structural issues after validation (parse, option count, answer-in-options, visual-spec
  consistency, duplicate-ID check all pass).
- Minor: BA_P3_0018 (matrix) and BA_P3_0028 (side increment) are on the easier side of "hard"/
  "medium" but acceptable as accessible entry points.

## 8. Scaling 30 -> 100 -> 300
- **30 (done):** hand-authored pilot, fully QA'd. Confirms item *quality bar* and the taxonomy.
- **100:** expand generative archetypes with parameterised templates (seeds + rules) for A1–A4,
  C1–C5, E1–E5, D5; add curated pools for B1/B2, D4; keep B3/B4/B6/D1–D3/D6 hand-crafted.
- **300:** full generator pipeline + a `visual_spec` renderer; introduce mixed/ multi-step items
  (e.g. combine a rule with a distractor trap); add difficulty tuning and per-archetype volume
  targets. Introduce light metadata now (`topic`, `syllabus_tag`, `est_time_sec`, `hint`) so the
  future DB schema is painless.

## 9. Is the 30-question pilot good enough to proceed?
**Yes — conditionally.** The pilot proves we can produce original, single-answer, explainable,
P3-appropriate reasoning items across all five families with correct `visual_spec` scaffolding.
Proceed to production **after**: (a) legal disclaimer is shown in-app/store, (b) a deterministic
visual renderer is built for the `visual_spec` items, and (c) the hand-crafted verbal/logical
archetypes get a second human review pass. Do **not** treat the pilot as a content volume — it is a
*quality and architecture* validation.

---
### Files in this deliverable set
1. `revamp/research/brainactive_content_research.md`
2. `revamp/taxonomy/brainactive_question_taxonomy.md`
3. `revamp/pilot/brainactive_p3_high_ability_pilot.json`
4. `revamp/research/brainactive_p3_high_ability_research_report.md`
