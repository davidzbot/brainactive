import React from 'react'
import { View, Text } from '@tarojs/components'
import './index.scss'

interface Props {
  lang?: 'en' | 'zh'
  onClick: () => void
  // Optional sub-caption rendered inside the button box (e.g. the
  // "check my answer" nudge). Keeps the quiz bottom row clean.
  checkHint?: string
}

export default function AskHeroButton({ lang = 'en', onClick, checkHint }: Props) {
  return (
    <View className='ask-hero-button' onClick={onClick}>
      <View className='ask-hero-button-main'>
        <View className='ask-hero-button-hero-mark' aria-label='Hero AI'>
          <Text className='hero-letter'>H</Text>
        </View>
        <Text className='ask-hero-button-text'>
          {lang === 'zh' ? '问问 Hero AI' : 'Ask Hero AI'}
        </Text>
      </View>
      {checkHint ? <Text className='ask-hero-button-hint'>{checkHint}</Text> : null}
    </View>
  )
}
