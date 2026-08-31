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
  return (
    transaction.products.some(product => product.id === SUBSCRIPTION_PRODUCT_ID) &&
    !transaction.isPending &&
    (transaction.state === 'approved' || transaction.state === 'finished')
  )
}

async function syncBackendEntitlement(transaction: CdvPurchase.Transaction): Promise<boolean> {
  const expirationDate = transaction.expirationDate
  if (!expirationDate || expirationDate.getTime() <= Date.now()) {
    console.warn('[BrainActive Billing] Backend entitlement sync skipped: no future expiry', {
      productId: SUBSCRIPTION_PRODUCT_ID,
      transactionId: transaction.transactionId,
      expirationDate: expirationDate?.toISOString() || null,
    })
    return false
  }

  try {
    const result = await syncBrainActivePurchaseEntitlement({
      product_id: SUBSCRIPTION_PRODUCT_ID,
      expiry_date: expirationDate.toISOString(),
      transaction_id: transaction.transactionId,
    })
    const synced = result?.is_pro === true
    console.info('[BrainActive Billing] Backend entitlement sync completed', {
      productId: SUBSCRIPTION_PRODUCT_ID,
      transactionId: transaction.transactionId,
      expiry: expirationDate.toISOString(),
      synced,
    })
    return synced
  } catch (error) {
    console.warn('[BrainActive Billing] Backend entitlement sync failed:', error)
    return false
  }
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
  const productIds = transaction.products.map(product => product.id)
  console.info('[BrainActive Billing] Approved transaction', {
    productIds,
    offerIds: transaction.products.map(product => product.offerId || null),
    state: transaction.state,
    transactionId: transaction.transactionId,
    expirationDate: transaction.expirationDate?.toISOString() || null,
  })
  if (!isSubscriptionTransaction(transaction)) return

  const expirationDate = transaction.expirationDate
  if (expirationDate && expirationDate.getTime() <= Date.now()) {
    console.warn('[BrainActive Billing] Approved transaction is already expired')
    setSubscriptionActive(false)
    setSubscriptionExpiry(null)
    notifyEntitlementChanged()
  } else {
    setSubscriptionActive(true)
    if (expirationDate) {
      setSubscriptionExpiry(expirationDate.toISOString())
      console.info('[BrainActive Billing] subscription_expiry written', {
        expirationDate: expirationDate.toISOString(),
      })
      await syncBackendEntitlement(transaction)
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
  const transaction = latestSubscriptionTransaction()
  if (transaction && isSubscriptionTransaction(transaction)) {
    console.info('[BrainActive Billing] Sync transaction', {
      productIds: transaction.products.map(product => product.id),
      offerIds: transaction.products.map(product => product.offerId || null),
      state: transaction.state,
      transactionId: transaction.transactionId,
      expirationDate: transaction.expirationDate?.toISOString() || null,
      recognizedProduct: transaction.products.some(product => product.id === SUBSCRIPTION_PRODUCT_ID),
    })
    if (transaction.expirationDate && transaction.expirationDate.getTime() <= Date.now()) {
      setSubscriptionActive(false)
      setSubscriptionExpiry(null)
      console.info('[BrainActive Billing] Cleared expired subscription_expiry')
      notifyEntitlementChanged()
      return false
    }
    setSubscriptionActive(true)
    if (transaction.expirationDate) {
      setSubscriptionExpiry(transaction.expirationDate.toISOString())
      console.info('[BrainActive Billing] subscription_expiry written', {
        expirationDate: transaction.expirationDate.toISOString(),
      })
      await syncBackendEntitlement(transaction)
    }
    notifyEntitlementChanged()
    return true
  }
  const state = String(transaction?.state || '')
  if (state === 'cancelled' || state === 'failed') {
    setSubscriptionActive(false)
    setSubscriptionExpiry(null)
    console.info('[BrainActive Billing] Cleared terminal subscription state', JSON.stringify({ state, transactionId: transaction?.transactionId || null }))
    notifyEntitlementChanged()
    return false
  }
  console.info('[BrainActive Billing] No transaction available; preserving cached entitlement')
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
