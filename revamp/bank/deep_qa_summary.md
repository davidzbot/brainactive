# Deep QA Summary — GEP/HA Production Quality Audit

**Date:** 2026-08-29
**Scope:** All 1000 questions in `brainactive_p3_question_bank.json` (v0.6-local)
**Method:** AI-reasoning audit — each question solved independently by an AI agent reasoning through it (not algorithmic parsing), then compared with stored answer/explanation. GEP/HA quality rated against official GEP Selection Test standards.

**Tracker:** `bank/deep_qa_tracker.json` (1000 entries, deduplicated)

---

## 1. Research: Singapore GEP/HA Standards

### GEP Selection Test Format
- **Day 1:** English + General Ability (Verbal Reasoning) — ~2.5 hours, 30-40 questions
- **Day 2:** Math + General Ability (Non-Verbal Reasoning) — ~2.5 hours, 30-40 questions
- **GA is IQ-like**, not syllabus-based. Tests *capacity to learn*, not content knowledge.

### GEP GA Question Types (from Think Academy, Joyous Learning, FA, Learning Sense)
**Verbal (GA1):**
- Word Analogies (relationship between word pairs, e.g., "Cannon:rifle:pistol : river:stream:?")
- Anagrams (unscramble letters)
- Decoding/Ciphers (letter-number codes, e.g., A=1, B=2; shift rules)
- Logic (deduce conclusion from given rules)
- Sentence Completion (context/grammar inference — capped for BrainActive)

**Non-Verbal (GA2):**
- Pattern Recognition (sequences, matrices, odd-one-out)
- Spatial Reasoning (rotation, reflection, cube nets, 3D orientation)
- SPONCS: Shape, Position, Orientation, Number, Colour, Size
- Logical Reasoning with visual elements

### GEP Quality Benchmarks
- Questions must be **self-contained** (all info in the question)
- **Single unambiguous answer** (no multiple valid interpretations)
- **Discoverable rule** (child can figure out the pattern)
- **Plausible distractors** (relationally wrong, not random)
- **Explanation restates the rule AND proves the answer**
- **P3-appropriate vocabulary** (no obscure words)
- **Non-routine** (reasoning bottleneck, not arithmetic)

---

## 2. Audit Results

### 2.1 Answer Accuracy
| Metric | Count | % |
|--------|------:|--:|
| **Answers match** | 789 | 78.9% |
| **Answers mismatch** | **11** | **1.1%** |
| **Visual-dependent** (can't solve from text) | 149 | 14.9% |
| **Not audited** (semantic-only) | 51 | 5.1% |

### 2.2 GEP Quality Distribution
| Quality | Count | % | Notes |
|---------|------:|--:|-------|
| **Production** | 653 | 65.3% | Meets all GEP standards |
| **Acceptable** | 44 | 4.4% | Minor issues, usable |
| **Below-standard** | 297 | 29.7% | Significant quality issues |
| **Reject** | 6 | 0.6% | Fundamentally flawed |

### 2.3 Explanation Quality
| Quality | Count | % |
|---------|------:|--:|
| Good | 843 | 84.3% |
| Weak | 71 | 7.1% |
| Acceptable | 73 | 7.3% |
| Poor/Bad | 13 | 1.3% |

---

## 3. Critical Issues Found

### 3.1 WRONG ANSWERS (6 reject — letter pattern errors)

All in skill 3.6 (letter patterns). The generator computes letter positions modulo 26 but has arithmetic errors:

| ID | Question | Stored | Correct | Issue |
|----|----------|--------|---------|-------|
| BA_P3_0516 | Q,S,V,Z,___ (gaps +2,+3,+4) | C (V) | **E** | Z(26)+5=31 mod26=5=E, not V(22) |
| BA_P3_0522 | Q,R,T,W,___ (gaps +1,+2,+3) | C (Z) | **A** | W(23)+4=27 mod26=1=A, not Z(26) |
| BA_P3_0536 | C,E,H,L,___ (gaps +2,+3,+4) | A (P) | **Q** | L(12)+5=17=Q, not P(16) |
| BA_P3_0576 | O,Q,T,X,___ (gaps +2,+3,+4) | C (T) | **B** | X(24)+4=28 mod26=2=B, not T(20) |
| BA_P3_0583 | Q,T,W,Z,___ (gaps +3,+3,+3) | A (W) | **C** | Z(26)+3=29 mod26=3=C, not W(23) |
| BA_P3_0647 | Q,T,W,Z,___ (same as 0583) | D (W) | **C** | Same error as 0583 |

### 3.2 EQUAL-WEIGHT / EQUAL-MARBLE SYSTEMS (6 mismatch — no unique answer)

Skills 1.3 (weight systems) and 1.4 (chain comparisons) where all values are equal, making the answer arbitrary:

| ID | Skill | Issue |
|----|-------|-------|
| BA_P3_0122 | 1.3 | All weights equal — any option is correct |
| BA_P3_0127 | 1.3 | All weights equal — any option is correct |
| BA_P3_0128 | 1.3 | All weights equal — any option is correct |
| BA_P3_0142 | 1.3 | All weights equal — any option is correct |
| BA_P3_0143 | 1.3 | All weights equal — any option is correct |
| BA_P3_0180 | 1.4 | All marble counts equal — no unique "most" |

### 3.3 TRIVIAL CONSTRAINT QUESTIONS (30 below-standard)

Skill 2.2 constraint questions where the answer is directly stated in the question text. Example:
> "Dee sits at the right end. Who sits at the right end?" → Answer: Dee (zero reasoning required)

Affected IDs: BA_P3_0279, 0303, 0319, 0320, 0324, 0334, 0336, 0338, 0359, 0361, 0363, 0379, 0382, 0401, 0406, 0411, 0418, 0423, 0436, 0439, 0440, 0445, 0457, 0468, 0477, 0479, 0488, 0489, 0496, 0505

### 3.4 FICTIONAL NUMBER CONTRADICTIONS (11 acceptable)

Conditional questions: "If a number is even, it is coloured blue. The number X is NOT blue." When X is actually even (12, 16, 18, 20, 22, 24, 26, 28), the contrapositive logic is correct but contradicts real-world math knowledge, confusing P3 children.

### 3.5 EXCESSIVE DUPLICATION (biggest systemic issue)

| Skill | Template | Duplicates |
|-------|----------|-----------|
| 6.6 Pattern Application | Machine rule 1→4, 2→7, 3→10 | 16 of 17 identical rule |
| 6.5 Make List | 3-letter codes from {A,B,C} | 11 of 23 identical |
| 6.4 Draw Diagram | Tree-gap (n-1)×gap | 22 of 23 identical formula |
| 6.3 Before/After | Amy/Ben sticker transfer | 22 of 26 near-identical |
| 2.2 Constraint | 4-name seating permutations | ~30 near-identical |
| 3.4 Anagram | STAR→RATS reversal | 6 times |
| 3.4 Anagram | STONE→TONES | 4 times |
| 2.4 Classification | Animal odd-one-out | ~15 times |
| 2.3 Conditional | Hot→swim→happy chain | 5 times |
| 3.7 Sentence Completion | Rain→umbrella | 3 times |

### 3.6 VISUAL QUESTIONS — TEXTADEQUACY (9 below-standard)

7 transformation questions have shape-name/side-count mismatches:
> "pentagon(3)" when pentagon has 5 sides; "triangle blue(6)" when triangle has 3 sides

Affected IDs: BA_P3_0677, 0692, 0701, 0705, 0728, 0764, 0908

### 3.7 ANSWER GIVEN IN EXAMPLE (8 verbal)

Questions where the example literally gives away the answer:
> "If STONE → TONES, what is FLAME → ?" (answer: LAMEF, which follows the same move-last-letter rule shown in the example)

Affected IDs: BA_P3_0557, 0605, 0612, 0619, 0623, 0625, 0640, 0666

---

## 4. Production Filtering Decision

Per instruction: *"check if easy fix, otherwise put a flag to filter out those which are not production quality. we only need production good questions."*

### Easy fixes applied (kept)
- **19 verbal logic name options** (skill 3.5): spurious `1` suffix stripped (`Ben1`→`Ben`, `Ali1`→`Ali`, `Cai1`→`Cai`).
- **141 option values** (skills 6.1/6.2/6.5): cast non-string option text to string (e.g., `27`→`"27"`).

### NOT easy fixes → flagged & filtered out
- **6 letter-pattern questions** (skill 3.6): corrupted option text (`V1`, `[`, `]`, `^`, `W1`) + wrong answers. Needs generator regeneration, not a safe patch.
- **6 equal-weight / equal-marble questions** (skills 1.3, 1.4): no unique answer. Needs weight regeneration.
- **297 below-standard** (mostly duplication / trivial / answer-in-example): needs regeneration with variety.
- **11 answer mismatches** (6 letter-pattern + 5 equal-weight/marble): covered above.
- **149 unverifiable visual questions**: audit could not solve from text — need separate image-based review.

### Deliverables
- **`brainactive_p3_question_bank_production.json`** — 548 production-good questions (504 strict production + 44 acceptable). All have clean options, valid answers, `production_ready: true`.
- **`brainactive_p3_question_bank_flagged.json`** — full 1000 questions, each tagged with `production_ready` and `qa_flags` listing why filtered (e.g., `not_production_quality:below-standard`, `needs_visual_review`, `content_corruption:letter_option_corrupted`, `easy_fixed:strip_trailing_digit`).
- **`deep_qa_tracker.json`** — per-question audit record (my solution, stored answer, match, gep_quality, issues).

### Production Bank Composition (548)
| Domain | Count |
|--------|------:|
| logical_reasoning | 150 |
| visual_spatial | 151 |
| numerical_reasoning | 79 |
| verbal_reasoning | 79 |
| pattern_abstract | 51 |
| problem_solving | 38 |

| Level | Count |
|-------|------:|
| Think | 328 |
| Explore | 95 |
| Challenge | 76 |
| Master | 49 |

> Note: 180 validated visual questions (audit solved them via figure description) are **kept** with flag `has_visual_review_recommended`. The 149 truly unverifiable visual questions are **excluded**. If stricter curation is wanted, drop the 44 `acceptable` and/or the 180 visual-recommended → leaves ~305 strict text-verified production questions.

---

## 5. Recommendations (for future regeneration)

### Must Fix (generator bugs)
1. **Skill 3.6 letter-pattern generator** — produces corrupted option text (out-of-range ASCII) and off-by-one answers. Regenerate with correct mod-26 letter mapping.
2. **Skill 1.3/1.4 weight/marble generators** — ensure weights are distinct (currently sometimes all equal → no unique answer).
3. **Skill 3.5 name generator** — stop appending spurious `1` to names (already patched in output, but fix at source).

### Should Fix (quality issues)
4. **Deduplicate heavily** — 82+ near-identical questions across skills 6.3-6.6 and 2.2
5. **Rewrite 30 trivial constraint questions** (skill 2.2) — answer must not be directly in the question
6. **Fix 11 fictional number contradictions** (skill 2.3) — use numbers that are actually odd
7. **Improve 61 weak explanations** — each must restate the rule AND prove the answer
8. **Fix 7 shape-name mismatches** (visual transformation) — correct side counts

### Nice to Have
9. **Add variety to pattern application** (skill 6.6) — diverse rules, not just 1→4, 2→7, 3→10
10. **Add variety to make list** (skill 6.5) — different letter sets and constraints
11. **Add variety to draw diagram** (skill 6.4) — different scenarios (lampposts, fences, stairs)
12. **Add variety to before/after** (skill 6.3) — different characters and transfer scenarios

---

## 6. Residual Caveats

- **149 unverifiable visual questions** excluded from production bank — need image-based review before inclusion.
- **AI1 independent QA** still required before production import (this audit is a pre-AI1 deep pass).
- The audit agent's reasoning was used, but edge cases (especially near-boundary numerical and visual) may need human verification.
- The production bank is a **curated subset**, not a full replacement — regeneration with fixed generators is needed to reach 1000 production-quality questions.
