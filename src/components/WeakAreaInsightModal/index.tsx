import React from 'react'
import { View, Text, Button } from '@tarojs/components'
import { TopicPerformance } from '@/utils/quizInsights'
import './index.scss'

interface WeakAreaInsightModalProps {
  isOpen: boolean
  insight: TopicPerformance
  lang: 'en' | 'zh'
  onClose: () => void
}

const copy = {
  en: {
    title: 'Hero Spotted Something For You',
    eyebrow: 'A thinking area to watch',
    correct: 'correct',
    accuracy: 'accuracy',
    context: 'Based on your saved practice history, this is currently one of your weakest thinking areas.',
    close: 'Got it'
  },
  zh: {
    title: '英雄发现了值得关注的地方',
    eyebrow: '值得关注的思维领域',
    correct: '答对',
    accuracy: '正确率',
    context: '根据你保存的练习记录，这是目前较需要加强的思维领域之一。',
    close: '知道了'
  }
}

export default function WeakAreaInsightModal({
  isOpen,
  insight,
  lang,
  onClose
}: WeakAreaInsightModalProps) {
  if (!isOpen) return null

  const t = copy[lang] || copy.en

  return (
    <View className="weak-area-insight-overlay" onClick={onClose}>
      <View className="weak-area-insight-card" onClick={event => event.stopPropagation()}>
        <View className="weak-area-insight-icon" aria-hidden="true">
          <Text>!</Text>
        </View>
        <Text className="weak-area-insight-eyebrow">{t.eyebrow}</Text>
        <Text className="weak-area-insight-title">{t.title}</Text>
        <Text className="weak-area-insight-topic">{insight.topic}</Text>

        <View className="weak-area-insight-metrics">
          <View className="weak-area-insight-metric">
            <Text className="weak-area-insight-metric-value">
              {insight.correct}/{insight.total}
            </Text>
            <Text className="weak-area-insight-metric-label">{t.correct}</Text>
          </View>
          <View className="weak-area-insight-metric weak-area-insight-metric-highlight">
            <Text className="weak-area-insight-metric-value">{insight.accuracy}%</Text>
            <Text className="weak-area-insight-metric-label">{t.accuracy}</Text>
          </View>
        </View>

        <Text className="weak-area-insight-context">{t.context}</Text>
        <Button className="weak-area-insight-close" onClick={onClose}>{t.close}</Button>
      </View>
    </View>
  )
}
