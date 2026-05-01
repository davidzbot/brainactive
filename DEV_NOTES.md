# BrainActive Android (Capacitor) - Developer Notes

## Project Configuration (Reusable for Android Projects)
- **Design Width**: `750px` (Configured in `config/index.js`). Use this scale for all pixel-to-viewport calculations.
- **Base Package**: `com.brainactive.app`
- **Build System**: Taro 4 + Webpack 5 + Capacitor 6
- **Target Platform**: Android (API 24+)
- **Output Directory**: `dist/h5` -> `android/app/src/main/assets/public`

## Share Messaging & URLs
Centralized in `src/config/share.ts` for zero-code message updates.

### 1. Official Store Link (Predefined)
- **URL**: `https://play.google.com/store/apps/details?id=com.brainactive.app`
- **Purpose**: Direct user acquisition and "Invite Friends" feature.

### 2. Marketing Placeholder (Fallback)
- **URL**: `https://brainactive.app`
- **Purpose**: Reserved for future custom landing page/PWA.

### Shared Text Templates
- **English**: "Train your brain daily with BrainActive. Stay sharp and focused."
- **Chinese**: "每天训练大脑，保持清晰思维。"

## UI/UX Design Standards (Professional Dark Theme)
- **Accessibility**: Optimized for older users with significantly enlarged font sizes and high contrast.
- **Header Style**: Professional dark headers with linear gradients (`linear-gradient(180deg, #1e293b 0%, #0f172a 100%)`).
- **Typography (750px Scale)**: 
  - Main Titles: 80px+ (Hero section)
  - Sub-labels: 32px - 34px
  - Instructions: 44px+
  - Buttons/Interactive: 48px+ bold text (min 100px touch target)
- **Color Palette**: 
  - Primary: Sky Blue (`#38bdf8`)
  - Success/Easy: Deep Green (`#064e3b`)
  - Info/Normal: Deep Blue (`#1e3a8a`)
  - Warning/Pro: Deep Amber (`#451a03`)

## UI Layout Improvements (Android Specific)
- **Edge-to-Edge**: `html, body, #app` set to 100% width/height. Removed all fixed `max-width` constraints.
- **Padding**: Minimal horizontal padding (16px) to maximize screen real estate on narrow devices.
- **Viewport**: `<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">`

## Key Logic Components
- **24-Hour Ad Unlock**: WATCH -> UNLOCK ALL (24h). 
  - Logic stored in `src/utils/common.ts` (`isAdUnlocked`, `unlockAllModes`).
  - Native AdMob integration in `src/utils/ad.ts`.
- **Daily Usage Guard**: `canPlayMode(level)` allows 1 free play per mode per day before requiring ad unlock.
- **Bilingual Support**: `src/utils/i18n.ts` with auto-detection of system language on first launch.

## Production QA & Security
- **AdMob**: `isTesting: false` and `initializeForTesting: false` for production.
- **Backdoor**: Tap app title 10 times to trigger debug Action Sheet (Force Unlock / Reset Storage).
- **Network**: 8-10s race-timeouts on Supabase fetches to prevent UI blocking.

## Build Commands
```bash
npm install
npm run build:android  # (taro build --type h5 && npx cap sync android)
```

## Feedback & Support
Email: pslehero@gmail.com
Project Version: 1.0.0
