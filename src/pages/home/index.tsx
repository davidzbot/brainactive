import React, { useState, useEffect } from 'react'
import { View, Text, Button } from '@tarojs/components'
import Taro, { useLoad, useDidShow, navigateTo, showModal, showActionSheet, clearStorage, reLaunch } from '@tarojs/taro'
import { getLang, setLang, getStorage, setStorage } from '@/utils/storage'
import { isAdUnlocked, unlockAllModes, canPlayMode, formatDate, parseDateSafe, setSafeTitle } from '@/utils/common'
import { showRewardAd } from '@/utils/ad'
import { dataUtils } from '@/utils/data'
import { t } from '@/utils/i18n'
import { SHARE_CONFIG } from '@/config/share'
import './index.scss'

export default function HomePage() {
  const [streak, setStreak] = useState(0)
  const [difficulty, setDifficulty] = useState('easy')
  const [currentTips, setCurrentTips] = useState<string[]>([])
  const [todayStatus, setTodayStatus] = useState('')
  const [isUnlocked, setIsUnlocked] = useState(false)
  const [unlockExpiry, setUnlockExpiry] = useState<number | null>(null)
  const [remainingTime, setRemainingTime] = useState('')
  const [language, setLanguage] = useState(getLang())
  const [tapCount, setTapCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [adLoading, setAdLoading] = useState(false)

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
    const expiry = getStorage('ad_unlock_until')
    setIsUnlocked(unlocked)
    setUnlockExpiry(expiry)
    if (unlocked && expiry) {
      updateRemainingTime(expiry)
    }
    return { unlocked, expiry }
  }

  const updateRemainingTime = (expiry: number) => {
    const now = Date.now()
    const diff = expiry - now
    if (diff <= 0) {
      setRemainingTime('')
      setIsUnlocked(false)
      return
    }
    const h = Math.floor(diff / (1000 * 60 * 60))
    const m = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
    setRemainingTime(t('app.expires_in', { h, m }))
  }

  useEffect(() => {
    let backListener: any = null
    const setupBackBtn = async () => {
      try {
        const { App } = require('@capacitor/app')
        backListener = await App.addListener('backButton', () => {
          App.exitApp()
        })
      } catch { }
    }
    setupBackBtn()
    return () => {
      if (backListener) backListener.remove()
    }
  }, [])

  useEffect(() => {
    let timer: any = null
    if (isUnlocked && unlockExpiry) {
      timer = setInterval(() => {
        updateRemainingTime(unlockExpiry)
      }, 60000)
    }
    return () => {
      if (timer) clearInterval(timer)
    }
  }, [isUnlocked, unlockExpiry])

  useLoad(() => {
    setLoading(true)
    const currentLang = getLang() || 'en'
    setLanguage(currentLang)
    
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
    if (adLoading) return
    console.log("[AD_DEBUG] CLICKED_WATCH_AD");
    setAdLoading(true)
    const success = await showRewardAd()
    setAdLoading(false)
    if (success) {
      const { unlocked } = checkUnlockStatus()
      updateStatus(streak, unlocked)
    }
  }

  const startTraining = async (level: string) => {
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
    navigateTo({ url: `/pages/task/index?difficulty=${level}` })
  }

  const handleInvite = async () => {
    try {
      const { Share } = require('@capacitor/share')
      const cfg = language === 'zh' ? SHARE_CONFIG.zh : SHARE_CONFIG.en
      await Share.share({
        title: cfg.title,
        text: cfg.text,
        url: SHARE_CONFIG.url,
        dialogTitle: t('button.invite'),
      })
    } catch (e) {
      console.error('Invite failed', e)
    }
  }

  const handleShare = async () => {
    try {
      const { Share } = require('@capacitor/share')
      const cfg = language === 'zh' ? SHARE_CONFIG.zh : SHARE_CONFIG.en
      await Share.share({
        title: cfg.title,
        text: cfg.text,
        url: SHARE_CONFIG.url,
      })
    } catch { }
  }

  const handleTitleTap = () => {
    const nc = tapCount + 1
    setTapCount(nc)
    if (nc >= 10) {
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

  const renderModeCard = (level: string, labelKey: any, emoji: string) => {
    const isModeUnlocked = canPlayMode(level)
    return (
      <View 
        className={`mode-card mode-${level} ${!isModeUnlocked ? 'locked' : ''}`}
        onClick={() => startTraining(level)}
      >
        <View className="mode-info">
          <Text className="mode-label">{t(labelKey).replace(/\(.*\)/, '')}</Text>
          <Text className="mode-sub-label">{t(labelKey).match(/\(.*\)/)?.[0] || ''}</Text>
        </View>
        <Text className="mode-status">{!isModeUnlocked ? '🔒' : emoji}</Text>
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
          <View className="streak-card">
            <Text className="streak-emoji">🔥</Text>
            <View className="streak-info">
              <Text className="streak-text">{streak}</Text>
              <Text className="streak-unit">{t('common.days')}</Text>
            </View>
          </View>
        </View>
      </View>

      <View className="main-content">
        <View className="description-box">
           <Text className="app-description">{t('app.description')}</Text>
        </View>

        <View className="mode-grid-header">
          <Text className="section-title">{t('panel.title')}</Text>
        </View>

        <View className="mode-grid">
          {renderModeCard('easy', 'difficulty.easy', '🍵')}
          {renderModeCard('normal', 'difficulty.normal', '⚡')}
          {renderModeCard('pro', 'difficulty.pro', '🚀')}
        </View>

        <View className="status-card-section">
          <View className={`status-card ${isUnlocked ? 'is-unlocked' : 'is-locked'}`}>
            <View className="status-header">
              <Text className="status-label">{isUnlocked ? '✅ ' + t('app.unlocked') : '🔒 ' + t('app.locked')}</Text>
              {isUnlocked && <Text className="status-expiry">{remainingTime}</Text>}
            </View>
            <Text className="status-desc">
              {isUnlocked ? t('app.unlimited') : t('app.unlock_desc')}
            </Text>
            
            <Button 
              className={`status-cta ${isUnlocked ? 'secondary' : 'primary'} ${adLoading ? 'loading' : ''}`}
              onClick={handleWatchAd}
              disabled={adLoading}
            >
              {adLoading ? (
                <View className="btn-loading-content">
                  <View className="btn-spinner" />
                  <Text>{t('task.loading').replace('...', '')}</Text>
                </View>
              ) : (
                isUnlocked ? t('button.watch_again') : t('button.watch_to_unlock')
              )}
            </Button>
          </View>
        </View>

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
