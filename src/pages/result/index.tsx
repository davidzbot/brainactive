import Taro, { useState, useEffect } from 'react'
import { View, Text, Button } from '@tarojs/components'
import { useLoad, reLaunch, navigateTo, setNavigationBarTitle } from '@tarojs/taro'
import { getStorage, setStorage } from '@/utils/storage'
import { isAdUnlocked, unlockAllModes, formatDate, parseDateSafe, incrementDailyUsage, canPlayMode } from '@/utils/common'
import { dataUtils } from '@/utils/data'
import { t } from '@/utils/i18n'
import './index.scss'

export default function ResultPage() {
  const [streak, setStreak] = useState(0)
  const [streakMessage, setStreakMessage] = useState('')
  const [progressWidth, setProgressWidth] = useState('0%')
  const [totalTime, setTotalTime] = useState('')
  const [score, setScore] = useState(0)
  const [performanceLevel, setPerformanceLevel] = useState('')
  const [currentTip, setCurrentTip] = useState('')
  const [funSummary, setFunSummary] = useState('')
  const [badge, setBadge] = useState<string | null>(null)
  const [difficulty, setDifficulty] = useState('easy')
  const [isUnlocked, setIsUnlocked] = useState(false)

  useLoad((options) => {
    const seconds = parseInt(options.time || '0')
    const scoreVal = parseInt(options.score || '0')
    const diff = getStorage('lastDifficulty') || 'easy'
    setDifficulty(diff)
    setIsUnlocked(isAdUnlocked())

    // Increment daily usage for this mode
    incrementDailyUsage(diff)
    
    const timeStr = seconds >= 60 
      ? Math.floor(seconds / 60) + t('result.min') + (seconds % 60) + t('result.sec')
      : seconds + t('result.sec')

    let historyBest = 0
    try {
      historyBest = getStorage('bestScore') || 0
    } catch (e) {
      console.error('Failed to read bestScore', e)
    }

    let newRecord = false
    if (scoreVal > historyBest && scoreVal > 0) {
      try {
        setStorage('bestScore', scoreVal)
      } catch (e) {
        console.error('Failed to save bestScore', e)
      }
      newRecord = true
    }

    const randomTip = dataUtils.tips[Math.floor(Math.random() * dataUtils.tips.length)]
    
    const evalKey = scoreVal >= 50 ? 'result.evaluation.perfect' : (scoreVal >= 30 ? 'result.evaluation.good' : 'result.evaluation.keep_going')

    setTotalTime(timeStr)
    setScore(scoreVal)
    setPerformanceLevel(newRecord ? t('result.best') : t(evalKey as any))
    setCurrentTip(randomTip)
    setFunSummary(t('result.summary', { score: scoreVal }))

    updateStreak()
    setNavigationBarTitle({ title: t('result.title') })
  })

  const updateStreak = () => {
    const today = formatDate(new Date())
    let last = ''
    let streakVal = 0
    try {
      last = getStorage('lastTrainingDate') || ''
      streakVal = getStorage('streak') || 0
    } catch (e) {
      console.error('Failed to read streak data', e)
    }

    if (last !== today) {
      if (last) {
        const lastDate = parseDateSafe(last)
        const todayDate = parseDateSafe(today)
        if (lastDate && todayDate) {
          const diff = (todayDate.getTime() - lastDate.getTime()) / (1000 * 60 * 60 * 24)
          streakVal = (diff <= 1) ? streakVal + 1 : 1
        } else {
          streakVal = 1
        }
      } else {
        streakVal = 1
      }
      try {
        setStorage('streak', streakVal)
        setStorage('lastTrainingDate', today)
      } catch (e) {
        console.error('Failed to save streak data', e)
      }
    }

    let badgeText: string | null = null
    if (streakVal >= 30) badgeText = t('badge.commander')
    else if (streakVal >= 7) badgeText = t('badge.core')
    else if (streakVal >= 3) badgeText = t('badge.pro')

    setStreak(streakVal)
    setBadge(badgeText)
    setStreakMessage(
      streakVal > 1 
        ? t('result.streak.msg.low', { s: streakVal })
        : t('result.streak.msg.0')
    )
    setProgressWidth(Math.min((streakVal / 7) * 100, 100) + '%')
  }

  const goHome = () => {
    Taro.reLaunch({ url: '/pages/home/index' })
  }

  const handleContinue = () => {
    if (canPlayMode(difficulty)) {
      Taro.navigateTo({ url: `/pages/task/index?difficulty=${difficulty}` })
    } else {
      handleWatchAd()
    }
  }

  const handleWatchAd = async () => {
    Taro.showLoading({ title: t('task.loading') })
    setTimeout(() => {
      Taro.hideLoading()
      unlockAllModes()
      setIsUnlocked(true)
      Taro.showToast({ title: t('app.unlimited'), icon: 'success' })
    }, 2000)
  }

  const handleShare = async () => {
    try {
      const { Share } = require('@capacitor/share')
      await Share.share({
        title: t('app.title'),
        text: `I scored ${score} on BrainActive! 🧠\n\nIt’s simple but surprisingly effective.\n\nTry it 👇`,
        url: 'https://brainactive.app',
        dialogTitle: t('button.share'),
      })
    } catch (e) {
      console.error('Capacitor Share failed', e)
    }
  }

  return (
    <View className="result-container">
      <View className="result-card">
        <View className="score-section">
          <Text className="score-label">{t('result.score')}</Text>
          <Text className="score-value">{score}</Text>
          <Text className="time-info">{t('result.time')} {totalTime}</Text>
        </View>

        <View className="performance-section">
          <Text className="performance-level">{performanceLevel}</Text>
          <Text className="fun-summary">{funSummary}</Text>
        </View>

        <View className="streak-section">
          <View className="streak-header">
            <Text className="streak-label">
              {badge ? `${badge} · ` : ''}{t('result.streak.label')}
            </Text>
            <Text className="streak-count">{streak} {getLang() === 'zh' ? '天' : 'Days'}</Text>
          </View>
          <View className="progress-bar-bg">
            <View className="progress-bar-fill" style={{ width: progressWidth }}></View>
          </View>
          <Text className="streak-message">{streakMessage}</Text>
        </View>

        <View className="tip-section">
          <Text className="tip-label">{t('result.tip.label')}</Text>
          <Text className="tip-text">{currentTip}</Text>
        </View>
      </View>

      <View className="action-buttons">
        <Button 
          className="btn-primary" 
          onClick={handleContinue}
        >
          {canPlayMode(difficulty) ? t('task.continue') : t('task.watch_ad')}
        </Button>

        <View className="secondary-actions">
          <Button className="btn-home-small" onClick={goHome}>
            🏠 {t('result.back_home')}
          </Button>
          <Button className="btn-share-small" onClick={handleShare}>
            🔗 {t('button.share')}
          </Button>
        </View>
      </View>
    </View>
  )
}