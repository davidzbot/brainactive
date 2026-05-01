import { 
  AdMob, 
  RewardAdOptions, 
  RewardAdPluginEvents, 
  AdLoadInfo, 
  AdmobAds 
} from '@capacitor-community/admob';
import { unlockAllModes } from './common';
import { t } from './i18n';
import { Toast } from '@capacitor/toast';
import Taro, { showLoading, hideLoading } from '@tarojs/taro';

/**
 * AdMob Configuration
 */
const REWARD_AD_UNIT_ID = 'ca-app-pub-8548627206908979/6689305699';
let isAdLoading = false;

/**
 * Integrated showRewardAd function
 * Enhanced with production debug logging
 */
export async function showRewardAd(): Promise<boolean> {
  if (isAdLoading) {
    return false;
  }

  isAdLoading = true;
  showLoading({ title: t('task.loading'), mask: true });

  try {
    // 1. Initialize AdMob
    await AdMob.initialize({
      requestTrackingAuthorization: true,
      testingDevices: [],
      initializeForTesting: false,
    });

    // 2. Prepare Rewarded Ad
    const options: RewardAdOptions = {
      adId: REWARD_AD_UNIT_ID,
      isTesting: false,
    };
    
    await AdMob.prepareRewardVideoAd(options);

    // 3. Define the Promise-based flow
    return new Promise((resolve) => {
      let rewardEarned = false;

      // Event: Reward Received
      const rewardListener = AdMob.addListener(RewardAdPluginEvents.Rewarded, (reward) => {
        rewardEarned = true;
      });

      // Event: Ad Dismissed
      const dismissListener = AdMob.addListener(RewardAdPluginEvents.Dismissed, () => {
        cleanup();
        executeUnlock();
        resolve(true);
      });

      // Event: Failed to Load
      const failedListener = AdMob.addListener(RewardAdPluginEvents.FailedToLoad, (info: AdLoadInfo) => {
        console.error('[AdMob] Failed to Load', info);
        cleanup();
        executeUnlock();
        resolve(true);
      });

      // Event: Failed to Show
      const showFailedListener = AdMob.addListener(RewardAdPluginEvents.FailedToShow, (error) => {
        console.error('[AdMob] Failed to Show', error);
        cleanup();
        executeUnlock();
        resolve(true);
      });

      // Helper: Remove listeners and hide loading
      const cleanup = () => {
        rewardListener.remove();
        dismissListener.remove();
        failedListener.remove();
        showFailedListener.remove();
        hideLoading();
        isAdLoading = false;
      };

      // Helper: Execute the 24h unlock (Business Logic Unchanged)
      const executeUnlock = () => {
        unlockAllModes();
        Toast.show({
          text: t('app.unlimited'),
          duration: 'short',
          position: 'bottom'
        });
      };

      // 4. Show the ad
      AdMob.showRewardVideoAd();
    });

  } catch (e) {
    console.error('[AdMob] Exception', e);
    
    hideLoading();
    isAdLoading = false;
    unlockAllModes();
    return true;
  }
}

/**
 * Legacy compatibility export
 */
export async function watchAdAndUnlock(): Promise<boolean> {
  return await showRewardAd();
}
