# AdMob Integration Guide (Android)

This project uses the `@capacitor-community/admob` plugin for Rewarded Ads to unlock premium features for 24 hours.

## 1. Credentials

- **App ID**: `ca-app-pub-8548627206908979~9870002801`
- **Reward Ad Unit ID**: `ca-app-pub-8548627206908979/6689305699`

## 2. Mandatory Setup

### AndroidManifest.xml
The following meta-data must exist inside the `<application>` tag in `android/app/src/main/AndroidManifest.xml`:

```xml
<meta-data
    android:name="com.google.android.gms.ads.APPLICATION_ID"
    android:value="ca-app-pub-8548627206908979~9870002801"/>
```

### capacitor.config.json
The App ID is also configured in the plugins section:

```json
"plugins": {
  "AdMob": {
    "appId": "ca-app-pub-8548627206908979~9870002801"
  }
}
```

## 3. Implementation Details

- **File**: `src/utils/ad.ts`
- **Function**: `showRewardAd()`
- **Logic**:
    1. SDK Initialization.
    2. Ad Preparation (Loading).
    3. Event Listeners for `Rewarded`, `Dismissed`, and `Errors`.
    4. **Safety Fallback (UX Optimized)**: If the ad fails to load, is skipped, or takes longer than **8 seconds** (safety timeout), the app automatically triggers the 24h unlock. This ensures users are never blocked by slow ad networks or long ad pods, matching a "fast" premium experience.

## 4. Testing & Debugging

### Debug Logs
Monitor logs via **Chrome Inspect** or **Android Studio Logcat** using the `[AdMob]` prefix.

- `LOAD_START`: Ad request initiated.
- `LOAD_SUCCESS`: Ad unit loaded successfully.
- `SHOW_START`: Ad is about to display.
- `REWARDED_EVENT`: User successfully watched and earned reward.
- `RESULT: REAL_AD_SHOWN`: Confirms a real ad was seen.
- `RESULT: FALLBACK_TRIGGERED`: Confirms the fallback unlock occurred (due to error or skip).

### Common Issues
1. **Error Code 3 (No Fill)**: Occurs on new AdMob accounts or new Unit IDs. Real ads may take 24-48 hours to appear.
2. **Missing App ID**: Causes immediate crash on startup. Ensure `AndroidManifest.xml` is updated.
3. **Internal Testing**: When testing via Google Play "Internal Testing" track, ensure `isTesting: true` is set in `src/utils/ad.ts` if you want to see test ads reliably.
