import React from 'react'
import { View, Text, Button } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { showRewardAd } from '@/utils/ad'
import {
  getDailyUsage,
  canWatchAdForRound,
  unlockBonusRound,
  MAX_AD_ROUNDS_PER_DAY,
  MAX_TOTAL_DAILY_ROUNDS
} from '@/utils/storage'
import './index.scss'

interface QuotaOverlayProps {
  isOpen: boolean
  onClose: () => void
  onUnlocked: () => void
}

export default function QuotaOverlay({ isOpen, onClose, onUnlocked }: QuotaOverlayProps) {
  if (!isOpen) return null

  const usage = getDailyUsage()
  const canWatch = canWatchAdForRound()
  const adRoundsUsed = usage.bonusRounds
  const nextAdRoundNum = adRoundsUsed + 1

  const handleWatchAd = async () => {
    const success = await showRewardAd()
    if (success) {
      onUnlocked()
      onClose()
    }
  }

  const handleGoPro = () => {
    onClose()
    Taro.navigateTo({ url: '/pages/pro/index' })
  }

  return (
    <View className="quota-overlay">
      <View className="quota-card">
        <View className="icon-badge">⚡</View>
        <Text className="title">
          {canWatch ? "Today's Included Rounds Done" : "Daily Free Limit Reached"}
        </Text>
        <Text className="desc">
          {canWatch
            ? `You've completed your 2 included rounds today. Watch a video to unlock ad round ${nextAdRoundNum} of ${MAX_AD_ROUNDS_PER_DAY}!`
            : `You've completed all ${MAX_TOTAL_DAILY_ROUNDS} daily practice rounds (25 questions). Upgrade to Pro for unlimited practice!`}
        </Text>

        <View className="options-box">
          {canWatch && (
            <Button className="btn-watch-ad" onClick={handleWatchAd}>
              🎬 Watch Video for Round {nextAdRoundNum}/{MAX_AD_ROUNDS_PER_DAY}
            </Button>
          )}
          <Button className="btn-go-pro" onClick={handleGoPro}>
            Go Pro — Unlimited Practice 👑
          </Button>
        </View>

        <Text className="btn-close-link" onClick={onClose}>
          Maybe Later
        </Text>
      </View>
    </View>
  )
}
