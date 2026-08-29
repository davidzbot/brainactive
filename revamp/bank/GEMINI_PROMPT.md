# Prompt for Gemini (copy-paste after attaching GEMINI_REGENERATION_BRIEF.md)

Please read the attached file `GEMINI_REGENERATION_BRIEF.md` in full — it contains the product
background, quality bar, exact JSON output schema, per-skill bug descriptions, required fixes, and
good examples.

Your task: regenerate **275** new, high-quality reasoning questions for the 9 skills listed in the
brief (skills 1.3, 1.4, 2.2, 2.3, 3.6, 6.3, 6.4, 6.5, 6.6), at the target counts given, following
ALL rules in sections 2–6 of the brief.

Key requirements (do not skip):
- Output a single JSON file `regenerated_questions.json`: a JSON array of 275 question objects.
- Use EXACTLY the schema in section 3. Omit `id`, `qa_status`, `provenance`, `image_path`.
- `options` = exactly 4 entries (ids A–D), distinct texts. `answer` = the correct letter, matching the
  correct option's text.
- `visual_required` = false, `visual_spec` = null for every question.
- For skill 3.6 every option text must be a single clean A–Z letter; never emit garbage like
  `[ ] ^ _` or names with a trailing digit (e.g. `Ben1`).
- For each skill, fix the specific bug described in section 5 and maximise diversity (no near-duplicates).
- Level distribution across the whole output: ~50% Think, ~25% Explore, ~25% Challenge.
- Every explanation must restate the rule AND prove the answer. Keep vocabulary P3-appropriate.
- Before finishing, self-check: is each answer unique? is each explanation correct? are options clean?

Return the JSON file and a one-line summary of how many questions you produced per skill.
