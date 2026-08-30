/**
 * BrainActive — Monetization identifiers (AdMob + Google Play subscription).
 *
 * These are the ONLY values you need to replace when the real IDs are provided.
 * Everything else in the app reads from here so there is one source of truth.
 *
 * AdMob App ID must ALSO be set in `capacitor.config.json` → AdMob.appId.
 * The subscription product / offers are used once a real IAP plugin
 * (e.g. capacitor-plugin-cdv-purchase) is wired into `pages/pro/index.tsx`.
 */

// AdMob App ID (Android). Replace with the real BrainActive app id.
export const ADMOB_APP_ID = 'ca-app-pub-xxxxxxxxxxxxxxxx~xxxxxxxxxxxx'

// Production rewarded ad unit. Leave as '' to safely fall back to the Google
// test unit until the real BrainActive rewarded unit is pasted in.
export const ADMOB_REWARDED_AD_UNIT_ID = ''

// Google Play subscription product id (matches Play Console → In-app products).
export const SUBSCRIPTION_PRODUCT_ID = 'brainactive_pro'
export const SUBSCRIPTION_OFFERS = {
  yearly: 'brainactive_pro@yearly',
  monthly: 'brainactive_pro@monthly'
} as const

// Display prices (overridden at runtime by store pricing once IAP is wired).
export const PLAN_PRICES = {
  yearly: 'S$29.98',
  monthly: 'S$4.98'
} as const
