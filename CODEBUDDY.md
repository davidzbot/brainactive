# CODEBUDDY.md

This file provides guidance to CodeBuddy Code when working with code in this repository.

## Repository scope

BrainActive is a Taro 4 + React 18 + TypeScript application delivered as H5 and wrapped for Android with Capacitor 6. The backend is Supabase PostgreSQL plus Edge Functions. Styling is SCSS. The product is bilingual (English/Chinese) and targets Singapore Primary 3 high-ability thinking practice.

Keep BrainActive resources isolated from MathHero, PSLE, and the legacy Brain Plan resources. Do not mix their tables, storage buckets, functions, assets, or question banks.

## Commands

Run commands from the repository root (`C:/Projects/brainactive-android`).

### Install and development

```bash
npm install
npm run dev:h5              # Taro H5 watch build
npm run build:h5            # Production H5 build into dist/
npx cap sync android        # Copy dist/ and update Capacitor Android plugins
npm run build:android       # H5 build followed by Capacitor Android sync
npm run open:android        # Open the Android project in Android Studio
```

Taro configuration is in `config/index.js`; source is `src/`, output is `dist/`, and the `@/*` alias maps to `src/*`. Capacitor uses `dist/` as `webDir` and the Android application ID is `com.brainactive.app`.

### Static checks

```bash
npx tsc --noEmit
```

TypeScript is strict and configured by `tsconfig.json`. There is no root `lint`, `test`, `typecheck`, or formatter script in `package.json`.

### Tests

There are no first-party TypeScript unit/integration tests under `src/`, and no Supabase function test suite. The Android project contains Capacitor template tests, but the instrumentation test has a stale package-name assertion and is not a reliable product baseline.

If Android tests are needed, use the Gradle wrapper from the repository root:

```bash
android/gradlew.bat test
android/gradlew.bat :app:testDebugUnitTest --tests "com.example.TestClass.testMethod"
android/gradlew.bat lint
android/gradlew.bat assembleDebug
```

The single-test command is the standard Gradle/JUnit selector; replace the class and method with a real test. Do not assume a passing Android test until the stale Capacitor template assertion is addressed.

### BrainActive content QA tools

Content tooling is under `revamp/`. These scripts may write JSON, rendered assets, or Supabase resources, so inspect their paths and QA status before running them.

```bash
# validate_import.py uses paths relative to revamp/bank/
python -c "import os,runpy; os.chdir('revamp/bank'); runpy.run_path('validate_import.py')"
python revamp/bank/validate_bank.py
python revamp/bank/generate_gapfill.py
python revamp/renderer/render.py revamp/bank/gapfill_candidates.json revamp/bank/gapfill_images
python revamp/bank/qa_gapfill.py
```

The production question flow is QA-gated. New questions must remain candidate/pending until structural checks, answer review, visual checks, and human approval pass. Upload only approved BrainActive questions and matching assets through the existing upload/activation scripts. Never treat generated JSON as production-approved by default.

## High-level architecture

### Frontend shell and pages

- `src/app.tsx` owns application startup, bilingual onboarding, local initialization, native back handling, and AdMob initialization.
- `src/app.config.ts` registers the five Taro pages: home, quiz, result, pro, and legacy task.
- `src/pages/home/` is the local-first dashboard and navigation entry point. It reads streak, quota, Pro, history, and wrong-question state from storage and opens modal overlays.
- `src/pages/quiz/QuizContent.tsx` loads questions, handles answer/skip/swipe state, images, retry behavior, scoring, local history, and attempt submission. It uses `mode=quick_test`, `pro_practice`, or `retry`.
- `src/pages/result/` consumes score/time route parameters and local quiz state to show results, retry mistakes, share, and navigation.
- `src/pages/pro/` calculates most analysis from local quiz history and synchronizes Pro/progress state with Supabase. Subscription behavior is currently simulated rather than backed by a billing plugin.
- `src/pages/task/` is a separate legacy cognitive-training flow with names, numbers, colors/shapes, cities, and sentences. It uses the older content-pool API and quota system; do not assume it shares the quiz question flow.

### Client data and state flow

- `src/utils/storage.ts` is the local persistence layer. It uses `localStorage` keys prefixed with `ba_` for device identity, language, daily usage, streaks, Pro state, wrong questions, and quiz history.
- The frontend has no Supabase Auth session. Requests identify the device with `x-device-id` and locally generated user IDs.
- `src/utils/request.ts` is the main BrainActive request layer. It builds Supabase requests, question queries, attempt payloads, progress/referral calls, Ask Hero calls, and public URLs for the `brainactive-assets` bucket.
- `src/utils/supabase.ts` supports the legacy task content-pool flow separately.
- `src/utils/ad.ts` owns rewarded-ad behavior; H5/non-native behavior is simulated and native behavior uses Capacitor AdMob.
- `src/components/` contains reusable BrainActive UI, including ConfirmModal, QuotaOverlay, ReferralModal, SettingsModal, AskHero, and Pro analysis/collection components.

### BrainActive question serving

`supabase/functions/brainactive-get-questions/index.ts` serves active rows from `public.brainactive_questions`. It applies topic and level filters, paginates the complete active pool, randomizes candidates, and applies Quick Quiz diversity selection. Retry mode fetches requested active IDs directly. Keep normal `pro_practice` retrieval behavior separate from Quick Quiz balancing.

The client uses a five-question fallback in `src/pages/quiz/QuizContent.tsx` when the remote function returns no usable data. Do not change fallback, scoring, retry, or attempt semantics when changing the backend sampler.

### Supabase schema and functions

The current isolated migration is `supabase/migrations/20260829000000_brainactive_schema.sql`. It creates:

- `public.brainactive_questions`
- `public.brainactive_profiles`
- `public.brainactive_referrals`
- `public.brainactive_attempts`
- `public.brainactive_progress`
- public storage bucket `brainactive-assets`

Configured Edge Functions are listed in `supabase/config.toml`:

- `brainactive-get-content`
- `brainactive-get-questions`
- `brainactive-submit-attempt`
- `brainactive-get-progress`
- `brainactive-apply-referral`

`brainactive-ask-hero` exists under `supabase/functions/` but is not currently registered in `supabase/config.toml`; deploy/register it before relying on it in a new environment.

The older `brainactive` schema/content pool is used by `brainactive-get-content`, while newer quiz/progress/attempt flows use `public.brainactive_*` tables. Check the function source and migration before changing either path.

### Content and visual asset pipeline

The content source and research pipeline are under `revamp/`:

- `revamp/research/` contains Singapore GEP/MOE/HAL context and archetype research.
- `revamp/curriculum/brainactive_p3_skill_framework.md` defines six domains and the skill taxonomy.
- `revamp/curriculum/brainactive_p3_content_blueprint.md` defines progression from Explore to Master.
- `revamp/bank/brainactive_p3_question_bank.json` is the large local development bank.
- `revamp/bank/brainactive_p3_question_bank_production.json` is the production candidate bank.
- `revamp/bank/transform_import.py` creates database-shaped import data.
- `revamp/bank/generate_1000.py` creates deterministic parameterized candidates but is not an approval gate and can rewrite its source path.
- `revamp/renderer/render.py` turns deterministic `visual_spec` values into SVG/PNG assets.
- `revamp/bank/validate_bank.py`, `validate_import.py`, and the QA scripts perform structural and asset checks.

Use original reasoning content only. Do not copy commercial/past-paper wording, answer choices, or diagrams. The product may use public research and sample papers as archetype/format references, but must not claim MOE/GEP affiliation or predict selection outcomes. Difficulty should increase through rule complexity, constraints, distractor quality, and integrated reasoning—not merely larger numbers or harder vocabulary.

For visual questions, preserve the question ID/image basename relationship and store relative paths such as `p3/BA_P3_xxxx.svg`; `getBrainActiveAssetUrl()` constructs the public URL. Do not mix BrainActive assets with other product buckets.

### Android/Capacitor boundary

`android/` is the native wrapper around the generated H5 bundle. `android/app/src/main/assets/public/` is generated by Capacitor sync, and files such as `android/capacitor.settings.gradle` explicitly warn against manual edits. Change web code/config first, then run the appropriate Capacitor sync/build command.

Native integration is intentionally thin (`MainActivity` extends `BridgeActivity`). AdMob configuration is duplicated across Capacitor/native configuration; billing/IAP is not installed. Check `capacitor.config.json`, Android manifest/build files, and `src/config/monetization.ts` together before changing monetization or app identity.

## Important repository caveats

- `README.md` documents the Taro/Capacitor/Supabase architecture and common commands, but its historical deployment-status section is stale. Trust current code and live configuration over that old status text.
- Supabase functions currently have `verify_jwt = false` in `supabase/config.toml`; device IDs and function logic are relied on for access. Review RLS and function behavior before changing data boundaries.
- There is no package-manager lint/test command to run by default. The reliable baseline checks are `npx tsc --noEmit`, the relevant Python/content QA scripts, and `npm run build:h5` or `npm run build:android`.
- Preserve unrelated working-tree changes. Before editing a file, inspect its current diff and avoid broad refactors.
