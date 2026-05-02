---
name: admob-troubleshooter
description: Diagnosing and fixing AdMob rewarded ad integration issues in Capacitor/Taro projects. Use when ads are not showing, 'preparing session' is slow, or platform-specific logic is being bypassed.
---

# AdMob Rewarded Ad Troubleshooting & Optimization

This skill provides a systematic workflow for diagnosing and fixing common AdMob issues in Capacitor + Taro projects.

## Core Issues Solved

1.  **Platform Detection Bug:** `process.env.TARO_ENV === 'h5'` is always true in Capacitor assets, causing ad logic to be bypassed on Android/iOS.
2.  **Slow Initialization:** Waiting for user click to initialize AdMob causes long "Preparing" delays.
3.  **Ad Fill Failures:** Lack of preloading leads to "No Fill" errors when the user wants to watch.
4.  **Zombie Listeners:** Multiple event registrations causing memory leaks or multiple reward triggers.

## Diagnostic Workflow

### 1. Trace Execution Path
Verify the button click actually triggers the ad function. Add instrumentation logs:
- `[AD_DEBUG] CLICKED_WATCH_AD`
- `[AD_DEBUG] ENTER showRewardAd`

### 2. Check Platform Detection
DO NOT use `TARO_ENV`. Use `Capacitor.getPlatform()`:
```typescript
import { Capacitor } from '@capacitor/core';
const platform = Capacitor.getPlatform(); // 'android', 'ios', or 'web'
```

### 3. Verify SDK State
Check if `AdMob.initialize()` has completed. Add logs:
- `[AD_DEBUG] ADMOB_INIT_SUCCESS`

## Implementation Patterns

### Early Initialization & Preloading
Initialize the SDK at app launch and fetch the first ad immediately.

```typescript
export async function initAdMob() {
  const platform = Capacitor.getPlatform();
  if (platform === 'web') return;
  
  await AdMob.initialize({ ... });
  setupGlobalListeners();
  preloadRewardAd(); // Fetch first ad in background
}
```

### Chain Preloading
Always fetch the *next* ad after the current one is closed or fails.

```typescript
AdMob.addListener(RewardAdPluginEvents.Dismissed, () => {
  preloadRewardAd(); // Always be ready for the next request
});
```

### Robust Fail-Open Logic
Preserve user experience by unlocking features even if Google has no ads available (Fill Rate issues).

```typescript
const finish = (success: boolean) => {
  if (success) grantReward();
  else grantReward(); // Fail-open: don't block user for Google's failures
};
```

## Professional Logging Flow
Expect this sequence for a healthy integration:
1. `[AD_DEBUG] ADMOB_INIT_SUCCESS`
2. `[AD_DEBUG] AD_LOADED` (background)
3. `[AD_DEBUG] CALLING_SHOW` (on click)
4. `[AD_DEBUG] REWARD_EARNED`
5. `[AD_DEBUG] AD_CLOSED`
6. `[AD_DEBUG] LOADING_AD` (fetching next)
