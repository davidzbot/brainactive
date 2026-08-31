# AdMob Integration Guide (Android)

This project uses the `@capacitor-community/admob` plugin for Rewarded Ads to unlock premium features for 24 hours.

## 1. Credentials

- **Closed-test App ID**: `ca-app-pub-3940256099942544~3347511713`
- **Closed-test Reward Ad Unit ID**: `ca-app-pub-3940256099942544/5224354917`

## 2. Mandatory Setup

### AndroidManifest.xml
The manifest references `@string/admob_application_id`. Main/release and debug resources use Google's official test App ID for the closed-test build.

```xml
<meta-data
    android:name="com.google.android.gms.ads.APPLICATION_ID"
    android:value="@string/admob_application_id"/>
```

### capacitor.config.json
The App ID is also configured in the plugins section:

```json
"plugins": {
  "AdMob": {
    "appId": "ca-app-pub-3940256099942544~3347511713"
  }
}
```

## 3. Test Ads (Current Development Configuration)

Google's official test identifiers are used by default so debug, wireless-debug, H5, and internal-testing builds do not generate real impressions or clicks:

- **Test App ID**: `ca-app-pub-3940256099942544~3347511713`
- **Test Rewarded Unit ID**: `ca-app-pub-3940256099942544/5224354917`

`src/config/monetization.ts` uses Google's official test App ID and keeps `ADMOB_USE_PRODUCTION_ADS` deliberately `false`. Do not enable that flag during the closed test.

## 4. Implementation Details

- **File**: `src/utils/ad.ts`
- **Function**: `showRewardAd()`
- **Logic**:
    1. SDK Initialization.
    2. Ad Preparation (Loading).
    3. Event Listeners for `Rewarded`, `Dismissed`, and `Errors`.
    4. Test-ad selection does not change reward callbacks, quota counters, daily limits, or Pro entitlement logic.

## 5. Google Play subscriptions

BrainActive uses `capacitor-plugin-cdv-purchase` with the Google Play Billing Library. The Play Console subscription setup is:

- **Product ID**: `brainactive_pro`
- **Monthly base plan ID**: `monthly`
- **Yearly base plan ID**: `yearly`
- **Offer lookup IDs**: `brainactive_pro@monthly` and `brainactive_pro@yearly`

The app reads localized prices from Play `ProductDetails` when available. Paid subscription expiry is kept separate from referral `pro_expiry`; both can contribute to the existing Pro entitlement.

## 6. Testing & Debugging

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
3. **Closed Testing**: Main/release and debug resources use the official test App ID, and `src/utils/ad.ts` uses the official test rewarded unit with `isTesting: true`. Do not enable `ADMOB_USE_PRODUCTION_ADS` for closed testing.
