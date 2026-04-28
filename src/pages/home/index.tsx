import Taro, { useState, useEffect } from 'react'
import { View, Text, Button } from '@tarojs/components'
import { useLoad, useDidShow, navigateTo, setNavigationBarTitle, setClipboardData } from '@tarojs/taro'
import { getLang, setLang, getStorage, setStorage } from '@/utils/storage'
import { isAdUnlocked, unlockAllModes, canPlayMode, getDailyUsage, formatDate, parseDateSafe } from '@/utils/common'
import { dataUtils } from '@/utils/data'
import { t } from '@/utils/i18n'
import './index.scss'

export default function HomePage() {
  const [streak, setStreak] = useState(0)
  const [difficulty, setDifficulty] = useState('easy')
  const [currentTips, setCurrentTips] = useState<string[]>([])
  const [todayStatus, setTodayStatus] = useState('')
  const [isUnlocked, setIsUnlocked] = useState(false)
  const [language, setLanguage] = useState(getLang())
  const [tapCount, setTapCount] = useState(0)

  useLoad(() => {
    // Default to 'en' if no language is set
    const savedLang = getLang()
    if (!savedLang) {
      setLang('en')
      setLanguage('en')
    }
    
    let savedDifficulty = 'easy'
    let savedStreak = 0
    try {
      savedDifficulty = getStorage('lastDifficulty') || 'easy'
      savedStreak = getStorage('streak') || 0
    } catch (e) {
      console.error('Storage read failed', e)
    }

    const randomTips = getRandomTips(dataUtils.tips)

    setStreak(savedStreak)
    setDifficulty(savedDifficulty)
    setCurrentTips(randomTips)
    setTodayStatus(generateStatus(savedStreak))
    setIsUnlocked(isAdUnlocked())
    
    setNavigationBarTitle({ title: t('app.title') })
  })

  useDidShow(() => {
    setIsUnlocked(isAdUnlocked())
    checkStreakGuard()
    setNavigationBarTitle({ title: t('app.title') })
  })

  const toggleLanguage = () => {
    const newLang = language === 'en' ? 'zh' : 'en'
    setLang(newLang)
    setLanguage(newLang)
    setNavigationBarTitle({ title: t('app.title') })
    setTodayStatus(generateStatus(streak))
    setCurrentTips(getRandomTips(dataUtils.tips))
  }

  const checkStreakGuard = () => {
    try {
      const last = getStorage('lastTrainingDate')
      if (!last) return

      const now = new Date()
      const todayStr = formatDate(now)
      
      const lastDate = parseDateSafe(last)
      const todayDate = parseDateSafe(todayStr)

      if (lastDate && todayDate) {
        const diff = Math.floor((todayDate.getTime() - lastDate.getTime()) / (1000 * 60 * 60 * 24))
        if (diff > 1) {
          setStorage('streak', 0)
          setStreak(0)
          setTodayStatus(generateStatus(0))
        }
      }
    } catch (e) {
      console.error('Streak guard failed', e)
    }
  }

  const getRandomTips = (arr: string[]) => {
    const count = Math.floor(Math.random() * 2) + 1
    const shuffled = [...arr].sort(() => 0.5 - Math.random())
    return shuffled.slice(0, count).map(t_str => t('tip.prefix') + t_str)
  }

  const generateStatus = (s: number): string => {
    if (isAdUnlocked()) return t('app.unlimited')
    if (s === 0) return t('app.status.0')
    if (s < 3) return t('app.status.low', { s })
    if (s < 7) return t('app.status.mid', { s })
    return t('app.status.high', { s })
  }

  const selectDifficulty = async (level: string) => {
    if (!canPlayMode(level)) {
      const res = await Taro.showModal({
        title: t('mode.limit'),
        content: t('cta.ad'),
        confirmText: language === 'zh' ? '观看解锁' : 'Watch to Unlock',
      })
      
      if (res.confirm) {
        handleWatchAd()
      }
      return
    }

    try {
      setStorage('lastDifficulty', level)
    } catch (e) {
      console.error('Failed to save difficulty', e)
    }
    setDifficulty(level)
  }

  const startExercise = () => {
    if (!canPlayMode(difficulty)) {
      selectDifficulty(difficulty)
      return
    }
    navigateTo({
      url: `/pages/task/index?difficulty=${difficulty}`
    })
  }

  const handleWatchAd = async () => {
    Taro.showLoading({ title: t('zh' ? '加载广告...' : 'Loading Ad...' as any) })
    
    // Simulate Ad loading and watching
    setTimeout(() => {
      Taro.hideLoading()
      unlockAllModes()
      setIsUnlocked(true)
      setTodayStatus(t('app.unlimited'))
      Taro.showToast({ title: t('app.unlimited'), icon: 'success' })
    }, 2000)
  }

  const handleShare = async () => {
    try {
      const { Share } = require('@capacitor/share')
      await Share.share({
        title: t('app.title'),
        text: "I’ve been using this brain training app daily 🧠\n\nIt’s simple but surprisingly effective.\n\nTry it 👇",
        url: 'https://brainactive.app',
        dialogTitle: t('button.share'),
      })
    } catch (e) {
      console.error('Capacitor Share failed', e)
    }
  }

  const copyEmail = () => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText('pslehero@gmail.com').then(() => {
        Taro.showToast({ title: t('footer.feedback' as any), icon: 'success' })
      })
    }
  }

  const handleTitleTap = () => {
    const newCount = tapCount + 1
    setTapCount(newCount)
    if (newCount >= 5) {
      Taro.showActionSheet({
        itemList: ['Force Unlock', 'Reset Storage', 'Simulate API Failure'],
        success: (res) => {
          if (res.tapIndex === 0) {
            unlockAllModes()
            setIsUnlocked(true)
            setTodayStatus(t('app.unlimited'))
            Taro.showToast({ title: 'Unlocked' })
          } else if (res.tapIndex === 1) {
            Taro.clearStorage()
            Taro.reLaunch({ url: '/pages/home/index' })
          } else if (res.tapIndex === 2) {
            setStorage('simulate_api_fail', true)
            Taro.showToast({ title: 'API will fail next time' })
          }
        }
      })
      setTapCount(0)
    }
  }

  const renderModeCard = (level: string, emoji: string, labelKey: any) => {
    const isModeUnlocked = canPlayMode(level)
    const isActive = difficulty === level
    
    return (
      <View 
        className={`card card-${level} ${isActive ? 'active' : ''} ${!isModeUnlocked ? 'locked' : ''}`}
        onClick={() => selectDifficulty(level)}
      >
        <View className="emoji">{emoji}</View>
        <Text className="label">{t(labelKey)}</Text>
        {!isModeUnlocked && <Text className="lock-text">🔒 {t('mode.done')}</Text>}
      </View>
    )
  }

  return (
    <View className="container">
      <View className="lang-switcher" onClick={toggleLanguage}>
        <Text>{language === 'en' ? '🇨🇳 中文' : '🇺🇸 English'}</Text>
      </View>

      <View className="hero">
        <Text className="title" onClick={handleTitleTap}>{t('app.title')}</Text>
        <Text className="status">{todayStatus}</Text>
      </View>

      <View className="panel">
        <Text className="panel-title">{t('panel.title')}</Text>

        <View className="grid">
          {renderModeCard('easy', '🍵', 'difficulty.easy')}
          {renderModeCard('normal', '⚡', 'difficulty.normal')}
          {renderModeCard('pro', '🚀', 'difficulty.pro')}
        </View>

        {!isUnlocked && (
          <Button className="ad-unlock-btn" onClick={handleWatchAd}>
            📺 {t('cta.ad')}
          </Button>
        )}
      </View>

      <Button className="start" onClick={startExercise}>
        {t('button.start')}
      </Button>

      <View className="secondary-actions">
        <Button className="share-btn-small" onClick={handleShare}>
          {t('button.share')}
        </Button>
      </View>

      <View className="tips">
        {currentTips.map((item, index) => (
          <View className="tip-item" key={index}>{item}</View>
        ))}
      </View>

      <View className="footer">
        <Text onClick={copyEmail}>{t('footer.feedback')}</Text>
      </View>
    </View>
  )
}