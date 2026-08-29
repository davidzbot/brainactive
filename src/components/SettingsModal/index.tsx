import React from 'react'
import { View, Text, Button } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { getLang, setLang } from '@/utils/storage'
import './index.scss'

interface SettingsModalProps {
  isOpen: boolean
  onClose: () => void
  onLangChanged: () => void
}

export default function SettingsModal({ isOpen, onClose, onLangChanged }: SettingsModalProps) {
  const currentLang = getLang()

  if (!isOpen) return null

  const handleToggleLang = (lang: 'en' | 'zh') => {
    setLang(lang)
    onLangChanged()
    Taro.showToast({ title: lang === 'zh' ? '已切换至中文' : 'Language set to English', icon: 'none' })
  }

  const handleSupport = () => {
    Taro.setClipboardData({
      data: 'pslehero@gmail.com',
      success: () => {
        Taro.showToast({ title: 'Support email copied! 📧', icon: 'success' })
      }
    })
  }

  return (
    <View className="settings-overlay">
      <View className="settings-card">
        <View className="card-header">
          <Text className="title">⚙️ Settings</Text>
          <Text className="close-btn" onClick={onClose}>✕</Text>
        </View>

        <View className="setting-section">
          <Text className="section-label">Language / 语言</Text>
          <View className="lang-options">
            <Button
              className={`btn-lang ${currentLang === 'en' ? 'active' : ''}`}
              onClick={() => handleToggleLang('en')}
            >
              English
            </Button>
            <Button
              className={`btn-lang ${currentLang === 'zh' ? 'active' : ''}`}
              onClick={() => handleToggleLang('zh')}
            >
              中文
            </Button>
          </View>
        </View>

        <View className="setting-section">
          <Text className="section-label">Product Info</Text>
          <View className="info-card">
            <Text className="info-title">BrainActive P3 High Ability</Text>
            <Text className="info-sub">Build Thinking Skills for Primary 3</Text>
            <Text className="info-ver">v1.7.0 · Reasoning Edition</Text>
          </View>
        </View>

        <Button className="btn-support" onClick={handleSupport}>
          💬 Contact Support (pslehero@gmail.com)
        </Button>
      </View>
    </View>
  )
}
