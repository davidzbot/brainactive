import { 
  AdMob, 
  RewardAdOptions, 
  RewardAdPluginEvents, 
  AdLoadInfo
} from '@capacitor-community/admob';
import { Capacitor } from '@capacitor/core';
import { unlockAllModes } from './common';
import { t } from './i18n';
import { Toast } from '@capacitor/toast';
import Taro, { showLoading, hideLoading } from '@tarojs/taro';

/**
 * AdMob Configuration
 */
const USE_TEST_AD = false; 
const REAL_AD_UNIT_ID = 'ca-app-pub-8548627206908979/6689305699';
const TEST_AD_UNIT_ID = 'ca-app-pub-3940256099942544/5224354917';

const REWARD_AD_UNIT_ID = USE_TEST_AD ? TEST_AD_UNIT_ID : REAL_AD_UNIT_ID;

let isAdLoading = false;
let isInitialized = false;
let isPrepared = false;

/**
 * Initialize AdMob and Preload the first ad
 */
export async function initAdMob(): Promise<void> {
  const platform = Capacitor.getPlatform();
  if (isInitialized || platform === 'web') return;
  
  try {
    await AdMob.initialize({
      testingDevices: [],
      initializeForTesting: USE_TEST_AD,
    });
    isInitialized = true;
    setupAdListeners();
    preloadRewardAd();
  } catch (e) {
    console.error('AdMob: Init failed', e);
  }
}

/**
 * Preload a rewarded ad in the background
 */
async function preloadRewardAd(): Promise<void> {
  if (!isInitialized || isAdLoading) return;
  
  try {
    const options: RewardAdOptions = {
      adId: REWARD_AD_UNIT_ID,
      isTesting: USE_TEST_AD,
    };
    await AdMob.prepareRewardVideoAd(options);
  } catch (e) {
    console.error('AdMob: Preload failed', e);
  }
}

function setupAdListeners() {
  AdMob.addListener(RewardAdPluginEvents.Loaded, (info: AdLoadInfo) => {
    isPrepared = true;
  });
  
  AdMob.addListener(RewardAdPluginEvents.FailedToLoad, (info: any) => {
    isPrepared = false;
  });

  AdMob.addListener(RewardAdPluginEvents.FailedToShow, (error) => {
    isPrepared = false;
  });

  AdMob.addListener(RewardAdPluginEvents.Dismissed, () => {
    isPrepared = false;
    preloadRewardAd(); 
  });
}

/**
 * Integrated showRewardAd function - Event Driven
 */
export async function showRewardAd(): Promise<boolean> {
  const platform = Capacitor.getPlatform();
  
  if (isAdLoading) return false;
  
  // Web/H5 fallback (Mock reward for dev/web environment)
  if (platform === 'web') {
    executeUnlock();
    return true;
  }

  isAdLoading = true;
  showLoading({ title: t('task.loading'), mask: true });

  try {
    if (!isInitialized) await initAdMob();

    // On-demand prep if background preload hasn't finished
    if (!isPrepared) {
      const options: RewardAdOptions = {
        adId: REWARD_AD_UNIT_ID,
        isTesting: USE_TEST_AD,
      };
      try {
        await AdMob.prepareRewardVideoAd(options);
        // Small wait buffer for on-demand load
        await new Promise(r => setTimeout(r, 2000)); 
      } catch (e) {}
    }

    return new Promise((resolve) => {
      let finished = false;
      let rewardEarned = false;

      const finish = (rewarded: boolean) => {
        if (finished) return;
        finished = true;

        // Cleanup resources immediately
        clearTimeout(timeoutId);
        cleanupListeners();
        hideLoading();
        isAdLoading = false;
        isPrepared = false;
        
        if (rewarded) {
          executeUnlock();
        } else {
          // Fail-open: still grant reward if ad failed to load/show to protect UX
          // but distinction is kept in logic for future strict enforcement if needed
          executeUnlock();
        }
        
        preloadRewardAd(); // Fetch next for future use
        resolve(true);
      };

      let listeners: any[] = [];
      const cleanupListeners = async () => {
        for (const l of listeners) {
          const handler = await l;
          handler.remove();
        }
      };

      // 1. Reward event - The gold standard
      listeners.push(AdMob.addListener(RewardAdPluginEvents.Rewarded, () => {
        rewardEarned = true;
      }));

      // 2. Dismiss event - Happens AFTER user closes ad
      listeners.push(AdMob.addListener(RewardAdPluginEvents.Dismissed, () => {
        finish(rewardEarned);
      }));

      // 3. Failure events
      listeners.push(AdMob.addListener(RewardAdPluginEvents.FailedToLoad, () => finish(false)));
      listeners.push(AdMob.addListener(RewardAdPluginEvents.FailedToShow, () => finish(false)));

      // 4. Safety Timeout (20s max for the PLUGIN to trigger the ad)
      const timeoutId = setTimeout(() => {
        finish(false);
      }, 20000);

      if (isPrepared) {
        AdMob.showRewardVideoAd().catch(e => {
          finish(false);
        });
      } else {
        finish(false);
      }
    });

  } catch (e) {
    hideLoading();
    isAdLoading = false;
    executeUnlock();
    return true;
  }
}

function executeUnlock() {
  unlockAllModes();
  Toast.show({
    text: t('app.unlimited'),
    duration: 'short',
    position: 'bottom'
  });
}

/**
 * Legacy compatibility export
 */
export async function watchAdAndUnlock(): Promise<boolean> {
  return await showRewardAd();
}
