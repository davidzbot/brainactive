---
name: admob-troubleshooter
description: Diagnosing and fixing AdMob rewarded ad integration issues in Capacitor/Taro projects. Use when ads are not showing, 'preparing session' is slow, or platform-specific logic is being bypassed.
---

# AdMob Rewarded Ad Troubleshooting & Optimization

This skill provides a systematic workflow for diagnosing and fixing common AdMob issues in Capacitor + Taro projects.

## Core Best Practices (Mandatory)

1.  **Event-Driven Logic:** DO NOT rely on durations (e.g. 30s) or safety timeouts to grant rewards. Rewards must be granted strictly based on the `Rewarded` event.
2.  **Platform Detection:** DO NOT use `TARO_ENV`. Use `Capacitor.getPlatform()` to ensure logic runs on Android/iOS but mocks on Web.
3.  **Resource Cleanup:** Always remove all event listeners and clear timeouts immediately after the ad flow finishes to prevent memory leaks and double rewards.
4.  **Single-Execution Guard:** Use a `finished` flag to ensure the internal `finish()` function is called exactly once.

## Implementation Pattern

### The `showRewardAd` Function

```typescript
export async function showRewardAd() {
  // ... check initialization and preloading ...

  return new Promise((resolve) => {
    let finished = false;
    let rewardEarned = false;

    const finish = (rewarded: boolean) => {
      if (finished) return;
      finished = true;

      clearTimeout(timeoutId);
      cleanupListeners();
      
      if (rewarded) grantReward();
      else handleFailure(); // e.g. fail-open or toast
      
      resolve(true);
    };

    // Listeners for Reward, Dismissal, and Failures
    const listeners = [
      AdMob.addListener(RewardAdPluginEvents.Rewarded, () => { rewardEarned = true; }),
      AdMob.addListener(RewardAdPluginEvents.Dismissed, () => { finish(rewardEarned); }),
      AdMob.addListener(RewardAdPluginEvents.FailedToLoad, () => finish(false)),
      AdMob.addListener(RewardAdPluginEvents.FailedToShow, () => finish(false))
    ];

    const timeoutId = setTimeout(() => finish(false), 20000); // 20s safety max

    AdMob.showRewardVideoAd().catch(() => finish(false));
  });
}
```

## Professional Logging Flow
Expect this sequence for a healthy integration:
1. `onRewardedVideoAdLoaded` -> Ad successfully fetched from Google.
2. `onRewardedVideoAdShowed` -> Ad successfully rendered on screen.
3. `onRewardedVideoAdReward` -> Reward logic triggered.
4. `onRewardedVideoAdDismissed` -> User closed the ad; cleanup triggered.
