import React, { useState, useEffect } from 'react'
import { View, Text, Button, ScrollView } from '@tarojs/components'
import Taro, { useRouter } from '@tarojs/taro'
import {
  getStreak,
  getWrongQuestions,
  canStartPractice,
  isPro,
  getLang,
  getQuizHistory
} from '@/utils/storage'
import { Share } from '@capacitor/share'
import QuotaOverlay from '@/components/QuotaOverlay'
import WeakAreaInsightModal from '@/components/WeakAreaInsightModal'
import { findMeaningfulWeakArea, TopicPerformance } from '@/utils/quizInsights'
import './index.scss'

const i18n = {
  en: {
    victory: 'Great Job, Hero!',
    score_prefix: 'Session Score',
    legend: 'Quest Legend 🏆',
    avenger: 'Elite Thinker 🌟',
    knight: 'Master Solver 🛡️',
    trainee: 'Rising Mind 🌱',
    restart: 'Start New Practice',
    retry_wrong: 'Review Mistakes',
    share_victory: 'Share Your Progress',
    go_home: 'Back to Home',
    keep_practicing: 'Every puzzle sharpens your thinking skills.',
    perfect_score: '🎉 Perfect Score! Outstanding work!',
    share_btn: 'Share Result',
    time: 'Time',
    pro_unlocked_msg: 'Pro Member Active',
    pro_unlimited: 'You have unlimited thinking skills practice',
    share_unlock: 'Unlock Unlimited Practice',
    power_up_desc: 'Unlimited rounds, step-by-step AI coach, and analytics.',
    pro_feature_cta: 'Unlock Pro Access',
    copied: 'Result copied! Share with your friends!',
    no_mistakes: 'No mistakes to review! Outstanding! 🎉'
  },
  zh: {
    victory: '太棒了，思维小英雄！',
    score_prefix: '本次成绩',
    legend: '思维传奇 🏆',
    avenger: '解题大师 🌟',
    knight: '逻辑高手 🛡️',
    trainee: '思维新星 🌱',
    restart: '开始新挑战',
    retry_wrong: '复习错题',
    share_victory: '分享你的进步',
    go_home: '返回首页',
    keep_practicing: '每一次练习都会让你的思维更敏捷。',
    perfect_score: '🎉 满分！表现非常出色！',
    share_btn: '分享成绩',
    time: '用时',
    pro_unlocked_msg: 'Pro 会员特权已开启',
    pro_unlimited: '您已拥有无限练习权限',
    share_unlock: '开启无限思维训练',
    power_up_desc: '无限挑战轮次，AI 导师专属解析与战力统计。',
    pro_feature_cta: '开启 Pro 会员',
    copied: '成绩已复制，快去分享吧！',
    no_mistakes: '全部答对，没有错题！🎉'
  }
}

export default function ResultContent() {
  const router = useRouter()
  const lang = (getLang() || 'en') as 'en' | 'zh'
  const t = i18n[lang] || i18n.en

  const score = parseInt(router.params.score || '0', 10)
  const total = parseInt(router.params.total || '5', 10)
  const timeSec = parseInt(router.params.time || '0', 10)
  const flawless = router.params.flawless === '1'

  const [isLoading, setIsLoading] = useState(true)
  const [animatedScore, setAnimatedScore] = useState(0)
  const [showConfetti, setShowConfetti] = useState(false)
  const [showQuota, setShowQuota] = useState(false)
  const [proActive, setProActive] = useState(false)
  const [weakAreaInsight, setWeakAreaInsight] = useState<TopicPerformance | null>(null)
  const [showWeakAreaInsight, setShowWeakAreaInsight] = useState(false)

  const streak = getStreak()
  const wrongList = getWrongQuestions()
  const wrongCount = Math.max(0, total - score)
  const percentage = total > 0 ? Math.round((score / total) * 100) : 0

  useEffect(() => {
    setProActive(isPro())
    const timer = setTimeout(() => {
      setIsLoading(false)
    }, 300)
    return () => clearTimeout(timer)
  }, [])

  useEffect(() => {
    if (isLoading) return
    if (percentage >= 80) setShowConfetti(true)

    try {
      const insight = findMeaningfulWeakArea(getQuizHistory())
      setWeakAreaInsight(insight)
      setShowWeakAreaInsight(Boolean(insight))
    } catch (error) {
      console.warn('[BrainActive Result] Weak-area insight unavailable', error)
    }

    const duration = 700
    const steps = 25
    const increment = score / steps
    let current = 0
    const interval = setInterval(() => {
      current += increment
      if (current >= score) {
        setAnimatedScore(score)
        clearInterval(interval)
      } else {
        setAnimatedScore(Math.round(current))
      }
    }, duration / steps)

    return () => clearInterval(interval)
  }, [isLoading, score, percentage])

  const getRatingText = () => {
    if (percentage >= 100) return t.legend
    if (percentage >= 80) return t.avenger
    if (percentage >= 50) return t.knight
    return t.trainee
  }

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60)
    const s = secs % 60
    return `${m}m ${s}s`
  }

  const handleRestart = () => {
    if (!canStartPractice()) {
      setShowQuota(true)
      return
    }
    Taro.redirectTo({
      url: '/pages/quiz/index?mode=quick_test'
    })
  }

  const handleReviewMistakes = () => {
    if (wrongList.length === 0) {
      Taro.showToast({ title: t.no_mistakes, icon: 'none' })
      return
    }
    Taro.navigateTo({
      url: '/pages/quiz/index?mode=retry'
    })
  }

  const handleShare = async () => {
    const text = `I scored ${score}/${total} (${percentage}%) in BrainActive Singapore P3 Thinking Skills! 🧠 Practise reasoning with me.`
    try {
      await Share.share({
        title: 'My BrainActive Score',
        text,
        dialogTitle: t.share_victory
      })
    } catch {
      Taro.setClipboardData({
        data: text,
        success: () => {
          Taro.showToast({ title: t.copied, icon: 'success' })
        }
      })
    }
  }

  const handleGoPro = () => {
    const url = '/pages/pro/index'
    Taro.navigateTo({
      url
    }).catch(() => Taro.reLaunch({ url }))
  }

  const handleHome = () => {
    Taro.reLaunch({
      url: '/pages/home/index'
    })
  }

  if (isLoading) {
    return (
      <View className="result-container">
        <View className="loading-container">
          <View className="loading-spinner" />
          <Text className="loading-text">{lang === 'en' ? 'Calculating your results...' : '正在计算成绩...'}</Text>
        </View>
      </View>
    )
  }

  return (
    <View className="result-container">
      {/* Confetti celebration for score >= 80% */}
      {showConfetti && (
        <View className="confetti-container" aria-hidden="true">
          {Array.from({ length: 28 }).map((_, i) => (
            <View
              key={i}
              className="confetti-piece"
              style={{
                left: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 1.5}s`,
                animationDuration: `${1.8 + Math.random() * 2}s`,
                backgroundColor: ['#0284c7', '#38bdf8', '#2563eb', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'][i % 7],
                width: `${7 + Math.random() * 8}px`,
                height: `${7 + Math.random() * 8}px`,
                borderRadius: Math.random() > 0.5 ? '50%' : '3px'
              }}
            />
          ))}
        </View>
      )}

      <ScrollView scrollY className="result-scroll">
        {/* Victory Header */}
        <View className="victory-header">
          <Text className="victory-title">{t.victory}</Text>
          <View className="rating-text-banner">
            <Text className="rating-text">{getRatingText()}</Text>
          </View>
        </View>

        {/* Score Circle & Section */}
        <View className="score-section">
          <Text className="score-label">{t.score_prefix}</Text>
          <View className="score-circle">
            <Text className="score-num">{animatedScore}</Text>
            <View className="score-divider" />
            <Text className="score-total">/ {total}</Text>
          </View>

          {timeSec > 0 && (
            <Text className="time-display">
              {t.time}: {formatTime(timeSec)}
            </Text>
          )}
        </View>

        {/* Perfect Score Celebration (only when truly flawless: no skips & all first-try correct) */}
        {score === total && total > 0 && flawless && (
          <View className="perfect-score-celebration">
            <Text className="perfect-score-text">{t.perfect_score}</Text>
          </View>
        )}

        {/* Hero Encouragement */}
        <View className="hero-encouragement">
          <Text className="encouragement-emoji">
            {score === total ? '🏆' : score >= total * 0.8 ? '🌟' : score >= total * 0.5 ? '💪' : '🌱'}
          </Text>
          <Text className="encouragement-text">{t.keep_practicing}</Text>
        </View>

        {/* Action Buttons */}
        <View className="result-actions-block">
          {wrongCount > 0 && (
            <View className="primary-actions">
              <View className="action-btn-large retry" onClick={handleReviewMistakes}>
                <View className="btn-content">
                  <Text className="btn-text">{t.retry_wrong}</Text>
                  <View className="count-badge-inline">{wrongCount}</View>
                </View>
              </View>
            </View>
          )}

          <View className="secondary-actions">
            <View className="action-btn-medium restart" onClick={handleRestart}>
              <Text className="btn-text">{t.restart}</Text>
            </View>
          </View>

          {/* Share Action */}
          <View className="result-share-container">
            <View className="share-action-btn" onClick={handleShare}>
              <Text className="btn-text">🎉 {t.share_btn}</Text>
            </View>
          </View>
        </View>

        {/* Pro CTA Card */}
        <View className="pro-cta-bottom" onClick={() => handleGoPro()}>
          <View className={`pro-card ${proActive ? 'active' : ''}`}>
            <Text className="pro-title">
              🚀 {proActive ? t.pro_unlocked_msg : t.share_unlock}
            </Text>
            <Text className="pro-desc">
              {proActive ? t.pro_unlimited : t.power_up_desc}
            </Text>
            {!proActive && (
              <Button className="pro-btn">{t.pro_feature_cta}</Button>
            )}
          </View>
        </View>

        {/* Bottom Home Link */}
        <View className="global-home-bottom-link" onClick={handleHome}>
          <Text className="bottom-home-icon">🏠</Text>
        </View>

        <View className="footer-spacer" />
      </ScrollView>

      <QuotaOverlay
        isOpen={showQuota}
        onClose={() => setShowQuota(false)}
        onUnlocked={() => {
          Taro.redirectTo({ url: '/pages/quiz/index?mode=quick_test' })
        }}
      />

      {weakAreaInsight && (
        <WeakAreaInsightModal
          isOpen={showWeakAreaInsight}
          insight={weakAreaInsight}
          lang={lang}
          onClose={() => setShowWeakAreaInsight(false)}
        />
      )}
    </View>
  )
}
