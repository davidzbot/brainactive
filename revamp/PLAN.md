# BrainActive Revamp — Plan

## Positioning (decided with owner + consultant)
Pivot BrainActive from a **generic senior+kids brain-training app** into a
**Singapore Primary 3 high-ability reasoning practice product**.

Consumer-facing wording (consultant tweak, 2026-08-27):
> **"Build Thinking Skills for Primary 3 High Ability"**
(closer to the owner's original phrasing; explicitly *not* an assessment/test claim).

This aligns with the existing PSLE / MathHero assets (Singapore education market)
and targets **paying parents** of high-ability / GEP-aspirant children — a
high-LTV, high-intent niche.

### Reconciliation with earlier ASO advice
- Earlier SEO plan favoured "brain games for adults & seniors" (low KD).
- This revamp favours "P3 thinking skills / GEP-style reasoning practice"
  (lower volume, higher parental willingness to pay).
- Decision: go all-in on the **high-ability kids** angle for the BrainActive brand.

## Guardrails (from consultant brief)
- No DB tables / migrations.
- No production app code changes yet.
- No UI implementation yet.
- No assumed final schema; JSON is the interim format.
- Do NOT copy commercial GEP/enrichment questions — only original questions
  inspired by underlying reasoning skills.
- No MOE/GEP official-claim or admission-prediction language.

## Deliverables (per consultant task)
1. `revamp/research/brainactive_content_research.md`
2. `revamp/taxonomy/brainactive_question_taxonomy.md`
3. `revamp/pilot/brainactive_p3_high_ability_pilot.json`  (30 original questions)
4. `revamp/report/brainactive_p3_high_ability_research_report.md`

Plus: self-QA pass on all 30 questions; JSON validation.

## Execution phases (REVISED roadmap — consultant, 2026-08-27)
Do NOT auto-scale 30 -> 100 -> 300. Instead:
- **Phase 1 — Research** (done): research md.
- **Phase 2 — Taxonomy** (done): taxonomy md.
- **Phase 3 — Pilot 30 questions** (done): pilot json.
- **Phase 4 — Self-QA** (done): structural + solve-each validation (report md).
- **Phase 4.5 — Curriculum & content research** (DONE, 2026-08-27): broader
  research than the 30-question pilot. Deliverables:
  - `research/brainactive_p3_curriculum_research.md` (MOE 2026 / SG materials / CogAT+11+)
  - `curriculum/brainactive_p3_skill_framework.md` (6 domains, ~40 skills, Tiers 1–3)
  - `curriculum/brainactive_p3_content_blueprint.md` (4-level progression + first-100 allocation)
  - `research/brainactive_competitive_positioning.md` (category map + differentiation + SEO intent)
  - This file updated.
  This established WHAT BrainActive should teach (reasoning-first, SG "thinking skills"
  identity), superseding the pilot's flat 5-category split. The pilot's even 6×5 split
  is explicitly recorded as a *test scaffold*, not the real curriculum.
- **Phase 5 — HUMAN / PRODUCT REVIEW**: (a) the revised 30 questions, AND (b) the
  proposed curriculum/skill framework and first-100 blueprint. Confirm the skill mix
  (≈20% numerical, 18% logical, 20% pattern, 16% visual, 14% verbal, 12% heuristics)
  before any generation.
- **Phase 6 — Renderer ONLY after review passes**: JSON -> deterministic SVG (no raster).
  Then visually inspect all items.
- **Phase 7 — First 100 questions** (curated per blueprint, NOT auto-bulk), then
  **user test** with real parents/students before any larger scaling to 300/1,000.

## Hard gates (current, 2026-08-28)
- NO database / migration changes. (still in force)
- NO production app code changes. (still in force)
- NO publish / upload to Supabase / Storage. (still in force)
- SVG renderer IS built (local, `revamp/renderer/render.py`) — used only for QA.
- Local 100-question bank IS built (`revamp/bank/...`) — JSON is the temporary source of truth.
- NO MOE/GEP official-claim or selection-prediction language anywhere. (still in force)
- All non-baseline items are `ai_generated_not_approved` until AI1 QA + human review.

Principle: 100 bad questions is worse than 30 excellent ones. Quality gates > count.

## Realised roadmap (update of Phases 1–7)
- Phase 1 Research — DONE.
- Phase 2 Taxonomy — DONE (superseded by skill framework).
- Phase 3 Pilot 30 — DONE, then expanded to **v0.4.1 = 50** (research-derived learning journey,
  29 progressions, validated; 6 items defect-fixed in v0.4.1).
- Phase 4 Self-QA — DONE (report + catalogue).
- Phase 4.5 Curriculum & content research — DONE (skill framework, blueprint, positioning).
- Phase 5 Human/product review — DONE (owner approved framework + first-100 blueprint).
- Phase 5b Verbal Reasoning research — DONE (4 research docs; A/B/C vocabulary distinction;
  ~15–16% verbal; 10-question pilot plan A1–G1). Owner approved.
- Phase 6 Renderer — DONE (local SVG/PNG; 34 visuals rendered for the bank).
- Phase 7 First 100 questions — DONE as **local development bank**
  (`revamp/bank/brainactive_p3_question_bank.json`, 100 Q):
  - 50 from frozen v0.4.1 baseline (validated)
  - 10 research-derived verbal extension (pilot plan A1–G1)
  - 40 newly generated (Num 9 / Log 9 / Vis 8 / Pat 11 / PS 3) deterministically + authored
  - Visuals rendered; structural validator clean (0 issues).
  - Deliverables: `bank/CONTENT_COVERAGE.md`, `bank/qa/AI1_QA_SPEC.md`,
    `bank/qa/local_validation_report.md`, `report/question_bank_build_report.md`.
- **Next gate (NOT started):** independent AI1 QA (per AI1_QA_SPEC.md) over all 100, then human
  review, then (only if clean) Master-tier top-up and Supabase import.

## Open questions for owner
1. Store positioning: kids-high-ability only, or keep a senior mode too?
2. Language: English only, or bilingual EN/ZH (existing app is bilingual)?
3. Approve the start of **AI1 independent QA** on the 100-question bank?
4. Approve a **Master-tier generation pass** (currently 2 vs ~8 target) before import?
