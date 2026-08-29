import React, { useState, useEffect } from 'react'
import { View, Text, Button } from '@tarojs/components'
import Taro, { useDidShow } from '@tarojs/taro'
import {
  getStreak,
  getDailyUsage,
  getRemainingFreeRounds,
  canStartPractice,
  isPro,
  getProExpiry,
  getLang,
  getDeviceId
} from '@/utils/storage'
import { getBrainActiveProgress } from '@/utils/request'
import ReferralModal from '@/components/ReferralModal'
import QuotaOverlay from '@/components/QuotaOverlay'
import SettingsModal from '@/components/SettingsModal'
import './index.scss'

export default function HomePage() {
  const [streak, setStreak] = useState(0)
  const [dailyRounds, setDailyRounds] = useState(0)
  const [remainingFree, setRemainingFree] = useState(2)
  const [proActive, setProActive] = useState(false)
  const [proExpiryText, setProExpiryText] = useState('')
  const [lang, setLocalLang] = useState<'en' | 'zh'>('en')

  const [showReferral, setShowReferral] = useState(false)
  const [showQuota, setShowQuota] = useState(false)
  const [showSettings, setShowSettings] = useState(false)

  const refreshState = () => {
    const currentStreak = getStreak()
    const usage = getDailyUsage()
    const remaining = getRemainingFreeRounds()
    const pro = isPro()
    const currentLang = getLang()

    setStreak(currentStreak)
    setDailyRounds(usage.roundsCompleted)
    setRemainingFree(remaining)
    setProActive(pro)
    setLocalLang(currentLang)

    const exp = getProExpiry()
    if (exp) {
      const d = new Date(exp)
      setProExpiryText(d.toLocaleDateString())
    }
  }

  useDidShow(() => {
    refreshState()
    // Sync with remote progress if available
    try {
      getBrainActiveProgress(getDeviceId()).then((data) => {
        if (data) {
          if (data.is_pro) setProActive(true)
          if (data.streak_count) setStreak(data.streak_count)
        }
      }).catch(() => {})
    } catch {}
  })

  const handleStartQuickTest = () => {
    if (!canStartPractice()) {
      setShowQuota(true)
      return
    }
    Taro.navigateTo({
      url: '/pages/quiz/index?mode=quick_test'
    })
  }

  const handleOpenPro = () => {
    Taro.navigateTo({
      url: '/pages/pro/index'
    })
  }

  const getUsageText = () => {
    if (proActive) return '👑 Unlimited Pro Access'
    if (remainingFree > 0) {
      return `🎯 ${remainingFree} free round${remainingFree !== 1 ? 's' : ''} left today`
    }
    const usage = getDailyUsage()
    const adRoundsLeft = Math.max(0, 3 - usage.bonusRounds)
    if (adRoundsLeft > 0) {
      return `🎬 ${adRoundsLeft} ad unlock${adRoundsLeft !== 1 ? 's' : ''} available today`
    }
    return '🏁 Daily free limit reached (5/5 rounds)'
  }

  return (
    <View className="home-container">
      {/* Top Bar: Settings & Streak */}
      <View className="top-bar">
        <View className="brand-badge">
          <Text className="brand-name">BrainActive</Text>
          <Text className="brand-tag">P3 High Ability</Text>
        </View>

        <View className="top-right-actions">
          <View className="streak-badge">
            <Text className="streak-icon">🔥</Text>
            <Text className="streak-count">
              {streak === 0 ? 'Start streak' : `${streak}d`}
            </Text>
          </View>
          <View className="settings-btn" onClick={() => setShowSettings(true)}>
            <Text className="settings-icon">⚙️</Text>
          </View>
        </View>
      </View>

      {/* Hero Banner / Header */}
      <View className="hero-section">
        <Text className="hero-subtitle">Singapore P3 Thinking Skills</Text>
        <Text className="hero-title">Daily Thinking Quest 🧠</Text>
        <Text className="hero-desc">
          Build reasoning power through non-routine questions — logic, patterns, and problem solving.
        </Text>
      </View>

      {/* Main Quick Test Card */}
      <View className="quick-test-card">
        <View className="card-top">
          <View className="card-badge">
            <Text className="badge-text">DAILY PRACTICE</Text>
          </View>
          <Text className="usage-info">{getUsageText()}</Text>
        </View>

        <View className="card-body">
          <Text className="quest-title">Daily Practice Round</Text>
          <Text className="quest-specs">5 Questions · 5–8 min</Text>
          <Text className="quest-tags">Logic · Pattern · Numerical · Verbal</Text>
        </View>

        <Button className="btn-start-quest" onClick={handleStartQuickTest}>
          Begin Today's Practice →
        </Button>
      </View>

      {/* Pro Membership / Practice Zone Banner */}
      <View className={`pro-banner ${proActive ? 'active' : ''}`} onClick={handleOpenPro}>
        <View className="pro-left">
          <Text className="pro-icon">👑</Text>
          <View className="pro-text-box">
            <Text className="pro-title">
              {proActive ? 'BrainActive Pro ✓' : 'BrainActive Pro'}
            </Text>
            <Text className="pro-sub">
              {proActive
                ? `Valid until ${proExpiryText || 'Active'}`
                : 'Unlimited practice · All 6 Topics · 4 Levels'}
            </Text>
          </View>
        </View>
        <Text className="pro-arrow">›</Text>
      </View>

      {/* Referral Card */}
      <View className="referral-banner" onClick={() => setShowReferral(true)}>
        <View className="ref-content">
          <Text className="ref-icon">🎁</Text>
          <View className="ref-text">
            <Text className="ref-title">Invite Friends, Get Pro Free</Text>
            <Text className="ref-sub">Each friend you invite = 7 days free Pro for both of you</Text>
          </View>
        </View>
        <Text className="ref-action">Invite</Text>
      </View>

      {/* Modals */}
      <ReferralModal
        isOpen={showReferral}
        onClose={() => setShowReferral(false)}
        onSuccess={refreshState}
      />
      <QuotaOverlay
        isOpen={showQuota}
        onClose={() => setShowQuota(false)}
        onUnlocked={refreshState}
      />
      <SettingsModal
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
        onLangChanged={refreshState}
      />
    </View>
  )
}
