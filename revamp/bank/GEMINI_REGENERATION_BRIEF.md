# Gemini Regeneration Brief — BrainActive P3 High-Ability Question Bank

**Purpose:** Regenerate high-quality questions for 9 specific skills whose current generators
produced bugs, duplication, or contradictions. You will produce a JSON file of new questions
that we will merge into the bank, replacing all existing questions for these skills.

---

## 1. Product Background (read this first)

**Product:** BrainActive — a reasoning-practice app for **Primary 3 (age 9) high-ability / GEP-track**
children in Singapore. Positioning: *"Build Thinking Skills for Primary 3 High Ability"*.

**What it is NOT:** not generic brain games, not English tuition, not a GEP mock exam, not syllabus
drilling. It is **thinking-skills practice** (the same reasoning family as the GEP Selection Test).

**GEP Selection Test context (Singapore):**
- Two days; each day ~2.5 hours with a General Ability (GA) paper of ~30–40 questions.
- GA is IQ-like, not syllabus-based — it tests *capacity to learn / reason*, not content knowledge.
- **Verbal GA:** word analogies, anagrams, decoding/ciphers, logic.
- **Non-Verbal GA:** pattern recognition, spatial reasoning, SPONCS (Shape, Position, Orientation,
  Number, Colour, Size), logical reasoning with visual elements.
- Good questions share these traits: **self-contained**, **single unambiguous answer**,
  **discoverable rule**, **plausible (relationally wrong) distractors**, and an **explanation that
  restates the rule AND proves the answer**.

**Audience:** bright 9-year-olds. Use **P3-appropriate vocabulary and numbers**. Questions must be
**non-routine** (the reasoning is the bottleneck, not arithmetic).

---

## 2. Quality Bar (every generated question MUST satisfy)

1. Self-contained — all needed information is in the question text.
2. Exactly one correct answer; the answer is unambiguous.
3. The rule/relationship is discoverable by a bright P3 child from the given info.
4. Distractors are *relationally* wrong (a plausible mistake), not random.
5. `explanation` restates the rule AND shows why the answer is correct.
6. Clean option text — **never** produce garbage like `[`, `]`, `^`, `_`, or names with a trailing
   digit such as `Ben1`. Option texts must be ordinary words/letters/numbers.
7. Diverse — within each skill, avoid near-duplicate questions (different scenarios, numbers,
   characters, rules). Heavy duplication is the #1 current defect.
8. P3-appropriate language and arithmetic.

---

## 3. Output Schema (JSON)

Produce a file `regenerated_questions.json` containing a JSON **array** of question objects.
Each object uses exactly these fields (omit `id`, `qa_status`, `provenance`, `image_path` — we assign
those when merging):

```json
{
  "domain": "numerical_reasoning",        // one of: numerical_reasoning, logical_reasoning,
                                          // verbal_reasoning, problem_solving
  "skill": "1.3",                          // the skill code (see section 5)
  "archetype": "weight_system",            // short snake_case tag describing the task
  "level": "Think",                        // Explore | Think | Challenge  (see distribution below)
  "difficulty": "medium",                  // easy | medium | hard
  "question_type": "multiple_choice",
  "question": "A triangle and a square together weigh 11 ...",
  "options": [                             // EXACTLY 4 options, ids A–D, distinct texts
    {"id": "A", "text": "triangle"},
    {"id": "B", "text": "square"},
    {"id": "C", "text": "circle"},
    {"id": "D", "text": "cannot tell"}
  ],
  "answer": "B",                           // the LETTER whose option text is the correct answer
  "explanation": "Add the three pair-weights ... so the square (6) is heaviest.",
  "reasoning": "Solving a small weight system by combining equations.",
  "tags": ["p3", "high_ability", "numerical", "deduction"],
  "visual_required": false,                // these 9 skills are non-visual -> false
  "visual_spec": null
}
```

**Critical correctness rules for the schema:**
- `options` must have **exactly 4** entries with ids `A`,`B`,`C`,`D` and **distinct** `text` values.
- `answer` must be one of `A`/`B`/`C`/`D`, and `options[answer_index].text` must equal the intended
  correct answer.
- For letter-pattern questions (skill 3.6), every option `text` must be a **single clean A–Z letter**.
- For name/logic questions, option text must be a clean name with **no trailing digit**.
- `level` distribution across the whole output: roughly **50% Think, 25% Explore, 25% Challenge**.

---

## 4. Regeneration Scope & Targets

Replace **ALL** existing questions for these 9 skills. Produce exactly these counts:

| Skill | Domain | Target count |
|------:|--------|-------------:|
| 1.3  | numerical_reasoning | 40 |
| 1.4  | numerical_reasoning | 20 |
| 2.2  | logical_reasoning    | 40 |
| 2.3  | logical_reasoning    | 35 |
| 3.6  | verbal_reasoning     | 20 |
| 6.3  | problem_solving      | 30 |
| 6.4  | problem_solving      | 30 |
| 6.5  | problem_solving      | 30 |
| 6.6  | problem_solving      | 30 |
| **Total** | | **275** |

(The existing bank had duplication and bugs in exactly these skills; regenerating them fresh at these
counts and merging will give a clean, diverse, production-ready set.)

---

## 5. Per-Skill Specification (current bug → required fix → good example)

### Skill 1.3 — Numerical: weight / balance system
- **Tests:** deduce individual weights from pair-weights (systems of equations lite).
- **Current bug:** the three shape weights are drawn independently `randint(2,6)`, so they can be
  **equal** → no unique heaviest/lightest (audit found 5 such "no unique answer" questions).
- **Fix:** the three weights MUST be **distinct**. Vary which shape is asked (heaviest/lightest),
  vary the pair combinations shown, vary the numbers.
- **Good example:**
  ```
  Q: A triangle and a square together weigh 11. A square and a circle together weigh 9.
     A triangle and a circle together weigh 8. Which shape is heaviest?
  Options: triangle / square / circle / cannot tell
  Answer: square   (t=s+c? solve: tri=5, sq=6, circ=3 → square heaviest)
  Explanation: The three pair-sums total 28 = 2×(tri+sq+circ), so all three = 14.
     circle = 14−11 = 3, triangle = 14−9 = 5, square = 14−8 = 6. Square is heaviest.
  ```

### Skill 1.4 — Numerical: chain comparison
- **Tests:** chain several "more/fewer" comparisons into a full order.
- **Current bug:** only 3 such questions exist (under-represented), and the arithmetic can produce a
  **tie** (no unique maximum). Only one scenario (marbles).
- **Fix:** ensure the three quantities are **distinct**; vary scenarios (cards, sweets, stickers,
  counters), vary relations (more/fewer), vary the asked extreme.
- **Good example:**
  ```
  Q: Ben has 3 more cards than Cai. Cai has 4 fewer than Dan. Dan has 12 cards. Who has the most?
  Options: Ben / Cai / Dan / cannot tell
  Answer: Dan   (Dan 12, Cai 8, Ben 11)
  Explanation: Dan = 12. Cai = 12−4 = 8. Ben = 8+3 = 11. Dan (12) has the most.
  ```

### Skill 2.2 — Logical: constraint placement
- **Tests:** place fixed positions, then apply constraints to fix every seat/position.
- **Current bug:** clues often **directly state the answer** for the asked seat (e.g., "A is at the
  left end" then asks "who is at the left end?") → trivial, zero reasoning. Audit found 30 such.
- **Fix:** **never** ask for a position whose occupant is explicitly given in the clues. The asked
  position must require inference. Use 4–5 people, varied arrangements (row, circle, relative order).
- **Good example:**
  ```
  Q: Ali, Ben, Cai and Dee sit in a row of four. Dee sits at the left end. Ben is not at either end.
     Cai sits immediately to the right of Ben. Who sits in the second seat from the left?
  Options: Ali / Ben / Cai / Dee
  Answer: Ben   (Dee=1, Ben & Cai adjacent and not at ends → Ben=2, Cai=3, Ali=4)
  Explanation: Dee is seat 1. Ben and Cai must be seats 2–3 (adjacent, not at ends), so Ben=2, Cai=3,
     leaving Ali=4. Second seat = Ben.
  ```

### Skill 2.3 — Logical: conditional / contrapositive
- **Tests:** draw a valid must-be-true conclusion (contrapositive or transitive chain).
- **Current bug:** the branch "if even→blue; N is NOT blue" picks N from a range that may be **even**,
  contradicting the rule (a real even number WOULD be blue) → invalid conclusion (fictional
  contradiction). Audit flagged 11.
- **Fix:** when the rule is "if P then Q" and the clue is "X is not Q", ensure X genuinely satisfies
  "not Q" in the real world (e.g., pick an **odd** number for the "not blue" case). The transitive
  chain branch (hot→swim→happy) is fine.
- **Good example:**
  ```
  Q: If a number is a multiple of 5, it is coloured green. The number 17 is not green.
     What can we conclude?
  Options: 17 is a multiple of 5 / 17 is not a multiple of 5 / 17 is green / cannot tell
  Answer: 17 is not a multiple of 5
  Explanation: Rule: multiple of 5 → green. 17 is not green, so by the contrapositive it is not a
     multiple of 5. (17 is indeed not a multiple of 5, so the premise is consistent.)
  ```

### Skill 3.6 — Verbal: letter pattern
- **Tests:** find the rule in a letter series and extend it.
- **Current bug (multiple):** (a) text says "gap grows by 1 each step" but gaps may be constant
  (`[2,2,2]`,`[3,3,3]`) → contradiction; (b) the next gap reuses the *last* gap instead of
  *last+1*, so off-by-one for increasing gaps; (c) on overflow it subtracts → wrong/backwards answer;
  (d) distractors compute `chr(91+)` → garbage options like `[ ] ^`, and padding yields `V1`.
- **Fix:** choose ONE clear, consistent rule (constant gap, or growing +2,+3,+4→next +5, or
  alternating). Compute the next letter **correctly** (apply the actual next gap; keep within A–Z by
  either wrapping with A=1..Z=26 modulo math OR choosing start/gaps so no wrap is needed). Ensure all
  4 options are **valid distinct A–Z letters** and the correct one is included. Question text must
  state the rule accurately (don't claim "grows by 1" if it's constant).
- **Letter math:** A=1 … Z=26. To wrap: `pos = ((raw-1) % 26) + 1`.
- **Good example (no wrap):**
  ```
  Q: A letter pattern goes: A, C, E, G, ___. Each step moves 2 letters forward. What comes next?
  Options: I / H / K / M
  Answer: I   (G=7, +2 = 9 = I)
  Explanation: A(1)→C(3)→E(5)→G(7); each step +2, so next is 7+2 = 9 = I.
  ```
- **Good example (with wrap, done correctly):**
  ```
  Q: A letter pattern goes: X, Z, B, D, ___. Each step moves 2 letters forward (wrapping A after Z).
     What comes next?
  Options: F / E / G / H
  Answer: F   (D=4, +2 = 6 = F)
  Explanation: X(24)→Z(26)→B(2)→D(4); +2 each step, so next is 4+2 = 6 = F.
  ```

### Skill 6.3 — Problem Solving: before/after (constant difference)
- **Tests:** heuristic — a transfer changes the gap by twice the amount moved.
- **Current bug:** single template (Amy/Ben stickers) varied only by numbers → heavy duplication
  (22 of 26 near-identical). Gap can be 0 → ambiguous "who has more".
- **Fix:** diverse scenarios (stickers, sweets, marbles, coins, books, beads), 2–3 people, varied
  operations (give / take / buy / eat / lose), and a clear single winner (or treat "equal" as a valid
  distinct answer choice only when intended). Explain the "transfer reduces gap by 2×" heuristic.
- **Good example:**
  ```
  Q: Amy has 5 more beads than Ben. Ben gives Amy 2 beads. Now who has more beads, and by how many?
  Options: Amy, by 1 / Ben, by 1 / They are equal / Amy, by 9
  Answer: Amy, by 1
  Explanation: Amy led by 5. When Ben gives Amy 2, the gap shrinks by 2×2 = 4, so Amy now leads by 1.
  ```

### Skill 6.4 — Problem Solving: draw a diagram (count gaps, not objects)
- **Tests:** heuristic — draw it; count the *intervals* between objects, not the objects.
- **Current bug:** always "trees in a line, (n−1)×gap" → heavy duplication (22 of 23 identical).
- **Fix:** diverse "count intervals" scenarios: fence posts, lamp posts, stairs, beads on a string,
  buses stopping, dots on a line. Vary line vs **circle** (circle has n gaps for n objects). Keep the
  core heuristic: draw it, count gaps.
- **Good example (line):**
  ```
  Q: 6 fence posts are placed in a row, 2 metres apart. How long is the fence from the first to the
     last post?
  Options: 10 m / 12 m / 6 m / 8 m
  Answer: 10 m   (5 gaps × 2 m)
  Explanation: 6 posts have 5 gaps between them; 5 × 2 = 10 m.
  ```
- **Good example (circle):**
  ```
  Q: 8 bushes are planted evenly around a circular pond, 3 metres apart. What is the distance around
     the pond?
  Options: 24 m / 21 m / 27 m / 8 m
  Answer: 24 m   (8 gaps × 3 m, because a circle has as many gaps as objects)
  Explanation: Around a circle, 8 bushes make 8 equal gaps; 8 × 3 = 24 m.
  ```

### Skill 6.5 — Problem Solving: make a list (organised counting)
- **Tests:** heuristic — make an organised list of all possibilities.
- **Current bug:** always 2–3 letters from {A,B,C}, answer = len^len (e.g., 27) → duplication
  (11 of 23 identical).
- **Fix:** diverse counting problems: codes with/without repetition, permutations of a word, choosing
  combinations, outfits (shirt+pants), paths. Vary the rule (repeat allowed vs not; order matters vs
  not). Ensure a child can list systematically.
- **Good example (repeat allowed):**
  ```
  Q: How many 2-letter codes can you make using A, B, C if you may repeat a letter?
  Options: 9 / 6 / 3 / 12
  Answer: 9   (3 choices for first × 3 for second = 9)
  Explanation: List them: AA, AB, AC, BA, BB, BC, CA, CB, CC → 9 codes.
  ```
- **Good example (no repeat / outfits):**
  ```
  Q: Mei has 3 shirts and 2 pairs of pants. How many different outfits can she make?
  Options: 6 / 5 / 3 / 12
  Answer: 6   (3 × 2)
  Explanation: Each of the 3 shirts pairs with each of the 2 pants: 3 × 2 = 6 outfits.
  ```

### Skill 6.6 — Problem Solving: pattern application (discover & apply a rule)
- **Tests:** heuristic — find the hidden rule from examples, apply it to a new case.
- **Current bug:** only ONE rule (input×3+1, i.e., 1→4, 2→7, 3→10) → 16 of 17 identical.
- **Fix:** **diverse rules**, e.g. ×2+1, ×3−1, +n then ×2, square+1, Fibonacci-like, alternating
  operations, position-based. Show 2–3 example input→output pairs that make the rule clear, then ask
  for a new input. Ensure the rule is uniquely determinable and the correct output is among options.
- **Good example:**
  ```
  Q: A machine follows this rule: 2 → 5, 3 → 7, 4 → 9. What does 7 become?
  Options: 15 / 14 / 16 / 13
  Answer: 15   (rule: output = input × 2 + 1)
  Explanation: 2→5 (2×2+1), 3→7 (3×2+1), 4→9 (4×2+1); so 7 → 7×2+1 = 15.
  ```

---

## 6. Output Instructions

1. Create **`regenerated_questions.json`** — a JSON array of 275 question objects per section 3 & 4.
2. Follow the schema exactly. Omit `id`, `qa_status`, `provenance`, `image_path` (we assign on merge).
3. `visual_required` = `false`, `visual_spec` = `null` for all (these skills are non-visual).
4. Every `answer` letter must match the correct option's text. Every option text clean (no symbols,
   no trailing digits on names, single A–Z letters for 3.6).
5. Within each skill, maximise diversity (different scenarios/numbers/characters/rules); no two
   questions should be near-duplicates.
6. Double-check each question: is the answer unique? Is the explanation correct and complete? Is the
   vocabulary P3-appropriate?
7. Return only the JSON file (and a one-line count summary). Do not modify other files.

---

## 7. Reference Files (you may read these for context)

- `revamp/bank/generate_1000.py` — current generators (the buggy functions for these 9 skills are
  `g_num_system`, `g_num_chain`, `g_log_constraint`, `g_log_cond`, `g_ver_letterpat`, `g_ps_ba`,
  `g_ps_patternapp`, `g_ps_draw`, `g_ps_list`). Use as examples of what NOT to replicate.
- `revamp/bank/brainactive_p3_question_bank.json` — the existing bank; inspect a few entries to match
  the exact field style/voice of `question`, `explanation`, `reasoning`, `tags`.
- `revamp/bank/deep_qa_summary.md` — the audit report; sections 3 (critical issues) and 4 (fix
  decisions) show the exact defects found per skill.
