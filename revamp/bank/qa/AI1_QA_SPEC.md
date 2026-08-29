# AI1 Independent QA Specification

This document defines how an **independent AI model (AI1)** should audit every question in
`revamp/bank/brainactive_p3_question_bank.json` before anything is imported into Supabase or
shown to a child. AI1 must be a *separate* pass from the generator (Hy3) — it does not see the
generation rationale, only the question as a child would.

## Inputs AI1 receives
- The question object: `question`, `options`, `answer`, `explanation`, `level`, `domain`, `skill`, `archetype`, `tags`, `visual_spec`, `image_path`.
- The child persona: a strong Singapore Primary 3 student, English-comfortable, not yet in secondary school. No GEP/mock framing.

## Per-question checks (output one verdict + notes per item)

1. **Answer correctness** — Solve the item independently. Is `answer` the only correct option? Flag if the marked answer is wrong or if a distractor is also correct.
2. **Distractor correctness** — Are the 3 wrong options *plausible* (near-misses that test the reasoning, not random)? Flag distractors that are impossible, give-aways, or themselves correct.
3. **Uniqueness** — Is there exactly one defensible answer? Flag ambiguity (two readings, two valid answers, "cannot tell" that is actually determinable or vice-versa).
4. **Reasoning quality** — Does the item test *reasoning*, not recall? Flag items whose difficulty comes mainly from obscure vocabulary, big numbers, or tricks.
5. **P3 appropriateness** — Is the wording, context and maths within a strong P3 student's reach? Flag anything needing P4+ syllabus (e.g., area of non-rectangles, algebra, long division) or unfamiliar SG context.
6. **Difficulty / level fit** — Given `level` (Explore/Think/Challenge/Master), is the reasoning complexity right?
   - Explore = one clear rule. Think = multi-step / first constraints. Challenge = complex / 3+ clues / spatial. Master = must *decide how to solve*, non-routine.
   - Flag if the item is levelled too easy or too hard for its stated `level`.
7. **Skill classification** — Does `domain` + `skill` + `archetype` match what the item actually tests? Flag misclassified items.
8. **Visual consistency** (only if `visual_required`) — Does the rendered SVG in `revamp/bank/images/<id>.svg` match `visual_spec` and the question? Are labels readable, no clipping, answer choices distinguishable? Flag mismatches.
9. **Explanation correctness** — Is `explanation` true and child-friendly? Does it reveal the *reasoning*, not just restate the answer?
10. **Potential ambiguity / copy risk** — Could the wording be read two ways? Does it reproduce any known commercial/online question (reject if so — must be original).

## Output format AI1 should produce
- A summary table: `id | verdict (PASS/FAIL/REVIEW) | check that failed | note`.
- Aggregate counts: PASS / FAIL / REVIEW.
- A short list of *systemic* issues (e.g., "verbal items lean on vocabulary", "Master tier missing", "reflection items need a clearer mirror axis label").
- NO fixes — AI1 only reports. A human then decides accept / reject / re-author.

## Hard rules for AI1
- Do NOT lower the bar because an item is "from the validated baseline". Re-audit all 100.
- Do NOT approve an item that depends on vocabulary the P3 child likely lacks (flag it instead).
- Do NOT approve a visual item whose SVG does not match the question.
- Originality is mandatory: any sign of copied wording = REJECT.

## Gate
Only after AI1 returns a clean PASS/REVIEW profile (FAILs addressed by re-generation) and a human
confirms, may the bank proceed to Supabase import. Until then: JSON only, no DB, no publish.
