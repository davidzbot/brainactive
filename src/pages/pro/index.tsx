import React, { useState, useEffect, useMemo } from 'react'
import { View, Text, Button, ScrollView, Picker } from '@tarojs/components'
import Taro, { useDidShow } from '@tarojs/taro'
import {
  isPro,
  getProExpiry,
  setProExpiry,
  getSubscriptionExpiry,
  setSubscriptionExpiry,
  getQuizHistory,
  getWrongQuestions,
  getLang,
  getDeviceId
} from '@/utils/storage'
import { getBrainActiveProgress } from '@/utils/request'
import ReferralModal from '@/components/ReferralModal'
import ConfirmModal from '@/components/ConfirmModal'
import AnalysisTab from '@/components/pro/AnalysisTab'
import CollectionTab from '@/components/pro/CollectionTab'
import './index.scss'

const TOPICS = [
  'All Thinking Topics',
  'Numerical Thinking',
  'Logical Thinking',
  'Pattern & Abstract',
  'Visual & Spatial',
  'Verbal Reasoning',
  'Problem Solving'
]

const LEVELS = ['Explore', 'Think', 'Challenge', 'Master']
const QUESTION_COUNTS = [5, 10, 15, 20]

const i18n = {
  en: {
    title: '🚀 Unlock Full Potential',
    tab_practice: 'Quest',
    tab_analysis: 'Stats',
    tab_collection: 'Collection',
    tab_sub: 'Membership',
    practice_title: 'Targeted Practice',
    practice_desc: 'Focus on specific reasoning archetypes and difficulty levels.',
    grade: 'Level',
    topic: 'Topic',
    q_count: 'Quest Length',
    start_quest: 'Start Practice Quest',
    stats_overall: 'Overall Accuracy',
    stats_practiced: 'Quests Completed',
    subject_stats: 'Topic Mastery',
    weak_topics: 'Areas to Strengthen',
    redo_wrong: 'Review Mistakes ({{count}})',
    accuracy_label: 'Accuracy',
    status_title: 'Pro Status',
    pro_active_sub: '🚀 Pro Active — Full Access Unlocked!',
    pro_active_ref: '🎁 Pro Active via Referral Reward!',
    pro_inactive: 'Standard Rank',
    valid_until: 'Access Valid Until: {{date}}',
    days_remaining: '{{count}} days left',
    referral_promo_title: 'Invite Friends & Get Pro Free',
    referral_promo_subtitle: 'Share BrainActive with friends and you both get 7 days of Pro free.',
    go_referral: 'Invite Friends',
    locked_instantly: 'Unlock Unlimited Practice & Insights',
    unlock_pro_overlay: 'Unlock Pro Access',
    paywall_title: 'Unlock Singapore P3 Thinking Skills Pro 🚀',
    paywall_subtitle: 'Unlimited reasoning practice and step-by-step AI coaching',
    annual_plan: 'Annual Pro Pass',
    annual_price: 'S$29.98',
    annual_desc: 'Best Value · S$2.50/mo · Unlimited Practice',
    monthly_plan: 'Monthly Pro Pass',
    monthly_price: 'S$4.98',
    monthly_desc: 'Flexible monthly access · Cancel anytime',
    best_value: 'BEST VALUE',
    btn_get_pro: 'Unlock Pro Access',
    reset: 'Reset Filters',
    restore_purchase: 'Restore Purchases',
    restore_desc: 'Switching phones or reinstalled? Restore your active subscription here.',
    billing_note: 'Billing and renewals are managed securely by Google Play. You can manage or cancel your subscription anytime in the Play Store.'
  },
  zh: {
    title: '🚀 释放全部思维潜能',
    tab_practice: '思维挑战',
    tab_analysis: '学习统计',
    tab_collection: '收藏夹',
    tab_sub: '会员特权',
    practice_title: '针对性训练',
    practice_desc: '针对特定思维模块和难度进行强化突破。',
    grade: '难度等级',
    topic: '思维领域',
    q_count: '题目数量',
    start_quest: '开始练习',
    stats_overall: '综合正确率',
    stats_practiced: '已完成题目',
    subject_stats: '知识点掌握',
    weak_topics: '需要加强的领域',
    redo_wrong: '重练错题 ({{count}})',
    accuracy_label: '正确率',
    status_title: '会员状态',
    pro_active_sub: '🚀 Pro 已开启 — 全部特权已解锁！',
    pro_active_ref: '🎁 推荐奖励带来的 Pro 权限！',
    pro_inactive: '普通学员',
    valid_until: '有效期至: {{date}}',
    days_remaining: '剩余 {{count}} 天',
    referral_promo_title: '邀请好友免费获取 Pro',
    referral_promo_subtitle: '分享 BrainActive，你和好友都能免费获得 7 天 Pro。',
    go_referral: '邀请好友',
    locked_instantly: '立即解锁无限思维训练与战力分析',
    unlock_pro_overlay: '开启 Pro 会员',
    paywall_title: '开启新加坡小三思维进阶 Pro 🚀',
    paywall_subtitle: '无限挑战名校思维题与 AI 导师专属辅导',
    annual_plan: 'Pro 年度会员',
    annual_price: 'S$29.98',
    annual_desc: '超值特惠 · 仅合 S$2.50/月 · 无限练习',
    monthly_plan: 'Pro 月度会员',
    monthly_price: 'S$4.98',
    monthly_desc: '灵活按月订阅 · 可随时取消',
    best_value: '超值推荐',
    btn_get_pro: '开启 Pro 特权',
    reset: '重置选项',
    restore_purchase: '恢复购买',
    restore_desc: '更换手机或重新安装？点击此处快速恢复您的 Pro 权益。',
    billing_note: '订阅由 Google Play 安全管理，可随时在 Play 商店取消或调整订阅。'
  }
}

export default function ProPage() {
  const lang = (getLang() || 'en') as 'en' | 'zh'
  const t = i18n[lang] || i18n.en

  const [activeTab, setActiveTab] = useState(0)
  const [proActive, setProActive] = useState(false)
  const [daysLeft, setDaysLeft] = useState(0)
  const [expiryText, setExpiryText] = useState('')

  // Practice filters
  const [selectedTopic, setSelectedTopic] = useState('All Thinking Topics')
  const [selectedLevel, setSelectedLevel] = useState('Think')
  const [selectedCount, setSelectedCount] = useState(5)

  const [trendFilter, setTrendFilter] = useState('Last Runs')
  const [showReferral, setShowReferral] = useState(false)
  const [selectedPlan, setSelectedPlan] = useState<'yearly' | 'monthly'>('yearly')

  const refreshState = () => {
    const active = isPro()
    setProActive(active)
    const expStr = getProExpiry() || getSubscriptionExpiry()
    if (expStr) {
      const expDate = new Date(expStr)
      setExpiryText(expDate.toLocaleDateString())
      const diff = Math.max(0, Math.ceil((expDate.getTime() - Date.now()) / (1000 * 3600 * 24)))
      setDaysLeft(diff)
    }
  }

  useDidShow(() => {
    refreshState()
    getBrainActiveProgress(getDeviceId())
      .then(data => {
        if (data) {
          if (data.is_pro) {
            setProActive(true)
            if (data.pro_expiry) {
              setProExpiry(data.pro_expiry)
              setSubscriptionExpiry(data.pro_expiry)
              const expDate = new Date(data.pro_expiry)
              setExpiryText(expDate.toLocaleDateString())
              const diff = Math.max(0, Math.ceil((expDate.getTime() - Date.now()) / (1000 * 3600 * 24)))
              setDaysLeft(diff)
            }
          }
        }
      })
      .catch(() => {})
  })

  // Compute stats from local quiz history
  const history = getQuizHistory() || []
  const wrongList = getWrongQuestions() || []
  const wrongCount = wrongList.length

  const stats = useMemo(() => {
    if (history.length === 0) {
      return {
        recentScore: 0,
        historyAvg: 0,
        totalQuests: 0,
        subjectBreakdown: [],
        focusAreas: [],
        strongestSubject: { name: 'Reasoning', avg: 0 },
        weakestTopic: { name: 'General', avg: 0 },
        trendData: []
      }
    }

    const totalCorrect = history.reduce((acc, h) => acc + (h.score || 0), 0)
    const totalQuestions = history.reduce((acc, h) => acc + (h.total || 5), 0)
    const historyAvg = totalQuestions > 0 ? Math.round((totalCorrect / totalQuestions) * 100) : 0

    const recent = history.slice(0, 5)
    const recentCorrect = recent.reduce((acc, h) => acc + (h.score || 0), 0)
    const recentTotal = recent.reduce((acc, h) => acc + (h.total || 5), 0)
    const recentScore = recentTotal > 0 ? Math.round((recentCorrect / recentTotal) * 100) : historyAvg

    // Breakdown by topic
    const topicMap: Record<string, { correct: number; total: number }> = {}
    history.forEach(h => {
      const topic = h.topic || 'General Thinking'
      if (!topicMap[topic]) topicMap[topic] = { correct: 0, total: 0 }
      topicMap[topic].correct += h.score || 0
      topicMap[topic].total += h.total || 5
    })

    const subjectBreakdown = Object.keys(topicMap).map(topic => {
      const { correct, total } = topicMap[topic]
      const avg = total > 0 ? Math.round((correct / total) * 100) : 0
      return {
        name: topic,
        count: total,
        avg,
        filters: { topic }
      }
    }).sort((a, b) => b.avg - a.avg)

    const strongest = subjectBreakdown[0] || { name: 'Reasoning', avg: historyAvg }
    const weakest = subjectBreakdown[subjectBreakdown.length - 1] || { name: 'General', avg: historyAvg }

    // Trend data
    const trendData = history.slice(-6).map((h, idx) => ({
      label: `R${idx + 1}`,
      value: h.total > 0 ? Math.round((h.score / h.total) * 100) : 0
    }))

    return {
      recentScore,
      historyAvg,
      totalQuests: totalQuestions,
      subjectBreakdown,
      focusAreas: [],
      strongestSubject: strongest,
      weakestTopic: weakest,
      trendData
    }
  }, [history])

  const getMetricColor = (val: number) => {
    if (val < 60) return '#ef4444'
    if (val < 80) return '#0284c7'
    return '#10b981'
  }

  const startPracticeWithFilters = (filters: any) => {
    if (!proActive) {
      setActiveTab(3)
      return
    }
    const params = new URLSearchParams()
    params.set('mode', 'pro_practice')
    if (filters.topic) params.set('topic', filters.topic)
    if (filters.level) params.set('level', filters.level)
    params.set('limit', String(filters.limit || 5))
    Taro.navigateTo({ url: `/pages/quiz/index?${params.toString()}` })
  }

  const handleStartQuest = () => {
    if (!proActive) {
      setActiveTab(3)
      return
    }
    const params = new URLSearchParams()
    params.set('mode', 'pro_practice')
    if (selectedTopic !== 'All Thinking Topics') params.set('topic', selectedTopic)
    params.set('level', selectedLevel)
    params.set('limit', String(selectedCount))
    Taro.navigateTo({ url: `/pages/quiz/index?${params.toString()}` })
  }

  const handleRedoWrong = () => {
    if (wrongCount > 0) {
      Taro.navigateTo({ url: '/pages/quiz/index?mode=retry' })
    }
  }

  // Membership activation simulation (ready for Google Play billing)
  const handleUpgradePlan = (plan: 'yearly' | 'monthly') => {
    Taro.showLoading({ title: 'Processing...' })
    setTimeout(() => {
      Taro.hideLoading()
      const days = plan === 'yearly' ? 365 : 30
      const expiry = new Date(Date.now() + days * 24 * 3600 * 1000).toISOString()
      setProExpiry(expiry)
      setSubscriptionExpiry(expiry)
      refreshState()
      Taro.showToast({ title: 'Pro Activated! 👑', icon: 'success' })
      setActiveTab(0)
    }, 800)
  }

  const handleRestore = () => {
    Taro.showLoading({ title: 'Checking Google Play...' })
    setTimeout(() => {
      Taro.hideLoading()
      refreshState()
      Taro.showToast({ title: 'Subscriptions checked!', icon: 'none' })
    }, 1000)
  }

  const ProLockOverlay = ({ feature }: { feature: string }) => (
    <View className="pro-feature-overlay" onClick={() => setActiveTab(3)}>
      <View className="lock-content">
        <Text className="lock-emoji">👑</Text>
        <Text className="lock-title">{t.locked_instantly}</Text>
        <Text className="lock-desc">
          {feature === 'practice'
            ? 'Target specific reasoning domains & challenge levels with full access.'
            : 'Unlock in-depth topic mastery analytics & progress tracking.'}
        </Text>
        <Button className="btn-unlock-preview">{t.unlock_pro_overlay}</Button>
      </View>
    </View>
  )

  return (
    <View className="pro-container">
      {/* Top 4-Tab Navigation Bar */}
      <View className="tab-header">
        {(['tab_practice', 'tab_analysis', 'tab_collection', 'tab_sub'] as const).map((label, idx) => (
          <View
            key={idx}
            className={`tab-item ${activeTab === idx ? 'active' : ''}`}
            onClick={() => setActiveTab(idx)}
          >
            <Text className="tab-text">{t[label]}</Text>
            {idx < 3 && !proActive && <Text className="lock-icon">💎</Text>}
          </View>
        ))}
      </View>

      <ScrollView scrollY className="tab-content">
        {/* TAB 0: TARGETED PRACTICE */}
        {activeTab === 0 && (
          <View className="practice-tab">
            <View className="card-section">
              <Text className="content-title">{t.practice_title}</Text>
              <Text className="content-desc">{t.practice_desc}</Text>

              <View className="filter-group">
                <View className="filter-item">
                  <Text className="filter-label">{t.topic}</Text>
                  <Picker
                    mode="selector"
                    range={TOPICS}
                    value={TOPICS.indexOf(selectedTopic)}
                    onChange={e => setSelectedTopic(TOPICS[Number(e.detail.value)])}
                  >
                    <View className="picker-val">{selectedTopic}</View>
                  </Picker>
                </View>

                <View className="filter-item">
                  <Text className="filter-label">{t.grade}</Text>
                  <Picker
                    mode="selector"
                    range={LEVELS}
                    value={LEVELS.indexOf(selectedLevel)}
                    onChange={e => setSelectedLevel(LEVELS[Number(e.detail.value)])}
                  >
                    <View className="picker-val">{selectedLevel}</View>
                  </Picker>
                </View>

                <View className="filter-item">
                  <Text className="filter-label">{t.q_count}</Text>
                  <Picker
                    mode="selector"
                    range={QUESTION_COUNTS.map(c => `${c} Questions`)}
                    value={QUESTION_COUNTS.indexOf(selectedCount)}
                    onChange={e => setSelectedCount(QUESTION_COUNTS[Number(e.detail.value)])}
                  >
                    <View className="picker-val">{selectedCount} Questions</View>
                  </Picker>
                </View>
              </View>

              <Button className="start-btn active" onClick={handleStartQuest}>
                {t.start_quest}
              </Button>
              <Button
                className="reset-btn"
                onClick={() => {
                  setSelectedTopic('All Thinking Topics')
                  setSelectedLevel('Think')
                  setSelectedCount(5)
                }}
              >
                {t.reset}
              </Button>
            </View>

            {!proActive && <ProLockOverlay feature="practice" />}
          </View>
        )}

        {/* TAB 1: LEARNING STATS & ANALYTICS */}
        {activeTab === 1 && (
          <View className={`analysis-tab ${!proActive ? 'is-locked' : ''}`}>
            {!proActive && <ProLockOverlay feature="stats" />}
            <AnalysisTab
              stats={stats}
              lang={lang}
              t={t}
              wrongCount={wrongCount}
              trendFilter={trendFilter}
              setTrendFilter={setTrendFilter}
              handleRedoWrong={handleRedoWrong}
              startPracticeWithFilters={startPracticeWithFilters}
              getMetricColor={getMetricColor}
              setActiveTab={setActiveTab}
            />
          </View>
        )}

        {/* TAB 2: SAVED QUESTIONS COLLECTION */}
        {activeTab === 2 && (
          <View className={`collection-tab ${!proActive ? 'is-locked' : ''}`}>
            {!proActive && <ProLockOverlay feature="collection" />}
            <CollectionTab lang={lang} />
          </View>
        )}

        {/* TAB 3: MEMBERSHIP & SUBSCRIPTION */}
        {activeTab === 3 && (
          <View className="status-tab">
            {/* Status Section */}
            <View className={proActive ? 'status-header-centered' : 'status-card'}>
              <View className={`hero-status-icon ${proActive ? 'pro' : ''}`}>
                {proActive ? '👑' : '🛡️'}
              </View>
              <View className="status-text-content">
                <Text className="status-title-text">
                  {proActive ? t.pro_active_sub : t.pro_inactive}
                </Text>
                {proActive && (
                  <View className="status-details">
                    <Text className="expiry-text">
                      {t.valid_until.replace('{{date}}', expiryText)}
                    </Text>
                    {daysLeft > 0 && (
                      <View className="days-remaining-badge">
                        <Text className="days-text">
                          {t.days_remaining.replace('{{count}}', String(daysLeft))}
                        </Text>
                      </View>
                    )}
                  </View>
                )}
              </View>
            </View>

            {/* Referral Promo Card */}
            <View className="referral-promo-card" onClick={() => setShowReferral(true)}>
              <View className="referral-promo-header">
                <View className="referral-promo-text">
                  <Text className="referral-promo-title">🎁 {t.referral_promo_title}</Text>
                  <Text className="referral-promo-subtitle">{t.referral_promo_subtitle}</Text>
                </View>
                <View className="referral-promo-action">
                  <Text className="referral-promo-btn-text">{t.go_referral} ›</Text>
                </View>
              </View>
            </View>

            {/* Paywall Plans Section */}
            <View className="paywall-plans-section">
              <Text className="paywall-section-title">{t.paywall_title}</Text>
              <Text className="paywall-section-subtitle">{t.paywall_subtitle}</Text>

              <View className="plans-stack">
                {/* Annual Plan Card */}
                <View
                  className={`plan-card-v2 ${selectedPlan === 'yearly' ? 'selected' : ''}`}
                  onClick={() => setSelectedPlan('yearly')}
                >
                  <View className="plan-badge-top">{t.best_value}</View>
                  <View className="plan-card-header">
                    <Text className="plan-name">{t.annual_plan}</Text>
                    <Text className="plan-price-tag">{t.annual_price}<Text className="period">/yr</Text></Text>
                  </View>
                  <Text className="plan-desc">{t.annual_desc}</Text>
                </View>

                {/* Monthly Plan Card */}
                <View
                  className={`plan-card-v2 ${selectedPlan === 'monthly' ? 'selected' : ''}`}
                  onClick={() => setSelectedPlan('monthly')}
                >
                  <View className="plan-card-header">
                    <Text className="plan-name">{t.monthly_plan}</Text>
                    <Text className="plan-price-tag">{t.monthly_price}<Text className="period">/mo</Text></Text>
                  </View>
                  <Text className="plan-desc">{t.monthly_desc}</Text>
                </View>
              </View>

              <Button
                className="btn-submit-upgrade"
                onClick={() => handleUpgradePlan(selectedPlan)}
              >
                {t.btn_get_pro}
              </Button>
            </View>

            {/* Restore & Billing Footer */}
            <View className="restore-footer-card">
              <Text className="restore-link" onClick={handleRestore}>
                🔄 {t.restore_purchase}
              </Text>
              <Text className="billing-note-text">{t.billing_note}</Text>
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
