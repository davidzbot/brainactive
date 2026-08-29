# Bank — Index

The live local content bank and its QA tooling. Master index: `../README.md`.

**Data**
- `brainactive_p3_question_bank.json` — **1000 questions, v0.6-local** (the bank; JSON = source of truth).
- `questions/verbal_extension_v05.json` — the 10 research-derived verbal items (separate extension).
- `images/` — rendered SVG + PNG per visual question. `previews/` — PNG previews.

**Reports**
- `CONTENT_COVERAGE.md` — auto-generated coverage (domain/skill/level/visual).
- `qa/local_validation_report.md` — structural validation results (0 issues at 1000).
- `qa/AI1_QA_SPEC.md` — **independent AI answer-verification spec** (required next gate).

**Tooling**
- `build_bank.py` — assembles the 100-q seed (baseline + verbal + 40 generated).
- `generate_1000.py` — scales seed → 1000 via 33 deterministic generators.
- `validate_bank.py` — structural validation.
- `generate_coverage.py` — regenerates `CONTENT_COVERAGE.md`.

**Renderer:** `../renderer/render.py` (deterministic SVG/PNG from `visual_spec`).
