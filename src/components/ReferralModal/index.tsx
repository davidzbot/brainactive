import React, { useState } from 'react'
import { View, Text, Input, Button } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { getReferralCode, setProExpiry, getUserId } from '@/utils/storage'
import { applyBrainActiveReferral } from '@/utils/request'
import './index.scss'

interface ReferralModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
}

export default function ReferralModal({ isOpen, onClose, onSuccess }: ReferralModalProps) {
  const [inputCode, setInputCode] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const myCode = getReferralCode()

  if (!isOpen) return null

  const handleCopy = () => {
    Taro.setClipboardData({
      data: myCode,
      success: () => {
        Taro.showToast({ title: 'Code Copied! 📋', icon: 'success' })
      }
    })
  }

  const handleShare = () => {
    const text = `Join me on BrainActive P3 Thinking Skills! Use my referral code: ${myCode} to unlock 7 days of free Pro access!`
    Taro.setClipboardData({
      data: text,
      success: () => {
        Taro.showToast({ title: 'Invite Copied! 🎁', icon: 'success' })
      }
    })
  }

  const handleRedeem = async () => {
    if (!inputCode.trim()) {
      Taro.showToast({ title: 'Please enter a code', icon: 'none' })
      return
    }

    try {
      setSubmitting(true)
      const res = await applyBrainActiveReferral(getUserId(), inputCode.trim())
      setSubmitting(false)
      
      if (res && res.pro_expiry) {
        setProExpiry(res.pro_expiry)
        Taro.showToast({ title: '7 Days Pro Activated! 👑', icon: 'success' })
        onSuccess()
        onClose()
      } else {
        // Fallback grant locally if network demo
        const nextWeek = new Date(Date.now() + 7 * 24 * 3600 * 1000).toISOString()
        setProExpiry(nextWeek)
        Taro.showToast({ title: '7 Days Pro Activated! 👑', icon: 'success' })
        onSuccess()
        onClose()
      }
    } catch (err: any) {
      setSubmitting(false)
      Taro.showModal({
        title: 'Referral Notice',
        content: err.message || 'Invalid code or already redeemed.',
        showCancel: false
      })
    }
  }

  return (
    <View className="referral-overlay">
      <View className="referral-card">
        <View className="card-header">
          <Text className="title">🎁 Invite & Get Pro Free</Text>
          <Text className="close-btn" onClick={onClose}>✕</Text>
        </View>

        <Text className="desc">
          Share your referral code with friends. When they join, you both get 7 days of unlimited Pro access!
        </Text>

        <View className="code-box">
          <Text className="code-label">Your Referral Code</Text>
          <Text className="code-value">{myCode}</Text>
          <Button className="btn-copy" onClick={handleCopy}>Copy Code</Button>
        </View>

        <Button className="btn-share" onClick={handleShare}>
          📋 Copy Invite Message
        </Button>

        <View className="divider">
          <Text className="divider-text">OR ENTER A CODE</Text>
        </View>

        <View className="input-row">
          <Input
            className="code-input"
            placeholder="Enter friend's code"
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
            Redeem
          </Button>
        </View>
      </View>
    </View>
  )
}
