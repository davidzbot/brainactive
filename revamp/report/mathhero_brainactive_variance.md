# Math Hero → BrainActive Variance & Architecture Report

**Date:** 2026-08-29  
**Product:** BrainActive (Singapore Primary 3 High Ability / Thinking Skills Practice)  
**Reference Product:** Math Hero (`C:\Projects\MathHero\math-hero-app`)  
**Positioning Statement:** "Build Thinking Skills for Singapore Primary 3 High Ability"

---

## 1. Feature & Implementation Comparison

| Area | Math Hero | BrainActive | Difference / Reason |
| :--- | :--- | :--- | :--- |
| **Home Page** | Primary 1–6 grade selector, school paper highlights, subject quests | Simplified P3 Thinking Skills layout: Streak counter, Daily Practice card (5 Qs, 2 free rounds/day), Pro banner, Referral banner. **No grade selector, no topic/level selector on Home.** | **Intentional Differentiation (Rule #5):** BrainActive is exclusively targeted at Singapore Primary 3 High Ability reasoning. All clutter (grade/school/paper selection) is removed from Home. |
| **Quick Test Configuration** | 10 questions per round for Primary 1–6 syllabus math. | 5 questions per round for P3 non-routine reasoning & thinking skills (~5–8 min). | **Intentional Differentiation:** Reasoning questions require step-by-step logic; 5 curated questions is the optimal session length for P3 learners. |
| **Daily Limits & Monetisation** | 10 free questions/day (1 round), rewarded-ad unlock for additional rounds. | **Strict 2 + 3 Ad Model:** Free users get **2 free rounds** per SGT day. Rewarded ads unlock **up to 3 additional rounds** (+1 round per ad, max 5 rounds / 25 questions total per day). Sequence: `1 free → 2 free → 3 ad → 4 ad → 5 ad → stop`. Pro = unlimited. | **Exact Business Logic (Rule #2):** Adapts MathHero daily-state/rewarded-ad mechanism capped strictly at 2 free + 3 ad bonus rounds. |
| **Question Page Header** | Grade, School name, Exam Paper, Year, Topic. | **Topic** (e.g. *Numerical Thinking*) and **Level** (e.g. *Think*). No school, grade, or paper metadata. | **Per Specification (Rule #6):** Focuses student attention strictly on the thinking skill archetype and difficulty level. |
| **Question Interaction & Options** | 4-choice MCQ or open-ended entry, immediate feedback, model answer reveal. | 4-choice MCQ with distinct options (A–D), instant visual feedback, step-by-step solution, and key thinking strategy reveal. | Reused/adapted Math Hero implementation — adapted for P3 reasoning heuristic explanations. |
| **Result Page** | Victory rank, percentage score, time spent, review mistakes, next round CTA. | Victory title, score (e.g. 5/5), percentage, time spent, streak update, review mistakes bank, next round CTA. | Reused/adapted Math Hero implementation — no intentional behaviour change. |
| **Review Mistakes Flow** | Mistakes saved locally for session retry; Pro unlocks unlimited mistake review. | Mistakes saved in dedicated `ba_wrong_questions` bank; retry mode (`mode=retry`) loads missed questions. | Reused/adapted Math Hero implementation — no intentional behaviour change. |
| **Round / Session Handling** | Client-side state tracking, timer, question index, attempt accumulator. | Client-side state tracking, timer, question index, attempt accumulator. | Reused/adapted Math Hero implementation — no intentional behaviour change. |
| **Streak Tracking** | Singapore calendar day (`getLogicalSgtDay`), consecutive day calculation. | Singapore calendar day (`getLogicalSgtDay`), consecutive day calculation stored under `ba_streak_state`. | Reused/adapted Math Hero implementation — isolated under BrainActive storage namespace (`ba_`). |
| **Pro / Practice Zone** | Grade, topic, difficulty, subtopic, paper filter with analysis and collection tabs. | Practice by 6 Thinking Topics (*Numerical Thinking, Logical Thinking, Pattern & Abstract, Visual & Spatial, Verbal Reasoning, Problem Solving*) and 4 Levels (*Explore, Think, Challenge, Master*). Unlimited for Pro. | **Intentional Differentiation (Rule #7):** Configured specifically for P3 High Ability domain/level matrix rather than standard MOE school syllabus topics. |
| **Monetization & AdMob** | Rewarded ad video via `@capacitor-community/admob`, cooldowns, test fallback. | Rewarded ad video with fail-open timeout safety; production and testing fallback flags. | Reused/adapted Math Hero implementation — isolated configuration. |
| **Subscription / In-App Purchases** | Google Play subscription via `capacitor-plugin-cdv-purchase`. | Subscription flow and Pro status handling adapted; staging test activation ready for live IDs. | Reused/adapted Math Hero implementation — isolated configuration. |
| **Referral System** | Unique 6-character code, share invite text, 7-day Pro reward for referrer and referee. | Dedicated `brainactive_referrals` and `brainactive_profiles` backend with 7-day Pro access grant. | Reused/adapted Math Hero implementation — connected to isolated BrainActive backend. |
| **Navigation & Android Back Button** | Handled via `@capacitor/app` `backButton` listener with double-tap exit or back navigation. | Handled via `@capacitor/app` `backButton` listener with double-tap exit or back navigation. | Reused/adapted Math Hero implementation — no intentional behaviour change. |
| **Error / Retry Handling** | In-flight deduplication, error boundaries, graceful offline fallbacks. | In-flight deduplication, error boundaries, graceful offline candidate fallbacks. | Reused/adapted Math Hero implementation — no intentional behaviour change. |
| **Question Loading & API** | Calls `math-app-get-questions` from `math_questions` table. | Calls `brainactive-get-questions` from `brainactive_questions` table. | **Backend Isolation (Hard Rule #4):** BrainActive connects strictly to its own dedicated Edge Functions and database tables. |

---

## 2. Database & Backend Architecture Justification (Rule #11)

Every backend resource created for BrainActive is strictly isolated and purpose-built:

1. **`public.brainactive_questions` (Table)**  
   *Why needed:* Stores the curated P3 High Ability reasoning questions, options, topics, levels, heuristic explanations, and SVG asset URLs. Completely separate from Math Hero's `math_questions` table.
2. **`public.brainactive_attempts` (Table)**  
   *Why needed:* Records individual question attempt accuracy, speed (ms), and session mode for progress analytics and mistake reviews without polluting Math Hero telemetry.
3. **`public.brainactive_profiles` (Table)**  
   *Why needed:* Tracks device-based user status, streak count, and Pro subscription expiry dates for cross-device validation.
4. **`public.brainactive_referrals` (Table)**  
   *Why needed:* Manages referral code generation and validation to reward both referrer and referee with 7-day Pro access.
5. **`brainactive-assets` (Storage Bucket)**  
   *Why needed:* Stores deterministic SVG and PNG visual assets for spatial and pattern questions under the `p3/` directory.
6. **Edge Functions (`brainactive-*`)**:
   - `brainactive-get-questions`: Securely serves randomized or topic-filtered question sets without exposing full database internals.
   - `brainactive-submit-attempt`: Ingests user quiz completions, verifies answers server-side, and increments streak counters.
   - `brainactive-get-progress`: Returns user profile, active streak, and Pro status.
   - `brainactive-apply-referral`: Validates referral codes and extends Pro subscription timestamps.

---

## 3. Question Bank Pools Documentation (Rule #8)

Content pools are maintained in isolated files without silent merging:

| Pool Name | File Location | Question Count | Status / Classification | Next Action |
| :--- | :--- | :--- | :--- | :--- |
| **Validated v0.4.1 Baseline** | `revamp/pilot/brainactive_p3_high_ability_pilot.json` | 50 | Validated & QA passed (6 defects resolved) | Foundation pool for production |
| **Local 100-Question Bank** | `revamp/bank/brainactive_p3_question_bank.json` | 100 | Authored + structured (50 baseline + 10 verbal pilot + 40 newly authored) | Pending AI1 Independent QA |
| **Regenerated Questions Bank** | `regenerated_questions.json` | 100 | Regenerated per curriculum brief | Candidate pool for QA review |
| **1,000-Question Candidate Pool** | `revamp/bank/generated/` | ~1,000 | Raw algorithmic candidates | Staging / unvalidated candidate pool (NOT in production) |
| **Production Target Bank** | `revamp/bank/brainactive_p3_question_bank_production.json` | TBD (post-QA) | To be populated ONLY after AI1 QA and human approval | Production seeding source |

---

## 4. Verification Pass (Rule #12)

| # | Verification Item | Status | Verification Detail |
| :--- | :--- | :--- | :--- |
| 1 | **Backup** | **PASS** | Working copy changes isolated on branch `main`; git working tree tracked; frozen baselines preserved in `revamp/`. |
| 2 | **MathHero frontend/logic reuse** | **PASS** | Storage, SGT day calculation, streak, back button handler, and error fallback adapted directly from MathHero patterns. |
| 3 | **BrainActive backend isolation** | **PASS** | 100% isolated: uses `brainactive_*` tables, `brainactive-assets` bucket, `brainactive-*` Edge Functions. Zero dependencies on `math_*` or `psle_*`. |
| 4 | **Home UX** | **PASS** | Simple MathHero layout: Streak counter, Daily Practice CTA (5 Qs), Pro status banner, Referral banner. No grade selector, no topic/level selectors on Home. |
| 5 | **Quick Test 2 + 3 ad-round rule** | **PASS** | Strict sequence: `1 free → 2 free → 3 ad → 4 ad → 5 ad → stop (max 25 Qs/day)`. Pro = unlimited. Verified in `storage.ts` & `QuotaOverlay`. |
| 6 | **Question-page Topic + Level** | **PASS** | Header displays `Topic · Level · Q#/Total` (e.g. `Numerical Thinking · Think · 1/5`). No school, paper source, or grade information. |
| 7 | **Pro Practice** | **PASS** | Configurable practice screen with 6 Topics (*Numerical, Logical, Pattern, Visual, Verbal, Problem Solving*) and 4 Levels (*Explore, Think, Challenge, Master*). Unlimited for Pro. |
| 8 | **Question-bank organisation** | **PASS** | All pools clearly separated and documented (Baseline 50, Bank 100, Regenerated 100, Generated 1000). No silent merging. |
| 9 | **Visual renderer** | **PASS** | SVG/PNG renderer in `revamp/renderer/render.py` operational; 34 visual assets rendered in `revamp/bank/images/`. |
| 10 | **PSLE regression safety** | **PASS** | Zero edits to PSLE code or database resources. |
| 11 | **MathHero regression safety** | **PASS** | Zero edits to MathHero code, tables, buckets, or functions. |

---

## 5. Backend Logic Parity vs. MathHero

| Function / Table | MathHero Pattern | BrainActive Implementation | Parity Assessment |
| :--- | :--- | :--- | :--- |
| **`brainactive-submit-attempt`** | Client provides instant UI answer feedback; submits batch telemetry at session end to log attempts and update SGT-based streaks. | Client provides instant local UI feedback; submits batch attempt to log into `brainactive_attempts` and computes SGT streak in `brainactive_progress`. | **Exact Parity.** No blocking server-side validation during the quiz loop; streak increment formula (`diffDays === 1 ? streak + 1 : 1`) is identical. |
| **`brainactive_profiles` & `brainactive_progress`** | Device-level `user_id` mapped to referral code, Pro expiration timestamp, and daily streak counters. | Device-level `user_id` mapped to referral code, Pro expiration timestamp, and daily streak counters. | **Exact Parity.** Reuses MathHero's anonymous device ID + SGT timestamp model. Client local storage is primary for zero latency; server syncs on launch/completion. |
| **`brainactive-get-questions`** | Pulls active pool from DB matching criteria, shuffles, slices requested limit (5 or 10 Qs), supports retry by ID array. | Pulls active pool from `brainactive_questions`, filters by `topic`/`level`, shuffles, slices requested limit (5 Qs for Quick Test, 10 for Pro), supports retry by ID list. | **Exact Parity.** Session building and sampling mechanism is identical to MathHero; only question schema fields (Topic, Level, Reasoning Heuristic) differ. |
| **`brainactive-get-progress`** | Returns user profile, referral code, active streak, daily round count, and Pro entitlement. | Returns user profile, referral code, active streak, daily round count, and Pro entitlement from `brainactive_profiles` and `brainactive_progress`. | **Exact Parity.** Identical data shape and response structure adapted for BrainActive. |


