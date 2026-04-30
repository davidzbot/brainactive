# BrainActive: Developer Setup & Integration Guide

This guide provides a standalone reference for building, configuring, and debugging the BrainActive Android application (Taro 4 + Capacitor).

---

## 1. Build Process (Taro & Android)

The project uses Taro for the frontend and Capacitor to bridge to native Android.

### Prerequisites
- **Node.js**: v18+
- **Android Studio**: Latest version with SDK 34+
- **Capacitor CLI**: `npm install -g @capacitor/cli`

### Step-by-Step Build
1. **Frontend Build**: Compile the React/Taro code into standard H5 web assets.
   ```bash
   npm run build:h5
   ```
2. **Capacitor Sync**: Synchronize the compiled assets and plugins into the native Android project.
   ```bash
   npx cap sync android
   ```
3. **Native Build**:
   - Open the `android/` folder in **Android Studio**.
   - Connect a device or start an emulator.
   - Click **Run** or use `Build > Build Bundle(s) / APK(s)`.

---

## 2. AdMob Integration

Used for Rewarded Ads to unlock features for 24 hours.

### Configuration
1. **AndroidManifest.xml**: Must include the App ID in the `<application>` tag.
   ```xml
   <meta-data
       android:name="com.google.android.gms.ads.APPLICATION_ID"
       android:value="ca-app-pub-8548627206908979~9870002801"/>
   ```
2. **capacitor.config.json**: Register the plugin.
   ```json
   "plugins": {
     "AdMob": { "appId": "ca-app-pub-8548627206908979~9870002801" }
   }
   ```

### Code Implementation (`src/utils/ad.ts`)
Call `showRewardAd()` to trigger the flow. It is Promise-based:
- **Success**: Resolves when ad is watched OR if the safety fallback triggers (ensures UX).
- **Events**: Listens for `Rewarded` (reward flag) and `Dismissed` (cleanup/unlock).

---

## 3. Supabase Integration

Used for fetching dynamic training content (names, cities, sentences).

### Setup
- **Base URL**: `https://mqpunjvdrkqvionsjosl.supabase.co`
- **Utility**: `src/utils/supabase.ts` contains the `fetchBrainActiveContent` function.

### Fetching Logic
The app calls an **Edge Function** (`brainactive-get-content`) which generates or retrieves localized content.
```typescript
const items = await fetchBrainActiveContent('city', 'zh', 10);
```

---

## 4. Debugging & API Fixes

### How to Debug on Android
1. **Remote Debugging**:
   - Connect device via USB.
   - Open Chrome on PC and go to `chrome://inspect/#devices`.
   - Click **Inspect** under your app to see the Console and Network tabs.
2. **Native Logs**:
   - In Android Studio, use the **Logcat** tab.
   - Search for `[AdMob]` or `Capacitor` to see native bridge errors.

### Common API Issues & Fixes
- **Timeout**: The app uses `Promise.race` with a 10s timer. If APIs are slow, it falls back to local `dataUtils`. Increase timeout in `src/utils/supabase.ts` if needed.
- **CORS/Auth**: Ensure the `apikey` and `Authorization` headers in `supabase.ts` match your Supabase project settings.
- **Language Mixing**: Always pass the result of `getLang()` to API calls. If the API returns the wrong language, check the Edge Function parameters.
- **Ad Not Showing**: 
    - Check if "Ad Fill" is 100% in AdMob console.
    - New App/Unit IDs often return "Error Code 3 (No Fill)" for the first 24-48 hours.

---

## 5. UI/UX Standards for Seniors
- **Font Size**: Minimum 32px for body, 48px for stimulus.
- **Layout**: Center main content vertically; avoid "top-heavy" designs.
- **Interaction**: Single-column vertical lists for answers (110px+ touch targets).
- **Safe Area**: Always use `env(safe-area-inset-top)` for padding to avoid status bar overlap.
