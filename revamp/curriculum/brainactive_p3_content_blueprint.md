# BrainActive P3 High Ability — Content Blueprint

## 1. Learning progression (not "easy/medium/hard")

The pilot used easy/medium/hard; for the product we recommend **four levels named by mindset**, so
parents and children understand the journey:

| Level | Name | What it means | Example skills |
|---|---|---|---|
| 1 | **Explore** | Accessible, single-rule reasoning. Build familiarity, low anxiety. | one-rule number sequences, simple analogies, basic rotation, classification |
| 2 | **Think** | Multi-step or less-obvious patterns; first constraints. | interleaved sequences, constraint matching, codes, 2×2 matrices |
| 3 | **Challenge** | Complex relationships, 3D/spatial, deductive systems. | nets/cubes, 3D orientation, conditional chains, cryptarithms |
| 4 | **Master** | Novel, non-routine, multi-constraint puzzles combining skills. | multi-step puzzles, mixed-reasoning sets, invented heuristics |

**How difficulty should rise (per the product promise):**
- More rule complexity, more constraints, better "near-miss" distractors, and **integration of skills** — *not* bigger numbers or harder vocabulary.
- A "Master" item for a P3 child is one where the familiar algorithm doesn't apply and they must **think**.

## 2. Product content model (learning, not UI)

- **Daily Brain Challenge** — 10-minute auto-pull across the curriculum, mixed levels (mostly L1–L3), weighted by the blueprint below. This is the flagship habit.
- **Skill Practice** — scaffolded sets within a single subskill (e.g. 5 figure-matrix items L1→L3).
- **Mixed Challenge** — cross-domain sets for breadth.
- **Timed Challenge** (optional) — speed, for confident users.
- **Progress & motivation** — per-domain strength radar, streaks, personal bests, mastery badges. (Content/learning design only; no UI code.)

## 3. Question-generation strategy (how we scale 30 → 100 → 300 → 1,000)

| Path | Skills | Method |
|---|---|---|
| **Deterministic generator** | 1.1, 1.2, 4.1, 4.2, 4.5, 4.6, 5.1, 5.2, 5.3, 5.4, 5.5, 3.3 | Rule/template engines + parameters; answers computed, not guessed. |
| **Visual generator (SVG/Canvas)** | all of Domain 4 + 5 (driven by `visual_spec`) | Render from structured specs; no raster images. |
| **AI-generated + strong QA** | 3.1, 3.2, 3.4, 3.5, 6.x scenarios | LLM drafts from curated word/pattern pools; must pass single-answer + distractor QA. |
| **Human-authored** | 2.2, 2.5, 6.7, Master-tier items | Hand-crafted; used sparingly for quality ceiling. |

This means ~half the library can be generated reliably and visually verified — the strategic
advantage noted earlier (hundreds of visual items without hand-drawn art).

## 4. The FIRST 100 questions — recommended allocation

The pilot's even 6×5 split was a *test scaffold*, not a curriculum. Research suggests a
reasoning-first weighting that leans into the skills school doesn't teach (pattern, visual,
logic) and keeps verbal moderate (SG P3 verbal is mostly English-comprehension territory we
shouldn't colonise). Proposed:

| Domain | Count | Sub-allocations (subskill : n) | Why |
|---|---|---|---|
| **Numerical Reasoning** | 20 | 1.1 Pattern Discovery 8 · 1.2 Relationships 5 · 1.3 Puzzles/Systems 4 · 1.4 Quantitative Logic 3 | Core differentiator; highly generatable; parents expect "maths thinking". |
| **Logical Reasoning** | 18 | 2.1 Ordering 4 · 2.2 Constraint 4 · 2.3 Conditional 4 · 2.4 Classification 3 · 2.5 Syllogism 3 | Reasoning backbone; strong "think" feel; mixed generation paths. |
| **Verbal Reasoning** | 14 | 3.1 Analogies 5 · 3.2 Classification 3 · 3.3 Codes 3 · 3.4 Anagrams 2 · 3.5 Sentence Logic 1 | Useful but kept moderate; avoid drifting into English-compre. |
| **Visual & Spatial** | 16 | 4.1 Rotation 4 · 4.2 Reflection 3 · 4.3 Nets 3 · 4.4 3D Orient 2 · 4.5 Position 2 · 4.6 Transform 2 | High generator leverage; visually distinctive in-store; non-school skill. |
| **Pattern & Abstract** | 20 | 5.1 Sequences 6 · 5.2 Matrices 6 · 5.3 Fig Classification 4 · 5.4 Fig Analogies 4 | The "wow" visual core; maps directly to deterministic renderer. |
| **Problem Solving & Heuristics** | 12 | 6.1 Work Backwards 2 · 6.2 Guess & Check 2 · 6.3 Before–After 2 · 6.4 Draw Diagram 2 · 6.5 Make List 2 · 6.6 Pattern 2 | The Singapore "thinking skills" identity hook; ties it all together. |
| **Total** | **100** | | |

**Mix by level (target):** ~30 Explore · ~40 Think · ~22 Challenge · ~8 Master.
**Why not even:** pattern/visual/logic are where BrainActive uniquely adds value vs school and vs
generic brain apps; verbal is capped so we don't become an English workbook.

## 5. Opinionated recommendation (if building from scratch today)

> Make the **first 100** a **reasoning-first** set: ~20% numerical, ~18% logical, ~20% pattern/abstract,
> ~16% visual/spatial, ~14% verbal, ~12% problem-solving heuristics. Lead with **figure matrices,
> sequences, rotation/reflection, and constraint logic** because they are (a) unfamiliar to school,
> (b) highly generatable, and (c) visually distinctive in a store listing. Wrap everyday sessions in
> the **10-minute Daily Brain Challenge** so the product sells a *habit*, not a test. Keep verbal light
> and never claim GEP prep.

This gives BrainActive a coherent identity: **"Singapore P3 high-ability thinking practice"** —
not P3 maths drills, not a GEP mock, not generic brain games.
