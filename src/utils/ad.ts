/**
 * BrainActive AdMob Rewarded Ad Handler
 * Adapts Math Hero's robust ad lifecycle, state machine, and reward callback logic.
 */

import { AdMob, RewardAdOptions, RewardAdPluginEvents, MaxAdContentRating } from '@capacitor-community/admob'
import { Capacitor } from '@capacitor/core'
import Taro from '@tarojs/taro'
import { unlockBonusRound } from './storage'
import {
  ADMOB_REWARDED_AD_UNIT_ID,
  ADMOB_USE_PRODUCTION_ADS
} from '../config/monetization'

// -----------------------------------------------------------------------------
// Production identifiers are centralized in src/config/monetization.ts.
// H5 keeps its simulated reward flow; native production uses the configured unit.
// -----------------------------------------------------------------------------
const USE_TEST_ADS = !ADMOB_USE_PRODUCTION_ADS || !Capacitor.isNativePlatform()

// Retained for non-production native builds only.
const ADMOB_TEST_ID_REWARDED = 'ca-app-pub-3940256099942544/5224354917'

export const REWARD_AD_UNIT_ID = USE_TEST_ADS
  ? ADMOB_TEST_ID_REWARDED
  : ADMOB_REWARDED_AD_UNIT_ID

let isAdMobReady = false
let isLoading = false
let isShowing = false
let rewardGranted = false

export async function initAdMob(): Promise<void> {
  if (!Capacitor.isNativePlatform() || isAdMobReady) return
  try {
    await AdMob.initialize({
      // Families Policy (9–12 sole-children audience): COPPA child-directed
      // treatment + General-audience creative cap on every ad request.
      tagForChildDirectedTreatment: true,
      maxAdContentRating: MaxAdContentRating.General,
    })
    isAdMobReady = true
    console.log('[BrainActive AdMob] Initialized successfully')
  } catch (err: any) {
    console.warn('[BrainActive AdMob] Init failed:', err.message)
  }
}

export async function preloadRewardAd(): Promise<boolean> {
  if (!Capacitor.isNativePlatform()) return true
  if (isLoading || isShowing) return false

  try {
    isLoading = true
    const options: RewardAdOptions = {
      adId: REWARD_AD_UNIT_ID,
      isTesting: USE_TEST_ADS,
      // Families Policy (9–12 sole-children audience): always serve
      // non-personalized ads — no IBA/remarketing to children.
      npa: true
    }
    await AdMob.prepareRewardVideoAd(options)
    return true
  } catch (err: any) {
    return false
  } finally {
    isLoading = false
  }
}

export const preloadAd = preloadRewardAd

let activeRewardAdPromise: Promise<boolean> | null = null

async function runRewardAd(): Promise<boolean> {
  // If in web browser / dev mode, simulate successful ad view
  if (!Capacitor.isNativePlatform()) {
    Taro.showLoading({ title: 'Playing Bonus Video...' })
    await new Promise(r => setTimeout(r, 1200))
    Taro.hideLoading()
    unlockBonusRound()
    Taro.showToast({ title: 'Bonus Round Unlocked! 🎉', icon: 'success' })
    return true
  }

  let rewardSub: { remove: () => void | Promise<void> } | null = null
  let dismissSub: { remove: () => void | Promise<void> } | null = null
  const removeListeners = () => {
    rewardSub?.remove()
    dismissSub?.remove()
    rewardSub = null
    dismissSub = null
  }

  try {
    rewardGranted = false
    await initAdMob()
    let bonusRoundGranted = false
    let resolveAdResult: ((success: boolean) => void) | null = null

    const grantBonusRound = () => {
      if (!rewardGranted || bonusRoundGranted) return
      bonusRoundGranted = true
      unlockBonusRound()
      Taro.showToast({ title: 'Bonus Round Unlocked! 🎉', icon: 'success' })
    }

    const adResult = new Promise<boolean>(resolve => {
      resolveAdResult = resolve
    })

    Taro.showLoading({ title: 'Loading Video...' })

    rewardSub = await AdMob.addListener(
      RewardAdPluginEvents.Rewarded,
      () => {
        console.log('[BrainActive AdMob] Reward Earned!')
        rewardGranted = true
        grantBonusRound()
      }
    )

    dismissSub = await AdMob.addListener(
      RewardAdPluginEvents.Dismissed,
      () => {
        isShowing = false
        removeListeners()
        resolveAdResult?.(rewardGranted)
      }
    )

    const prepared = await preloadRewardAd()
    if (!prepared) throw new Error('Rewarded ad could not be prepared')
    isShowing = true
    Taro.hideLoading()
    await AdMob.showRewardVideoAd()
    return await adResult
  } catch (err: any) {
    Taro.hideLoading()
    isShowing = false
    removeListeners()
    console.error('[BrainActive AdMob] Show error:', err.message)
    if (rewardGranted) return true
    Taro.showModal({
      title: 'Bonus Round',
      content: 'Could not load video at this moment. Please try again later.',
      showCancel: false
    })
    return false
  }
}

export function showRewardAd(): Promise<boolean> {
  if (activeRewardAdPromise) return activeRewardAdPromise
  activeRewardAdPromise = runRewardAd()
  return activeRewardAdPromise.finally(() => {
    activeRewardAdPromise = null
  })
}
