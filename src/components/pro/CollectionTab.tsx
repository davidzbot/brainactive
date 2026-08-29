import React, { useState, useEffect } from 'react'
import { View, Text, Button } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { getWrongQuestions } from '@/utils/storage'

interface CollectionTabProps {
  lang: 'en' | 'zh'
}

export default function CollectionTab({ lang }: CollectionTabProps) {
  const [items, setItems] = useState<any[]>([])

  useEffect(() => {
    const list = getWrongQuestions()
    setItems(list || [])
  }, [])

  const openQuestion = (q: any) => {
    Taro.navigateTo({
      url: `/pages/quiz/index?mode=retry&ids=${q.id}`
    })
  }

  const translations = {
    en: {
      title: 'Saved Reasoning Puzzles',
      empty: 'Your collection is empty.\nQuestions you want to review will appear here!',
      start: 'Start Practice',
      count: 'Tricky Questions',
      retry: 'Review All'
    },
    zh: {
      title: '思维收藏夹',
      empty: '您的收藏夹是空的。\n练习中需要复习的难题会显示在这里！',
      start: '去探索题目',
      count: '个待复习题目',
      retry: '复习全部'
    }
  }

  const t = translations[lang] || translations.en

  if (items.length === 0) {
    return (
      <View className="empty-stats-hero">
        <Text className="empty-emoji">📑</Text>
        <Text className="empty-title">{t.title}</Text>
        <Text className="empty-desc">{t.empty}</Text>
      </View>
    )
  }

  return (
    <View className="collection-wrapper">
      <View className="collection-header">
        <Text className="collection-title">{t.title}</Text>
        <Text className="collection-count">{items.length} {t.count}</Text>
      </View>

      <View className="collection-list">
        {items.map((item, idx) => (
          <View key={item.id || idx} className="collection-card" onClick={() => openQuestion(item)}>
            <View className="card-top">
              <Text className="card-topic">{item.topic || 'Reasoning'}</Text>
              <Text className="card-level">{item.level || 'Think'}</Text>
            </View>
            <Text className="card-question-preview">{item.question}</Text>
            <View className="card-bottom">
              <Text className="card-cta">Practice Again →</Text>
            </View>
          </View>
        ))}
      </View>
    </View>
  )
}
