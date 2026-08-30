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
      title: 'Questions to Review',
      empty: 'No tricky questions yet.\nQuestions you need to revisit will appear here!',
      start: 'Start Practice',
      count: 'Tricky Questions',
      retry: 'Review All'
    },
    zh: {
      title: '待复习题库',
      empty: '暂时还没有错题。\n需要再次思考的题目会显示在这里！',
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
        <Button
          className="start-btn empty-start-btn"
          onClick={() => Taro.navigateTo({ url: '/pages/quiz/index?mode=quick_test' })}
        >
          {t.start}
        </Button>
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
              <Text className="card-topic">{item.topic || (lang === 'zh' ? '思维推理' : 'Reasoning')}</Text>
              <Text className="card-level">{item.level || (lang === 'zh' ? '思考' : 'Think')}</Text>
            </View>
            <Text className="card-question-preview">{item.question}</Text>
            <View className="card-bottom">
              <Text className="card-cta">{lang === 'zh' ? '再练一次 →' : 'Practice Again →'}</Text>
            </View>
          </View>
        ))}
      </View>
    </View>
  )
}
