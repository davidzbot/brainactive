import React from 'react'
import { View, Text, Button } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { Share } from '@capacitor/share'
import { getLang } from '@/utils/storage'
import { SHARE_CONFIG } from '@/config/share'
import './index.scss'

interface ReferralModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
}

const i18n = {
  en: {
    title: 'Share BrainActive',
    desc: 'Love BrainActive? Share it with friends and family who enjoy thinking challenges.',
    copyInvite: 'Share App Link',
    copied: 'Link copied — send it to a friend!',
  },
  zh: {
    title: '分享 BrainActive',
    desc: '喜欢 BrainActive？分享给喜欢思维挑战的亲友们吧。',
    copyInvite: '分享应用链接',
    copied: '链接已复制，快发给好友吧！',
  }
}

export default function ReferralModal({ isOpen, onClose }: ReferralModalProps) {
  const lang = (getLang() || 'en') as 'en' | 'zh'
  const t = i18n[lang]

  if (!isOpen) return null

  const inviteMessage = lang === 'zh'
    ? `🧠 BrainActive — 新加坡 P3 高能力思维训练\n每天锻炼逻辑、图形与推理能力！\n\n下载 BrainActive：\n${SHARE_CONFIG.url}`
    : `🧠 BrainActive — Singapore P3 High Ability Thinking Skills\nTrain logic, patterns & reasoning daily!\n\nDownload BrainActive:\n${SHARE_CONFIG.url}`

  const handleShare = async () => {
    try {
      await Share.share({
        title: t.title,
        text: inviteMessage,
        url: SHARE_CONFIG.url
      })
    } catch {
      Taro.setClipboardData({
        data: inviteMessage,
        success: () => Taro.showToast({ title: t.copied, icon: 'success' })
      })
    }
  }

  return (
    <View className="referral-overlay">
      <View className="referral-card">
        <View className="card-header">
          <Text className="title">{t.title}</Text>
          <Text className="close-btn" onClick={onClose}>✕</Text>
        </View>

        <Text className="desc">{t.desc}</Text>

        <Button className="btn-share" onClick={handleShare}>
          {t.copyInvite}
        </Button>
      </View>
    </View>
  )
}
