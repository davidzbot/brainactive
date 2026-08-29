# BrainActive P3 Content & Database Handover Guide

**Target Audience:** Content & Backend Deployment Worker  
**Product:** BrainActive — Build Thinking Skills for Singapore Primary 3 High Ability  
**Date:** 2026-08-29  

---

## 1. Overview of Completed Architecture & Client State

The frontend and client networking layers are **100% complete, type-checked, and verified**:
- **Taro H5 Build:** `npm run build:h5` compiled cleanly (`dist/h5`).
- **Capacitor Android Sync:** `npx cap sync android` synchronized.
- **TypeScript:** `npx tsc --noEmit` passed with 0 errors.
- **Strict Monetisation Rule:** 2 Free rounds/day + up to 3 Rewarded-Ad rounds (max 5 rounds / 25 questions per day). Unlimited for Pro users.
- **Client Question Consumer:** The app consumes questions via Edge Function `brainactive-get-questions` and renders SVG/PNG images seamlessly via public Supabase bucket URLs.

---

## 2. Database Schema & Tables

All BrainActive backend resources are **completely isolated** from MathHero and PSLE tables.

Migration file ready to run:  
[`supabase/migrations/20260829000000_brainactive_schema.sql`](file:///c:/Projects/brainactive-android/supabase/migrations/20260829000000_brainactive_schema.sql)

### Tables Created by Migration:

### A. `public.brainactive_questions`
| Column | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(64) PRIMARY KEY` | Unique Question ID | `'BA_P3_0001'` |
| `domain` | `VARCHAR(64) NOT NULL` | Domain slug | `'numerical_reasoning'`, `'logical_reasoning'`, `'pattern_abstract'`, `'visual_spatial'`, `'verbal_reasoning'`, `'problem_solving'` |
| `topic` | `VARCHAR(64) NOT NULL` | UI Topic Display Name | `'Numerical Thinking'`, `'Logical Thinking'`, `'Pattern & Abstract'`, `'Visual & Spatial'`, `'Verbal Reasoning'`, `'Problem Solving'` |
| `skill` | `VARCHAR(32) NOT NULL` | Skill taxonomy code | `'1.3'`, `'2.1'` |
| `archetype` | `VARCHAR(64) NOT NULL` | Question pattern archetype | `'weight_system'`, `'spatial_matrix'` |
| `level` | `VARCHAR(32) NOT NULL` | Difficulty Tier | `'Explore'`, `'Think'`, `'Challenge'`, `'Master'` |
| `difficulty` | `VARCHAR(32) NOT NULL` | Relative difficulty | `'easy'`, `'medium'`, `'hard'` |
| `question_type` | `VARCHAR(32) NOT NULL` | Default `'multiple_choice'` | `'multiple_choice'` |
| `question` | `TEXT NOT NULL` | The question stem | `'A triangle and a square together weigh 11 kg...'` |
| `options` | `JSONB NOT NULL` | 4 MCQ options array | `[{"id": "A", "text": "triangle"}, {"id": "B", "text": "square"}, ...]` |
| `answer` | `VARCHAR(8) NOT NULL` | Correct option ID | `'B'` |
| `explanation` | `TEXT NOT NULL` | Step-by-step thinking process | `'Add all three pair-weights: 2 × (tri + sq + circ) = 28 kg...'` |
| `reasoning` | `TEXT` | Core Thinking Strategy / Heuristic | `'Solving a 3-variable balance system by summing pairs.'` |
| `tags` | `TEXT[]` | Optional indexing tags | `ARRAY['balance_scale', 'algebraic_thinking']` |
| `visual_required`| `BOOLEAN DEFAULT FALSE` | Flag if image is required | `true` or `false` |
| `visual_spec` | `JSONB` | Optional SVG generation spec | `{ "type": "balance_scale", ... }` |
| `image_path` | `TEXT` | Relative path inside bucket | `'p3/BA_P3_0017.svg'` (or `.png`) |
| `is_active` | `BOOLEAN DEFAULT TRUE` | Active for serving | `true` |

### B. Other Tables (Created automatically):
- `public.brainactive_attempts`: User quiz attempt logs & telemetry.
- `public.brainactive_profiles`: User profile, referral code, and Pro expiry status.
- `public.brainactive_referrals`: 7-day Pro access referral redemptions.
- `public.brainactive_progress`: Streak count and daily round tracking.

---

## 3. Storage Bucket & Image Asset Guidelines

* **Bucket Name:** `brainactive-assets` (Public bucket, created by migration).
* **Directory Structure inside bucket:**  
  `p3/`
* **File Naming:**  
  `p3/BA_P3_xxxx.svg` (or `p3/BA_P3_xxxx.png`)
* **How App Loads Images:**  
  The app calls `getBrainActiveAssetUrl(image_path)` which constructs:  
  `https://pgvdsztkhqrwfbpwhugz.supabase.co/storage/v1/object/public/brainactive-assets/p3/BA_P3_xxxx.svg`

---

## 4. Edge Functions to Deploy

The following 4 Edge Functions are created in [`supabase/functions/`](file:///c:/Projects/brainactive-android/supabase/functions):

1. **`brainactive-get-questions`**:
   - `GET /functions/v1/brainactive-get-questions?mode=quick_test&limit=5`
   - `GET /functions/v1/brainactive-get-questions?mode=pro_practice&topic=Numerical+Thinking&level=Think&limit=10`
   - `GET /functions/v1/brainactive-get-questions?mode=retry&ids=BA_P3_0001,BA_P3_0002`
2. **`brainactive-submit-attempt`**:
   - `POST /functions/v1/brainactive-submit-attempt`
   - Ingests batch attempt records and updates SGT daily streaks.
3. **`brainactive-get-progress`**:
   - `GET /functions/v1/brainactive-get-progress?user_id=ba_usr_...`
   - Returns streak count, Pro validity, and referral code.
4. **`brainactive-apply-referral`**:
   - `POST /functions/v1/brainactive-apply-referral`
   - Grants 7 days of Pro access to both referrer and referee.

---

## 5. Deployment Step-by-Step Checklist for Worker

1. **Step 1: Execute Database Migration**  
   Run [`supabase/migrations/20260829000000_brainactive_schema.sql`](file:///c:/Projects/brainactive-android/supabase/migrations/20260829000000_brainactive_schema.sql) in Supabase SQL editor (or via `supabase db push`).
2. **Step 2: Upload Images to Supabase Storage**  
   Upload the rendered SVGs/PNGs into the `brainactive-assets` bucket under the `p3/` folder (e.g. `p3/BA_P3_0017.svg`).
3. **Step 3: Ingest Production Questions**  
   Insert the validated question JSON dataset into `public.brainactive_questions`. Ensure `image_path` is populated for all items where `visual_required = true` (e.g., `'p3/BA_P3_0017.svg'`).
4. **Step 4: Deploy Edge Functions**  
   Run:
   ```bash
   supabase functions deploy brainactive-get-questions
   supabase functions deploy brainactive-submit-attempt
   supabase functions deploy brainactive-get-progress
   supabase functions deploy brainactive-apply-referral
   ```
5. **Step 5: Verify in App**  
   Launch the app (`npm run dev:h5` or Android build) and verify:
   - Daily Quick Test loads 5 questions from `public.brainactive_questions`.
   - Visual questions display the rendered SVGs correctly.
   - Submitting a quiz increments streak and records attempt telemetry.
