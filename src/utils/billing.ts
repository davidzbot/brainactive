import { Capacitor } from '@capacitor/core'
import Taro from '@tarojs/taro'
import {
  CdvPurchase,
  Platform,
  ProductType,
  PurchasePlugin,
} from 'capacitor-plugin-cdv-purchase'
import {
  SUBSCRIPTION_OFFERS,
  SUBSCRIPTION_PRODUCT_ID
} from '@/config/monetization'
import { syncBrainActivePurchaseEntitlement } from './request'
import {
  getDeviceId,
  getSubscriptionActive,
  getSubscriptionExpiry,
  setSubscriptionActive,
  setSubscriptionExpiry,
} from './storage'

let billingInitPromise: Promise<boolean> | null = null
let billingListenersRegistered = false
let nativePurchaseListenersPromise: Promise<void> | null = null
let nativePurchaseEventVersion = 0
let nativePurchaseWaiters: Array<{
  afterVersion: number
  resolve: () => void
  timer: ReturnType<typeof setTimeout>
}> = []

function notifyEntitlementChanged() {
  Taro.eventCenter.trigger('brainactive_billing_entitlement_changed')
}

function normalizeExpiry(value: any): string | null {
  if (!value) return null
  if (value instanceof Date) return Number.isNaN(value.getTime()) ? null : value.toISOString()
  if (typeof value === 'number') {
    const d = new Date(value)
    return Number.isNaN(d.getTime()) ? null : d.toISOString()
  }
  if (typeof value === 'string') {
    const t = value.trim()
    if (!t) return null
    const asNum = Number(t)
    if (!Number.isNaN(asNum) && t === String(asNum)) {
      const d = new Date(asNum)
      return Number.isNaN(d.getTime()) ? null : d.toISOString()
    }
    const d = new Date(t)
    return Number.isNaN(d.getTime()) ? null : d.toISOString()
  }
  return null
}

function getFallbackSubscriptionExpiry(): string {
  return new Date(Date.now() + 31 * 24 * 60 * 60 * 1000).toISOString()
}

function extractTransactionExpiry(transaction: any): string | null {
  return normalizeExpiry(
    transaction?.expiryTimeMillis ||
    transaction?.expiryDate ||
    transaction?.expirationDate ||
    transaction?.transaction?.expirationDate ||
    transaction?.nativePurchase?.expiryTimeMillis ||
    transaction?.receipt?.expiryTimeMillis
  )
}

function isAutoRenewingTransaction(transaction: any): boolean {
  return Boolean(transaction?.nativePurchase?.autoRenewing || transaction?.autoRenewing)
}

function logNativePurchaseEvent(eventName: string, data: any) {
  const purchases = Array.isArray(data?.purchases) ? data.purchases : []
  const productIds = [...new Set(purchases.flatMap((purchase: any) => {
    const ids = Array.isArray(purchase?.productIds) ? purchase.productIds : []
    return ids.length > 0 ? ids : [purchase?.productId]
  }).filter(Boolean))]
  const states = [...new Set(purchases.map((purchase: any) => String(
    purchase?.getPurchaseState ?? purchase?.state ?? 'unknown'
  )))]
  const offerIds = [...new Set(purchases.map((purchase: any) => purchase?.offerId || purchase?.basePlanId || null))]
  console.info('[BrainActive Billing] Native purchase event', JSON.stringify({
    eventName,
    count: purchases.length,
    productIds,
    basePlanIds: offerIds,
    offerIds,
    states,
    transactionIds: purchases.map((purchase: any) => purchase?.orderId || null),
    expiryTimestamps: purchases.map((purchase: any) => purchase?.expiryTimeMillis || null),
  }))
}

function handleNativePurchaseEvent(eventName: string, data: any) {
  nativePurchaseEventVersion += 1
  logNativePurchaseEvent(eventName, data)
  const version = nativePurchaseEventVersion
  setTimeout(() => {
    const ready = nativePurchaseWaiters.filter(waiter => waiter.afterVersion < version)
    nativePurchaseWaiters = nativePurchaseWaiters.filter(waiter => waiter.afterVersion >= version)
    ready.forEach(waiter => {
      clearTimeout(waiter.timer)
      waiter.resolve()
    })
  }, 0)
}

async function ensureNativePurchaseListeners() {
  if (!Capacitor.isNativePlatform()) return
  if (!nativePurchaseListenersPromise) {
    nativePurchaseListenersPromise = Promise.all([
      PurchasePlugin.addListener('setPurchases', data => handleNativePurchaseEvent('setPurchases', data)),
      PurchasePlugin.addListener('purchasesUpdated', data => handleNativePurchaseEvent('purchasesUpdated', data)),
    ]).then(() => {
      console.info('[BrainActive Billing] Native purchase listeners registered')
    })
  }
  await nativePurchaseListenersPromise
}

function waitForNativePurchaseUpdate(afterVersion: number, timeoutMs = 8000) {
  if (nativePurchaseEventVersion > afterVersion) {
    return {
      promise: Promise.resolve(true),
      cancel: () => {},
    }
  }

  let waiter: {
    afterVersion: number
    resolve: () => void
    timer: ReturnType<typeof setTimeout>
  }
  let resolveWaiter: ((value: boolean) => void) | null = null
  const promise = new Promise<boolean>(resolve => {
    resolveWaiter = resolve
    const timer = setTimeout(() => {
      nativePurchaseWaiters = nativePurchaseWaiters.filter(item => item !== waiter)
      console.warn('[BrainActive Billing] Timed out waiting for native purchase update', { timeoutMs })
      resolve(false)
    }, timeoutMs)
    waiter = {
      afterVersion,
      timer,
      resolve: () => resolve(true),
    }
    nativePurchaseWaiters.push(waiter)
  })

  return {
    promise,
    cancel: () => {
      clearTimeout(waiter.timer)
      nativePurchaseWaiters = nativePurchaseWaiters.filter(item => item !== waiter)
      resolveWaiter?.(false)
    },
  }
}

function isSubscriptionTransaction(transaction: CdvPurchase.Transaction) {
  const t: any = transaction
  const hasProduct = transaction.products.some(product => product.id === SUBSCRIPTION_PRODUCT_ID)
  const pending = (transaction as any).isPending
  const state = String((transaction as any).state || '')
  const approved = state === 'approved' || state === 'finished' || state === 'owned' || t.owned === true
  return hasProduct && !pending && approved
}

async function syncBackendEntitlement(transaction: CdvPurchase.Transaction): Promise<boolean> {
  const rawExpiry = extractTransactionExpiry(transaction) || (transaction as any).expirationDate?.toISOString?.() || null
  let expiryIso = rawExpiry
  let usedFallback = false
  if (!expiryIso && isAutoRenewingTransaction(transaction)) {
    expiryIso = getFallbackSubscriptionExpiry()
    usedFallback = true
  }
  const expiryDate = expiryIso ? new Date(expiryIso) : null
  if (!expiryDate || Number.isNaN(expiryDate.getTime()) || expiryDate.getTime() <= Date.now()) {
    console.warn('[BrainActive Billing] Backend entitlement sync skipped: no future expiry', {
      productId: SUBSCRIPTION_PRODUCT_ID,
      transactionId: (transaction as any).transactionId,
      rawExpiry,
      usedFallback,
      expiry: expiryIso,
    })
    return false
  }

  try {
    const result = await syncBrainActivePurchaseEntitlement({
      product_id: SUBSCRIPTION_PRODUCT_ID,
      expiry_date: expiryDate.toISOString(),
      transaction_id: (transaction as any).transactionId,
    })
    const synced = result?.is_pro === true
    console.info('[BrainActive Billing] Backend entitlement sync completed', {
      productId: SUBSCRIPTION_PRODUCT_ID,
      transactionId: (transaction as any).transactionId,
      expiry: expiryDate.toISOString(),
      usedFallback,
      synced,
    })
    return synced
  } catch (error) {
    console.warn('[BrainActive Billing] Backend entitlement sync failed:', error)
    return false
  }
}

function latestSubscriptionTransaction() {
  const all = CdvPurchase.store.localTransactions.filter(transaction =>
    transaction.products.some(product => product.id === SUBSCRIPTION_PRODUCT_ID)
  )
  const valid = all.filter(t => {
    const state = String((t as any).state || '')
    return state !== 'cancelled' && state !== 'failed' && state !== 'expired'
  })
  const pool = valid.length > 0 ? valid : all
  return pool.sort((a, b) => {
    const aExp = extractTransactionExpiry(a) ? new Date(extractTransactionExpiry(a)!).getTime() : 0
    const bExp = extractTransactionExpiry(b) ? new Date(extractTransactionExpiry(b)!).getTime() : 0
    const aTime = aExp || (a as any).lastRenewalDate?.getTime?.() || (a as any).purchaseDate?.getTime?.() || 0
    const bTime = bExp || (b as any).lastRenewalDate?.getTime?.() || (b as any).purchaseDate?.getTime?.() || 0
    return bTime - aTime
  })[0]
}

async function applyApprovedTransaction(transaction: CdvPurchase.Transaction) {
  const t: any = transaction
  const productIds = transaction.products.map(product => product.id)
  const rawExpiry = extractTransactionExpiry(transaction) || t.expirationDate?.toISOString?.() || null
  let expiryIso = rawExpiry
  let usedFallback = false
  if (!expiryIso && isAutoRenewingTransaction(transaction)) {
    expiryIso = getFallbackSubscriptionExpiry()
    usedFallback = true
  }
  const expiryDate = expiryIso ? new Date(expiryIso) : null
  console.info('[BrainActive Billing] Approved transaction', {
    productIds,
    offerIds: transaction.products.map(product => product.offerId || null),
    state: t.state,
    transactionId: t.transactionId,
    rawExpiry,
    expiry: expiryIso,
    usedFallback,
    autoRenewing: isAutoRenewingTransaction(transaction),
  })
  if (!isSubscriptionTransaction(transaction)) return

  if (expiryDate && expiryDate.getTime() <= Date.now()) {
    console.warn('[BrainActive Billing] Approved transaction is already expired', { expiry: expiryIso })
    setSubscriptionActive(false)
    setSubscriptionExpiry(null)
    notifyEntitlementChanged()
  } else {
    setSubscriptionActive(true)
    if (expiryIso && expiryDate) {
      setSubscriptionExpiry(expiryDate.toISOString())
      console.info('[BrainActive Billing] subscription_expiry written', {
        expiry: expiryDate.toISOString(),
        usedFallback,
      })
      await syncBackendEntitlement(transaction)
    } else {
      console.warn('[BrainActive Billing] Approved without expiry and not autoRenewing — local active without backend sync', { productIds })
      notifyEntitlementChanged()
      // still notify but no backend sync possible
      return
    }
    notifyEntitlementChanged()
  }

  console.info('[BrainActive Billing] Finishing approved transaction', { productIds })
  try {
    await transaction.finish()
    console.info('[BrainActive Billing] Finished approved transaction', { productIds })
  } catch (error) {
    console.warn('[BrainActive Billing] Could not acknowledge purchase:', error)
  }
}

export async function syncBillingEntitlement(): Promise<boolean> {
  if (!Capacitor.isNativePlatform()) return getSubscriptionActive() || Boolean(getSubscriptionExpiry())
  const transaction: any = latestSubscriptionTransaction()
  if (transaction && isSubscriptionTransaction(transaction)) {
    const rawExpiry = extractTransactionExpiry(transaction) || transaction.expirationDate?.toISOString?.() || null
    let expiryIso = rawExpiry
    let usedFallback = false
    if (!expiryIso && isAutoRenewingTransaction(transaction)) {
      expiryIso = getFallbackSubscriptionExpiry()
      usedFallback = true
    }
    const expiryDate = expiryIso ? new Date(expiryIso) : null
    console.info('[BrainActive Billing] Sync transaction', {
      productIds: transaction.products.map((p: any) => p.id),
      offerIds: transaction.products.map((p: any) => p.offerId || null),
      state: transaction.state,
      transactionId: transaction.transactionId,
      rawExpiry,
      expiry: expiryIso,
      usedFallback,
      autoRenewing: isAutoRenewingTransaction(transaction),
      recognizedProduct: true,
    })
    if (expiryDate && expiryDate.getTime() <= Date.now()) {
      setSubscriptionActive(false)
      setSubscriptionExpiry(null)
      console.info('[BrainActive Billing] Cleared expired subscription_expiry', { expiry: expiryIso })
      notifyEntitlementChanged()
      return false
    }
    setSubscriptionActive(true)
    if (expiryIso && expiryDate) {
      setSubscriptionExpiry(expiryDate.toISOString())
      console.info('[BrainActive Billing] subscription_expiry written', {
        expiry: expiryDate.toISOString(),
        usedFallback,
      })
      await syncBackendEntitlement(transaction)
    } else {
      console.warn('[BrainActive Billing] No expiry and not autoRenewing — local active without backend sync', { expiry: expiryIso })
    }
    notifyEntitlementChanged()
    return true
  }
  const state = String(transaction?.state || '')
  if (state === 'cancelled' || state === 'failed' || state === 'expired') {
    // Only clear if we actually have a terminal transaction, not empty
    if (transaction) {
      setSubscriptionActive(false)
      setSubscriptionExpiry(null)
      console.info('[BrainActive Billing] Cleared terminal subscription state', JSON.stringify({ state, transactionId: transaction?.transactionId || null }))
      notifyEntitlementChanged()
      return false
    }
  }
  console.info('[BrainActive Billing] No transaction available; preserving cached entitlement', {
    hasCachedActive: getSubscriptionActive(),
    hasCachedExpiry: Boolean(getSubscriptionExpiry()),
  })
  return getSubscriptionActive() || Boolean(getSubscriptionExpiry())
}

export async function initializeBilling(): Promise<boolean> {
  if (!Capacitor.isNativePlatform()) return false
  if (billingInitPromise) return billingInitPromise

  billingInitPromise = (async () => {
    try {
      console.info('[BrainActive Billing] Billing initialization started', {
        productId: SUBSCRIPTION_PRODUCT_ID,
        monthlyOffer: SUBSCRIPTION_OFFERS.monthly,
        yearlyOffer: SUBSCRIPTION_OFFERS.yearly,
      })
      await ensureNativePurchaseListeners()
      const { store } = CdvPurchase
      if (!billingListenersRegistered) {
        store.register({
          id: SUBSCRIPTION_PRODUCT_ID,
          type: ProductType.PAID_SUBSCRIPTION,
          platform: Platform.GOOGLE_PLAY
        })
        store.when().approved(applyApprovedTransaction)
        store.when().receiptUpdated((receipt: CdvPurchase.Receipt) => {
          console.info('[BrainActive Billing] Receipt updated', {
            transactionCount: receipt.transactions.length,
          })
          void syncBillingEntitlement()
        })
        store.when().pending(() => {
          console.info('[BrainActive Billing] Subscription purchase pending')
        })
        billingListenersRegistered = true
      }

      const purchaseEventVersion = nativePurchaseEventVersion
      const initialPurchaseUpdate = waitForNativePurchaseUpdate(purchaseEventVersion)
      const errors = await store.initialize([Platform.GOOGLE_PLAY])
      await initialPurchaseUpdate.promise
      if (errors?.length) {
        console.warn('[BrainActive Billing] Initialization warnings:', errors)
      }
      const hasErrors = Boolean(errors?.some(error => error.isError))
      if (hasErrors) {
        billingInitPromise = null
        return false
      }
      const entitlementActive = await syncBillingEntitlement()
      console.info('[BrainActive Billing] Billing initialization completed', { entitlementActive })
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
  console.info('[BrainActive Billing] Purchase refresh started')
  const purchaseEventVersion = nativePurchaseEventVersion
  const purchaseUpdate = waitForNativePurchaseUpdate(purchaseEventVersion)
  try {
    await PurchasePlugin.getPurchases()
  } catch (error) {
    console.warn('[BrainActive Billing] Purchase query failed:', error)
    purchaseUpdate.cancel()
  }
  await purchaseUpdate.promise
  const active = await syncBillingEntitlement()
  console.info('[BrainActive Billing] Purchase refresh completed', { active })
  return active
}

export async function restoreBillingPurchases(): Promise<boolean> {
  if (!Capacitor.isNativePlatform()) return false
  const ready = await initializeBilling()
  if (!ready) return false
  console.info('[BrainActive Billing] Restore started')
  const purchaseEventVersion = nativePurchaseEventVersion
  const purchaseUpdate = waitForNativePurchaseUpdate(purchaseEventVersion)
  try {
    const restoreError = await CdvPurchase.store.restorePurchases()
    if (restoreError?.isError) {
      purchaseUpdate.cancel()
      console.warn('[BrainActive Billing] Restore failed:', restoreError.message)
      return false
    }
    const receivedPurchaseUpdate = await purchaseUpdate.promise
    const active = await syncBillingEntitlement()
    console.info('[BrainActive Billing] Restore completed', JSON.stringify({ receivedPurchaseUpdate, active }))
    return active
  } catch (error) {
    purchaseUpdate.cancel()
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
  console.info('[BrainActive Billing] Selecting subscription offer', {
    productId: SUBSCRIPTION_PRODUCT_ID,
    plan,
    basePlan: plan,
    offerId,
    productFound: Boolean(product),
  })
  const offer = product?.getOffer(offerId)
  if (!offer) return { isError: true, message: 'This subscription plan is not available yet.' }

  console.info('[BrainActive Billing] offer.order() started', { productId: SUBSCRIPTION_PRODUCT_ID, basePlan: plan, offerId })
  const purchaseEventVersion = nativePurchaseEventVersion
  const purchaseUpdate = waitForNativePurchaseUpdate(purchaseEventVersion)
  try {
    const orderResult = await offer.order()
    if (orderResult?.isError) {
      purchaseUpdate.cancel()
      console.warn('[BrainActive Billing] offer.order() failed', { message: orderResult.message })
      return orderResult
    }
    const receivedPurchaseUpdate = await purchaseUpdate.promise
    console.info('[BrainActive Billing] offer.order() completed', { receivedPurchaseUpdate })
    return orderResult
  } catch (error) {
    purchaseUpdate.cancel()
    console.warn('[BrainActive Billing] offer.order() threw:', error)
    throw error
  }
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
