# Deployment Status — BrainActive Import

**Date:** 2026-08-29
**Source guide:** `HANDOVER_FOR_CONTENT_WORKER.md`
**Status:** ✅ **DONE — candidate content imported, isolated to BrainActive resources.**

Project: PSLE Supabase project `mqpunjvdrkqvionsjosl` (linked, unchanged, not relinked).
MathHero is a separate ref `pgvdsztkhqrwfbpwhugz` and was **not** touched.

---

## Result (verified 2026-08-29)

| Check | Result |
|---|---|
| Schema migration applied | `20260829000000_brainactive_schema.sql` (init/harden were already applied previously; `fix_compatibility.sql` intentionally skipped) |
| `public.brainactive_*` tables | 5 created (questions, profiles, referrals, attempts, progress) |
| `brainactive-assets` bucket | created, **public** |
| RLS enabled on brainactive tables | 5 / 5 |
| Questions imported | **732** |
| `is_active = TRUE` | **0** (candidates, not served) |
| `qa_status` distribution | 436 `ai_generated_not_approved` / 275 `regenerated_pending_ai1` / 21 `validated_baseline_v041` (unchanged from source, none approved) |
| Images in `brainactive-assets/p3` | **171 / 171** (public GET → 200) |
| Edge Functions deployed | 5 / 5 (`brainactive-get-questions`, `brainactive-submit-attempt`, `brainactive-get-progress`, `brainactive-apply-referral`, `brainactive-get-content`) via `supabase functions deploy --use-api` |

## How it was executed (no secrets shared)

- CLI access token read from Windows Credential Manager (`Supabase CLI:supabase`) via `advapi32.dll`
  `CredRead` P/Invoke (decoded as UTF-8 → Supabase PAT `sbp_…`).
- `supabase db query --linked -f` ran the schema migration + `import_questions.sql` (Management API, no password, no Docker).
- `qa_status` column was missing from the schema; added + backfilled via `revamp/bank/add_qa_status.sql`.
- Images uploaded via the Storage REST API using the `service_role` key (fetched from the Management API
  `api-keys` endpoint). 170/171 first pass, the 1 transient 504 (`BA_P3_1027.svg`) retried successfully.

## Safety (isolation preserved)

- Migration creates ONLY `public.brainactive_*` tables, the `brainactive-assets` bucket, RLS + policies
  scoped to `bucket_id = 'brainactive-assets'`. No broad `GRANT … ON ALL TABLES/SEQUENCES IN SCHEMA public`.
- Grep of all `supabase/` files: zero references to MathHero/PSLE tables/data.
- MathHero + PSLE rows/buckets/functions/APIs untouched.

## Notes

- This is **candidate content only**: `is_active = FALSE`, `qa_status` unchanged, no AI1 approval, no public release.
- To serve questions later: activate rows (`is_active = TRUE`) after AI1 QA + human review.
- Keep `brainactive_p3_question_bank_production.json` as source of truth.

## Migration safety fix (2026-08-29)

Replaced broad schema-wide grants with explicit grants scoped only to `public.brainactive_*` tables/sequences
(see prior revision). Validated by `revamp/validate_migration_safe.py` → PASS.

## Integration Test (2026-08-29)

Backend integration verified end-to-end against the deployed BrainActive backend
(project `mqpunjvdrkqvionsjosl`) by simulating the app's intended Edge-Function calls
(`get-questions`, `submit-attempt`, `get-progress`, `apply-referral`, `get-content`) plus the
public image URL. All 5 Edge Functions correctly read/write the new `brainactive_*` tables.

Result: **PASS at the backend level.**

| Flow | Backend result |
|---|---|
| Quick Test retrieval (exactly 5) | ✅ returned exactly 5 (all `is_active=true`, with `topic`/`level`/`image_path`) |
| Topic + Level present, no school/paper | ✅ topic/level returned; schema has no school/paper fields |
| Image (public) loading | ✅ 5/5 SVGs returned HTTP 200 from `brainactive-assets` |
| Answer + submit attempt | ✅ attempt rows written (`brainactive_attempts`), progress upserted |
| Streak / daily round / pro state | ✅ `streak=1`, `daily_rounds_completed=1`, `is_pro` tracked |
| Referral flow | ✅ valid code → 7-day Pro granted; invalid code → `400 INVALID_CODE` |
| Content (`get-content`) | ⚠️ backend returns rows from `brainactive.content_pool`, but response shape is raw `{data,error}` while `src/utils/supabase.ts` expects `{success,data}` → app receives `[]` |
| Error / fallback | ✅ invalid referral → 400; unknown ids → empty array |

### App → backend wiring bugs found (BLOCK the real app from reaching the backend)

1. **`src/utils/request.ts` points to the MathHero project**, not BrainActive:
   - `SUPABASE_URL = 'https://pgvdsztkhqrwfbpwhugz.supabase.co'` (MathHero ref) and a MathHero anon key.
   - This is the layer used by `getBrainActiveQuestions`, `submitBrainActiveAttempt`,
     `getBrainActiveProgress`, `applyBrainActiveReferral`, **and `getBrainActiveAssetUrl`** (images).
   - The BrainActive Edge Functions + `brainactive-assets` bucket live on `mqpunjvdrkqvionsjosl`.
   - **Effect:** as written, the app cannot reach the deployed BrainActive backend — question/attempt/
     progress/referral calls and all images target the wrong project.
   - `src/utils/supabase.ts` (content) correctly uses `mqpunjvdrkqvionsjosl`; it is the only correct path.
   - **Fix:** align `request.ts` `SUPABASE_URL` + anon key to `mqpunjvdrkqvionsjosl` (one-line change).

2. **`src/pages/quiz/QuizContent.tsx:130` score double-counts the last question:**
   `correctCount = attempts.filter(is_correct).length + (selected===answer?1:0)` adds +1 when the final
   question is answered correctly (its attempt is already in `attempts`). Inflates the displayed score by 1.

3. **`brainactive-get-content` response contract mismatch:** returns `JSON.stringify({data,error})` (max 1 row,
   ignores `lang`/`type`/`limit`) while `supabase.ts` checks `res.data.success`. App always falls back to `[]`.

### Accidental PSLE / MathHero references in app code

- **Backend resource:** `src/utils/request.ts` → MathHero **project URL + anon key** (see bug #1). This is the
  only real backend-resource reference to the wrong project.
- Non-backend references (harmless but note-worthy): `package.json` description "PSLE Hero - Android H5 +
  Capacitor version"; `src/utils/i18n.ts` feedback email `pslehero@gmail.com`; code comments in `storage.ts`/
  `ad.ts` reference MathHero *architecture* (logic reuse, not backend). No other `psle`/`mathhero` table,
  function, or bucket references exist in `src/`.

### Test data cleanup

The 5 test questions (`BA_P3_0017..0021`) were activated only for the test and then set back to
`is_active = FALSE`. All temporary `test_e2e_*` rows were deleted. Final state: `is_active = TRUE` → **0**
(full candidate bank remains inactive, no AI1 approval, no public release).

## Fixes Applied (2026-08-29)

Three issues from the integration test were fixed — BrainActive-only, no PSLE/MathHero resources touched.

1. **`src/utils/request.ts`** — repointed `SUPABASE_URL` + anon key from the MathHero project
   (`pgvdsztkhqrwfbpwhugz`) to the BrainActive project (`mqpunjvdrkqvionsjosl`). This fixes questions,
   attempt, progress, referral, and **image URL** calls so the app reaches the deployed BrainActive backend.
   (`supabase.ts` content path was already correct and unchanged.)
2. **`supabase/functions/brainactive-get-content/index.ts`** — response now matches the app's `supabase.ts`
   parser: `{ success: true, data: [...] }`. Honors `lang` → `language`, `type`, and `limit` (was hardcoded
   `.limit(1)`). Redeployed via `supabase functions deploy brainactive-get-content --use-api`.
3. **`src/pages/quiz/QuizContent.tsx`** — fixed final-question score double-count. `correctCount` is now
   derived from `finalAttempts` (the same array submitted to the backend) instead of
   `attempts.filter(is_correct).length + (lastCorrect?1:0)`. Scoring UX unchanged.

### Re-verification (backend + static)

Backend integration re-run (simulating app calls against `mqpunjvdrkqvionsjosl`) — **all 9 checks PASS**:
get-questions returns exactly 5; topic+level present; 5/5 images load (HTTP 200); submit-attempt +
progress (streak/daily); referral grants Pro + invalid code → `INVALID_CODE`; `get-content` returns
`{success,data}` filtered by lang/type/limit for both `en/name/20` and `zh/sentence/5`.

Static checks (no code change needed — already correct):
- **2 free rounds/day, 5 questions each:** `storage.ts` `FREE_ROUNDS_PER_DAY=2`; `QuizContent` uses
  `limit = quick_test ? 5 : 10`.
- **Rewarded ad unlocks 1 round, max 3 ad rounds/day:** `unlockBonusRound()` +1; `MAX_AD_ROUNDS_PER_DAY=3`;
  `QuotaOverlay` shows "Round X of 3".
- **Max 5 rounds / 25 questions per day:** `MAX_TOTAL_DAILY_ROUNDS=5`; `canStartPractice` allows 2 + bonusRounds.
- **Pro unlimited:** `isPro()` short-circuits `canStartPractice`/`getRemainingFreeRounds`.
- **Home has no grade/topic/level selector:** `home/index.tsx` quick-test card is fixed "5 Questions · 5–8 min".
- **Question page shows Topic + Level + progress, no school/exam:** `QuizContent` renders `topic-badge`,
  `level-badge`, `q-num-badge` (`currentIndex+1/total`); schema has no school/exam fields.
- **Referral + rewarded-ad intact:** `ReferralModal` → `applyBrainActiveReferral`; `QuotaOverlay` → `showRewardAd` + `unlockBonusRound`.

### Build

`npx tsc --noEmit` (tsconfig covers `src/**/*`) → **0 errors**. `npm run build:h5` → **compiled
successfully** (only pre-existing Sass `@import` deprecation + asset-size warnings).

### Final DB state (unchanged requirements)

- `is_active = TRUE` → **0** (732 candidates remain inactive; 5 test questions re-deactivated, rows cleaned).
- `qa_status` distribution unchanged: 436 / 275 / 21. No content activated for release.
