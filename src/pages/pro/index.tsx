import React, { useState } from 'react'
import { View, Text, Button, ScrollView } from '@tarojs/components'
import Taro, { useDidShow } from '@tarojs/taro'
import {
  isPro,
  getProExpiry,
  setProExpiry,
  getSubscriptionExpiry,
  setSubscriptionExpiry
} from '@/utils/storage'
import ReferralModal from '@/components/ReferralModal'
import './index.scss'

const TOPICS = [
  { id: 'All', name: 'All Thinking Topics', icon: '🌟' },
  { id: 'Numerical Thinking', name: 'Numerical Thinking', icon: '🔢' },
  { id: 'Logical Thinking', name: 'Logical Thinking', icon: '🧩' },
  { id: 'Pattern & Abstract', name: 'Pattern & Abstract', icon: '💠' },
  { id: 'Visual & Spatial', name: 'Visual & Spatial', icon: '📐' },
  { id: 'Verbal Reasoning', name: 'Verbal Reasoning', icon: '📖' },
  { id: 'Problem Solving', name: 'Problem Solving', icon: '💡' }
]

const LEVELS = [
  { id: 'All', name: 'Mixed Levels', desc: 'All Topics Mixed · Great Starting Point' },
  { id: 'Explore', name: 'Explore', desc: 'Foundational Concepts' },
  { id: 'Think', name: 'Think', desc: 'Core Reasoning Power' },
  { id: 'Challenge', name: 'Challenge', desc: 'Advanced Non-Routine' },
  { id: 'Master', name: 'Master', desc: 'Competition / GEP Standard' }
]

export default function ProPage() {
  const [proActive, setProActive] = useState(false)
  const [selectedTopic, setSelectedTopic] = useState('All')
  const [selectedLevel, setSelectedLevel] = useState('All')
  const [showReferral, setShowReferral] = useState(false)
  const [expiryText, setExpiryText] = useState('')

  const refreshState = () => {
    const active = isPro()
    setProActive(active)
    const exp = getProExpiry() || getSubscriptionExpiry()
    if (exp) {
      setExpiryText(new Date(exp).toLocaleDateString())
    }
  }

  useDidShow(() => {
    refreshState()
  })

  const handleStartProPractice = () => {
    if (!proActive) {
      Taro.showToast({ title: 'Please activate Pro first 👑', icon: 'none' })
      return
    }
    const query = new URLSearchParams()
    query.set('mode', 'pro_practice')
    if (selectedTopic !== 'All') query.set('topic', selectedTopic)
    if (selectedLevel !== 'All') query.set('level', selectedLevel)

    Taro.navigateTo({
      url: `/pages/quiz/index?${query.toString()}`
    })
  }

  // Simulated subscription activation for staging/dev (ready for live Google Play IDs)
  const handleUpgradePlan = (planName: string) => {
    Taro.showLoading({ title: 'Processing...' })
    setTimeout(() => {
      Taro.hideLoading()
      const expiry = new Date(Date.now() + 30 * 24 * 3600 * 1000).toISOString()
      setProExpiry(expiry)
      setSubscriptionExpiry(expiry)
      setProActive(true)
      setExpiryText(new Date(expiry).toLocaleDateString())
      Taro.showToast({ title: 'Pro Activated! 👑', icon: 'success' })
    }, 800)
  }

  return (
    <View className="pro-page-container">
      {/* Header */}
      <View className="pro-header">
        <View className="pro-badge">
          <Text className="badge-icon">👑</Text>
          <Text className="badge-title">Unlimited Practice Zone</Text>
        </View>
        <Text className="header-sub">
          {proActive
            ? `Unlimited practice active until ${expiryText}`
            : 'Unlock unlimited practice across all Singapore P3 thinking skills'}
        </Text>
      </View>

      <ScrollView scrollY className="pro-scroll-content">
        {/* Practice Config Section */}
        <View className="config-card">
          <Text className="section-title">Choose a Topic</Text>
          <View className="topic-grid">
            {TOPICS.map(t => (
              <View
                key={t.id}
                className={`topic-chip ${selectedTopic === t.id ? 'selected' : ''}`}
                onClick={() => setSelectedTopic(t.id)}
              >
                <Text className="topic-icon">{t.icon}</Text>
                <Text className="topic-name">{t.name}</Text>
              </View>
            ))}
          </View>

          <Text className="section-title" style={{ marginTop: 20 }}>Choose a Level</Text>
          <View className="level-list">
            {LEVELS.map(l => (
              <View
                key={l.id}
                className={`level-item ${selectedLevel === l.id ? 'selected' : ''}`}
                onClick={() => setSelectedLevel(l.id)}
              >
                <View className="level-left">
                  <Text className="level-name">{l.name}</Text>
                  <Text className="level-desc">{l.desc}</Text>
                </View>
                <View className="radio-circle">
                  {selectedLevel === l.id && <View className="radio-inner" />}
                </View>
              </View>
            ))}
          </View>
        </View>

        {/* Start Button if Pro */}
        {proActive ? (
          <Button className="btn-start-pro" onClick={handleStartProPractice}>
            🚀 Start Unlimited Practice
          </Button>
        ) : (
          /* Paywall Section */
          <View className="paywall-section">
            <Text className="paywall-heading">Choose a Membership Plan</Text>

            <View className="plans-grid">
              <View className="plan-card featured" onClick={() => handleUpgradePlan('Yearly')}>
                <View className="popular-tag">BEST VALUE</View>
                <Text className="plan-title">Annual Pro Pass</Text>
                <Text className="plan-price">S$48.00<Text className="plan-period">/year</Text></Text>
                <Text className="plan-sub">Just S$4.00/month · Unlimited Access</Text>
                <Button className="btn-plan-select">Get Annual Pass</Button>
              </View>

              <View className="plan-card" onClick={() => handleUpgradePlan('Monthly')}>
                <Text className="plan-title">Monthly Pro Pass</Text>
                <Text className="plan-price">S$7.98<Text className="plan-period">/month</Text></Text>
                <Text className="plan-sub">Flexible monthly access · Cancel anytime</Text>
                <Button className="btn-plan-select secondary">Get Monthly Pass</Button>
              </View>
            </View>

            {/* Free Referral Option */}
            <View className="free-ref-box" onClick={() => setShowReferral(true)}>
              <Text className="ref-free-icon">🎁</Text>
              <View className="ref-free-text">
                <Text className="ref-free-title">Earn 7 Days Free — Invite a Friend</Text>
                <Text className="ref-free-desc">When your friend joins, you both get 7 days of Pro access!</Text>
              </View>
              <Text className="ref-free-cta">Invite →</Text>
            </View>
          </View>
        )}
      </ScrollView>

      <ReferralModal
        isOpen={showReferral}
        onClose={() => setShowReferral(false)}
        onSuccess={refreshState}
      />
    </View>
  )
}
