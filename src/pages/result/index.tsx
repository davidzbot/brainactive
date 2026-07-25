import React, { useState } from 'react'
import { View, Text, Button } from '@tarojs/components'
import Taro, { useLoad, navigateTo, reLaunch } from '@tarojs/taro'
import { getStorage, setStorage, getLang } from '@/utils/storage'
import { formatDate, setSafeTitle } from '@/utils/common'
import { t } from '@/utils/i18n'
import { SHARE_CONFIG } from '@/config/share'
import './index.scss'

export default function ResultPage() {
  const [score, setScore] = useState(0)
  const [time, setTime] = useState(0)
  const [evaluation, setEvaluation] = useState('')
  const [newStreak, setNewStreak] = useState(0)
  const [brainAge, setBrainAge] = useState(25)

  useLoad((options) => {
    const s = parseInt(options.score || '0')
    const tm = parseInt(options.time || '0')
    setScore(s)
    setTime(tm)
    
    setSafeTitle(t('result.title'))

    // Brain Age Calculation (Gamified & Encouraging)
    // Higher score and lower time yield younger brain age
    let estimatedAge = 35
    if (s >= 80) estimatedAge = Math.max(18, 22 - Math.floor(s / 20))
    else if (s >= 50) estimatedAge = 25 + Math.floor((100 - s) / 5)
    else estimatedAge = 38 + Math.floor((50 - s) / 3)

    setBrainAge(estimatedAge)

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
      const lang = getLang() || 'en'
      const cfg = lang === 'zh' ? SHARE_CONFIG.zh : SHARE_CONFIG.en
      const shareMsg = lang === 'zh'
        ? `🧠 我刚在【大脑每日练】完成了大脑健康测试！\n得分: ${score} 分 | 评估大脑年龄: ${brainAge} 岁！\n${evaluation}\n快来一起打卡练脑，预防老年痴呆！`
        : `🧠 Just completed my daily brain test on BrainActive!\nScore: ${score} | Brain Age: ${brainAge}!\n${evaluation}\nTrain daily to keep your mind sharp!`
      
      await Share.share({
        title: cfg.title,
        text: shareMsg,
        url: SHARE_CONFIG.url,
      })
    } catch { }
  }

  return (
    <View className="result-container">
      <View className="header-section">
        <Text className="result-title">{t('result.title')}</Text>
        <View className="streak-badge">
          <Text className="streak-text">🔥 {newStreak} {t('common.days')} {t('common.streak')}</Text>
        </View>
      </View>

      <View className="score-panel">
        <View className="score-box">
          <Text className="score-label">{t('result.score')}</Text>
          <Text className="score-value">{score}</Text>
        </View>
        <View className="time-box">
          <Text className="time-label">{getLang() === 'zh' ? '预估大脑年龄' : 'Brain Age'}</Text>
          <Text className="time-value" style={{ color: '#10b981' }}>{brainAge} {getLang() === 'zh' ? '岁' : 'y/o'}</Text>
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
