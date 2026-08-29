import React from 'react'
import { View, Text } from '@tarojs/components'
import './index.scss'

interface Props {
  role: 'user' | 'assistant'
  content: string
  lang?: 'en' | 'zh'
}

export default function AskHeroMessage({ role, content, lang = 'en' }: Props) {
  const isAssistant = role === 'assistant'

  return (
    <View className={`ask-hero-msg ask-hero-msg--${role}`}>
      {isAssistant && (
        <View className='ask-hero-msg-avatar'>
          <Text className='avatar-letter'>H</Text>
        </View>
      )}
      <View className={`ask-hero-msg-bubble ${isAssistant ? '' : 'user'}`}>
        {isAssistant && (
          <Text className='ask-hero-msg-name'>Hero AI</Text>
        )}
        <Text className='ask-hero-msg-content'>{content}</Text>
      </View>
    </View>
  )
}
