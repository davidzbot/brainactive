# BrainActive — Verbal Reasoning Skill Framework (GEP-oriented, P3 High Ability)

> Companion to `brainactive_verbal_reasoning_research.md`. Defines **7 core verbal skills** for
> BrainActive's first 100. Each skill carries: description, SG/international evidence, P3 suitability,
> HA relevance, reasoning depth, vocabulary dependency (A/B/C), difficulty progression, generation
> difficulty, and AI-vs-human note.
> We do **not** generate questions here.

---

## How to read the class column
- **C** = genuine verbal reasoning (preferred, low vocabulary dependency where possible).
- **B** = vocabulary + reasoning (use with P3-accessible words, capped).
- **A** = pure vocabulary (excluded from BrainActive).

---

## VR1 — Verbal Analogies  *(class C / sometimes B)*
- **Description:** find the relationship in `A : B` and apply it to `C : ?`. Relations: function, part-whole, category, degree, characteristic, cause-effect.
- **SG evidence:** S3 (weapons→water), S7 triangle example, S5 Word Relation, S9/S10 CogAT.
- **P3 suitability:** high — relationships are intuitive; we control vocabulary to stay P3-accessible (keep B minimal).
- **HA relevance:** high — GEP GA analogies are the most-cited verbal type.
- **Reasoning depth:** high at Challenge/Master (dual relations, e.g., both function *and* size).
- **Vocab dependency:** Mostly C; can slip to B if we use rare words (avoid).
- **Progression:** Explore = single clear relation (function/part-whole) → Think = category/characteristic → Challenge = dual-relation or abstract → Master = novel/compound relation.
- **Generation difficulty:** moderate (distractors must be relation-plausible, not just wrong words).
- **AI vs human:** AI good at generating; needs human check that distractors are *relationally* tempting and words age-appropriate.

## VR2 — Verbal Classification & Odd-One-Out  *(class C)*
- **Description:** pick the item that does/doesn't belong by a shared property; advanced = two-dimension odd-one-out.
- **SG evidence:** S7 "sensitivity towards words"; S9/S10 CogAT Verbal Classification; S11/S12 GL odd-one-out.
- **P3 suitability:** high.
- **HA relevance:** medium-high — trains category flexibility.
- **Reasoning depth:** high when the property is non-obvious (semantic field, not surface form).
- **Vocab dependency:** C (everyday words).
- **Progression:** Explore = obvious category → Think = subtle shared property → Challenge = two valid groupings, pick the stronger → Master = abstract/relational property.
- **Generation difficulty:** moderate.
- **AI vs human:** AI can generate; human must verify the "odd" reason is unique and fair.

## VR3 — Codes & Ciphers (letter/number decoding)  *(class C)*
- **Description:** decipher/encipher using a rule (shift, position-in-alphabet, letter↔number arithmetic). Subsumes GL "word/letter codes".
- **SG evidence:** S4 (letter↔number square rule), S1 (cipher), S5 Decoding.
- **P3 suitability:** high — pure structure, no vocabulary.
- **HA relevance:** high — this is the verbal type most *distinct* from English tuition and most "thinking-skill".
- **Reasoning depth:** high (discover the rule, then apply).
- **Vocab dependency:** none (C).
- **Progression:** Explore = simple shift → Think = position-based rule → Challenge = arithmetic rule (S4-style) → Master = two-step/mixed rule.
- **Generation difficulty:** low (deterministic) — **strong AI candidate**.
- **AI vs human:** AI reliable; human spot-checks arithmetic and uniqueness of decode.

## VR4 — Word Manipulation (anagrams, hidden words, move-a-letter)  *(class C)*
- **Description:** rearrange scrambled letters (anagram), find a hidden word inside a string, or move one letter to form a new word.
- **SG evidence:** S1, S5, S8 (anagram explicitly a GA type); S11/S13 (hidden word, move-a-letter in GL).
- **P3 suitability:** high — playful, structural.
- **HA relevance:** medium-high — "think flexibly", a stated GEP aim (S8).
- **Reasoning depth:** medium-high; can be a warm-up to VR3.
- **Vocab dependency:** C (uses given letters, not recall).
- **Progression:** Explore = short anagram → Think = hidden word in a phrase → Challenge = move-a-letter transformation → Master = chained transformation.
- **Generation difficulty:** low-moderate (need a valid word list + verifier).
- **AI vs human:** AI good; human verifies the target word is P3-known and unique.
- **Gap note:** **v0.4.1 currently has ZERO VR4 items** despite the framework listing 3.4 — must be added (see pilot plan).

## VR5 — Letter & Word Patterns (letter series, word-number codes)  *(class C)*
- **Description:** continue/complete an alphabet-sequence or letter-pattern; combine letters with numbers in a code.
- **SG evidence:** under-catalogued in SG sources, but present (S4 decoding). Strong in UK GL (S11/S12/S13 letter series, alphabet sequences).
- **P3 suitability:** high.
- **HA relevance:** medium — trains systematic pattern-seeking (transferable to non-verbal).
- **Reasoning depth:** medium-high.
- **Vocab dependency:** none (C).
- **Progression:** Explore = simple +1/-1 letter step → Think = skip/alternating → Challenge = rule with a twist → Master = combined letter+number pattern.
- **Generation difficulty:** low (deterministic).
- **AI vs human:** AI reliable; human checks pattern uniqueness.

## VR6 — Sentence Logic & Verbal Deduction  *(class C)*
- **Description:** read 2–3 clues and deduce a must-be-true fact (ordering, membership, mapping). Distinct from cloze.
- **SG evidence:** S1 (inference from passage), S5/S6 (Logic: deduce conclusion), S8 (conclusion from statements).
- **P3 suitability:** high with simple wording.
- **HA relevance:** high — pure reasoning, the heart of "thinking skills".
- **Reasoning depth:** high; can exceed analogy at Challenge/Master (multiple constraints).
- **Vocab dependency:** C (clues use simple words).
- **Progression:** Explore = 1-clue ordering → Think = 2-clue → Challenge = 3-clue with a conflict to resolve → Master = open constraint-satisfaction.
- **Generation difficulty:** moderate (must be solvable & unique).
- **AI vs human:** AI good at drafting; human must verify unique solution and no hidden assumptions.

## VR7 — Sentence Completion (light, capped)  *(class B — use sparingly)*
- **Description:** choose the word that fits a sentence by context/grammar.
- **SG evidence:** S6, S9/S10 CogAT.
- **P3 suitability:** medium — risk of becoming vocabulary test.
- **HA relevance:** low-medium.
- **Reasoning depth:** low-medium (context inference, but vocabulary-gated).
- **Vocab dependency:** B (high).
- **Progression:** Explore = obvious context → Think = needs grammar cue → (cap beyond Think).
- **Generation difficulty:** moderate.
- **AI vs human:** AI can; **we deliberately cap this skill** to protect product identity (not English tuition).

---

## Skill → existing framework mapping
| BrainActive skill | Prior framework code | Tier |
|---|---|---|
| VR1 Verbal Analogies | 3.1 | 1 |
| VR2 Classification/Odd-One-Out | 3.2 | 1 |
| VR3 Codes & Ciphers | 3.3 (extend) | 1 |
| VR4 Word Manipulation | 3.4 | 2 |
| VR5 Letter & Word Patterns | 3.4 (extend) / 3.6 new | 2 |
| VR6 Sentence Logic & Deduction | 3.5 (extend) | 1 |
| VR7 Sentence Completion (light) | — (new, capped) | 2 |

## Cross-domain note
VR3/VR4/VR5 are **vocabulary-light** and reinforce the same structural reasoning as the non-verbal and logic domains — this is the glue that makes BrainActive a *coherent thinking-skills* product rather than a GEP mock or an English app.
