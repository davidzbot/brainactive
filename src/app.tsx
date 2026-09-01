import React, { useState, useEffect } from 'react'
import { View, Text, Button } from '@tarojs/components'
import Taro, { useLaunch } from '@tarojs/taro'
import { Capacitor } from '@capacitor/core'
import { App as CapApp } from '@capacitor/app'
import { getLang, setLang, getStorage, setStorage } from '@/utils/storage'
import { initAdMob } from '@/utils/ad'
import { initializeBilling, refreshBillingEntitlement } from '@/utils/billing'
import './styles/index.scss'

/**
 * P3 Thinking Skills Onboarding
 */
const ONBOARDING_PAGES = [
  {
    en: { title: 'Welcome to BrainActive', subtitle: 'Build Thinking Skills for Singapore Primary 3 High Ability.' },
    zh: { title: '欢迎来到 BrainActive', subtitle: '专为新加坡小三高能力学生打造的思维与推理训练。' }
  },
  {
    en: { title: 'Sharp Thinking, Not Memorisation', subtitle: 'Practise logic, patterns, spatial and verbal reasoning — the thinking skills that truly matter.' },
    zh: { title: '思维训练，而非死记硬背', subtitle: '逻辑、图形、空间与语言推理全面训练，培养真正重要的思维能力。' }
  },
  {
    en: { title: 'Daily Thinking Quest', subtitle: 'Just 5 curated questions a day. Train your reasoning power consistently.' },
    zh: { title: '每日思维挑战', subtitle: '每天精选 5 道思维好题，循序渐进培养高阶解题能力。' }
  }
]

const ONBOARDING_KEY = 'onboarding_done_v2'
let lastBackPress = 0

function App({ children }: { children?: React.ReactNode }) {
  const [showOnboarding, setShowOnboarding] = useState(false)
  const [currentPage, setCurrentPage] = useState(0)

  useEffect(() => {
    // Android Back Button handler
    if (Capacitor.isNativePlatform()) {
      const backSub = CapApp.addListener('backButton', () => {
        const now = Date.now()
        const pages = Taro.getCurrentPages()
        const currentRoute = pages[pages.length - 1]?.route

        if (currentRoute === 'pages/home/index' || pages.length <= 1) {
          if (now - lastBackPress < 2000) {
            CapApp.exitApp()
          } else {
            lastBackPress = now
            Taro.showToast({ title: 'Press Back again to close the app', icon: 'none', duration: 2000 })
          }
        } else {
          Taro.navigateBack()
        }
      })
      const appStateSub = CapApp.addListener('appStateChange', ({ isActive }) => {
        if (isActive) refreshBillingEntitlement()
      })

      return () => {
        backSub.then(sub => sub.remove())
        appStateSub.then(sub => sub.remove())
      }
    }
  }, [])

  useLaunch(() => {
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

    // Initialize test-safe AdMob and native Play Billing.
    initAdMob()
    initializeBilling()
  })

  const lang = getLang() || 'en'
  const t = ONBOARDING_PAGES[currentPage] || ONBOARDING_PAGES[0]
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

  return (
    <>
      {children}
      {showOnboarding && (
        <View 
          className='onboarding-container' 
          catchMove 
          onTouchMove={(e) => e.stopPropagation()}
        >
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
                : (lang === 'zh' ? '开始训练' : 'Get Started')}
            </Button>
          </View>
        </View>
      )}
    </>
  )
}

export default App
