---
name: admob-troubleshooter
description: Diagnosing and fixing AdMob rewarded ad integration issues in Capacitor/Taro projects. Use when ads are not showing, 'preparing session' is slow, or multiple ads trigger on one click.
---

# AdMob Rewarded Ad Troubleshooting & Optimization

This skill provides a systematic workflow for diagnosing and fixing common AdMob issues in Capacitor + Taro projects.

## Core Best Practices (Mandatory)

1.  **Event-Driven Logic:** DO NOT rely on durations (e.g. 30s) or safety timeouts to grant rewards. Rewards must be granted strictly based on the `Rewarded` event.
2.  **Concurrency Guard:** Use a global `isShowingAd` lock to prevent multiple concurrent ads from triggering on a single user click. 
3.  **Platform Detection:** DO NOT use `TARO_ENV`. Use `Capacitor.getPlatform()` to ensure logic runs on Android/iOS but mocks on Web.
4.  **Resource Cleanup:** Always remove all event listeners and clear timeouts immediately after the ad flow finishes to prevent memory leaks and double rewards.
5.  **Single-Execution Guard:** Use a `finished` flag inside the Promise to ensure the internal `finish()` function is called exactly once.

## Implementation Pattern

### The `showRewardAd` Function

```typescript
let isShowingAd = false; // Global Lock

export async function showRewardAd() {
  if (isShowingAd) return false;
  
  isShowingAd = true;
  console.log('[AD_DEBUG] SHOW_CALLED');

  return new Promise((resolve) => {
    let finished = false;
    let rewardEarned = false;

    const finish = (rewarded: boolean) => {
      if (finished) return;
      finished = true;

      clearTimeout(timeoutId);
      cleanupListeners();
      
      isShowingAd = false; // Release Global Lock
      
      if (rewarded) grantReward();
      else handleFailure(); 
      
      resolve(true);
    };

    const listeners = [
      AdMob.addListener(RewardAdPluginEvents.Rewarded, () => { rewardEarned = true; }),
      AdMob.addListener(RewardAdPluginEvents.Dismissed, () => { finish(rewardEarned); }),
      AdMob.addListener(RewardAdPluginEvents.FailedToLoad, () => finish(false)),
      AdMob.addListener(RewardAdPluginEvents.FailedToShow, () => finish(false))
    ];

    const timeoutId = setTimeout(() => finish(false), 20000);

    AdMob.showRewardVideoAd().catch(() => finish(false));
  });
}
```

## Professional Logging Flow
Expect this sequence for a healthy integration:
1. `[AD_DEBUG] SHOW_CALLED` -> User click recognized, lock acquired.
2. `onRewardedVideoAdShowed` -> Ad rendered on screen.
3. `onRewardedVideoAdReward` -> Reward earned event.
4. `onRewardedVideoAdDismissed` -> User closed the ad; cleanup and lock release.
