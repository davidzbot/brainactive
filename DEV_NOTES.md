# BrainActive Android (Capacitor)

## Isolated Project Details
- **Target**: H5 + Android (`h5` + Capacitor)
- **Framework**: Taro 4 + React
- **Lock System**: 24-hour ad-unlock system (simulated/ready for AdMob)
- **Native APIs**: Capacitor (Share, Toast, Dialog, App)
- **Positioning**: Scientific Brain Training & Alzheimer's Prevention for Seniors & Professionals.
- **Reference**: `reference_brain-plan` (WeChat Mini Program version) used for UI/UX alignment.

## UI/UX Design Standards (Updated for Senior Accessibility)
- **Accessibility**: Optimized for older users with significantly enlarged font sizes and high contrast.
- **Layout**: Top-aligned content to minimize eye and finger movement.
- **Header Style**: Vibrant, clean headers (white background or soft gradients).
- **Typography**: 
  - Titles: 64px+ (Main headers)
  - Subtitles/Descriptions: 28px - 32px
  - Instructions: 36px+
  - Buttons/Cards: 40px+ bold text
- **Color Palette (Cheerful Theme)**: 
  - Primary: Sky Blue (`#4a90e2`)
  - Easy Mode: Mint Green (`#f0fdf4`)
  - Normal Mode: Sky Blue (`#f0f9ff`)
  - Pro Mode: Lavender Purple (`#faf5ff`)
- **Interaction**: Extra-large rounded buttons (60px+ radius), 3D press effects, and scale feedback.

## Key Logic & Engagement
- **Ad Unlock**: One "ad watch" (3s mock) unlocks all modes for 24 hours.
- **Daily Streak**: Tracks consecutive days of check-ins with prominent "Fire" emoji (🔥) to build addictive healthy habits.
- **Top Alignment**: All pages (Home, Task, Result) should start from the top with consistent padding, avoiding large middle-screen gaps.
- **Sharing**: Prominent share/invite buttons to encourage social check-ins.

## Task Generation Logic (Production Standard)
- **Task Types**: 
  - 0: Names (Sequence-based in Normal/Pro)
  - 1: Numbers (Calculation-based in Normal/Pro, Memory-only in Easy)
  - 2: Colors/Shapes (Sequence-based in Normal/Pro)
  - 3: Cities (Sequence-based in Normal/Pro)
  - 4: Sentences (Memory/Typo-detection)
- **Sequence Validation**: If `sequenceMode` is active, selection order MUST match the target order.
- **Calculation Logic**: For number tasks in Normal/Pro, memory phase shows operands, and answer phase requires the calculated result.

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
