import React, { useState } from 'react'
import { View, Text, Input, Button } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { Share } from '@capacitor/share'
import { getReferralCode, setProExpiry, getUserId, getLang } from '@/utils/storage'
import { applyBrainActiveReferral } from '@/utils/request'
import { SHARE_CONFIG } from '@/config/share'
import './index.scss'

interface ReferralModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
}

const i18n = {
  en: {
    title: '🎁 Share with Friends',
    desc: 'Send BrainActive to a friend — you can both unlock 7 days of Pro free!',
    codeLabel: 'Your Referral Code',
    copyCode: 'Copy Code',
    copyInvite: '📤 Share Invite',
    copied: 'Invite copied — send it to a friend!',
    codeCopied: 'Code copied!',
    divider: 'OR ENTER A FRIEND CODE',
    placeholder: "Enter your friend's code",
    redeem: 'Redeem',
    enterCode: 'Please enter a code',
    activated: '7 Days Pro Activated! 👑',
    notice: 'Referral Notice',
    invalid: 'Invalid code or already redeemed.'
  },
  zh: {
    title: '🎁 分享给好友',
    desc: '把 BrainActive 分享给好友——你们都可以免费获得 7 天 Pro！',
    codeLabel: '你的推荐码',
    copyCode: '复制推荐码',
    copyInvite: '📤 分享邀请',
    copied: '邀请内容已复制，快发给好友吧！',
    codeCopied: '推荐码已复制！',
    divider: '或输入好友推荐码',
    placeholder: '输入好友的推荐码',
    redeem: '兑换',
    enterCode: '请输入推荐码',
    activated: '7 天 Pro 已激活！👑',
    notice: '推荐提示',
    invalid: '推荐码无效或已经兑换过。'
  }
}

export default function ReferralModal({ isOpen, onClose, onSuccess }: ReferralModalProps) {
  const [inputCode, setInputCode] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const myCode = getReferralCode()
  const lang = (getLang() || 'en') as 'en' | 'zh'
  const t = i18n[lang]

  if (!isOpen) return null

  const inviteMessage = lang === 'zh'
    ? `🎁 分享 BrainActive，和好友一起练习新加坡 P3 高能力思维题！\n\n使用我的推荐码即可免费获得 7 天 Pro：\n${myCode}\n\n下载 BrainActive：\n${SHARE_CONFIG.url}`
    : `🎁 Share BrainActive with me and practise Singapore P3 thinking skills!\n\nUse my referral code to get 7 days of Pro free:\n${myCode}\n\nDownload BrainActive:\n${SHARE_CONFIG.url}`

  const handleCopy = () => {
    Taro.setClipboardData({
      data: myCode,
      success: () => Taro.showToast({ title: t.codeCopied, icon: 'success' })
    })
  }

  const handleShare = async () => {
    try {
      await Share.share({
        title: t.title,
        text: inviteMessage,
        url: SHARE_CONFIG.url
      })
    } catch (error) {
      Taro.setClipboardData({
        data: inviteMessage,
        success: () => Taro.showToast({ title: t.copied, icon: 'success' })
      })
    }
  }

  const handleRedeem = async () => {
    if (!inputCode.trim()) {
      Taro.showToast({ title: t.enterCode, icon: 'none' })
      return
    }

    try {
      setSubmitting(true)
      const res = await applyBrainActiveReferral(getUserId(), inputCode.trim())
      setSubmitting(false)

      if (res && res.pro_expiry) {
        setProExpiry(res.pro_expiry)
        Taro.showToast({ title: t.activated, icon: 'success' })
        onSuccess()
        onClose()
      } else {
        // Keep the existing local demo fallback for the current referral flow.
        const nextWeek = new Date(Date.now() + 7 * 24 * 3600 * 1000).toISOString()
        setProExpiry(nextWeek)
        Taro.showToast({ title: t.activated, icon: 'success' })
        onSuccess()
        onClose()
      }
    } catch (err: any) {
      setSubmitting(false)
      Taro.showModal({
        title: t.notice,
        content: err.message || t.invalid,
        showCancel: false
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

        <View className="code-box">
          <Text className="code-label">{t.codeLabel}</Text>
          <Text className="code-value">{myCode}</Text>
          <Button className="btn-copy" onClick={handleCopy}>{t.copyCode}</Button>
        </View>

        <Button className="btn-share" onClick={handleShare}>
          {t.copyInvite}
        </Button>

        <View className="divider">
          <Text className="divider-text">{t.divider}</Text>
        </View>

        <View className="input-row">
          <Input
            className="code-input"
            placeholder={t.placeholder}
            value={inputCode}
            onInput={(e) => setInputCode(e.detail.value.toUpperCase())}
            maxlength={8}
          />
          <Button
            className="btn-redeem"
            onClick={handleRedeem}
            loading={submitting}
            disabled={submitting}
          >
            {t.redeem}
          </Button>
        </View>
      </View>
    </View>
  )
}
