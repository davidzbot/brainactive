# BrainActive Android (Capacitor)

## Isolated Project Details
- **Target**: H5 + Android (`h5` + Capacitor)
- **Framework**: Taro 4 + React
- **Lock System**: Ad-unlock system (simulated)
- **Native APIs**: Capacitor (Share, Toast, Dialog, App)

## Structure
- `config/index.js`: Targets only `h5`.
- `src/`: Contains Android/H5 logic only.
- `src/index.html`: Web template for Capacitor.
- Removed all WeChat-specific code (`wx.*`, `openType="share"`).

## Build
```bash
npm install
npm run build:android
```
