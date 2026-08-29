import React from 'react'
import { View, Text } from '@tarojs/components'
import './index.scss'

interface Props {
  lang?: 'en' | 'zh'
  onClick: () => void
}

export default function AskHeroButton({ lang = 'en', onClick }: Props) {
  return (
    <View className='ask-hero-button' onClick={onClick}>
      <View className='ask-hero-button-hero-mark' aria-label='Hero AI'>
        <Text className='hero-letter'>H</Text>
      </View>
      <Text className='ask-hero-button-text'>
        {lang === 'zh' ? '问问 Hero AI' : 'Ask Hero AI'}
      </Text>
    </View>
  )
}
