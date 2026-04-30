# BrainActive Android (Capacitor)

## Isolated Project Details
- **Target**: H5 + Android (`h5` + Capacitor)
- **Framework**: Taro 4 + React
- **Lock System**: 24-hour ad-unlock system (simulated/ready for AdMob)
- **Native APIs**: Capacitor (Share, Toast, Dialog, App)
- **Positioning**: Scientific Brain Training & Alzheimer's Prevention for Seniors & Professionals.
- **Reference**: `reference_brain-plan` (WeChat Mini Program version) used for UI/UX alignment.

## UI/UX Design Standards (Updated for Professional Dark Theme)
- **Accessibility**: Optimized for older users with significantly enlarged font sizes and high contrast.
- **Layout**: Top-aligned content with consistent 2-column grid systems for Home and Task pages.
- **Header Style**: Professional dark headers with linear gradients (linear-gradient(180deg, #1e293b 0%, #0f172a 100%)).
- **Typography**: 
  - Titles: 80px+ (Hero section)
  - Subtitles/Descriptions: 32px - 34px
  - Instructions: 44px+
  - Buttons/Cards: 48px+ bold text
- **Color Palette (Professional Dark)**: 
  - Primary: Sky Blue (`#38bdf8`)
  - Easy Mode: Deep Green (`#064e3b`)
  - Normal Mode: Deep Blue (`#1e3a8a`)
  - Pro Mode: Deep Amber/Brown (`#451a03`)
- **Interaction**: Extra-large rounded buttons (60px+ radius), polished 3D press effects (shadow-based), and scale feedback.

## Key Logic & Engagement
- **Ad Unlock**: One "ad watch" (3s mock) unlocks all modes for 24 hours.
- **Back to Review**: Answer phase allows returning to the memory phase (Back to Review) to reinforce cognitive retention.
- **Daily Streak**: Tracks consecutive days of check-ins with prominent "Fire" emoji (🔥) to build addictive healthy habits.
- **Top Alignment**: All pages (Home, Task, Result) start from the top with consistent padding and professional dashboard alignment.

## Task Generation Logic (Production Standard)
- **Task Types**: 
  - 0: Names (Sequence-based in Normal/Pro)
  - 1: Numbers (Calculation-based in Normal/Pro, Memory-only in Easy). **Answer phase masks real numbers with placeholders like "(number 1)" to test pure memory.**
  - 2: Colors/Shapes (Sequence-based in Normal/Pro)
  - 3: Cities (Sequence-based in Normal/Pro)
  - 4: Sentences (Memory/Typo-detection)

## Production QA & Security
- **Console Logs**: All `console.log` and `console.warn` (non-essential) are stripped for production performance and privacy.
- **Debug Backdoor**: Tap title 10 times to access debug tools (Action Sheet).
- **Network Resilience**: Uses `Promise.allSettled` and race-timeouts (8-10s) to ensure the UI never hangs on slow connections.
- **Memory Optimization**: Minimal asset size and clean build patterns for small APK footprint.

## Build Commands
```bash
npm install
npm run build:android
```

## Feedback
Email: pslehero@gmail.com
