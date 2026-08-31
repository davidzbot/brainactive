# BrainActive QA Audit Tracker — Other Coder Work + MOE GEP/HA Review

> **Rule:** BrainActive scope only. No storage, Supabase DB, MathHero, or PSLE changes; current G275 question-bank repairs are documented below.
> **Date:** 2026-08-31
> **Branch:** `main` @ `1b28f8e` (coder fixes committed, working tree clean — re-audit 2026-08-31 09:15)
> **Auditor:** AI review (read-only)
> **Bank file:** `revamp/bank/brainactive_p3_question_bank_production.json` (732 questions: 21 validated_baseline_v041 / 436 ai_generated_not_approved / 275 regenerated_pending_ai1)
> **Related files:** `revamp/bank/deep_qa_tracker.json`, `revamp/bank/qa/AI1_QA_SPEC.md`, `revamp/upload_passing.py`
> **Historical note:** `deep_qa_tracker.json` contains the legacy 1,000-question bank. IDs 0103, 0576, 0605, 0638, 1128, and 1142 cited below are historical unless they are present in the current 732-question production bank.

---

## TODO List (as requested)

- [x] **1. QA review — audit report only** of other coder's finished work (billing, AdMob, ConfirmModal, pro page, app wiring)
- [x] **2. Compare Watch-Ad status-change flow** — homepage button & box changes related to Watch Ad / Bonus Round
- [x] **3. Review new questions/answers vs MOE GEP & HA guidelines**
- [x] **Tracker updated** — this file, grouped by filename

---

## 1) QA REVIEW — OTHER CODER'S WORK (per-file, with filename)

### 1.1 Summary — what the other coder changed (from `git status` + `git diff HEAD`)

| File | Change type |
|---|---|
| `src/utils/billing.ts` | **NEW** 155 LOC — Play Billing via `capacitor-plugin-cdv-purchase` |
| `src/utils/ad.ts` | Refactor reward-ad lifecycle, test/prod flag |
| `src/config/monetization.ts` | Test App ID + rewarded unit + basePlan constants |
| `src/pages/pro/index.tsx` | Real purchase/restore/pricing vs simulated timeout |
| `src/app.tsx` | Init billing + `appStateChange` entitlement refresh |
| `src/components/ConfirmModal/index.tsx` | Stacked layout (confirm primary full-width + cancel link) |
| `src/components/ConfirmModal/index.scss` | Typography/size/padding upscale |
| `src/components/QuotaOverlay/index.tsx` | *Not changed* (but part of Watch-Ad flow) |
| `src/pages/home/index.tsx` / `index.scss` | *Not changed* in diff (flow caller) |
| `capacitor.config.json` | AdMob `appId` mirrored to test ID |
| `package.json` / `package-lock.json` | Adds `capacitor-plugin-cdv-purchase@^13.17.2`, `@capacitor-community/admob@^8.0.0` |
| `android/app/src/main/res/**` | Launcher icon tint |
| `ADMOB_README.md` / `DEV_SETUP_GUIDE.md` | Docs for test IDs |

No `supabase/migrations/*`, no storage bucket changes, and no MathHero/PSLE paths. The 12 current G275 question-bank repairs are tracked below; no database or storage upload occurred.

### 1.2 Per-file audit

#### `src/utils/billing.ts` — PASS (lightweight, correct isolation)
- **What it does:** `store.register({id: brainactive_pro, type: PAID_SUBSCRIPTION, platform: GOOGLE_PLAY})`, `store.when().approved(applyApprovedTransaction)`, `initialize([GOOGLE_PLAY])`, `syncBillingEntitlement()` picks latest tx by `expirationDate`, `finish()` ack, notifies via `Taro.eventCenter 'brainactive_billing_entitlement_changed'`. Exposes `initializeBilling`, `refreshBillingEntitlement` (`store.update` + sync), `restoreBillingPurchases`, `purchaseSubscription(plan)` (`getOffer(offerId).order()`), `getSubscriptionPrices`.
- **Checks:** `isActiveTransaction` (`src/utils/billing.ts:21`) requires correct product id, `!isPending`, `approved|finished`, future `expirationDate`. Latest-tx sort (`:30`) correct. Web path returns `false`/`null` without native — intentional H5 no-op.
- **Issues (low):** `billingInitPromise` cleared to `null` on init error (`:85`, `:92`) allows retry but has tiny race if two callers await simultaneously. `sync` clears `subscriptionExpiry` when no active tx (`:55`) — will briefly revoke Pro on cold start until `update()` resolves (expected).
- **Maintainability:** Single source via `src/config/monetization.ts` constants, ~155 LOC, no cross-app leakage.

#### `src/utils/ad.ts` — PASS; production fixes applied
- **Before:** `USE_TEST_ADS = process.env.NODE_ENV==='development' || !Capacitor.isNativePlatform()`, `REWARD_AD_UNIT_ID = USE_TEST_ADS ? TEST : (PROD || TEST)`, listeners inline, `showRewardAd` always `return true` after `showRewardVideoAd()`, no dedup, no promise on `Dismissed`.
- **After (`src/utils/ad.ts:10-12,71-135`):** `USE_TEST_ADS = !ADMOB_USE_PRODUCTION_ADS || !Capacitor.isNativePlatform()` (now gated by `ADMOB_USE_PRODUCTION_ADS=false` for closed test — test-safe default), `REWARD_AD_UNIT_ID = USE_TEST_ADS ? TEST : PROD`, adds `removeListeners()` (`:77`), `bonusRoundGranted` dedup (`:90` `grantBonusRound`), returns `Promise<boolean>` that resolves on `RewardAdPluginEvents.Dismissed` with `rewardGranted` (`:109-119`), error path returns `rewardGranted` (`:135`) not always true.
- **Good:** Fixes prior "always success" bug; listener cleanup now explicit; keeps web fallback (`:69` `unlockBonusRound` directly).
- **Fixed:** Native no-fill/load/show errors no longer grant a bonus round without a rewarded event; the user receives a retry message and the flow returns `false`.
- **Fixed:** Preload loading state is reset after both success and failure, and concurrent ad calls share one in-flight promise.

#### `src/config/monetization.ts` — PASS (unchanged by QA fixes)
- **Before:** `ADMOB_APP_ID='ca-app-pub-xxxxxxxxxxxxxxxx~xxxxxxxxxxxx'`, `REWARDED=''`, offers `brainactive_pro@yearly` strings.
- **After (`src/config/monetization.ts:10-16`):** `ADMOB_APP_ID='ca-app-pub-3940256099942544~3347511713'` (Google test App ID, safe for internal track), `ADMOB_REWARDED_AD_UNIT_ID='ca-app-pub-8548627206908979/6689305699'`, `ADMOB_USE_PRODUCTION_ADS=false`, `SUBSCRIPTION_BASE_PLANS={yearly, monthly}`, `SUBSCRIPTION_OFFERS` built as `${product}@${basePlan}`. Separates product/basePlan from display names, removes empty-string fallback. Mirrors `capacitor.config.json` AdMob `appId`.

#### `src/pages/pro/index.tsx` — PASS (real billing, scope intact)
- **Before:** `handleUpgradePlan` used `setTimeout 800ms` + `setProExpiry(expiry)` simulation, `handleRestore` simulated `setTimeout 1000ms`, static `PLAN_PRICES` only.
- **After (`src/pages/pro/index.tsx:193-248`):** `useDidShow` calls `initializeBilling().then(getSubscriptionPrices).then(setPlayPrices)` and `refreshBillingEntitlement().then(refreshState)`, subscribes to `brainactive_billing_entitlement_changed` (`:217`), `handleUpgradePlan` → `await purchaseSubscription(plan)` (`:331` + `src/utils/billing.ts:131` `product.getOffer(offerId).order()`), `handleRestore` → `restoreBillingPurchases()`, price tag shows `playPrices?.yearly || t.annual_price`. Removes direct `setSubscriptionExpiry` simulation (now via `billing.ts`).
- **Note:** `Taro.showLoading/hideLoading` in `finally` may hide before Play sheet appears (minor UX race). No `quiz history`/`analysis` logic touched.

#### `src/app.tsx` — PASS
- **Diff (`src/app.tsx:6,55-79`):** Adds `import {initializeBilling, refreshBillingEntitlement} from '@/utils/billing'`, `CapApp.addListener('appStateChange', ({isActive})=> isActive && refreshBillingEntitlement())` with cleanup (`:60`), calls `initializeBilling()` after `initAdMob()` (`:79`). Minimal, no routing/nav change.

#### `src/components/ConfirmModal/index.tsx` + `index.scss` — PASS with 1 a11y nit
- **Before:** `View.modal-actions` with two `flex:1 Button` side-by-side, `title 26px`, `content 18px`, `btn 17px min-height 56px`.
- **After (`src/components/ConfirmModal/index.tsx:29`, `index.scss:31-50`):** Wraps in `.modal-header`, `title 26→28px weight 800`, `content 18→19px line 1.6`, `btn-confirm full-width min-height 56→60px font 17→19px weight 700`, `btn-cancel: View min-height 48px font 18px underline, margin-top 12px`. Matches MathHero upscale intent (larger container, hierarchy, touch target).
- **Fixed:** Cancel is rendered as a Taro `Button` again, preserving the stacked text-link styling while restoring native button semantics and touch behavior. Callers include Home and Quiz exit/bonus flows.

#### `capacitor.config.json` / `package.json` / icons / docs — PASS (unchanged by QA fixes)
- AdMob `appId` in config mirrors `monetization.ts` test ID (consistency). New dep `capacitor-plugin-cdv-purchase` correctly pinned. Launcher `ic_launcher*` tint change unrelated to logic, no functional risk.

**Overall Task 1 verdict (re-audit @ `1b28f8e`):** **PASS — fixes verified, lightweight, BrainActive-only.** No MathHero/PSLE table/storage/function/code touches. No bank upload. Two prior nits **closed**: (1) ConfirmModal cancel now `Button` (`src/components/ConfirmModal/index.tsx:36`), (2) ad no-fill error now returns `false` with retry (`src/utils/ad.ts:135-141`). Residual low cosmetic: `src/components/ConfirmModal/index.scss:69` `.btn-cancel` pending `background: transparent` to fully suppress Taro Button default fill (functional PASS).

---

## 2) WATCH-AD STATUS-CHANGE FLOW — Button & Box on Homepage (Before → After)

### 2.1 Files involved (filename-keyed)
- `src/pages/home/index.tsx` (caller, unchanged in this diff)
- `src/pages/home/index.scss` (styling, unchanged)
- `src/components/ConfirmModal/index.tsx` + `index.scss` (Unlock Bonus modal)
- `src/components/QuotaOverlay/index.tsx` + `index.scss` (quota-exhausted overlay with Watch-Ad button)
- `src/utils/storage.ts` (state: `FREE_ROUNDS_PER_DAY=2`, `MAX_AD_ROUNDS_PER_DAY=3`, `unlockBonusRound()`, `canWatchAdForRound()`, `canStartPractice()`)
- `src/utils/ad.ts` (reward handler, changed)

### 2.2 Before (HEAD)

**State:** `DailyUsage {roundsCompleted, bonusRounds}` in `src/utils/storage.ts:101`. Derived in `src/pages/home/index.tsx:266-270`:
```ts
adsLeft = MAX(0, 3 - bonusRounds)
bonusAvailable = bonusRounds>0 && roundsCompleted < (2 + bonusRounds)
```

**Boxes/Buttons:**
- **Hero `daily5-card` (`src/pages/home/index.tsx:539`):** CTA text branches:
  - `proStatus` → `daily_continue` (`handleStartQuickTest`)
  - `isBonusReady` → `daily_start_bonus` (`handleWatchAdClick` → navigates to `quick_test&origin=bonus`)
  - `remainingAds>0` → `daily_continue_free` (`handleWatchAdClick` → shows `ConfirmModal`)
  - else → `daily_come_back_tmr` + `daily_upgrade_pro`
- **Extra-Practice card (`src/pages/home/index.tsx:683`):** `class=extra-practice-section [disabled if !pro && !bonusReady && adsLeft<=0] [loading if isLoadingAd]` + `onClick=handleWatchAdClick`. Inner emoji `⚡/📺/⏳`, title switches `extra_practice_ready / extra_practice / extra_practice_limit` (`src/pages/home/index.tsx:690`), plus `extra-practice-start-btn Start` when `isBonusReady` (stopPropagation).
- **Header `usage-summary-box` (`:472`):** `usageSummaryText` + `motivationText` (`:340`): free-rounds → bonus-ready → ad-unlocks remaining → all-done.

**Click flow (`src/pages/home/index.tsx:385`, HEAD `src/utils/ad.ts:64`):**
1. `handleWatchAdClick`: if `pro` → start quiz; if `isBonusReady` → start bonus quiz; if `adsLeft<=0` → `setShowQuota(true)`; else `setShowAdConfirm(true)` (shows `ConfirmModal` title `ad_confirm_title` / content `ad_confirm_content`).
2. `handleConfirmAd`: `success = await showRewardAd()`; if success → `refreshState()` + toast.
3. `showRewardAd` (HEAD): `initAdMob()` → `rewardGranted=false` → `addListener(Rewarded)→rewardGranted=true` + `addListener(Dismissed)→ if(rewardGranted) unlockBonusRound()` → `preloadRewardAd()` → `showRewardVideoAd()` → **`return true` unconditionally**; `catch` → `showModal("Could not load… You get 1 bonus round")` → `unlockBonusRound()` + `return true`.

**Box/button visual before:** ConfirmModal side-by-side 56px buttons, 26/18px type — cramped per audit brief.

### 2.3 After (working tree)

**Homepage boxes/buttons logic — UNCHANGED** (no diff in `src/pages/home/index.tsx` / `index.scss`). Same `remainingAds/isBonusReady/proStatus` branches, same `extra-practice-section` `disabled/loading` classes, same `QuotaOverlay` path via `canStartPractice()` (`src/pages/home/index.tsx:376`).

**What changed that affects the homepage experience:**
- **`src/utils/ad.ts` state change:** `showRewardAd` now **returns `rewardGranted` not always `true`** (`src/utils/ad.ts:90-119`). Homepage `handleConfirmAd` (`src/pages/home/index.tsx:402`) does `setShowAdConfirm(false); setIsLoadingAd(true); success=await showRewardAd(); setIsLoadingAd(false); if(success){refreshState(); toast}` — now correctly **no refresh/toast if ad dismissed without reward** (before it refreshed even on dismiss without Rewarded). Also adds `bonusRoundGranted` dedup so `unlockBonusRound()` fires once even if `Rewarded` fires multiple times, and `removeListeners()` via closure (`:77`) prevents leak.
- **`src/components/ConfirmModal` size:** `Unlock Bonus Round` modal (and `Leave this practice round?` which reuses same `ConfirmModal` in `src/pages/quiz/index.tsx`) now **stacked**: primary `btn-confirm` full-width 60px/19px, secondary `btn-cancel` link 48px/18px underline, title 28px, content 19px, padding/spacing increased — matches MathHero upscale scale per `src/components/ConfirmModal/index.scss:31`. **Box change:** card feels larger, readable for P3; **Button change:** confirm is dominant CTA (was 50/50 split), cancel is secondary link — reduces mis-tap.
- **`src/utils/storage.ts` untouched:** quota 2 free + max 3 ad unlocks (total 5) unchanged.
- **`src/components/QuotaOverlay` unchanged** but benefits from same `ad.ts` fix when `Watch Ad` is tapped there (`src/components/QuotaOverlay/index.tsx:76`).

**End-to-end after:**
```
Tap extra-practice-section / daily5-cta (if adsLeft>0 & !bonusReady)
  → ConfirmModal (large title/content, primary CTA full-width)
  → handleConfirmAd sets isLoadingAd → extra-practice-section gets .loading (emoji ⏳) + home disables handleWatchAdClick re-entry
  → showRewardAd: init → listeners (Rewarded→grant once, Dismissed→resolve(success)) → preload → show → Dismissed resolves
  → homepage checks success===true ? refreshState (isBonusReady=true, adsLeft--, header usageSummary flips to "Bonus Round Ready!") else stays (no bonus)
  → next tap on same box now hits isBonusReady branch → navigates to bonus quiz (⚡ Start)
  → QuotaOverlay path similarly now only unlocks on actual reward (except no-fill fallback still grants once)
```

**Verify:** `src/utils/ad.ts:69` web fallback still `unlockBonusRound` directly; native path respects `ADMOB_USE_PRODUCTION_ADS` flag.

---

## 3) NEW QUESTIONS/ANSWERS vs MOE GEP & HA GUIDELINES

### 3.1 Scope & provenance (file: `revamp/bank/brainactive_p3_question_bank_production.json`)
- 732 items: 21 `validated_baseline_v041` (production baseline, e.g., `BA_P3_0001`, `0034`, `0039`, `0017-0021`, `0044-0047`), 436 `ai_generated_not_approved`, 275 `regenerated_pending_ai1`.
- **New worker Pilots:** `BA_P3_V01/02/04/05/06/07/09` (verbal pilots A1/F1 etc.) + deterministic `BA_P3_0060-0074` batch (e.g., `0060`, `0061`, `0066-0074`) — all carry `qa_status=ai_generated_not_approved` and `provenance.source_inspiration=v0.5 … Deterministic generator`.
- **Upload gate per `revamp/upload_passing.py:157` + `AI1_QA_SPEC.md:40`:** Only `canonical ∩ pass-only` (`approved`) should be `is_active=true` / `image_path` set. Current diff does NOT upload — audit therefore flags `ai_generated_not_approved` as **must not publish** until AI1 re-audit + human confirm.

### 3.2 MOE GEP / HA lens (P3 High-Ability — reasoning over recall, no secondary syllabus)

> The IDs in the historical-finding bullets below come from the legacy 1,000-question tracker unless explicitly listed in the current 732-question production bank. They are audit references, not current-bank upload candidates.
- **GEP HA expects:** novel problem solving, pattern/logic/spatial/verbal reasoning, non-routine heuristics, not content acceleration (no algebra, no area of non-rectangles, no formal logic notation). Vocabulary should be P3-accessible; difficulty from inference, not trick wording.
- **Validated baseline (21 items) — fits HA:**
  - `BA_P3_0001` (numerical `1,2,4,7,11,16→22` +1..+5) / `0002` (interleaved `3,5,7… / 6,12,24→48`) — pattern discovery, Explore→Think progression, P3 arithmetic only.
  - `BA_P3_0034/0007` ordering (`Tom>Sam>Lee`, 4-team merge `Yellow<Red<Blue<Green>`) — transitive deduction, clean.
  - `BA_P3_0011` syllogism (`All squares blue…→all squares small`) / `0016` contrapositive (`reads if Saturday OR rain → NOT reading ⇒ not Sat AND not raining`) — correct HA verbal logic.
  - `BA_P3_0039/0017/0018/0019/0021` rotation/reflection/cube-net/3D (`L corner top-left→top-right 90° cw`, `arrow up→down via 180°`, `b→d vertical mirror`, `cube net Y front→U back`, `dot top star front→right after 90° vertical right`) — spatial, visual_required with `image_path p3/…svg` and `visual_spec` matching.
  - `BA_P3_0044-0046` working-backwards ladder (1-step `+5=12→7`, 2-step `×2+3=15→6`, real context `bus 8 off 5 on→14→17`, 3-step with forward check) — heuristic progression Explore→Master.
- **New pilots — mixed, needs gating:**
  - **Strong HA (would pass AI1):** `V02` set-analogy (`cup/plate/bowl : rose/tulip/sunflower : apple/banana→orange` — category-to-category), `V05` square code (`E=25` via `5²`, trap `Y=25th letter`), `V06` alternating cipher (`DOG→GLJ +3/-3/+3 → PIG→SFJ`), `V09` 3-box deduction (`blue=book, red≠ball, green≠coin → green=ball` — constraint satisfaction), `0068` particular syllogism (`Some squares red + All red small → Some squares small` avoids over-generalise). These test inference, not vocab — HA-appropriate.
  - **Acceptable P3 verbal with nits:** `V01` part-whole (`leaf:tree :: page:book`), `V04` function odd-one (`clock/watch/timer vs ruler`), `V07` word manipulation (`TRAIN→RAINT, PLANT→LANTP: move first→end → HOUSE→OUSEH`). P3 wording, maybe low ceiling but not out-of-syllabus.
  - **Below-standard / Do NOT upload as-is (per `deep_qa_tracker.json` gep_quality=below-standard/reject + audit):**
    - Trivial/degenerate: `BA_P3_0605/0666` `TRAIN→RAINT` where answer `RAINT` is literally in the example (read-off, no inference), `0103` `5 is to 5 as 10 is to ?` identity, `0208` `5 is to 11 as 5 is to ?` degenerate.
    - Massive duplication (inflates bank, not HA): tree interval `(n-1)*gap` repeated 11× (`1128 5001 4 trees 2m`, `1143 5002 4 trees 3m`, `1210 7 trees 3m`, etc.), 3-letter codes `ABC→27` repeated 11× (`1142`), `gap=3 give=3` before/after 3× (`1203`), `TRAIN→RAINT` 3×, cube-net `1117/1171/0741/0765` near-identical, grid `0769/0814/0845/0759/0882` top-left→below→right duplicates.
    - Math errors / misleading text: `0576` `O,Q,T,X→?` explanation claims `24+4=20=T` (28→B), `0638` says gap grows by 1 but gap is constant +3.
    - Trivial deduction: `0411/0436/0303/0279` asks `Who sits at left/right end?` answer is stated verbatim in the stem.
    - Syllabus/vocab risk: `0100` `square+circle=9…` within P3 but `0040` trivial `star front vs ?` adds irrelevant marks.

### 3.3 Per-question outcomes (sample — full bank needs AI1 pass; do not publish ai_generated_not_approved)

| File: `revamp/bank/brainactive_p3_question_bank_production.json` — ID | Verdict | MOE GEP/HA fit | Note |
|---|---|---|---|
| `BA_P3_0001` `validated_baseline_v041` | PASS | HA pattern, Explore | keep |
| `BA_P3_0002` Think | PASS | interleaved ×2 | keep |
| `BA_P3_0034/0007` 2.1 ordering | PASS | transitive/merge | keep |
| `BA_P3_0011` 2.5 syllogism | PASS | transitive | keep |
| `BA_P3_0016` 3.5 logic | PASS | OR contrapositive | keep |
| `BA_P3_0039/0017/0018/0019/0021` spatial | PASS | rotation/net/3D | keep, visual matched |
| `BA_P3_0044-0046` 6.1 backwards | PASS | heuristic ladder | keep |
| `BA_P3_V01` verbal | REVIEW | P3 vocab ok, low ceiling | allow after AI1 |
| `BA_P3_V02` verbal set analogy | PASS | HA category reasoning | allow after AI1 |
| `BA_P3_V05` code square | PASS | infer square rule | allow after AI1 |
| `BA_P3_V06` cipher +3/-3 | PASS | alternating rule | allow after AI1 |
| `BA_P3_V09` box logic | PASS | constraint deduce | allow after AI1 |
| `BA_P3_0060/0061` ordering | REVIEW | clean but near-duplicate of `0034/0007` | dedup before publish |
| `BA_P3_0068` syllogism particular | PASS | avoids over-generalise | allow |
| `BA_P3_0605/0666` TRAIN→RAINT | **FAIL** | answer in example | **reject** — not HA |
| `BA_P3_0103` identity | **FAIL** | trivial | reject |
| `BA_P3_0576` letter pattern | **FAIL** | math error in explanation | reject |
| `BA_P3_0638` gap text | **FAIL** | misleading stem | rewrite |
| `BA_P3_1128 tree interval` (×11) | **FAIL** dup | (n-1)*gap repeated | keep 1, reject rest |
| `BA_P3_1142 ABC codes` (×11) | **FAIL** dup | 27 repeated | keep 1 |

**Rule applied:** Per `AI1_QA_SPEC.md:9-10`, any `visual_required` must have matching `p3/<id>.svg` + `visual_spec` (e.g., `BA_P3_0039.svg`, `0073.svg`). The upload gate now also requires an allowed canonical `qa_status`; current approved status is `validated_baseline_v041`. No `ai_generated_not_approved` or `regenerated_pending_ai1` question enters Supabase through `upload_passing.py` until its status is explicitly approved.

---

## QA Tracker (status)

| Task | Tracker entry | File(s) | Result | Action |
|---|---|---|---|---|
| 1 | Billing/AdMob wiring | `src/utils/billing.ts:1`, `src/utils/ad.ts:1`, `src/config/monetization.ts:1`, `src/app.tsx:1`, `src/pages/pro/index.tsx:1`, `revamp/upload_passing.py:28` | **PASS (fixed)** | Billing IDs/production config unchanged; `src/utils/ad.ts:1` now dedups (`activeRewardAdPromise:65`, `finally isLoading:59`, `preload check:124`) and denies free round on no-fill (`:135-141`); `revamp/upload_passing.py:28` adds `APPROVED_QA_STATUSES={'validated_baseline_v041'}` gate + `qa_status` required field (`:94`) + `status_blocked` hold. |
| 1 | Modal scale | `src/components/ConfirmModal/index.tsx:1`, `index.scss:1` | **PASS (fixed)** | Visual upscale retained; cancel action restored to `Button` (`src/components/ConfirmModal/index.tsx:36`); re-audit notes `index.scss:69` should add `background:transparent` to fully clear Taro default. |
| 2 | Watch-Ad box/button | `src/pages/home/index.tsx:266-400,683`, `src/utils/ad.ts:71`, `src/utils/storage.ts:95`, `src/components/QuotaOverlay/index.tsx:1` | PASS | Homepage boxes unchanged; reward status remains gated on `Rewarded`; preload/re-entry/error handling hardened. |
| 3 | Question bank GEP/HA | `revamp/bank/brainactive_p3_question_bank_production.json` + `revamp/bank/qa/G275_QA_TRACKER.json` + `G275_QA_REPORT.md` | REVIEW (12 repaired) | G081–G090 ranking defects and G146/G152 sequence defects are corrected; all 275 G-items now match, but all remain `regenerated_pending_ai1`. Upload gate still requires explicit approved `qa_status`; no DB/storage upload occurred. |

**Question-bank repair update (2026-08-31):** The authoritative bank now contains corrections for `BA_P3_G081`–`G090`, `G146`, and `G152`. `G275_QA_TRACKER.json` is synchronized at 275 matching answers with no critical/sequence highlights; `G275_QA_REPORT.md` records the repairs. The 12 records remain `regenerated_pending_ai1`, and no records were promoted or uploaded.

**Next gate:** Run AI1 per `revamp/bank/qa/AI1_QA_SPEC.md` over the repaired records, obtain human confirmation, then dedup current-bank repeats and obtain explicit approval status before `revamp/upload_passing.py` promotes any generated question. Historical `deep_qa_tracker.json` IDs must not be treated as current-bank fixes.
