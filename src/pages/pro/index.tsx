import React, { useState, useEffect, useMemo } from 'react'
import { View, Text, Button, ScrollView } from '@tarojs/components'
import Taro, { useDidShow } from '@tarojs/taro'
import {
  isPro,
  getProExpiry,
  setProExpiry,
  getSubscriptionExpiry,
  getQuizHistory,
  getWrongQuestions,
  getLang,
  getDeviceId
} from '@/utils/storage'
import { getBrainActiveProgress } from '@/utils/request'
import { aggregateQuizTopicPerformance } from '@/utils/quizInsights'
import { PLAN_PRICES } from '@/config/monetization'
import {
  getSubscriptionPrices,
  initializeBilling,
  purchaseSubscription,
  refreshBillingEntitlement,
  restoreBillingPurchases
} from '@/utils/billing'
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
// Available question counts per Topic×Level (live DB, 1533 active incl. new-600)
const AVAILABLE_MAP: Record<string, Record<string, number>> = {
  'All Thinking Topics': { Explore: 353, Think: 751, Challenge: 258, Master: 71 },
  'Numerical Thinking': { Explore: 68, Think: 179, Challenge: 45, Master: 27 },
  'Logical Thinking': { Explore: 65, Think: 178, Challenge: 41, Master: 6 },
  'Pattern & Abstract': { Explore: 95, Think: 121, Challenge: 19, Master: 4 },
  'Visual & Spatial': { Explore: 48, Think: 111, Challenge: 30, Master: 6 },
  'Verbal Reasoning': { Explore: 22, Think: 117, Challenge: 51, Master: 22 },
  'Problem Solving': { Explore: 53, Think: 145, Challenge: 68, Master: 12 },
}
const TOPIC_LABELS = {
  en: TOPICS,
  zh: ['全部思维领域', '数理思维', '逻辑思维', '图形与抽象', '视觉与空间', '语言推理', '问题解决']
}
const LEVEL_LABELS = {
  en: LEVELS,
  zh: ['探索', '思考', '挑战', '大师']
}

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
    stats_practiced: 'Questions Solved',
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
    referral_promo_title: 'Share with Friends & Family',
    referral_promo_subtitle: 'Love BrainActive? Share it with friends and family who enjoy thinking challenges.',
    go_referral: 'Share Now',
    locked_instantly: 'Unlock Unlimited Practice & Insights',
    unlock_pro_overlay: 'Unlock Pro Access',
    paywall_title: 'Unlock Singapore P3 Thinking Skills Pro 🚀',
    paywall_subtitle: 'Unlimited reasoning practice and step-by-step AI coaching',
    annual_plan: 'Annual Pro Pass',
    annual_price: PLAN_PRICES.yearly,
    annual_desc: 'Best Value · S$2.50/mo · Unlimited Practice',
    monthly_plan: 'Monthly Pro Pass',
    monthly_price: PLAN_PRICES.monthly,
    monthly_desc: 'Flexible monthly access · Cancel anytime',
    best_value: 'BEST VALUE',
    btn_get_pro: 'Unlock Pro Access',
    reset: 'Reset Filters',
    restore_purchase: 'Restore Purchases',
    restore_desc: 'Switching phones or reinstalled? Restore your active subscription here.',
    billing_note: 'Billing and renewals are managed securely by Google Play. You can manage or cancel your subscription anytime in the Play Store.',
    period_year: '/yr',
    period_month: '/mo',
    practice_lock: 'Target specific reasoning domains and challenge levels with full access.',
    stats_lock: 'Unlock topic mastery insights and progress tracking.',
    processing: 'Processing...',
    activated: 'Pro Activated! 👑',
    checking: 'Checking Google Play...',
    checked: 'Subscriptions checked!'

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
    referral_promo_title: '分享给亲友',
    referral_promo_subtitle: '喜欢 BrainActive？分享给喜欢思维挑战的亲友们吧。',
    go_referral: '立即分享',
    locked_instantly: '立即解锁无限思维训练与战力分析',
    unlock_pro_overlay: '开启 Pro 会员',
    paywall_title: '开启新加坡小三思维进阶 Pro 🚀',
    paywall_subtitle: '无限挑战名校思维题与 AI 导师专属辅导',
    annual_plan: 'Pro 年度会员',
    annual_price: PLAN_PRICES.yearly,
    annual_desc: '超值特惠 · 仅合 S$2.50/月 · 无限练习',
    monthly_plan: 'Pro 月度会员',
    monthly_price: PLAN_PRICES.monthly,
    monthly_desc: '灵活按月订阅 · 可随时取消',
    best_value: '超值推荐',
    btn_get_pro: '开启 Pro 特权',
    reset: '重置选项',
    restore_purchase: '恢复购买',
    restore_desc: '更换手机或重新安装？点击此处快速恢复您的 Pro 权益。',
    billing_note: '订阅由 Google Play 安全管理，可随时在 Play 商店取消或调整订阅。',
    period_year: '/年',
    period_month: '/月',
    practice_lock: '解锁全部思维领域和挑战难度，进行针对性训练。',
    stats_lock: '解锁领域掌握度分析与学习进度追踪。',
    processing: '正在处理…',
    activated: 'Pro 已激活！👑',
    checking: '正在检查 Google Play…',
    checked: '订阅状态已检查！'
  }
}

export default function ProPage() {
  const [lang, setLang] = useState<'en' | 'zh'>(() => (getLang() || 'en') as 'en' | 'zh')
  const t = i18n[lang] || i18n.en
  const topicLabels = TOPIC_LABELS[lang]
  const levelLabels = LEVEL_LABELS[lang]

  const [activeTab, setActiveTab] = useState(
    Taro.getCurrentInstance().router?.params?.tab === 'analysis' ? 1 : 0
  )
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
  const [playPrices, setPlayPrices] = useState<{ yearly: string | null; monthly: string | null } | null>(null)
  const [pickerOpen, setPickerOpen] = useState<null | 'topic' | 'level' | 'count'>(null)

  // Dynamic available levels based on topic (follow MathHero)
  const availableLevels = useMemo(() => {
    const map = AVAILABLE_MAP[selectedTopic] || AVAILABLE_MAP['All Thinking Topics']
    return LEVELS.filter(lv => (map[lv] || 0) > 0)
  }, [selectedTopic])

  useEffect(() => {
    if (!availableLevels.includes(selectedLevel)) {
      setSelectedLevel(availableLevels[0] || 'Think')
    }
  }, [availableLevels, selectedLevel])

  const availableForCurrent = (AVAILABLE_MAP[selectedTopic]?.[selectedLevel] ?? 0)

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
    setLang((getLang() || 'en') as 'en' | 'zh')
    refreshState()
    initializeBilling()
      .then(() => getSubscriptionPrices())
      .then(prices => { if (prices) setPlayPrices(prices) })
      .catch(() => {})
    refreshBillingEntitlement().then(refreshState).catch(() => {})
    getBrainActiveProgress(getDeviceId())
      .then(data => {
        if (data) {
          if (data.is_pro) {
            setProActive(true)
            if (data.pro_expiry) {
              setProExpiry(data.pro_expiry)
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

  useEffect(() => {
    const handleBillingEntitlement = () => refreshState()
    Taro.eventCenter.on('brainactive_billing_entitlement_changed', handleBillingEntitlement)
    return () => {
      Taro.eventCenter.off('brainactive_billing_entitlement_changed', handleBillingEntitlement)
    }
  }, [])

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

    const subjectBreakdown = aggregateQuizTopicPerformance(history).map(performance => ({
      name: performance.topic,
      count: performance.total,
      avg: performance.accuracy,
      filters: { topic: performance.topic }
    }))

    const strongest = subjectBreakdown[0] || { name: 'Reasoning', avg: historyAvg }
    const weakest = subjectBreakdown[subjectBreakdown.length - 1] || { name: 'General', avg: historyAvg }

    // Trend data — respects selected filter (Last Runs / 7D / 30D / All Time)
    let filteredForTrend = history
    if (trendFilter === '7D' || trendFilter === '30D') {
      const days = trendFilter === '7D' ? 7 : 30
      const cutoff = Date.now() - days * 24 * 60 * 60 * 1000
      filteredForTrend = history.filter(h => {
        const t = h.date ? new Date(h.date).getTime() : 0
        return t >= cutoff
      })
    } else if (trendFilter === 'All Time') {
      filteredForTrend = history
    } else {
      // Last Runs — last 6 attempts
      filteredForTrend = history.slice(0, 6)
    }
    const trendData = filteredForTrend.slice(0, 6).reverse().map((h, idx) => ({
      label: `R${idx + 1}`,
      value: h.total > 0 ? Math.round((h.score / h.total) * 100) : 0
    }))

    const focusAreas = [...subjectBreakdown].sort((a, b) => a.avg - b.avg).slice(0, 3)

    return {
      recentScore,
      historyAvg,
      totalQuests: totalQuestions,
      subjectBreakdown,
      focusAreas,
      strongestSubject: strongest,
      weakestTopic: weakest,
      trendData,
      recentSessions: history.slice(0, 5)
    }
  }, [history, trendFilter])

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
    if (filters.topic && filters.topic !== 'Mixed' && filters.topic !== 'General Thinking') {
      params.set('topic', filters.topic)
    }
    if (filters.level) params.set('level', filters.level)
    params.set('limit', String(filters.limit || 5))
    Taro.navigateTo({ url: `/pages/quiz/index?${params.toString()}` })
  }

  const handleStartQuest = () => {
    if (!proActive) {
      setActiveTab(3)
      return
    }
    if (availableForCurrent === 0) return
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

  const handleGoHome = () => {
    Taro.reLaunch({ url: '/pages/home/index' }).catch(() => {
      Taro.navigateBack().catch(() => {})
    })
  }

  const handleUpgradePlan = async (plan: 'yearly' | 'monthly') => {
    Taro.showLoading({ title: t.processing })
    try {
      const result = await purchaseSubscription(plan)
      if (result?.isError) {
        Taro.showToast({ title: result.message || t.checked, icon: 'none' })
        return
      }
      Taro.showToast({ title: lang === 'zh' ? '正在打开 Google Play…' : 'Opening Google Play…', icon: 'none' })
    } catch {
      Taro.showToast({ title: t.checked, icon: 'none' })
    } finally {
      Taro.hideLoading()
    }
  }

  const handleRestore = async () => {
    Taro.showLoading({ title: t.checking })
    try {
      const restored = await restoreBillingPurchases()
      refreshState()
      Taro.showToast({
        title: restored ? (lang === 'zh' ? 'Pro 已恢复！' : 'Pro restored!') : t.checked,
        icon: 'none'
      })
    } catch {
      Taro.showToast({ title: t.checked, icon: 'none' })
    } finally {
      Taro.hideLoading()
    }
  }

  const ProLockOverlay = ({ feature }: { feature: string }) => (
    <View className="pro-feature-overlay" onClick={() => setActiveTab(3)}>
      <View className="lock-content">
        <Text className="lock-emoji">👑</Text>
        <Text className="lock-title">{t.locked_instantly}</Text>
        <Text className="lock-desc">
          {feature === 'practice' ? t.practice_lock : t.stats_lock}
        </Text>
        <Button className="btn-unlock-preview">{t.unlock_pro_overlay}</Button>
      </View>
    </View>
  )

  return (
    <View className="pro-container">
      {/* Top Navigation Bar */}
      <View className="tab-header">
        <View className="pro-tabs">
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
                  <View className="picker-val" onClick={() => setPickerOpen('topic')}>
                    {topicLabels[TOPICS.indexOf(selectedTopic)]}
                  </View>
                </View>

                <View className="filter-item">
                  <Text className="filter-label">{t.grade}</Text>
                  <View className="picker-val" onClick={() => setPickerOpen('level')}>
                    {levelLabels[LEVELS.indexOf(selectedLevel)]}
                  </View>
                </View>

                <View className="filter-item">
                  <Text className="filter-label">{t.q_count}</Text>
                  <View className="picker-val" onClick={() => setPickerOpen('count')}>
                    {lang === 'zh' ? `${selectedCount} 道题` : `${selectedCount} Questions`}
                  </View>
                  {availableForCurrent > 0 && availableForCurrent < selectedCount && (
                    <Text className="filter-hint">{lang === 'zh' ? `仅 ${availableForCurrent} 题可用，将显示全部` : `Only ${availableForCurrent} available`}</Text>
                  )}
                </View>
              </View>

              {availableForCurrent === 0 && (
                <Text className="filter-hint" style={{ color: '#ef4444' }}>{lang === 'zh' ? '该组合暂无题目，请选择其他' : 'No questions for this combination'}</Text>
              )}
              <Button className={`start-btn ${availableForCurrent === 0 ? '' : 'active'}`} onClick={handleStartQuest} disabled={availableForCurrent === 0}>
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
                    <Text className="plan-price-tag">{playPrices?.yearly || t.annual_price}<Text className="period">{t.period_year}</Text></Text>
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
                    <Text className="plan-price-tag">{playPrices?.monthly || t.monthly_price}<Text className="period">{t.period_month}</Text></Text>
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

      {/* Central bottom Home button — consistent with quiz/result */}
      <View className="pro-bottom-home">
        <View className="global-home-bottom-link" onClick={handleGoHome}>
          <Text className="bottom-home-icon">⌂</Text>
        </View>
      </View>

      {/* Custom Picker Overlay — i18n aware, replaces native Picker */}
      {pickerOpen && (
        <View className="picker-overlay" onClick={() => setPickerOpen(null)}>
          <View className="picker-sheet" onClick={(e: any) => e.stopPropagation()}>
            <View className="picker-sheet-header">
              <Text className="picker-cancel" onClick={() => setPickerOpen(null)}>
                {lang === 'zh' ? '取消' : 'Cancel'}
              </Text>
              <Text className="picker-title">
                {pickerOpen === 'topic' ? t.topic : pickerOpen === 'level' ? t.grade : t.q_count}
              </Text>
              <Text className="picker-confirm" onClick={() => setPickerOpen(null)}>
                {lang === 'zh' ? '确定' : 'Confirm'}
              </Text>
            </View>
            <ScrollView scrollY className="picker-options">
              {(pickerOpen === 'topic' ? TOPICS : pickerOpen === 'level' ? availableLevels : QUESTION_COUNTS).map((opt: any, idx: number) => {
                const label = pickerOpen === 'topic' ? (TOPIC_LABELS as any)[lang][idx] : pickerOpen === 'level' ? (LEVEL_LABELS as any)[lang][LEVELS.indexOf(opt)] ?? opt : lang === 'zh' ? `${opt} 道题` : `${opt} Questions`
                const isSelected = pickerOpen === 'topic' ? opt === selectedTopic : pickerOpen === 'level' ? opt === selectedLevel : opt === selectedCount
                return (
                  <View
                    key={idx}
                    className={`picker-option ${isSelected ? 'selected' : ''}`}
                    onClick={() => {
                      if (pickerOpen === 'topic') setSelectedTopic(opt)
                      else if (pickerOpen === 'level') setSelectedLevel(opt)
                      else setSelectedCount(opt)
                      setPickerOpen(null)
                    }}
                  >
                    <Text className="picker-option-text">{label}</Text>
                    {isSelected && <Text className="picker-check">✓</Text>}
                  </View>
                )
              })}
            </ScrollView>
          </View>
        </View>
      )}

      <ReferralModal
        isOpen={showReferral}
        onClose={() => setShowReferral(false)}
        onSuccess={refreshState}
      />
    </View>
  )
}
