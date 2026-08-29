# BrainActive — Verbal Reasoning Pilot Plan (adds to v0.4.1, 50 → 60 questions)

> **Research-only intent of this doc:** specify *exactly what to add* to the current 50-question pilot
> to demonstrate the Verbal hierarchy. **No questions are generated here.** This is the authoring spec
> for a later build step.
> Rationale references: `brainactive_verbal_reasoning_research.md`, `..._framework.md`, `..._100_allocation.md`.

---

## Current pilot verbal state (v0.4.1, 6 verbal items)
- 0005 — Verbal Analogy (function) — Explore (3.1)
- 0037 — Verbal Analogy (antonym) — Think (3.1)
- 0022 — Word Relationship / classification (noun vs action) — Think (3.2)
- 0015 — Code (shift) — Explore (3.3)
- 0038 — Code (position) — Think (3.3)
- 0016 — Verbal Deduction (1–2 clues) — Think (3.5)

**Gaps vs framework:** no VR4 (Word Manipulation/anagram), no VR5 (letter/word patterns), no
VR2 advanced classification, no VR6 multi-clue deduction, no VR7 (capped sentence completion), and
VR1 has no Challenge-tier dual relation.

---

## Proposed additions: 10 questions → pilot verbal becomes 16

| # | Skill (code) | Level | Purpose | Source evidence | Why it belongs |
|---|---|---|---|---|---|
| A1 | VR1 Verbal Analogy — function/part-whole (3.1) | Think | Strengthen analogy beyond Explore | S3, S5, S9 | Currently only Explore+Think single-relation; add a clearer function pair to firm the tier |
| A2 | VR1 Verbal Analogy — dual relation / category-to-category (3.1) | Challenge | Introduce harder analogy reasoning | S3 (set analogy) | Tests relation discovery, not vocab; the C-type flagship |
| B1 | VR2 Classification — semantic category (3.2) | Explore | Add a reasoning-based (not noun/action) classification | S7, S9, S11 | Current 0022 is surface-form; add a meaning-based one |
| B2 | VR2 Classification — two-dimension odd-one-out (3.2) | Think | Advanced classification | S11/S12 GL odd-one-out | Shows depth within VR2 |
| C1 | VR3 Code — letter↔number arithmetic (3.3) | Think | Mirror the S4 GA archetype (rule discovery) | S4, S1 | Deterministic, C-type, GEP-flavoured |
| C2 | VR3 Code — word/letter substitution code (3.3) | Challenge | Harder decode | S11/S12 GL word codes | Extends 0015/0038 upward |
| D1 | VR4 Word Manipulation — anagram (3.4) | Think | **Fill the missing VR4 skill** | S1, S5, S8 | Currently zero anagram items; framework lists 3.4 — mandatory gap-fill |
| E1 | VR5 Letter & Word Pattern — letter series (3.6) | Think | Add pattern reasoning with letters | S11/S13 letter series | Vocabulary-free, deterministic, transfers to non-verbal |
| F1 | VR6 Sentence Logic & Deduction — 3-clue (3.5) | Challenge | Advanced deduction | S1, S5, S6, S8 | Current 0016 is light; add a constraint-rich deduction |
| G1 | VR7 Sentence Completion (light, capped) (new) | Explore | Represent GEP sentence-completion, capped | S6, S9 | One B-type item only, to show the skill exists but is bounded |

---

## Principles for the (future) authoring step
1. **Vocabulary:** every item uses P3-accessible words except where the *relationship* is the challenge (C-type). No isolated-rare-word traps (avoid the FOUR/SQUARE failure mode).
2. **Distractors:** relation-plausible for analogies/classification; arithmetically/structurally near-miss for codes/patterns.
3. **Uniqueness:** each code/pattern/deduction item must have a single valid answer; verify by generation.
4. **No copying:** archetypes are drawn from sources (e.g., set analogy, letter-number square rule) but every item is original and parameterised.
5. **Progression integrity:** keep Explore→Think→Challenge→Master ordering within each skill's progression.
6. **Cap VR7:** exactly one sentence-completion item in the pilot; do not expand without review.

## Out of scope (do NOT do in this research phase)
- Do not modify `brainactive_p3_high_ability_pilot.json` (frozen at v0.4.1).
- Do not generate the 10 items now — this doc is the spec only.
- Do not touch renderer/DB/production code.

## Next step after human approval of this plan
Author the 10 items per the table, append to a **v0.5 pilot** (or a verbal-only extension set), validate, then fold the verbal allocation into the first-100 blueprint update.
