import React from 'react'
import { View, Text, Button } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { showRewardAd } from '@/utils/ad'
import {
  getDailyUsage,
  canWatchAdForRound,
  getLang,
  FREE_ROUNDS_PER_DAY,
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
  const lang = (getLang() || 'en') as 'en' | 'zh'
  const copy = lang === 'zh'
    ? {
        includedTitle: '今日免费练习已完成',
        limitTitle: '今日练习次数已用完',
        includedDesc: `你已完成今天的 ${FREE_ROUNDS_PER_DAY} 轮免费练习。观看短视频即可解锁第 ${nextAdRoundNum}/${MAX_AD_ROUNDS_PER_DAY} 轮！`,
        limitDesc: `你已完成今天全部 ${MAX_TOTAL_DAILY_ROUNDS} 轮练习（25 道题）。升级 Pro，畅享无限练习！`,
        watch: `🎬 看视频解锁第 ${nextAdRoundNum}/${MAX_AD_ROUNDS_PER_DAY} 轮`,
        pro: '升级 Pro — 无限练习 👑',
        later: '稍后再说'
      }
    : {
        includedTitle: 'Today\'s Free Practice Is Complete',
        limitTitle: 'Today\'s Practice Limit Is Reached',
        includedDesc: `You completed your ${FREE_ROUNDS_PER_DAY} free rounds today. Watch a short video to unlock round ${nextAdRoundNum}/${MAX_AD_ROUNDS_PER_DAY}!`,
        limitDesc: `You completed all ${MAX_TOTAL_DAILY_ROUNDS} practice rounds today (25 questions). Upgrade to Pro for unlimited practice!`,
        watch: `🎬 Watch Video for Round ${nextAdRoundNum}/${MAX_AD_ROUNDS_PER_DAY}`,
        pro: 'Go Pro — Unlimited Practice 👑',
        later: 'Maybe Later'
      }

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
          {canWatch ? copy.includedTitle : copy.limitTitle}
        </Text>
        <Text className="desc">
          {canWatch ? copy.includedDesc : copy.limitDesc}
        </Text>

        <View className="options-box">
          {canWatch && (
            <Button className="btn-watch-ad" onClick={handleWatchAd}>
              {copy.watch}
            </Button>
          )}
          <Button className="btn-go-pro" onClick={handleGoPro}>
            {copy.pro}
          </Button>
        </View>

        <Text className="btn-close-link" onClick={onClose}>
          {copy.later}
        </Text>
      </View>
    </View>
  )
}
