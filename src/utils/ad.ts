import Taro, { showLoading, hideLoading } from '@tarojs/taro'
import { unlockAllModes } from './common'
import { t } from './i18n'
import { Toast } from '@capacitor/toast'

/**
 * Mock function to simulate showing an ad.
 * In a real app, this would integrate with AdMob or another provider.
 */
async function showAd(): Promise<void> {
  return new Promise((resolve, reject) => {
    showLoading({ title: t('task.loading') })
    
    // Simulate ad playback delay
    setTimeout(() => {
      hideLoading()
      // 90% success rate for mock
      if (Math.random() > 0.1) {
        resolve()
      } else {
        reject(new Error('Ad failed to load'))
      }
    }, 2000)
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
    console.error('Ad failed', e)
    await Toast.show({
      text: 'Ad failed. Try again.',
      duration: 'short',
      position: 'bottom'
    })
    return false
  }
}
