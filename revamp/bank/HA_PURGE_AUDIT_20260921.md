# BrainActive HA Purge + Regen Audit (2026-09-21)
Source bank: revamp/bank/brainactive_p3_question_bank_production.json (973 rows; 933 live).
Final bank: revamp/bank/brainactive_p3_question_bank_ha20260921.json (1353 rows; 931 live).
Status: JSON is the source of truth. New items ship as inactive candidates pending human review.
## 1. The bar (MOE + GEP General Ability + past papers)
- MOE: 2026 one-stage P3 identification, reasoning first; HAL habits (inquiry, puzzles, heuristics), not syllabus drilling.
- GEP GA format: verbal analogy with relation matching (Company:President :: Army:General), anagrams, decoding; non-verbal combined rules (size change plus 90-degree turn), number series with two-step rules (x2 then +1), Fibonacci gaps, weight elimination, figure counting to N, gap concept.
- 2019 GEP sample style: substitution conditionals, tap method rates, elimination-substitution weights, Fibonacci with missing middles, pattern-to-Nth counting, gap-concept money problems.
- HA rule used here: difficulty must come from rule discovery and multi-step inference, never from single obvious attributes, stated rules, transcription, or routine computation. Explore = one hidden rule; Think = multi-step; Challenge = 3+ clues or spatial chains; Master = open strategy.
## 2. Delete rules and counts
- R1 figure_odd_one_out x53: single-feature discrimination (size-only or dot-only, 3-identical-1-different). GEP needs abstract SPONCS rules across all four figures.
- R2 linear_order x48 (kept merged exemplar BA_P3_0060): fully-given chains, transcription only. HA ordering must merge partial orders.
- R3 figure_analogy x50 (kept double-change BA_P3_0025/0087): single-attribute change stated in stem, matching only.
- R4 letter_series x20: gap rule stated in every stem, application not discovery.
- R5 conditional_contrapositive x10: direct modus ponens read-offs mislabelled as contrapositive.
- R6 number_analogy x20 plus R6c x4: single-operation rules on small numbers; 4 items with copy-pasted sequence explanations (numbers absent from stem and options).
- R7 doubling dot sequences x6 (kept 2 exemplars, later removed as imageless): pure doubling counts.
- R8 single 90-degree rotations x10; R9 one-step working backwards x1 (BA_P3_0044).
- R10 machine-rule swarm x11: identical x3+1 template repeated; kept 2 per rule.
- R11 routine-arithmetic swarms x76: before_after_transfer/chain_comparison/before_after/draw_diagram_gaps trimmed to 2-4 exemplars each.
- Round 2 (independent solver finds): 42 weight_system with duplicate option texts; 15 sentence_logic with duplicate option texts; BA_P3_0564 wrong answer (gap +4 answered O); BA_P3_ADD_0046 duplicate options; 14 figure_sequence constant-step dot counts that are also imageless (visual_required=true, image_path null).
- Total removed from live set: 382. Total live: 931.
## 3. Regeneration (deterministic, computed answers, unique fingerprints)
- 53 SPONCS odd-one-out with hidden abstract rules, agreement-filtered so exactly one rule family member set agrees on the odd one.
- 50 compound figure analogies with hidden two-step rules and deterministic colour cycle (random colour made old items ambiguous).
- 48 merged 4-5 entity orders (full order, position, must-be-true forms).
- 27 two-transfer and hidden-total before-after items; 26 straight/circular/both-sides fence items with fencepost traps.
- 24 dual-relation number analogies guarded against every simple rule in the solver family (no ambiguous options).
- 20 hidden-rule letter series, all 5 letters, const/alternating/growing only (period-4 dropped as unverifiable).
- 17 four-person chain comparisons with corrected sign and unique-max enforcement.
- 11 varied function machines; 10 multi-step rotations and mirrors; 8 compound sequences; 6 gap-double before-after; 1 two-step backwards.
- 42 proper 3-variable weight systems; 15 sentence-logic contrapositives and chains; 14 compound figure sequences.
- All text-sufficient (visual_required=false), so no new image pipeline was needed and no broken-image risk was added. 380 new IDs BA_P3_HA_0001-0384 range.
- Grammar pass: fixed auxiliary-verb forms (does NOT build, did NOT save) across chain items.

## 4. Independent solver QA over all 931 live EN questions
- Separate solver code re-derived every answer from stem text only (orders by chain assembly, SPONCS rule search, analogy projection, gap-pattern detection, rule-family fit, fence and transfer simulation, rotation simulation, 3-variable linear solve, syllogism closure, contrapositive engine, machine refit, combinatorics recount).
- Result: 0 FAIL, 540 PASS with exact derived-answer match, 391 REVIEW.
- REVIEW split: 244 honest abstains (single-pair analogies with several fitting rules, exotic series, complex wordings), 134 visual or semantic items needing human eyes (cube nets, 3D rotation, matrices, seating CSPs, verbal classification), 13 answer-verified items with explanation polish notes for human review.
- Solver bugs found and fixed during the pass (not bank bugs): topological order assembly, alternating-subsequence base, article-A in letter parse, direction set, size toggle, unicode arrow, gap-double math, fencepost circle rule, changed-by op parser, clause stemming, given-sentence fallback.
- True bank bugs removed: 42 + 15 duplicate-option items, 1 wrong answer, 1 duplicate matrix, 4 wrong explanations, 9 grammar slips (fixed, not removed), 14 imageless trivial sequences.
## 5. Validation
- Structural validator revamp/bank/ha_validate.py: 0 issues on live set (4 options, answer in options, unique option texts, string types, valid levels, visual consistency, unique fingerprints).
- No CJK text. No duplicate (question, answer) fingerprints. All new items carry qa_status validated_ha_20260921.
## 6. Deploy
- Migration supabase/migrations/20260921000000_brainactive_ha_purge_regen.sql: 3 reject updates (382 rows to rejected_* and is_active=false, guarded by qa_status not like rejected percent) plus 380 inserts with on conflict do nothing, all is_active=false.
- revamp/upload_passing.py now also approves validated_ha_20260921.
- Activation of the 380 new rows happens only after human review sign-off. Serving set otherwise unchanged.
## 7. Files
- ha_audit_20260921.json (per-id verdicts), ha_audit_purge.py, ha_regen.py, ha_regen2.py, ha_regen3.py, ha_regen4.py, ha_fix3.py, ha_solver_qa.py, ha_solver_tracker_20260921.json, ha_merge.py, ha_merge2.py, ha_validate.py, ha_migration.py, ha_new_20260921.json, ha_extra_20260921.json, ha_dels2_20260921.json, ha_dels3_20260921.json.
- Reviewer entry points: this file, ha_solver_tracker_20260921.json (filter verdict REVIEW), CONTENT note in section 4.

## 8. Round-2 QA and deploy addendum (2026-09-21, later same day)
- Independent solver extended (topological orders, size-toggle analogy, unicode arrows, gap-double math, fencepost circle rule, changed-by parser with xN multiply, clause stemming, given-sentence fallback, seating CSP, 3x3 grid tracker, square/geometric sequences, decode ciphers, two-word weights, combinatorics forms). Final: 0 FAIL, 628 PASS, 295 REVIEW over 923 live.
- Hand QA of all 391 REVIEW rows: 62 verbal classifications and analogies verified (1 explanation rewritten for BA_P3_0323); 40 cinema seating plus 16 row seating plus race orders verified one by one; 23 contrapositives and chains verified; 17 kept dual analogies proved ambiguous by rule-family computation (2 or more consistent options) and held with needs_option_fix status; 11 digit-suffixed corrupt options plus 1 corrupt matrix option held; 8 more too-simple items removed (single-feature classification sets, single-op analogy, doubling and constant-step sequences, imageless dot counts).
- 9 explanations repaired with asserted recomputation (7 shift-reverse codes, G112 red-tag, 4 alternating-jump wordings) and 9 grammar slips fixed (does NOT build, did NOT save).
- 6 missing matrix SVGs rendered deterministically and verified (4 two-by-two answers re-derived from specs; 3x3 0092 verified consistent; 0091 held for a stem direction mismatch).
- Deploy: 6 images uploaded (public 200); migration 20260921000000 applied (382 rejects inactive, 380 HA inserts); migration 20260921010000 applied (8 more rejects, 27 option-fix holds inactive, 9 explanation repairs); 380 HA rows activated. Final DB: 380 HA active, 515 validated_fix active, 591 new600 plus 10 repaired untouched, all rejected and held inactive. Edge smoke test returns 5 mixed questions including new HA content.
- Activation set: revamp/bank/ha_activate_20260921.json (896 IDs: 516 already-active kept plus 380 new HA).

