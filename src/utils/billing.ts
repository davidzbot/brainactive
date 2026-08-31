import { Capacitor } from '@capacitor/core'
import Taro from '@tarojs/taro'
import {
  CdvPurchase,
  Platform,
  ProductType,
} from 'capacitor-plugin-cdv-purchase'
import {
  SUBSCRIPTION_OFFERS,
  SUBSCRIPTION_PRODUCT_ID
} from '@/config/monetization'
import {
  getSubscriptionActive,
  getSubscriptionExpiry,
  setSubscriptionActive,
  setSubscriptionExpiry,
} from './storage'

let billingInitPromise: Promise<boolean> | null = null
let billingListenersRegistered = false

function notifyEntitlementChanged() {
  Taro.eventCenter.trigger('brainactive_billing_entitlement_changed')
}

function isSubscriptionTransaction(transaction: CdvPurchase.Transaction) {
  return (
    transaction.products.some(product => product.id === SUBSCRIPTION_PRODUCT_ID) &&
    !transaction.isPending &&
    (transaction.state === 'approved' || transaction.state === 'finished')
  )
}

function latestSubscriptionTransaction() {
  return CdvPurchase.store.localTransactions
    .filter(transaction => transaction.products.some(product => product.id === SUBSCRIPTION_PRODUCT_ID))
    .sort((a, b) => (
      (b.expirationDate?.getTime() || b.lastRenewalDate?.getTime() || b.purchaseDate?.getTime() || 0) -
      (a.expirationDate?.getTime() || a.lastRenewalDate?.getTime() || a.purchaseDate?.getTime() || 0)
    ))[0]
}

async function applyApprovedTransaction(transaction: CdvPurchase.Transaction) {
  if (!isSubscriptionTransaction(transaction)) return
  setSubscriptionActive(true)
  if (transaction.expirationDate && transaction.expirationDate.getTime() > Date.now()) {
    setSubscriptionExpiry(transaction.expirationDate.toISOString())
  }
  notifyEntitlementChanged()
  try {
    await transaction.finish()
  } catch (error) {
    console.warn('[BrainActive Billing] Could not acknowledge purchase:', error)
  }
}

export async function syncBillingEntitlement(): Promise<boolean> {
  if (!Capacitor.isNativePlatform()) return getSubscriptionActive() || Boolean(getSubscriptionExpiry())
  const transaction = latestSubscriptionTransaction()
  if (transaction && isSubscriptionTransaction(transaction)) {
    if (transaction.expirationDate && transaction.expirationDate.getTime() <= Date.now()) {
      setSubscriptionActive(false)
      setSubscriptionExpiry(null)
      notifyEntitlementChanged()
      return false
    }
    setSubscriptionActive(true)
    if (transaction.expirationDate) {
      setSubscriptionExpiry(transaction.expirationDate.toISOString())
    }
    notifyEntitlementChanged()
    return true
  }
  const state = String(transaction?.state || '')
  if (state === 'cancelled' || state === 'failed') {
    setSubscriptionActive(false)
    setSubscriptionExpiry(null)
    notifyEntitlementChanged()
    return false
  }
  return getSubscriptionActive() || Boolean(getSubscriptionExpiry())
}

export async function initializeBilling(): Promise<boolean> {
  if (!Capacitor.isNativePlatform()) return false
  if (billingInitPromise) return billingInitPromise

  billingInitPromise = (async () => {
    try {
      const { store } = CdvPurchase
      if (!billingListenersRegistered) {
        store.register({
          id: SUBSCRIPTION_PRODUCT_ID,
          type: ProductType.PAID_SUBSCRIPTION,
          platform: Platform.GOOGLE_PLAY
        })
        store.when().approved(applyApprovedTransaction)
        store.when().receiptUpdated(() => {
          void syncBillingEntitlement()
        })
        store.when().pending(() => {
          console.info('[BrainActive Billing] Subscription purchase pending')
        })
        billingListenersRegistered = true
      }

      const errors = await store.initialize([Platform.GOOGLE_PLAY])
      if (errors?.length) {
        console.warn('[BrainActive Billing] Initialization warnings:', errors)
      }
      const hasErrors = Boolean(errors?.some(error => error.isError))
      if (hasErrors) {
        billingInitPromise = null
        return false
      }
      await syncBillingEntitlement()
      return true
    } catch (error) {
      billingInitPromise = null
      console.warn('[BrainActive Billing] Initialization failed:', error)
      return false
    }
  })()

  return billingInitPromise
}

export async function refreshBillingEntitlement(): Promise<boolean> {
  if (!Capacitor.isNativePlatform()) return false
  const ready = await initializeBilling()
  if (!ready) return false
  try {
    await CdvPurchase.store.update()
  } catch (error) {
    console.warn('[BrainActive Billing] Purchase query failed:', error)
  }
  return syncBillingEntitlement()
}

export async function restoreBillingPurchases(): Promise<boolean> {
  if (!Capacitor.isNativePlatform()) return false
  const ready = await initializeBilling()
  if (!ready) return false
  try {
    const restoreError = await CdvPurchase.store.restorePurchases()
    if (restoreError?.isError) {
      console.warn('[BrainActive Billing] Restore failed:', restoreError.message)
      return false
    }
    await CdvPurchase.store.update()
    return syncBillingEntitlement()
  } catch (error) {
    console.warn('[BrainActive Billing] Restore failed:', error)
    return false
  }
}

export async function purchaseSubscription(plan: 'yearly' | 'monthly') {
  if (!Capacitor.isNativePlatform()) {
    return { isError: true, message: 'Google Play subscriptions are available in the Android app.' }
  }
  const ready = await initializeBilling()
  if (!ready) return { isError: true, message: 'Google Play billing is unavailable.' }

  const product = CdvPurchase.store.get(SUBSCRIPTION_PRODUCT_ID, Platform.GOOGLE_PLAY)
  const offerId = SUBSCRIPTION_OFFERS[plan]
  const offer = product?.getOffer(offerId)
  if (!offer) return { isError: true, message: 'This subscription plan is not available yet.' }
  return offer.order()
}

export async function getSubscriptionPrices() {
  if (!Capacitor.isNativePlatform()) return null
  const ready = await initializeBilling()
  if (!ready) return null
  const product = CdvPurchase.store.get(SUBSCRIPTION_PRODUCT_ID, Platform.GOOGLE_PLAY)
  if (!product) return null
  return {
    yearly: product.getOffer(SUBSCRIPTION_OFFERS.yearly)?.pricingPhases[0]?.price || null,
    monthly: product.getOffer(SUBSCRIPTION_OFFERS.monthly)?.pricingPhases[0]?.price || null
  }
}
