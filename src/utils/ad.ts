import Taro, { showLoading, hideLoading } from '@tarojs/taro'
import { unlockAllModes } from './common'
import { t } from './i18n'
import { Toast } from '@capacitor/toast'

/**
 * Professional Ad Simulation
 * 
 * FOR GOOGLE PLAY STORE INTEGRATION:
 * 1. Install @capacitor-community/admob
 * 2. Follow the setup guide: https://github.com/capacitor-community/admob
 * 3. Replace the mock delay below with real AdMob lifecycle events:
 *    - AdMob.showRewardVideoAd()
 *    - Listen for 'onRewardedVideoAdReward' event to call unlockAllModes()
 */
async function showAd(): Promise<void> {
  return new Promise((resolve) => {
    showLoading({ title: t('task.loading') })
    
    // Professional delay (3 seconds) for mock
    setTimeout(() => {
      hideLoading()
      resolve()
    }, 3000)
  })
}

export async function watchAdAndUnlock(): Promise<boolean> {
  try {
    await showAd()
    unlockAllModes()
    await Toast.show({
      text: t('app.unlimited'),
      duration: 'short',
      position: 'bottom'
    })
    return true
  } catch (e) {
    console.error('Ad session interrupted', e)
    await Toast.show({
      text: 'Session interrupted. Please try again.',
      duration: 'short',
      position: 'bottom'
    })
    return false
  }
}
