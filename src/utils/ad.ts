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

let isShowingAd = false; // Global lock to prevent multiple concurrent ads
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
  if (!isInitialized || isShowingAd) return;
  
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
    if (!isShowingAd) preloadRewardAd(); 
  });
}

/**
 * Integrated showRewardAd function - Event Driven with Global Lock
 */
export async function showRewardAd(): Promise<boolean> {
  const platform = Capacitor.getPlatform();
  
  // 1. Check Global Lock
  if (isShowingAd) {
    return false;
  }
  
  // Web/H5 fallback
  if (platform === 'web') {
    executeUnlock();
    return true;
  }

  isShowingAd = true;
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
        
        isShowingAd = false; // Release Global Lock
        isPrepared = false;
        
        if (rewarded) {
          executeUnlock();
        } else {
          // Fail-open for UX consistency
          executeUnlock();
        }
        
        preloadRewardAd(); // Fetch next
        resolve(true);
      };

      let listeners: any[] = [];
      const cleanupListeners = async () => {
        for (const l of listeners) {
          try {
            const handler = await l;
            handler.remove();
          } catch (e) {}
        }
      };

      // Register listeners for this specific show attempt
      listeners.push(AdMob.addListener(RewardAdPluginEvents.Rewarded, () => {
        rewardEarned = true;
      }));

      listeners.push(AdMob.addListener(RewardAdPluginEvents.Dismissed, () => {
        finish(rewardEarned);
      }));

      listeners.push(AdMob.addListener(RewardAdPluginEvents.FailedToLoad, () => finish(false)));
      listeners.push(AdMob.addListener(RewardAdPluginEvents.FailedToShow, () => finish(false)));

      // Safety Timeout (8s) - Matches fast experience by unlocking early if ad is slow
      const timeoutId = setTimeout(() => {
        finish(false);
      }, 8000);

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
    isShowingAd = false;
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
