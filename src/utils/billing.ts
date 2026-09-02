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
  getStorage,
  getSubscriptionActive,
  getSubscriptionExpiry,
  getProExpiry,
  setStorage,
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

function getFallbackSubscriptionExpiry(transaction?: any): string {
  const offerIds: string[] = []
  const products = transaction?.products || []
  for (const product of products) {
    if (product?.offerId) offerIds.push(String(product.offerId))
  }
  if (transaction?.offerId) offerIds.push(String(transaction.offerId))
  if (transaction?.basePlanId) offerIds.push(String(transaction.basePlanId))
  if (transaction?.nativePurchase?.offerId) offerIds.push(String(transaction.nativePurchase.offerId))
  if (transaction?.nativePurchase?.basePlanId) offerIds.push(String(transaction.nativePurchase.basePlanId))
  if (Array.isArray(transaction?.productIds)) {
    offerIds.push(...transaction.productIds.map((id: string) => String(id)))
  }

  const joined = offerIds.join(' ').toLowerCase()
  let plan: 'yearly' | 'monthly' | null = null
  if (joined.includes('yearly') || offerIds.includes(SUBSCRIPTION_OFFERS.yearly)) plan = 'yearly'
  if (joined.includes('monthly') || offerIds.includes(SUBSCRIPTION_OFFERS.monthly)) plan = 'monthly'
  if (!plan) {
    const lastPlan = getStorage('last_purchase_plan')
    if (lastPlan === 'yearly' || lastPlan === 'monthly') plan = lastPlan
  }

  // This is an effective client entitlement date, not a Google Play expiry.
  const days = plan === 'monthly' ? 31 : 365
  const effectiveExpiry = new Date(Date.now() + days * 24 * 60 * 60 * 1000).toISOString()
  console.info('[BrainActive Billing] Effective fallback entitlement date', JSON.stringify({
    source: 'client_fallback',
    plan: plan || 'unknown-default-yearly',
    days,
    effectiveExpiry,
    transactionId: transaction?.transactionId || null,
  }))
  return effectiveExpiry
}

function setSubscriptionExpiryIfLater(expiryIso: string): boolean {
  const existingExpiries = [getSubscriptionExpiry(), getProExpiry()]
    .filter(Boolean)
    .map(value => new Date(value as string).getTime())
    .filter(Number.isFinite)
  const nextTime = new Date(expiryIso).getTime()
  const latestExisting = Math.max(...existingExpiries, 0)
  if (Number.isFinite(nextTime) && nextTime <= latestExisting) {
    console.info('[BrainActive Billing] Skip expiry write — existing is later', {
      existing: new Date(latestExisting).toISOString(),
      next: expiryIso,
    })
    return false
  }
  setSubscriptionExpiry(expiryIso)
  return true
}

function logNativePurchaseEvent(eventName: string, data: any) {
  const purchases = Array.isArray(data?.purchases) ? data.purchases : []
  const productIds = [...new Set(purchases.flatMap((purchase: any) => {
    const ids = Array.isArray(purchase?.productIds) ? purchase.productIds : []
    return ids.length > 0 ? ids : [purchase?.productId]
  }).filter(Boolean))]
  console.info('[BrainActive Billing] Native purchase detected', JSON.stringify({
    eventName,
    count: purchases.length,
    productIds,
    basePlanIds: purchases.map((purchase: any) => purchase?.basePlanId || null),
    offerIds: purchases.map((purchase: any) => purchase?.offerId || null),
    states: purchases.map((purchase: any) => String(purchase?.getPurchaseState ?? purchase?.state ?? 'unknown')),
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
    return { promise: Promise.resolve(true), cancel: () => {} }
  }
  let waiter: { afterVersion: number; resolve: () => void; timer: ReturnType<typeof setTimeout> }
  let resolveWaiter: ((value: boolean) => void) | null = null
  const promise = new Promise<boolean>(resolve => {
    resolveWaiter = resolve
    const timer = setTimeout(() => {
      nativePurchaseWaiters = nativePurchaseWaiters.filter(item => item !== waiter)
      console.warn('[BrainActive Billing] Timed out waiting for native purchase update', { timeoutMs })
      resolve(false)
    }, timeoutMs)
    waiter = { afterVersion, timer, resolve: () => resolve(true) }
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
  const state = String(t.state || '')
  return hasProduct && !t.isPending && (state === 'approved' || state === 'finished' || state === 'owned' || t.owned === true)
}

async function syncBackendEntitlement(transaction: CdvPurchase.Transaction, effectiveExpiry?: string): Promise<boolean> {
  const rawExpiry = extractTransactionExpiry(transaction)
  const expiryIso = effectiveExpiry || rawExpiry
  if (!expiryIso) {
    console.info('[BrainActive Billing] Backend sync blocked: no real or effective expiry', JSON.stringify({
      productId: SUBSCRIPTION_PRODUCT_ID,
      transactionId: transaction.transactionId,
      realExpiryFound: false,
    }))
    return false
  }
  const expiryDate = new Date(expiryIso)
  if (Number.isNaN(expiryDate.getTime()) || expiryDate.getTime() <= Date.now()) return false
  console.info('[BrainActive Billing] Backend sync attempted', JSON.stringify({
    productId: SUBSCRIPTION_PRODUCT_ID,
    transactionId: transaction.transactionId,
    realExpiryFound: Boolean(rawExpiry),
    expiry: expiryDate.toISOString(),
  }))
  try {
    const result = await syncBrainActivePurchaseEntitlement({
      product_id: SUBSCRIPTION_PRODUCT_ID,
      expiry_date: expiryDate.toISOString(),
      transaction_id: transaction.transactionId,
    })
    const synced = result?.is_pro === true
    console.info('[BrainActive Billing] Backend sync completed', JSON.stringify({
      success: synced,
      finalIsPro: result?.is_pro ?? false,
      expiry: result?.pro_expiry || expiryDate.toISOString(),
    }))
    return synced
  } catch (error) {
    console.warn('[BrainActive Billing] Backend sync failed:', error)
    return false
  }
}

function latestSubscriptionTransaction() {
  const all = CdvPurchase.store.localTransactions.filter(transaction =>
    transaction.products.some(product => product.id === SUBSCRIPTION_PRODUCT_ID)
  )
  const valid = all.filter(transaction => !['cancelled', 'failed', 'expired'].includes(String((transaction as any).state || '')))
  if (valid.length === 0) return undefined
  return valid.sort((a, b) => {
    const aExpiry = extractTransactionExpiry(a)
    const bExpiry = extractTransactionExpiry(b)
    const aTime = aExpiry ? new Date(aExpiry).getTime() : ((a as any).purchaseDate?.getTime?.() || 0)
    const bTime = bExpiry ? new Date(bExpiry).getTime() : ((b as any).purchaseDate?.getTime?.() || 0)
    return bTime - aTime
  })[0]
}

async function applyApprovedTransaction(transaction: CdvPurchase.Transaction) {
  const rawExpiry = extractTransactionExpiry(transaction)
  const effectiveExpiry = rawExpiry || getFallbackSubscriptionExpiry(transaction)
  const realExpiryFound = Boolean(rawExpiry)
  console.info('[BrainActive Billing] Purchase detected', JSON.stringify({
    productId: transaction.products.map(product => product.id),
    state: transaction.state,
    transactionId: transaction.transactionId,
    realExpiryFound,
    expiry: effectiveExpiry,
  }))
  if (!isSubscriptionTransaction(transaction)) return
  setSubscriptionActive(true)
  setSubscriptionExpiryIfLater(effectiveExpiry)
  await syncBackendEntitlement(transaction, effectiveExpiry)
  notifyEntitlementChanged()
  try {
    await transaction.finish()
    console.info('[BrainActive Billing] finish completed', { transactionId: transaction.transactionId })
  } catch (error) {
    console.warn('[BrainActive Billing] finish failed:', error)
  }
}

export async function syncBillingEntitlement(): Promise<boolean> {
  if (!Capacitor.isNativePlatform()) return getSubscriptionActive() || Boolean(getSubscriptionExpiry())
  const transaction = latestSubscriptionTransaction()
  if (!transaction || !isSubscriptionTransaction(transaction)) {
    console.info('[BrainActive Billing] No valid subscription transaction; preserving entitlement cache')
    return getSubscriptionActive() || Boolean(getSubscriptionExpiry())
  }
  const rawExpiry = extractTransactionExpiry(transaction)
  const effectiveExpiry = rawExpiry || getFallbackSubscriptionExpiry(transaction)
  console.info('[BrainActive Billing] Entitlement sync', JSON.stringify({
    productId: transaction.products.map(product => product.id),
    state: transaction.state,
    transactionId: transaction.transactionId,
    realExpiryFound: Boolean(rawExpiry),
    expiry: effectiveExpiry,
  }))
  setSubscriptionActive(true)
  setSubscriptionExpiryIfLater(effectiveExpiry)
  await syncBackendEntitlement(transaction, effectiveExpiry)
  notifyEntitlementChanged()
  return true
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
        store.register({ id: SUBSCRIPTION_PRODUCT_ID, type: ProductType.PAID_SUBSCRIPTION, platform: Platform.GOOGLE_PLAY })
        store.when().approved(applyApprovedTransaction)
        store.when().receiptUpdated((receipt: CdvPurchase.Receipt) => {
          console.info('[BrainActive Billing] Receipt updated', { transactionCount: receipt.transactions.length })
          void syncBillingEntitlement()
        })
        store.when().pending(() => console.info('[BrainActive Billing] Subscription purchase pending'))
        billingListenersRegistered = true
      }
      const wait = waitForNativePurchaseUpdate(nativePurchaseEventVersion)
      const errors = await store.initialize([Platform.GOOGLE_PLAY])
      await wait.promise
      if (errors?.some(error => error.isError)) {
        billingInitPromise = null
        return false
      }
      await syncBillingEntitlement()
      console.info('[BrainActive Billing] Billing initialization completed')
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
  if (!await initializeBilling()) return false
  const wait = waitForNativePurchaseUpdate(nativePurchaseEventVersion)
  try { await PurchasePlugin.getPurchases() } catch { wait.cancel() }
  await wait.promise
  return syncBillingEntitlement()
}

export async function restoreBillingPurchases(): Promise<boolean> {
  if (!Capacitor.isNativePlatform()) return false
  if (!await initializeBilling()) return false
  console.info('[BrainActive Billing] Restore started')
  const wait = waitForNativePurchaseUpdate(nativePurchaseEventVersion)
  try {
    const restoreError = await CdvPurchase.store.restorePurchases()
    if (restoreError?.isError) { wait.cancel(); return false }
    const received = await wait.promise
    const active = await syncBillingEntitlement()
    console.info('[BrainActive Billing] Restore completed', { receivedPurchaseUpdate: received, active })
    return active
  } catch (error) {
    wait.cancel()
    console.warn('[BrainActive Billing] Restore failed:', error)
    return false
  }
}

export async function purchaseSubscription(plan: 'yearly' | 'monthly') {
  if (!Capacitor.isNativePlatform()) return { isError: true, message: 'Google Play subscriptions are available in the Android app.' }
  if (!await initializeBilling()) return { isError: true, message: 'Google Play billing is unavailable.' }
  setStorage('last_purchase_plan', plan)
  const product = CdvPurchase.store.get(SUBSCRIPTION_PRODUCT_ID, Platform.GOOGLE_PLAY)
  const offerId = SUBSCRIPTION_OFFERS[plan]
  console.info('[BrainActive Billing] Offer selected', { productId: SUBSCRIPTION_PRODUCT_ID, plan, offerId })
  const offer = product?.getOffer(offerId)
  if (!offer) return { isError: true, message: 'This subscription plan is not available yet.' }
  const wait = waitForNativePurchaseUpdate(nativePurchaseEventVersion)
  try {
    const result = await offer.order()
    if (result?.isError) { wait.cancel(); return result }
    await wait.promise
    return result
  } catch (error) {
    wait.cancel()
    throw error
  }
}

export async function getSubscriptionPrices() {
  if (!Capacitor.isNativePlatform()) return null
  if (!await initializeBilling()) return null
  const product = CdvPurchase.store.get(SUBSCRIPTION_PRODUCT_ID, Platform.GOOGLE_PLAY)
  if (!product) return null
  return {
    yearly: product.getOffer(SUBSCRIPTION_OFFERS.yearly)?.pricingPhases[0]?.price || null,
    monthly: product.getOffer(SUBSCRIPTION_OFFERS.monthly)?.pricingPhases[0]?.price || null
  }
}
