import React, { useState, useEffect } from 'react'
import { View, Text, Button } from '@tarojs/components'
import Taro, { useLoad, useDidShow, navigateTo, showModal, showActionSheet, clearStorage, reLaunch } from '@tarojs/taro'
import { getLang, setLang, getStorage, setStorage } from '@/utils/storage'
import { isAdUnlocked, unlockAllModes, canPlayMode, formatDate, parseDateSafe, setSafeTitle } from '@/utils/common'
import { watchAdAndUnlock } from '@/utils/ad'
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
  const [loading, setLoading] = useState(true)

  const updateStatus = (s: number, unlocked: boolean) => {
    if (unlocked) {
      setTodayStatus(t('app.unlimited'))
    } else if (s === 0) {
      setTodayStatus(t('app.status.0'))
    } else if (s < 3) {
      setTodayStatus(t('app.status.low', { s }))
    } else if (s < 7) {
      setTodayStatus(t('app.status.mid', { s }))
    } else {
      setTodayStatus(t('app.status.high', { s }))
    }
  }

  const checkUnlockStatus = () => {
    const unlocked = isAdUnlocked()
    setIsUnlocked(unlocked)
    return { unlocked }
  }

  useLoad(() => {
    setLoading(true)
    const savedLang = getLang() || 'en'
    if (!getLang()) setLang('en')
    
    const savedDiff = getStorage('lastDifficulty') || 'easy'
    const savedStreak = getStorage('streak') || 0
    const { unlocked } = checkUnlockStatus()

    setStreak(savedStreak)
    setDifficulty(savedDiff)
    setCurrentTips(getRandomTips(dataUtils.tips))
    updateStatus(savedStreak, unlocked)
    setSafeTitle(t('app.title'))
    
    setTimeout(() => setLoading(false), 500)
  })

  useDidShow(() => {
    const { unlocked } = checkUnlockStatus()
    checkStreakGuard()
    updateStatus(streak, unlocked)
    setSafeTitle(t('app.title'))
  })

  const toggleLanguage = () => {
    const newLang = language === 'en' ? 'zh' : 'en'
    setLang(newLang)
    setLanguage(newLang)
    setSafeTitle(t('app.title'))
    updateStatus(streak, isUnlocked)
    setCurrentTips(getRandomTips(dataUtils.tips))
  }

  const checkStreakGuard = () => {
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
        updateStatus(0, isUnlocked)
      }
    }
  }

  const getRandomTips = (arr: string[]) => {
    const shuffled = [...arr].sort(() => 0.5 - Math.random())
    return shuffled.slice(0, 1).map(ts => t('tip.prefix') + ts)
  }

  const handleWatchAd = async () => {
    const success = await watchAdAndUnlock()
    if (success) {
      const { unlocked } = checkUnlockStatus()
      updateStatus(streak, unlocked)
    }
  }

  const selectDifficulty = async (level: string) => {
    if (!canPlayMode(level)) {
      const res = await showModal({
        title: t('mode.limit'),
        content: t('app.unlock_desc'),
        confirmText: language === 'zh' ? '开启访问' : 'Unlock Now',
      })
      if (res.confirm) handleWatchAd()
      return
    }
    setStorage('lastDifficulty', level)
    setDifficulty(level)
  }

  const startExercise = () => {
    if (!canPlayMode(difficulty)) {
      selectDifficulty(difficulty)
      return
    }
    navigateTo({ url: `/pages/task/index?difficulty=${difficulty}` })
  }

  const handleInvite = async () => {
    try {
      const { Share } = require('@capacitor/share')
      await Share.share({
        title: t('app.title'),
        text: t('invite.text'),
        url: 'https://brainactive.app',
        dialogTitle: t('button.invite'),
      })
    } catch (e) {
      console.error('Invite failed', e)
    }
  }

  const handleShare = async () => {
    try {
      const { Share } = require('@capacitor/share')
      await Share.share({
        title: t('app.title'),
        text: t('app.subtitle'),
        url: 'https://brainactive.app',
      })
    } catch (e) {}
  }

  const handleTitleTap = () => {
    const nc = tapCount + 1
    setTapCount(nc)
    if (nc >= 5) {
      showActionSheet({
        itemList: ['Force Unlock', 'Reset Storage'],
        success: (res) => {
          if (res.tapIndex === 0) {
            unlockAllModes()
            checkUnlockStatus()
            updateStatus(streak, true)
          } else if (res.tapIndex === 1) {
            clearStorage()
            reLaunch({ url: '/pages/home/index' })
          }
        }
      })
      setTapCount(0)
    }
  }

  const renderModeCard = (level: string, labelKey: any) => {
    const isModeUnlocked = canPlayMode(level)
    const isActive = difficulty === level
    return (
      <View 
        className={`mode-card mode-${level} ${isActive ? 'active' : ''} ${!isModeUnlocked ? 'locked' : ''}`}
        onClick={() => selectDifficulty(level)}
      >
        <Text className="mode-label">{t(labelKey).replace(/\(.*\)/, '')}</Text>
        <Text className="mode-sub-label">{t(labelKey).match(/\(.*\)/)?.[0] || ''}</Text>
        {!isModeUnlocked && <Text className="mode-status">🔒</Text>}
      </View>
    )
  }

  return (
    <View className="home-container">
      {loading && (
        <View className="loading-screen">
          <View className="spinner" />
        </View>
      )}

      <View className="hero-section">
        <View className="top-bar">
          <View className="lang-toggle" onClick={toggleLanguage}>
            <Text>{language === 'en' ? '中' : 'EN'}</Text>
          </View>
        </View>
        
        <View className="hero-content">
          <Text className="app-title" onClick={handleTitleTap}>{t('app.title')}</Text>
          <Text className="app-subtitle">{t('app.subtitle')}</Text>
          <View className="status-badge">
            <Text className="status-text">{todayStatus}</Text>
          </View>
        </View>
      </View>

      <View className="main-content">
        <View className="description-box">
           <Text className="app-description">{t('app.description')}</Text>
        </View>

        <Text className="section-title">{t('panel.title')}</Text>
        <View className="mode-grid">
          {renderModeCard('easy', 'difficulty.easy')}
          {renderModeCard('normal', 'difficulty.normal')}
          {renderModeCard('pro', 'difficulty.pro')}
        </View>

        {!isUnlocked && (
          <View className="unlock-card" onClick={handleWatchAd}>
            <Text className="unlock-title">📺 {t('cta.ad')}</Text>
            <Text className="unlock-desc">{t('app.unlock_desc')}</Text>
          </View>
        )}

        <Button className="primary-btn" onClick={startExercise}>
          {t('button.start')}
        </Button>

        <Button className="invite-btn" onClick={handleInvite}>
          👥 {t('button.invite')}
        </Button>
      </View>

      <View className="footer-section">
        <View className="insight-box">
          {currentTips.map((tip, i) => (
            <Text key={i} className="insight-text">{tip}</Text>
          ))}
        </View>
        <Text className="share-link" onClick={handleShare}>{t('button.share')}</Text>
        <Text className="feedback-text">{t('footer.feedback')}</Text>
      </View>
    </View>
  )
}
