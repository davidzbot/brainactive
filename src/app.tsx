import React, { useState } from 'react'
import { View, Text, Button } from '@tarojs/components'
import Taro, { useLaunch } from '@tarojs/taro'
import { getLang, setLang, getStorage, setStorage } from '@/utils/storage'
import { initAdMob } from '@/utils/ad'
import './styles/index.scss'

/**
 * Simple 3-page onboarding for new users
 */
const ONBOARDING_PAGES = [
  {
    en: { title: 'Welcome', subtitle: 'Daily brain training to keep your mind sharp.' },
    zh: { title: '欢迎', subtitle: '每日健脑训练，保持思维清晰。' }
  },
  {
    en: { title: 'Train Your Brain', subtitle: 'Memory, math, and language exercises combined for complete brain workout.' },
    zh: { title: '健脑训练', subtitle: '记忆、数学、语言综合训练，全方位锻炼大脑。' }
  },
  {
    en: { title: 'Start Now', subtitle: 'Just 10 minutes a day. Begin your brain health journey today.' },
    zh: { title: '开始训练', subtitle: '每天十分钟。现在开始您的健脑之旅。' }
  }
]

const ONBOARDING_KEY = 'onboarding_done'

function App({ children }: { children?: React.ReactNode }) {
  const [showOnboarding, setShowOnboarding] = useState(false)
  const [currentPage, setCurrentPage] = useState(0)

  useLaunch(() => {
    // Check if onboarding completed
    const onboardingDone = getStorage(ONBOARDING_KEY)
    if (!onboardingDone) {
      setShowOnboarding(true)
    }

    // Detect system language on first launch
    const savedLang = getLang()
    if (!savedLang) {
      try {
        const sysLang = Taro.getSystemInfoSync().language || ''
        const isChinese = sysLang.toLowerCase().includes('zh')
        setLang(isChinese ? 'zh' : 'en')
      } catch {
        setLang('en')
      }
    }

    // Initialize AdMob
    initAdMob()
  })

  const lang = getLang() || 'en'
  const t = ONBOARDING_PAGES[currentPage]
  const content = t[lang as 'en' | 'zh']

  const handleSkip = () => {
    setStorage(ONBOARDING_KEY, 'true')
    setShowOnboarding(false)
  }

  const handleNext = () => {
    if (currentPage < ONBOARDING_PAGES.length - 1) {
      setCurrentPage(currentPage + 1)
    } else {
      handleSkip()
    }
  }

  if (showOnboarding) {
    return (
      <View className='onboarding-container'>
        <View className='onboarding-dots'>
          {ONBOARDING_PAGES.map((_, idx) => (
            <View key={idx} className={`onboarding-dot ${idx === currentPage ? 'active' : ''}`} />
          ))}
        </View>
        <Button className='onboarding-skip' onClick={handleSkip}>
          {lang === 'zh' ? '跳过' : 'Skip'}
        </Button>
        <View className='onboarding-content'>
          <Text className='onboarding-title'>{content.title}</Text>
          <Text className='onboarding-subtitle'>{content.subtitle}</Text>
        </View>
        <View className='onboarding-footer'>
          <Button className='onboarding-next-btn' onClick={handleNext}>
            {currentPage < ONBOARDING_PAGES.length - 1
              ? (lang === 'zh' ? '下一步' : 'Next')
              : (lang === 'zh' ? '开始' : 'Get Started')}
          </Button>
        </View>
      </View>
    )
  }

  return children
}

export default App
