/**
 * BrainActive — Monetization identifiers (AdMob + Google Play subscription).
 *
 * These are the ONLY values you need to replace when the real IDs are provided.
 * Everything else in the app reads from here so there is one source of truth.
 *
 * AdMob App ID must ALSO be set in `capacitor.config.json` → AdMob.appId.
 * Google Play Billing is wired through capacitor-plugin-cdv-purchase and the
 * purchase lifecycle is coordinated by `src/utils/billing.ts`.
 */

export const ADMOB_APP_ID = 'ca-app-pub-8548627206908979~9870002801'
export const ADMOB_REWARDED_AD_UNIT_ID = 'ca-app-pub-8548627206908979/6689305699'
export const ADMOB_USE_PRODUCTION_ADS = true

// Google Play subscription identifiers. Product/base-plan IDs are separate from
// localized display names and must match the Play Console configuration.
export const SUBSCRIPTION_PRODUCT_ID = 'brainactive_pro'
export const SUBSCRIPTION_BASE_PLANS = {
  yearly: 'yearly',
  monthly: 'monthly'
} as const
export const SUBSCRIPTION_OFFERS = {
  yearly: `${SUBSCRIPTION_PRODUCT_ID}@${SUBSCRIPTION_BASE_PLANS.yearly}`,
  monthly: `${SUBSCRIPTION_PRODUCT_ID}@${SUBSCRIPTION_BASE_PLANS.monthly}`
} as const

// Display prices used as fallback when Play ProductDetails are unavailable.
export const PLAN_PRICES = {
  yearly: 'S$29.98',
  monthly: 'S$4.98'
} as const
