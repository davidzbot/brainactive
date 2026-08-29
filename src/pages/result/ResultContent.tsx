import React, { useState } from 'react'
import { View, Text, Button } from '@tarojs/components'
import Taro, { useRouter } from '@tarojs/taro'
import {
  getStreak,
  getWrongQuestions,
  getRemainingFreeRounds,
  canStartPractice,
  isPro
} from '@/utils/storage'
import QuotaOverlay from '@/components/QuotaOverlay'
import './index.scss'

export default function ResultContent() {
  const router = useRouter()
  const score = parseInt(router.params.score || '0', 10)
  const total = parseInt(router.params.total || '5', 10)
  const timeSec = parseInt(router.params.time || '0', 10)

  const [showQuota, setShowQuota] = useState(false)
  const streak = getStreak()
  const wrongList = getWrongQuestions()
  const percentage = Math.round((score / (total || 1)) * 100)

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60)
    const s = secs % 60
    return `${m}m ${s}s`
  }

  const getVictoryTitle = () => {
    if (percentage === 100) return 'Outstanding Mastery! 🏆'
    if (percentage >= 80) return 'Great Thinking! 🌟'
    if (percentage >= 60) return 'Good Effort! 💡'
    return 'Keep Going — every attempt sharpens your reasoning! 🌱'
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
      Taro.showToast({ title: 'No mistakes to review! 🎉', icon: 'success' })
      return
    }
    const ids = wrongList.slice(0, 5).map(q => q.id)
    Taro.navigateTo({
      url: `/pages/quiz/index?mode=retry&ids=${ids.join(',')}`
    })
  }

  const handleShare = () => {
    const msg = `I scored ${score}/${total} (${percentage}%) in BrainActive P3 Thinking Skills! 🧠 Practise reasoning with me.`
    Taro.setClipboardData({
      data: msg,
      success: () => {
        Taro.showToast({ title: 'Result copied! 📋', icon: 'success' })
      }
    })
  }

  const handleHome = () => {
    Taro.reLaunch({
      url: '/pages/home/index'
    })
  }

  return (
    <View className="result-container">
      {/* Header Badge */}
      <View className="result-header">
        <View className="trophy-badge">
          <Text className="trophy-icon">{percentage >= 80 ? '🏆' : '🎯'}</Text>
        </View>
        <Text className="victory-title">{getVictoryTitle()}</Text>
        <Text className="victory-sub">Singapore P3 Thinking Skills</Text>
      </View>

      {/* Score Summary Card */}
      <View className="score-summary-card">
        <View className="score-main">
          <Text className="score-number">{score}</Text>
          <Text className="score-denom">/{total}</Text>
        </View>
        <Text className="score-pct">{percentage}% Correct</Text>

        <View className="stats-row">
          <View className="stat-item">
            <Text className="stat-label">TIME</Text>
            <Text className="stat-val">{formatTime(timeSec)}</Text>
          </View>
          <View className="stat-divider" />
          <View className="stat-item">
            <Text className="stat-label">STREAK</Text>
            <Text className="stat-val">🔥 {streak} Days</Text>
          </View>
          <View className="stat-divider" />
          <View className="stat-item">
            <Text className="stat-label">TO REVIEW</Text>
            <Text className="stat-val">{total - score}</Text>
          </View>
        </View>
      </View>

      {/* Review card (if applicable) */}
      {wrongList.length > 0 && (
        <View className="review-mistakes-card" onClick={handleReviewMistakes}>
          <View className="review-left">
            <Text className="review-icon">📝</Text>
            <View className="review-text">
              <Text className="review-title">Review & Learn</Text>
              <Text className="review-sub">Revisit the questions you found tricky</Text>
            </View>
          </View>
          <Text className="review-arrow">→</Text>
        </View>
      )}

      {/* Primary Actions */}
      <View className="actions-section">
        <Button className="btn-next-round" onClick={handleRestart}>
          Practice Again
        </Button>
        <Button className="btn-share" onClick={handleShare}>
          Copy Result to Share 📋
        </Button>
        <Button className="btn-home" onClick={handleHome}>
          ← Home
        </Button>
      </View>

      <QuotaOverlay
        isOpen={showQuota}
        onClose={() => setShowQuota(false)}
        onUnlocked={() => {
          Taro.redirectTo({ url: '/pages/quiz/index?mode=quick_test' })
        }}
      />
    </View>
  )
}
