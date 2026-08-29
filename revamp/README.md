# BrainActive — Documentation Index & Project Record

> Scope: local content-bank work only. **No DB, no Supabase, no production app code, no publish.**
> JSON is the temporary source of truth. Independent AI1 QA + human review are required before any import.

This file is the **master index** for all BrainActive markdown docs. It also records (a) what has been
done, (b) the research results, and (c) the standing guidelines/constraints. Per-area indexes live in
each folder (`research/INDEX.md`, `curriculum/INDEX.md`, `report/INDEX.md`, `taxonomy/INDEX.md`,
`bank/INDEX.md`).

> **Deployment status (2026-08-29):** A Supabase/Edge-Function handover exists
> (`HANDOVER_FOR_CONTENT_WORKER.md`) but **import is BLOCKED** — see `DEPLOYMENT_STATUS.md`
> (no human review sign-off, broken image linking, no credentials in this environment). JSON remains
> the source of truth.

---

## 1. Folder structure

```
revamp/
├── README.md                         ← this file (master index + record)
├── PLAN.md                           ← rolling plan / next steps
├── research/                         ← market, curriculum, verbal, competitive research
│   ├── INDEX.md
│   ├── brainactive_content_research.md
│   ├── brainactive_p3_curriculum_research.md
│   ├── brainactive_verbal_reasoning_research.md
│   ├── brainactive_competitive_positioning.md
│   └── brainactive_p3_high_ability_research_report.md   (consolidated research + pilot report)
├── taxonomy/
│   ├── INDEX.md
│   └── brainactive_question_taxonomy.md                  (A–E archetype catalogue)
├── curriculum/                       ← skill frameworks, blueprints, pilot plans
│   ├── INDEX.md
│   ├── brainactive_p3_skill_framework.md                 (6-domain skill map, Tiers 1–3)
│   ├── brainactive_p3_content_blueprint.md               (first-100 volume/allocation blueprint)
│   ├── brainactive_verbal_reasoning_framework.md        (7 verbal skills, A/B/C class)
│   ├── brainactive_verbal_100_allocation.md             (verbal % in first 100)
│   └── brainactive_verbal_pilot_plan.md                 (10-item verbal pilot A1–G1)
├── report/                           ← build reports, catalogues, self-reviews
│   ├── INDEX.md
│   ├── question_bank_build_report.md                     (v0.6-local 1000-q build report)
│   ├── v0.4_content_design.md
│   ├── v0.4_content_review.md
│   ├── v0.4_question_catalogue.md
│   ├── v0.4.1_question_catalogue.md
│   ├── v0.4.1_delta.md
│   ├── v0.3_content_audit.md
│   └── pilot_self_review.md
├── bank/                             ← the live content bank + coverage + QA
│   ├── INDEX.md
│   ├── brainactive_p3_question_bank.json                (1000 questions, v0.6-local — the bank)
│   ├── CONTENT_COVERAGE.md                              (auto-generated coverage report)
│   ├── build_bank.py / generate_1000.py / validate_bank.py / generate_coverage.py
│   ├── questions/verbal_extension_v05.json
│   ├── images/  (rendered SVG+PNG)   ├── previews/
│   └── qa/
│       ├── AI1_QA_SPEC.md                             (independent AI answer-verification spec)
│       └── local_validation_report.md                 (structural validation results)
└── renderer/render.py                ← deterministic SVG/PNG renderer for visual_spec
```

---

## 2. What has been done (work log)

| # | Date | Version | What | Result / status |
|---|------|---------|------|-----------------|
| 1 | — | research | Curriculum + content + verbal + competitive research; built taxonomy, skill framework, blueprint, verbal framework, allocation, pilot plan | 9 research/curriculum docs; positioning locked |
| 2 | — | v0.4.1 | 50-question frozen, validated baseline (`pilot/brainactive_p3_high_ability_pilot.json`) | Validated; `qa_status = validated_baseline_v041` |
| 3 | — | v0.5 | 10 research-derived verbal items (pilot plan A1–G1) as a separate extension | `verbal_extension_v05.json` |
| 4 | — | v0.5-local | Assembled **100-question** local bank (50 baseline + 10 verbal + 40 generated) | `brainactive_p3_question_bank.json`; 0 structural issues; 34 visuals |
| 5 | 2026-08-28 | v0.6-local | Scaled to **1000 questions** (`generate_1000.py`, 33 deterministic generators) | 180/180/160/160/200/120 by domain; 0 issues |
| 5a | — | — | Fixed generator bugs (undefined `rng`, seed-fingerprint dedup) and expanded the 5 pattern generators with combinatorial variety | Each pattern generator yields 30+ distinct items |
| 5b | — | — | Added 4 **Master-tier** generators (numerical alternating-rule, multi-step working-backwards, chained conditional, two-step cipher) | Master tier 2 → **68** |
| 5c | — | — | Extended `renderer/render.py` to parse richer figure descriptions (matrix / odd-one-out / figure-analogy) | 326 visuals rendered correctly |
| 5d | — | — | Regenerated `CONTENT_COVERAGE.md`; updated `question_bank_build_report.md` and `qa/local_validation_report.md` | Reports reflect 1000 scale |
| 6 | **TODO** | — | **Independent AI1 answer-verification pass** over all 1000 (`qa/AI1_QA_SPEC.md`) + human review | Not started — required gate before import |

**Key facts**
- The 1000-question bank = 100 validated seed + 900 deterministically generated items.
- All 900 generated items carry `qa_status = ai_generated_not_approved` (pending AI1 + human review).
- Every generated item's answer is **computed** by the generator (not hand-typed), with auto-built
  near-miss distractors; duplicates rejected by `(question, answer)` fingerprint vs seed and new items.
- Current level mix: Explore 215, Think 604, Challenge 113, Master 68.

---

## 3. Research results (summary)

### 3.1 Market & positioning (from `brainactive_competitive_positioning.md`)
- **Positioning (locked):** *"BrainActive — Build Thinking Skills for Primary 3 High Ability."*
  A 10-minute daily, game-like reasoning app that **teaches** via explanations.
- **Not** a test, **not** affiliated with MOE/GEP, **not** English tuition, **not** syllabus drilling.
- Audience: Singapore **P3 high-ability** children; English-first copy. (Cross-sell to MathHero's maths-seeking parents.)
- Moat: precise niche (P3 high-ability, Singapore) + deterministic `visual_spec` engine that scales
  content cheaply; non-routine reasoning (pattern / logic / spatial / heuristics) — the skills *not*
  taught in primary school.

### 3.2 Curriculum context (from `*_curriculum_research.md`, `*_research_report.md`)
- Singapore high-ability identification is **reasoning-first**. MOE **2026 moves to a single stage**
  emphasising reasoning, language and problem-solving (not syllabus drilling). GEP General Ability is
  split verbal (analogy, anagram, decoding, logic) vs non-verbal (patterns, odd-one-out, spatial
  rotation/reflection/3D nets, logic). HAL programmes (E2K, MEW) reward the same habits.
- High-ability P3 items are **non-routine**: the bottleneck is reasoning, not arithmetic.
- **SPONCS** = the standard visual-analysis heuristic (Shape, Position, Orientation, Number, Colour, Size).

### 3.3 Taxonomy & skills
- Original taxonomy: 5 families (A Numerical, B Logical, C Pattern, D Verbal, E Visual) — `taxonomy/brainactive_question_taxonomy.md`.
- Adopted skill framework: **6 domains, 41 skills** (`curriculum/brainactive_p3_skill_framework.md`):
  Numerical (1.1–1.4), Logical (2.1–2.5), Verbal (3.1–3.7), Visual/Spatial (4.1–4.8),
  Pattern/Abstract (5.1–5.5), Problem Solving & Heuristics (6.1–6.7).
- Generation-readiness ranking (taxonomy + skill framework):
  - **Highly generative (safe to auto-generate):** A1–A4 / 1.1–1.2, C1–C5 / 5.1–5.5, E1/E2/E4/E5 / 4.1–4.2/4.6, D5 / 3.3.
  - **Partial (template + curated pool):** A5/A6, B1/B2, C6, D4, E3/E6.
  - **Hand-crafted (quality-critical, low volume):** B3–B6, D1–D3, D6 — author carefully, human review.

### 3.4 Verbal framework (from `brainactive_verbal_reasoning_framework.md` + allocation)
- **7 verbal skills** (VR1–VR7). Class system:
  - **C** = genuine verbal reasoning (preferred, vocabulary-light) — VR1/VR2/VR3/VR4/VR5/VR6.
  - **B** = vocabulary + reasoning (use P3-accessible words, **capped**) — VR7 (sentence completion).
  - **A** = pure vocabulary — **excluded** from BrainActive.
- **Verbal allocation:** **~15–16%** of the first 100 (recommended over 10/20/25). Keep verbal in the
  **15–20%** band when scaling, **always C-dominated**; let VR3/VR4/VR5 (codes / anagrams / letter patterns)
  absorb any growth because they are deterministic and vocabulary-free. **Never let VR7 (B) exceed ~1 per 100.**
- Favoured types: **VR3 Codes & VR4 Word Manipulation** (vocab-light, reasoning-heavy). **A2 / C1** (dual-relation
  analogy) and code/anagram items must require **rule discovery**, not mechanical application.

### 3.5 Scaling path (research report §8)
- 30 (done, QA'd pilot) → 100 (parameterised templates) → 300 (full generator + renderer, mixed/multi-step).
  We have now gone to **1000** via the same deterministic-template approach; multi-step / mixed items are
  present in the Master tier.

---

## 4. Standing guidelines & constraints

### 4.1 Hard project gates (non-negotiable)
- **NO** database tables / migrations. **NO** Supabase connect or upload. **NO** production app-code changes.
- **NO** publish, **NO** upload to Storage. JSON is the temporary source of truth.
- **AI1 QA + human review are mandatory** before any question is imported/treated as production content.
- **MathHero is read-only reference** — never modified.

### 4.2 Content-generation rules (applied in `generate_1000.py`)
- Deterministic, parameterised generators; **answers computed**, not hand-typed; distractors are
  relation/near-miss plausible, unique, and ≠ correct.
- Reject duplicate `(question, answer)` fingerprints (vs seed **and** new items).
- Keep the research-derived **domain balance**: numerical 18% / logical 18% / verbal 16% / visual 16% /
  pattern 20% / problem_solving 12% (scaled proportionally).
- **Verbal 15–20%, C-dominated**; cap VR7 (B) at ~1 per 100.
- Visual items driven by `visual_spec` → **deterministic SVG** (never raster images), so rendering is
  exact and answers unambiguous.
- Every item carries `provenance` (basis = GEP GA / CogAT / UK 11+ archetypes) and `explanation` that
  **restates the rule and proves the answer**.

### 4.3 Quality bar
- Single-answer, explainable, P3-appropriate, original (not copied from any source).
- Level mix should include **Master (expert)** items where the child must decide *how* to solve
  (multi-step / open-strategy) — now 68 of 1000.
- Structural validation (`validate_bank.py`) must report **0 issues** (parse, 4 options, answer-in-options,
  visual-spec consistency, duplicate-ID, duplicate-fingerprint, valid SVG) before sign-off.

### 4.4 Next gate (do not skip)
1. **Independent AI1 QA** per `bank/qa/AI1_QA_SPEC.md` — re-derive every answer, check P3 appropriateness
   and the verbal A/B/C split.
2. **Human review** of AI1 REVIEW/FAIL items; re-author as needed.
3. Only after 1–2: import to Supabase + Storage for visual assets, then production app.

---

## 5. Quick links
- Bank (1000 q): `bank/brainactive_p3_question_bank.json`
- Build report: `report/question_bank_build_report.md`
- Coverage: `bank/CONTENT_COVERAGE.md`
- Structural QA results: `bank/qa/local_validation_report.md`
- Independent QA spec: `bank/qa/AI1_QA_SPEC.md`
- Generators: `bank/generate_1000.py` (1000) · `bank/build_bank.py` (seed 100)
- Validator: `bank/validate_bank.py` · Coverage: `bank/generate_coverage.py`
- Renderer: `renderer/render.py`
