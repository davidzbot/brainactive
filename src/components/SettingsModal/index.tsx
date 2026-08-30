import React, { useState } from 'react'
import { View, Text, Button } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { getLang, setLang } from '@/utils/storage'
import './index.scss'

interface SettingsModalProps {
  isOpen: boolean
  onClose: () => void
  onLangChanged: () => void
}

const SUPPORT_EMAIL = 'pslehero@gmail.com'
const SUPPORT_WEBSITE = 'https://pslehero.org/'

const i18n = {
  en: {
    title: '⚙️ Settings',
    language: 'Language / 语言',
    productInfo: 'Product Info',
    productSub: 'Build Thinking Skills for Primary 3',
    version: 'v1.7.0 · Reasoning Edition',
    support: '💬 Contact Support',
    website: '🌐 Visit Website',
    emailCopied: 'Support email copied!',
    languageSet: 'Language set to English',
    websiteOpen: 'Opening website...'
  },
  zh: {
    title: '⚙️ 设置',
    language: '语言 / Language',
    productInfo: '产品信息',
    productSub: '培养小学三年级思维能力',
    version: 'v1.7.0 · 思维训练版',
    support: '💬 联系客服',
    website: '🌐 访问官网',
    emailCopied: '客服邮箱已复制！',
    languageSet: '已切换至中文',
    websiteOpen: '正在打开官网…'
  }
}

export default function SettingsModal({ isOpen, onClose, onLangChanged }: SettingsModalProps) {
  const [currentLang, setCurrentLang] = useState<'en' | 'zh'>(() => (getLang() || 'en') as 'en' | 'zh')
  const t = i18n[currentLang]

  if (!isOpen) return null

  const handleToggleLang = (lang: 'en' | 'zh') => {
    setCurrentLang(lang)
    setLang(lang)
    onLangChanged()
    Taro.showToast({ title: i18n[lang].languageSet, icon: 'none' })
  }

  const handleSupport = () => {
    Taro.setClipboardData({
      data: SUPPORT_EMAIL,
      success: () => Taro.showToast({ title: t.emailCopied, icon: 'success' })
    })
  }

  const handleWebsite = () => {
    if (typeof window !== 'undefined') {
      window.open(SUPPORT_WEBSITE, '_blank')
      Taro.showToast({ title: t.websiteOpen, icon: 'none' })
    }
  }

  return (
    <View className="settings-overlay">
      <View className="settings-card">
        <View className="card-header">
          <Text className="title">{t.title}</Text>
          <Text className="close-btn" onClick={onClose}>✕</Text>
        </View>

        <View className="setting-section">
          <Text className="section-label">{t.language}</Text>
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
          <Text className="section-label">{t.productInfo}</Text>
          <View className="info-card">
            <Text className="info-title">BrainActive P3 High Ability</Text>
            <Text className="info-sub">{t.productSub}</Text>
            <Text className="info-ver">{t.version}</Text>
          </View>
        </View>

        <View className="support-actions">
          <Button className="btn-support" onClick={handleSupport}>
            {t.support}
          </Button>
          <Text className="support-email">{SUPPORT_EMAIL}</Text>
          <Button className="btn-website" onClick={handleWebsite}>
            {t.website}
          </Button>
          <Text className="website-url" onClick={handleWebsite}>{SUPPORT_WEBSITE}</Text>
        </View>
      </View>
    </View>
  )
}
