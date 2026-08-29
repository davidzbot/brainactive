/**
 * BrainActive AdMob Rewarded Ad Handler
 * Adapts Math Hero's robust ad lifecycle, state machine, and reward callback logic.
 */

import { AdMob, RewardAdOptions, RewardAdPluginEvents } from '@capacitor-community/admob'
import { Capacitor } from '@capacitor/core'
import Taro from '@tarojs/taro'
import { unlockBonusRound } from './storage'

// -----------------------------------------------------------------------------
// ADMOB IDs CONFIGURATION (Rule #13)
// Old / placeholder values commented out, ready for new production BrainActive IDs.
// -----------------------------------------------------------------------------
const USE_TEST_ADS = process.env.NODE_ENV === 'development' || !Capacitor.isNativePlatform()

// Test ad unit fallback
const ADMOB_TEST_ID_REWARDED = 'ca-app-pub-3940256099942544/5224354917'

// OLD BrainActive rewarded unit: // 'ca-app-pub-8548627206908979/9317757823'
// NEW BrainActive rewarded unit placeholder (uncomment when provided):
// export const BRAINACTIVE_REWARDED_AD_UNIT_ID = 'ca-app-pub-xxxxxxxxxxxxxxxx/yyyyyyyyyy'

export const REWARD_AD_UNIT_ID = USE_TEST_ADS
  ? ADMOB_TEST_ID_REWARDED
  : 'ca-app-pub-3940256099942544/5224354917' // Default to test unit until new ID provided

let isAdMobReady = false
let isLoading = false
let isShowing = false
let rewardGranted = false

export async function initAdMob(): Promise<void> {
  if (!Capacitor.isNativePlatform() || isAdMobReady) return
  try {
    await AdMob.initialize({})
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
      isTesting: USE_TEST_ADS
    }
    await AdMob.prepareRewardVideoAd(options)
    isLoading = false
    return true
  } catch (err: any) {
    return false
  }
}

export const preloadAd = preloadRewardAd

export async function showRewardAd(): Promise<boolean> {
  // If in web browser / dev mode, simulate successful ad view
  if (!Capacitor.isNativePlatform()) {
    Taro.showLoading({ title: 'Playing Bonus Video...' })
    await new Promise(r => setTimeout(r, 1200))
    Taro.hideLoading()
    unlockBonusRound()
    Taro.showToast({ title: 'Bonus Round Unlocked! 🎉', icon: 'success' })
    return true
  }

  try {
    await initAdMob()
    rewardGranted = false
    isShowing = true

    Taro.showLoading({ title: 'Loading Video...' })

    // Setup listener for reward earned
    const rewardSub = await AdMob.addListener(
      RewardAdPluginEvents.Rewarded,
      () => {
        console.log('[BrainActive AdMob] Reward Earned!')
        rewardGranted = true
      }
    )

    const dismissSub = await AdMob.addListener(
      RewardAdPluginEvents.Dismissed,
      () => {
        isShowing = false
        rewardSub.remove()
        dismissSub.remove()
        if (rewardGranted) {
          unlockBonusRound()
          Taro.showToast({ title: 'Bonus Round Unlocked! 🎉', icon: 'success' })
        }
      }
    )

    await preloadRewardAd()
    Taro.hideLoading()
    await AdMob.showRewardVideoAd()
    return true
  } catch (err: any) {
    Taro.hideLoading()
    isShowing = false
    console.error('[BrainActive AdMob] Show error:', err.message)
    // Graceful fallback in case of no fill
    Taro.showModal({
      title: 'Bonus Round',
      content: 'Could not load video at this moment. You get 1 bonus round on us!',
      showCancel: false,
      success: () => {
        unlockBonusRound()
        Taro.showToast({ title: 'Bonus Round Unlocked! 🎉', icon: 'success' })
      }
    })
    return true
  }
}
