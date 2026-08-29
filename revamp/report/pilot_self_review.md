# Pilot Self-Review — BrainActive P3 High Ability

**Version:** 0.3 (rebuilt 2026-08-27 from the curriculum research)
**Mix:** 6 numerical · 6 logical · 4 verbal · 5 visual/spatial · 6 pattern/abstract · 3 problem-solving heuristics (30 total)
**Principle applied:** v0.3 is **research-derived** — a miniature of the eventual product, sampled from the
6-domain skill framework and the first-100 blueprint (≈20% numerical, 18% logical, 14% verbal, 17% visual/spatial,
20% pattern/abstract, 11% heuristics). v0.2 was a revision of the *original 5-category brief* and is **not** used as
the basis for the curriculum questions — it is superseded by v0.3.

## What v0.3 is (and is not)
- It is a **curriculum-sampling pilot**: each item is tagged with a `skill_code` from the framework so coverage is
  traceable. New research-highlighted areas are explicitly represented:
  - Figure matrices `5.2` (0023), 3D orientation `4.4` (0021), combining/hidden shapes `4.7` (0027).
  - Singapore heuristics: working backwards `6.1` (0028), guess-&-check `6.2` (0029), before-after `6.3` (0030).
- It is **not** a GEP mock, not a worksheet, and makes no selection/MOE claim (see dataset disclaimer).

## Coverage (skill_code → item)
| Domain | Skills sampled | Items |
|---|---|---|
| 1 Numerical | 1.1×2, 1.2, 1.3×2, 1.4 | 0001–0006 |
| 2 Logical | 2.1, 2.2×2, 2.3, 2.4, 2.5 | 0007–0012 |
| 3 Verbal | 3.1, 3.2, 3.3, 3.5 | 0013–0016 |
| 4 Visual/Spatial | 4.1, 4.2, 4.3, 4.4, 4.6, 4.7 | 0017–0021, 0027 |
| 5 Pattern/Abstract | 5.1, 5.2, 5.3, 5.4, 5.5 | 0022–0026 |
| 6 Problem-Solving | 6.1, 6.2, 6.3 | 0028–0030 |

## Level / difficulty distribution
- Level: Explore 10 · Think 13 · Challenge 7 (maps to the blueprint's Explore/Think/Challenge/Master model; no Master-tier
  items yet — that tier is reserved for non-routine items in the scaled product).
- Difficulty: medium 11 · hard 12 · challenge 7.

## Self-QA (all 30)
- Independently re-solved each; **every answer is present in its 4 options**.
- `visual_required` / `visual_spec` consistency checked: 11 visual items carry a spec; 19 non-visual items have `null`.
- JSON parses; 4 options each; no duplicate IDs. **0 structural issues.**
- 0001–0026 largely reuse strong v0.2 items (re-selected to fit the curriculum map). 0027–0030 (combining shapes,
  working-backwards, guess-&-check, before-after) are new and written fresh.

## Known caveats (honest flags)
- **0012** was rewritten cleanly (the first draft had a contradictory clue); the final version is consistent:
  Ben cycles, Cindy runs, Amy does not swim, Dan does not skate → Dan swims.
- Verbal items (0013–0016) are intentionally accessible warm-ups; correct and P3-appropriate but generic-IQ in flavour.
- The clarity of spatial/pattern items (0017–0027) depends on the (not-yet-built) SVG renderer; `visual_spec` is
  descriptive and renderer-ready, but must be visually inspected once the generator exists.
- Tier-2/Tier-3 framework skills (e.g. paper folding `4.8`, 3×3 matrices, number-series advanced) are **not** in v0.3
  by design — v0.3 samples Tier-1 only. They belong in the scaled 100+ build.

## Verdict
v0.3 is a curriculum-faithful miniature: it demonstrates the 6-domain model, the level progression, and the
research-highlighted gaps (matrices, 3D, combining, Singapore heuristics). Recommend product/consultant review of the
30 items (content, not code) — **and the curriculum framework** — before any renderer work or scaling to 100+ begins.

(End of file)
