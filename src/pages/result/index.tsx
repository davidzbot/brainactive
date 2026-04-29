import React, { useState } from 'react'
import { View, Text, Button } from '@tarojs/components'
import Taro, { useLoad, navigateTo, reLaunch } from '@tarojs/taro'
import { getStorage, setStorage } from '@/utils/storage'
import { formatDate, setSafeTitle } from '@/utils/common'
import { t } from '@/utils/i18n'
import './index.scss'

export default function ResultPage() {
  const [score, setScore] = useState(0)
  const [time, setTime] = useState(0)
  const [evaluation, setEvaluation] = useState('')
  const [newStreak, setNewStreak] = useState(0)

  useLoad((options) => {
    const s = parseInt(options.score || '0')
    const tm = parseInt(options.time || '0')
    setScore(s)
    setTime(tm)
    
    setSafeTitle(t('result.title'))

    // Evaluation logic
    if (s < 30) setEvaluation(t('result.eval.low'))
    else if (s < 70) setEvaluation(t('result.eval.mid'))
    else setEvaluation(t('result.eval.high'))

    // Handle Streak
    const lastDate = getStorage('lastTrainingDate')
    const today = formatDate(new Date())
    
    if (lastDate !== today) {
      const currentStreak = getStorage('streak') || 0
      const updatedStreak = currentStreak + 1
      setStorage('streak', updatedStreak)
      setStorage('lastTrainingDate', today)
      setNewStreak(updatedStreak)
    } else {
      setNewStreak(getStorage('streak') || 0)
    }
  })

  const goHome = () => {
    reLaunch({ url: '/pages/home/index' })
  }

  const handleShare = async () => {
    try {
      const { Share } = require('@capacitor/share')
      await Share.share({
        title: t('app.title'),
        text: `${t('result.score')}: ${score}. ${evaluation}`,
        url: 'https://brainactive.app',
      })
    } catch (e) {}
  }

  return (
    <View className="result-container">
      <View className="header-section">
        <Text className="result-title">{t('result.title')}</Text>
        <View className="streak-badge">
          <Text className="streak-text">🔥 {newStreak} {t('app.status.low').split('训练')[1] || 'Days'}</Text>
        </View>
      </View>

      <View className="score-panel">
        <View className="score-box">
          <Text className="score-label">{t('result.score')}</Text>
          <Text className="score-value">{score}</Text>
        </View>
        <View className="time-box">
          <Text className="time-label">{t('result.time')}</Text>
          <Text className="time-value">{time}s</Text>
        </View>
      </View>

      <View className="eval-section">
        <Text className="eval-text">{evaluation}</Text>
      </View>

      <View className="action-section">
        <Button className="primary-btn" onClick={goHome}>{t('button.home')}</Button>
        <Button className="secondary-btn" onClick={handleShare}>{t('button.share')}</Button>
      </View>
    </View>
  )
}
