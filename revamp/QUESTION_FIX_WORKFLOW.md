# BrainActive Question-Fix Workflow

This is the project record for the protected question-repair workflow. The reusable `report-question-repair` skill is already installed in the Codex skill catalog; this file preserves the BrainActive-specific checks and audit history.

## Production workflow

1. Read the open rows from `public.brainactive_question_issue_reports` through the linked Supabase CLI. Record the report ID, question ID, issue type, detail, and status.
2. Read the complete row from `public.brainactive_questions`, including `question`, `options`, `answer`, `explanation`, `visual_spec`, `visual_required`, and `image_path`.
3. Compare the row with the authoritative local bank and the actual storage object. For visual questions, inspect the rendered asset itself; filename or path alone is not evidence.
4. Audit related rows in the same generated batch for copied image paths, full-URL/path-format drift, missing assets, and visual labels that disagree with the prompt or `visual_spec`.
5. Make the smallest source-backed repair. Preserve ID-to-asset naming (`p3/<question-id>.svg`) and record the database change in a timestamped migration with restrictive predicates.
6. Upload the exact replacement asset, apply the linked migration, re-query the repaired rows and report statuses, and verify the public asset returns HTTP 200 with the expected labels/content.

## 2026-09-20 audit result

- Reviewed all five open student reports. BA_P3_0801 had a real label mismatch: the prompt used F/B/C/E while the asset rendered W/X/V/Z. BA_P3_2042 and BA_P3_G040 were independently correct.
- Proactively audited active visual rows. Nine questions reused generic neighboring assets: BA_P3_2350, BA_P3_2356, BA_P3_2361, BA_P3_2375, and BA_P3_2389–BA_P3_2393.
- Replaced those nine clock/cube-net assets with ID-matched, prompt-aligned SVGs and updated their database paths.
- Shared assets for BA_P3_2396–BA_P3_2398, BA_P3_2412–BA_P3_2424, and BA_P3_2436 were checked and left unchanged because their generic diagrams match their prompts.
- The final normalized asset-path audit found no remaining active visual row whose stored path points to a different question ID. Absolute public URLs are treated as equivalent to their normalized `p3/...` paths.

## Repair migration

`supabase/migrations/20260920000000_brainactive_reported_question_repairs.sql` contains the report resolution and proactive visual-audit updates. Data-only repairs do not require an H5 or Android rebuild.
