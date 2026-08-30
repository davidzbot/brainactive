import React, { useState, useEffect, useMemo, useRef } from 'react'
import { View, Text, ScrollView, Button, Swiper, SwiperItem } from '@tarojs/components'
import Taro, { useLoad, useDidShow, navigateTo, setNavigationBarTitle, showModal } from '@tarojs/taro'
import {
  getStreak,
  getDailyUsage,
  getRemainingFreeRounds,
  canStartPractice,
  isPro as checkIsPro,
  getProExpiry,
  getSubscriptionExpiry,
  getLang,
  setLang,
  getDeviceId,
  getUserId,
  getStorage,
  setStorage,
  getLogicalSgtDay,
  unlockBonusRound,
  canWatchAdForRound,
  getWrongQuestions,
  getQuizHistory,
  FREE_ROUNDS_PER_DAY,
  MAX_AD_ROUNDS_PER_DAY,
  MAX_TOTAL_DAILY_ROUNDS
} from '@/utils/storage'
import { getBrainActiveProgress } from '@/utils/request'
import { showRewardAd, preloadAd } from '@/utils/ad'
import ReferralModal from '@/components/ReferralModal'
import QuotaOverlay from '@/components/QuotaOverlay'
import SettingsModal from '@/components/SettingsModal'
import ConfirmModal from '@/components/ConfirmModal'
import './index.scss'

const i18n = {
  en: {
    title: 'BrainActive',
    curriculum_badge: 'Singapore P3 High Ability Thinking Skills',
    daily_title: 'Daily Practice Round',
    daily_specs: '5 Questions · 5–8 Mins · Non-Routine Reasoning',
    daily_cta: 'Begin Today\'s Practice →',
    daily_complete: 'Today\'s Practice Complete! 🎉',
    daily_complete_msg: 'Great job finishing today\'s thinking set!',
    daily_continue: 'Practice More',
    daily_continue_free: '📺 Watch Ad for Bonus Round',
    daily_start_bonus: 'Start Bonus Round ⚡',
    daily_come_back_tmr: 'Come back tomorrow for a new set 🌙',
    daily_upgrade_pro: '👑 Go Pro for unlimited practice →',
    streak_title: 'Day Streak!',
    longest_streak: 'Longest',
    next_goal: 'Next Goal:',
    days_unit: 'Days',
    day_unit: 'Day',
    pro_title: 'BrainActive Pro',
    pro_active_title: 'BrainActive Pro Active',
    pro_sub: 'Unlimited Practice · All 6 Domains · 4 Levels',
    pro_active_sub: '👑 Pro Member Activated · Full Access',
    pro_upgrade_cta: 'Upgrade to Pro',
    pro_active_cta: 'Enter Pro Zone',
    usage_free: '🎯 {{free}} Free Round{{s}} • {{ads}} Ad Unlocks',
    usage_pro: '👑 BrainActive Pro Active • Unlimited Practice',
    usage_all_done: '✅ All 5 Practice Rounds Completed Today',
    progress_title: 'Your Progress Journey',
    progress_weekly: 'This Week',
    progress_questions: 'Questions Done',
    progress_mistakes: 'Mistakes',
    progress_topics: 'Recent Domains',
    progress_empty: 'Start practicing to see your progress!',
    retry_wrong: 'Review Mistakes',
    retry_wrong_sub: 'Practice your recent tricky questions',
    extra_practice: 'Extra Practice Available',
    extra_practice_sub: 'Watch a short video to unlock another round',
    extra_practice_ready: 'Bonus Round Ready!',
    extra_practice_ready_sub: 'Start your unlocked bonus round now!',
    extra_practice_limit: 'Daily free limit reached (5/5 rounds)',
    extra_practice_limit_sub: 'Come back tomorrow for more practice.',
    ad_confirm_title: 'Unlock Bonus Round?',
    ad_confirm_content: 'Watch a short video to unlock 1 additional practice round. This helps support our development!',
    ad_confirm_ok: 'Watch Video',
    ad_confirm_cancel: 'Cancel',
    referral_title: 'Share with Friends — Pro Free!',
    referral_sub: 'Send BrainActive to a friend. You can both unlock 7 days of Pro free!',
    referral_btn: 'Invite',
    tips_title: 'Thinking Skills Heuristics',
    tips: [
      { title: '⚖️ Balance & Weight Systems', desc: 'Sum all pairs together first, then subtract individual pair equations to isolate each unknown.' },
      { title: '🔄 Working Backwards', desc: 'Start from the final result and invert each operation (add becomes subtract, multiply becomes divide).' },
      { title: '🧩 Pattern & Invariant Detection', desc: 'Look for what stays constant between steps: differences, sums, or geometric symmetry.' },
      { title: '🗺️ Spatial Elimination & Nets', desc: 'Opposite faces on a standard cube net are always separated by exactly one square or along alternating arms.' },
      { title: '🔎 Systematic Listing & Tree Logic', desc: 'List cases in orderly alphabetical or numerical sequence to avoid double-counting or missing options.' }
    ],
    feedback: 'Feedback',
    support_email: 'Support: pslehero@gmail.com',
    website: 'Website: https://pslehero.org/',
    more_hero_title: 'More from Hero',
    more_hero: [
      { emoji: '🧠', name: 'High-Ability P3 Guide', sub: 'See how Math Hero spots giftedness — free' },
      { emoji: '🏆', name: 'PSLE Hero', sub: 'Top PSLE exam practice app' },
      { emoji: '➗', name: 'Singapore Primary Math', sub: 'Master Primary Math concepts' }
    ]
  },
  zh: {
    title: 'BrainActive',
    curriculum_badge: '新加坡 P3 高能力思维特训',
    daily_title: '今日思维特训',
    daily_specs: '5 道题 · 5–8 分钟 · 高难度思维拓展',
    daily_cta: '开始今日特训 →',
    daily_complete: '今日特训已完成！🎉',
    daily_complete_msg: '太棒了！你已顺利完成今日思维挑战。',
    daily_continue: '继续特训',
    daily_continue_free: '📺 看广告解锁新一轮',
    daily_start_bonus: '开始额外挑战 ⚡',
    daily_come_back_tmr: '明天再来挑战新题目吧 🌙',
    daily_upgrade_pro: '👑 升级 Pro 畅享无限练习 →',
    streak_title: '天连胜！',
    longest_streak: '最高连胜',
    next_goal: '下一个目标：',
    days_unit: '天',
    day_unit: '天',
    pro_title: 'BrainActive Pro',
    pro_active_title: 'BrainActive Pro 专区',
    pro_sub: '无限特训 · 涵盖全部 6 大思维领域 · 4 级难度',
    pro_active_sub: '👑 Pro 会员已激活 · 畅享全部特训',
    pro_upgrade_cta: '升级为 Pro',
    pro_active_cta: '进入 Pro 专区',
    usage_free: '🎯 今日剩余 {{free}} 次免费 · {{ads}} 次广告解锁',
    usage_pro: '👑 Pro 会员已激活 · 无限思维特训',
    usage_all_done: '✅ 今日 5 轮特训已全部完成',
    progress_title: '学习进度与足迹',
    progress_weekly: '本周答题',
    progress_questions: '道题已完成',
    progress_mistakes: '错题珍藏',
    progress_topics: '最近练习领域',
    progress_empty: '开始练习即可查看学习进度！',
    retry_wrong: '复习错题',
    retry_wrong_sub: '针对最近做错的题目专项突破',
    extra_practice: '额外挑战可用',
    extra_practice_sub: '观看简短视频，解锁新一轮特训',
    extra_practice_ready: '额外挑战已就绪！',
    extra_practice_ready_sub: '立即开始您已解锁的额外挑战！',
    extra_practice_limit: '今日特训次数已达上限 (5/5)',
    extra_practice_limit_sub: '明天再来挑战新题目吧。',
    ad_confirm_title: '解锁额外挑战？',
    ad_confirm_content: '观看一段简短视频即可解锁 1 次额外练习机会。您的支持是我们持续精进的动力！',
    ad_confirm_ok: '立即观看',
    ad_confirm_cancel: '取消',
    referral_title: '分享给好友，免费赢 Pro！',
    referral_sub: '把 BrainActive 分享给好友，双方都可免费获得 7 天 Pro！',
    referral_btn: '去邀请',
    tips_title: '核心思维方法精讲',
    tips: [
      { title: '⚖️ 天平代换与等式消元', desc: '将所有组合式相加求总和，再减去单个组合式快速求出未知量。' },
      { title: '🔄 倒推法 (Working Backwards)', desc: '从已知最终结果出发，反向执行逆运算，步步还原起始数值。' },
      { title: '🧩 寻找规律与不变量', desc: '观察变化过程中的恒定特征：差不变、和不变或几何对称性。' },
      { title: '🗺️ 空间折叠与展开图排查', desc: '正方体展开图中，相对的面中间隔着一个正方形，或呈 Z 字形分布。' },
      { title: '🔎 有序列举与树状排查', desc: '按固定字母或大小顺序逐一列举，做到不重复、不遗漏。' }
    ],
    feedback: '意见反馈',
    support_email: '支持: pslehero@gmail.com',
    website: '官网: https://pslehero.org/',
    more_hero_title: '来自 Hero 的更多内容',
    more_hero: [
      { emoji: '🧠', name: '高能力 P3 识别指南', sub: '了解 Math Hero 如何识别天赋 · 免费' },
      { emoji: '🏆', name: 'PSLE Hero', sub: '小六会考备考首选应用' },
      { emoji: '➗', name: '新加坡小学数学', sub: '系统掌握小学数学' }
    ]
  }
}

const STREAK_MESSAGES = [
  { zh: '积少成多，持之以恒！', en: 'Small steps add up every day!' },
  { zh: '思维敏锐，不断突破！', en: 'Sharp thinking makes great strides!' },
  { zh: '探寻本质，稳步向前！', en: 'Practice builds powerful intuition!' },
  { zh: '勇于探索，挑战非凡！', en: 'Curiosity unlocks deep reasoning!' },
  { zh: '每日精进，更进一步！', en: 'Every quest strengthens your mind!' }
]

const WEEK_DAYS = [
  { en: 'Mon', zh: '一' },
  { en: 'Tue', zh: '二' },
  { en: 'Wed', zh: '三' },
  { en: 'Thu', zh: '四' },
  { en: 'Fri', zh: '五' },
  { en: 'Sat', zh: '六' },
  { en: 'Sun', zh: '日' }
]

export default function HomePage() {
  const [lang, setLangState] = useState<'en' | 'zh'>('en')
  const [currentSwiperIndex, setCurrentSwiperIndex] = useState(0)
  const [showHint, setShowHint] = useState(false)

  const [streakCount, setStreakCount] = useState(0)
  const [longestStreak, setLongestStreak] = useState(0)
  const [proStatus, setProStatus] = useState(false)
  const [proExpiryText, setProExpiryText] = useState('')
  const [dailyRounds, setDailyRounds] = useState(0)
  const [remainingFree, setRemainingFree] = useState(FREE_ROUNDS_PER_DAY)
  const [remainingAds, setRemainingAds] = useState(MAX_AD_ROUNDS_PER_DAY)
  const [isBonusReady, setIsBonusReady] = useState(false)

  const [wrongCount, setWrongCount] = useState(0)
  const [weeklyCount, setWeeklyCount] = useState(0)
  const [topicActivity, setTopicActivity] = useState<{ topic: string; count: number }[]>([])

  const [showReferral, setShowReferral] = useState(false)
  const [showQuota, setShowQuota] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [showAdConfirm, setShowAdConfirm] = useState(false)
  const [isLoadingAd, setIsLoadingAd] = useState(false)

  const logoTapCountRef = useRef(0)
  const logoTapTimeoutRef = useRef<any>(null)

  // Developer Pro toggle on 3 taps of brand title
  const handleLogoTap = () => {
    logoTapCountRef.current += 1
    if (logoTapTimeoutRef.current) clearTimeout(logoTapTimeoutRef.current)

    if (logoTapCountRef.current >= 3) {
      logoTapCountRef.current = 0
      const currentDev = getStorage('dev_pro_unlocked') === 'true' || getStorage('dev_pro_unlocked') === true
      const nextDev = !currentDev
      setStorage('dev_pro_unlocked', nextDev ? 'true' : 'false')
      if (nextDev) {
        setStorage('pro_expiry', new Date(Date.now() + 30 * 24 * 3600 * 1000).toISOString())
      } else {
        setStorage('pro_expiry', null)
      }
      refreshState()
      Taro.showToast({
        title: nextDev ? 'Developer Pro Unlocked 👑' : 'Developer Pro Reset',
        icon: 'none',
        duration: 2000
      })
    } else {
      logoTapTimeoutRef.current = setTimeout(() => {
        logoTapCountRef.current = 0
      }, 1000)
    }
  }

  const refreshState = () => {
    const currentLang = getLang() || 'en'
    setLangState(currentLang)
    setNavigationBarTitle({ title: i18n[currentLang]?.title || 'BrainActive' })

    const streak = getStreak()
    const storedLongest = parseInt(getStorage('longest_streak') || '0', 10)
    const longest = Math.max(storedLongest, streak)
    if (longest > storedLongest) {
      setStorage('longest_streak', String(longest))
    }
    setStreakCount(streak)
    setLongestStreak(longest)

    const usage = getDailyUsage()
    setDailyRounds(usage.roundsCompleted)

    const isProMember = checkIsPro()
    setProStatus(isProMember)

    const freeLeft = getRemainingFreeRounds()
    setRemainingFree(freeLeft)

    const adsLeft = Math.max(0, MAX_AD_ROUNDS_PER_DAY - usage.bonusRounds)
    setRemainingAds(adsLeft)

    const bonusAvailable = usage.bonusRounds > 0 && usage.roundsCompleted < (FREE_ROUNDS_PER_DAY + usage.bonusRounds)
    setIsBonusReady(bonusAvailable)

    const exp = getProExpiry() || getSubscriptionExpiry()
    if (exp) {
      setProExpiryText(new Date(exp).toLocaleDateString())
    }

    const wrongList = getWrongQuestions()
    setWrongCount(Array.isArray(wrongList) ? wrongList.length : 0)

    const history = getQuizHistory()
    if (Array.isArray(history)) {
      const weekAgo = Date.now() - 7 * 24 * 60 * 60 * 1000
      const recent = history.filter((a: any) => new Date(a.date).getTime() >= weekAgo)
      const totalWeeklyQuestions = recent.reduce((sum: number, a: any) => sum + (a.total || 5), 0)
      setWeeklyCount(totalWeeklyQuestions)

      const topicMap: Record<string, number> = {}
      recent.forEach((a: any) => {
        if (a.topic) topicMap[a.topic] = (topicMap[a.topic] || 0) + 1
      })
      setTopicActivity(
        Object.entries(topicMap)
          .sort((a, b) => b[1] - a[1])
          .slice(0, 4)
          .map(([topic, count]) => ({ topic, count }))
      )
    }
  }

  useLoad(() => {
    refreshState()
    setTimeout(() => {
      preloadAd()
    }, 2000)
  })

  useDidShow(() => {
    refreshState()
    setShowHint(true)
    setTimeout(() => setShowHint(false), 3000)

    try {
      getBrainActiveProgress(getDeviceId())
        .then(data => {
          if (data) {
            if (data.is_pro) setProStatus(true)
            if (data.streak_count) setStreakCount(data.streak_count)
          }
        })
        .catch(() => {})
    } catch {}
  })

  const currentStreakMessage = useMemo(() => {
    const sgtLogical = new Date(Date.now() + (8 - 5) * 60 * 60 * 1000)
    const dayIndex = Math.floor(sgtLogical.getTime() / 86400000) % STREAK_MESSAGES.length
    return STREAK_MESSAGES[dayIndex]
  }, [])

  const currentDayOfWeekIndex = useMemo(() => {
    const sgtLogical = new Date(Date.now() + (8 - 5) * 60 * 60 * 1000)
    const d = sgtLogical.getUTCDay()
    return d === 0 ? 6 : d - 1
  }, [])

  const t = i18n[lang] || i18n.en

  const isDailyRoundCompleted = !proStatus && remainingFree === 0 && !isBonusReady

  const usageSummaryText = useMemo(() => {
    if (proStatus) {
      return t.usage_pro
    }
    if (remainingFree > 0) {
      return t.usage_free
        .replace('{{free}}', String(remainingFree))
        .replace('{{s}}', remainingFree !== 1 ? 's' : '')
        .replace('{{ads}}', String(remainingAds))
    }
    if (isBonusReady) {
      return t.extra_practice_ready
    }
    if (remainingAds > 0) {
      return lang === 'en' ? `📺 ${remainingAds} Ad Unlock${remainingAds !== 1 ? 's' : ''} Remaining` : `📺 剩余 ${remainingAds} 次广告解锁机会`
    }
    return t.usage_all_done
  }, [proStatus, remainingFree, remainingAds, isBonusReady, lang, t])

  const motivationText = useMemo(() => {
    if (proStatus) {
      return lang === 'en' ? '✨ Unlimited Access Active' : '✨ 无限特训已激活'
    }
    if (isBonusReady) {
      return lang === 'en' ? '⚡ Bonus Round Ready to Start!' : '⚡ 额外挑战已就绪！'
    }
    if (remainingFree > 0) {
      return lang === 'en' ? '🎯 Ready for your daily thinking quest!' : '🎯 准备好开始今日思维挑战了吗？'
    }
    if (remainingAds > 0) {
      return lang === 'en' ? '🎬 Watch a short video to unlock more!' : '🎬 观看视频解锁新一轮！'
    }
    return lang === 'en' ? '🌙 Great job today! Back tomorrow for more.' : '🌙 今日挑战已完成，明天见！'
  }, [proStatus, isBonusReady, remainingFree, remainingAds, lang])

  const handleStartQuickTest = () => {
    if (!canStartPractice()) {
      setShowQuota(true)
      return
    }
    navigateTo({
      url: '/pages/quiz/index?mode=quick_test&origin=home'
    })
  }

  const handleWatchAdClick = () => {
    if (isLoadingAd) return
    if (proStatus) {
      navigateTo({ url: '/pages/quiz/index?mode=quick_test&origin=home' })
      return
    }
    if (isBonusReady) {
      navigateTo({ url: '/pages/quiz/index?mode=quick_test&origin=bonus' })
      return
    }
    if (remainingAds <= 0) {
      setShowQuota(true)
      return
    }
    setShowAdConfirm(true)
  }

  const handleConfirmAd = async () => {
    setShowAdConfirm(false)
    setIsLoadingAd(true)
    try {
      const success = await showRewardAd()
      setIsLoadingAd(false)
      if (success) {
        refreshState()
        Taro.showToast({
          title: lang === 'en' ? 'Bonus Round Unlocked! ⚡' : '额外挑战已解锁！⚡',
          icon: 'success'
        })
      }
    } catch (e) {
      setIsLoadingAd(false)
    }
  }

  const handleRetryWrong = () => {
    if (wrongCount === 0) return
    navigateTo({
      url: '/pages/quiz/index?mode=retry&origin=home'
    })
  }

  const handleOpenPro = () => {
    navigateTo({ url: '/pages/pro/index' })
  }

  const handleFeedback = () => {
    showModal({
      title: lang === 'en' ? 'BrainActive Feedback' : '意见反馈',
      content: lang === 'en'
        ? 'Have suggestions or found a question issue? Email us at pslehero@gmail.com'
        : '有任何建议或发现题目问题？欢迎发送邮件至 pslehero@gmail.com',
      showCancel: false
    })
  }

  const handleOpenWebsite = () => {
    if (typeof window !== 'undefined') {
      window.open('https://pslehero.org/', '_blank')
    }
  }

  const handleOpenGuide = () => {
    if (typeof window !== 'undefined') {
      window.open('https://pslehero.org/p3-high-ability-identification-guide.html', '_blank')
    }
  }

  return (
    <View className='home-viewport'>
      {/* Fixed Top Header */}
      <View className='hero-header-fixed'>
        <View className='hero-header'>
          <View className='top-school-badge'>
            <Text className='badge-text'>🏆 {t.curriculum_badge}</Text>
          </View>
          <View className='settings-entry' onClick={() => setShowSettings(true)}>
            <Text className='settings-icon'>⚙️</Text>
          </View>
          <View className='title-section'>
            <View className='hero-brand-mark' onClick={handleLogoTap}>
              <Text className='hero-brand-title'>{t.title}</Text>
            </View>
          </View>
        </View>

        {/* Daily Usage Summary Box */}
        <View className='usage-summary-box text-center'>
          <View className='usage-main-row'>
            <Text className='usage-text text-center'>{usageSummaryText}</Text>
          </View>
          <Text className='usage-motivation text-center'>{motivationText}</Text>
        </View>
      </View>

      {/* Main 2-Page Horizontal Swiper */}
      <Swiper
        className={`home-swiper home-swiper-page-${currentSwiperIndex}`}
        circular={false}
        indicatorDots={false}
        onChange={(e) => setCurrentSwiperIndex(e.detail.current)}
        duration={200}
      >
        {/* ================= PAGE 1: PRIMARY PRACTICE & PRO ================= */}
        <SwiperItem>
          <ScrollView className='home-page-scroll' scrollY>
            {/* Premium Streak Card */}
            <View className='premium-streak-container'>
              <View className='streak-card'>
                <View className='streak-card-top'>
                  <View className='streak-fire-wrap'>
                    <Text className='streak-fire-emoji'>🦸</Text>
                    <View className='streak-fire-glow' />
                  </View>
                  <View className='streak-info-main'>
                    <Text className='streak-title'>
                      {streakCount} {t.streak_title}
                    </Text>
                    <Text className='streak-sub'>
                      {lang === 'zh' ? currentStreakMessage.zh : currentStreakMessage.en}
                    </Text>
                  </View>
                  <View className='streak-best-box'>
                    <Text className='streak-best-label'>{t.longest_streak}</Text>
                    <Text className='streak-best-val'>
                      {longestStreak} {longestStreak === 1 ? t.day_unit : t.days_unit}
                    </Text>
                  </View>
                </View>

                {/* 7-Day Weekly Checkbox Row */}
                <View className='streak-week-row'>
                  {WEEK_DAYS.map((day, idx) => {
                    const isActive = streakCount > 0 && idx > currentDayOfWeekIndex - streakCount && idx <= currentDayOfWeekIndex
                    return (
                      <View key={idx} className='streak-day-col'>
                        <View className={`streak-day-dot ${isActive ? 'active' : ''}`}>
                          {isActive && <Text className='streak-check'>✓</Text>}
                        </View>
                        <Text className='streak-day-name'>{lang === 'en' ? day.en : day.zh}</Text>
                      </View>
                    )
                  })}
                </View>

                <View className='streak-goal-footer'>
                  <Text className='streak-goal-text'>
                    🎁 {t.next_goal} {Math.ceil((streakCount + 1) / 5) * 5} {t.days_unit}
                  </Text>
                </View>
              </View>
            </View>

            {/* Daily Practice Hero Card */}
            <View className='daily5-card'>
              {isDailyRoundCompleted ? (
                <View className='daily5-layout'>
                  <View className='daily5-right'>
                    <Text className='daily5-title-complete'>{t.daily_complete}</Text>
                    <Text className='daily5-subtitle'>{t.daily_complete_msg}</Text>
                    <View className='daily5-stats-row'>
                      <View className='daily5-stat'>
                        <Text className='daily5-stat-value'>{streakCount}</Text>
                        <Text className='daily5-stat-label'>{lang === 'en' ? 'Day Streak' : '连续天数'}</Text>
                      </View>
                      <View className='daily5-stat-divider' />
                      <View className='daily5-stat'>
                        <Text className='daily5-stat-value'>{weeklyCount}</Text>
                        <Text className='daily5-stat-label'>{lang === 'en' ? 'This Week' : '本周题数'}</Text>
                      </View>
                    </View>

                    {proStatus ? (
                      <View className='daily5-cta' onClick={handleStartQuickTest} style={{ marginTop: '12px' }}>
                        <Text className='daily5-cta-text'>{t.daily_continue}</Text>
                      </View>
                    ) : isBonusReady ? (
                      <View className='daily5-cta' onClick={handleWatchAdClick} style={{ marginTop: '12px' }}>
                        <Text className='daily5-cta-text'>{t.daily_start_bonus}</Text>
                      </View>
                    ) : remainingAds > 0 ? (
                      <View className='daily5-cta' onClick={handleWatchAdClick} style={{ marginTop: '12px' }}>
                        <Text className='daily5-cta-text'>{t.daily_continue_free}</Text>
                      </View>
                    ) : (
                      <View style={{ marginTop: '12px' }}>
                        <View className='daily5-status-note'>
                          <Text className='daily5-status-note-text'>{t.daily_come_back_tmr}</Text>
                        </View>
                        <View className='daily5-pro-prompt' onClick={handleOpenPro} style={{ marginTop: '10px' }}>
                          <Text className='daily5-pro-prompt-text'>{t.daily_upgrade_pro}</Text>
                        </View>
                      </View>
                    )}
                  </View>
                </View>
              ) : (
                <View className='daily5-layout'>
                  <View className='daily5-right'>
                    <Text className='daily5-title'>{t.daily_title}</Text>
                    <View className='daily5-meta-row'>
                      <View className='daily5-meta-item'>
                        <Text className='daily5-meta-text'>📝 5 {lang === 'en' ? 'Questions' : '道精选题'}</Text>
                      </View>
                      <View className='daily5-meta-item'>
                        <Text className='daily5-meta-text'>⏱️ 5–8 {lang === 'en' ? 'Mins' : '分钟'}</Text>
                      </View>
                    </View>
                    <Text className='daily5-subtitle'>{t.daily_specs}</Text>
                    <View className='daily5-cta' onClick={handleStartQuickTest}>
                      <Text className='daily5-cta-text'>{t.daily_cta}</Text>
                    </View>
                  </View>
                </View>
              )}
            </View>

            {/* BrainActive Pro Card */}
            <View className='pro-cta-container'>
              <View className={`pro-cta-card ${proStatus ? 'active' : ''}`} onClick={handleOpenPro}>
                <View className='pro-cta-content text-center'>
                  <Text className='pro-cta-title'>
                    {proStatus ? `👑 ${t.pro_active_title}` : `🚀 ${t.pro_title}`}
                  </Text>
                  <Text className='pro-cta-subtitle'>
                    {proStatus
                      ? (proExpiryText ? `${t.pro_active_sub} (Until ${proExpiryText})` : t.pro_active_sub)
                      : t.pro_sub}
                  </Text>
                </View>
                <View className='pro-cta-action-btn-wrapper'>
                  <View className='pro-cta-action-btn'>
                    <Text className='pro-cta-btn-text'>
                      {proStatus ? t.pro_active_cta : t.pro_upgrade_cta}
                    </Text>
                  </View>
                </View>
              </View>
            </View>

            <View className='footer-spacer' />
          </ScrollView>
        </SwiperItem>

        {/* ================= PAGE 2: PROGRESS, MISTAKES, HEURISTICS ================= */}
        <SwiperItem>
          <ScrollView className='home-page-scroll' scrollY>
            {/* Progress Journey Widget */}
            <View className='progress-section'>
              <Text className='progress-title'>{t.progress_title}</Text>

              {/* 3-Column Stats Grid */}
              <View className='progress-stats-grid'>
                <View className='progress-stat-col'>
                  <Text className='progress-stat-val'>{weeklyCount}</Text>
                  <Text className='progress-stat-lbl'>{t.progress_weekly}</Text>
                </View>
                <View className='progress-stat-col'>
                  <Text className='progress-stat-val'>{streakCount}</Text>
                  <Text className='progress-stat-lbl'>{lang === 'en' ? 'Streak' : '连胜天数'}</Text>
                </View>
                <View className='progress-stat-col'>
                  <Text className='progress-stat-val'>{wrongCount}</Text>
                  <Text className='progress-stat-lbl'>{t.progress_mistakes}</Text>
                </View>
              </View>

              {topicActivity.length > 0 ? (
                <View className='progress-topics'>
                  <Text className='progress-topics-title'>{t.progress_topics}</Text>
                  <View className='progress-topics-list'>
                    {topicActivity.map((item, idx) => (
                      <View key={idx} className='progress-topic-tag'>
                        <Text className='progress-topic-name'>{item.topic}</Text>
                        <Text className='progress-topic-count'>{item.count}x</Text>
                      </View>
                    ))}
                  </View>
                </View>
              ) : (
                <View className='progress-empty'>
                  <Text className='progress-empty-text'>{t.progress_empty}</Text>
                </View>
              )}
            </View>

            {/* Review Mistakes Card */}
            <View className={`retry-mistakes-section ${wrongCount === 0 ? 'disabled' : ''}`} onClick={handleRetryWrong}>
              <View className='retry-mistakes-card'>
                <Text className='retry-emoji'>🔄</Text>
                <View className='retry-text-stack'>
                  <Text className='retry-title'>{t.retry_wrong} ({wrongCount})</Text>
                  <Text className='retry-sub'>{t.retry_wrong_sub}</Text>
                </View>
              </View>
            </View>

            {/* Extra Practice / Ad Unlock Card */}
            <View
              className={`extra-practice-section ${!proStatus && !isBonusReady && remainingAds <= 0 ? 'disabled' : ''} ${isLoadingAd ? 'loading' : ''}`}
              onClick={handleWatchAdClick}
            >
              <View className='extra-practice-card'>
                <Text className='extra-practice-emoji'>{isLoadingAd ? '⏳' : isBonusReady ? '⚡' : '📺'}</Text>
                <View className='extra-practice-text-stack'>
                  <Text className='extra-practice-title'>
                    {proStatus
                      ? (lang === 'en' ? 'Unlimited Practice Active' : '无限特训已激活')
                      : isBonusReady
                        ? t.extra_practice_ready
                        : remainingAds <= 0
                          ? t.extra_practice_limit
                          : t.extra_practice}
                  </Text>
                  <Text className='extra-practice-sub'>
                    {proStatus
                      ? (lang === 'en' ? 'Practice as many rounds as you want!' : '随时畅享无限思维特训！')
                      : isBonusReady
                        ? t.extra_practice_ready_sub
                        : remainingAds <= 0
                          ? t.extra_practice_limit_sub
                          : t.extra_practice_sub}
                  </Text>
                </View>
                {isBonusReady && (
                  <View className='extra-practice-start-btn' onClick={(e) => { e.stopPropagation(); handleWatchAdClick() }}>
                    <Text>{lang === 'en' ? 'Start' : '开始'}</Text>
                  </View>
                )}
              </View>
            </View>

            {/* Invite Friends Card */}
            <View className='invite-friends-section' onClick={() => setShowReferral(true)}>
              <View className='invite-friends-card'>
                <Text className='invite-friends-emoji'>🎁</Text>
                <View className='invite-friends-text-stack'>
                  <Text className='invite-friends-title'>{t.referral_title}</Text>
                  <Text className='invite-friends-sub'>{t.referral_sub}</Text>
                </View>
              </View>
            </View>

            {/* BrainActive Thinking Heuristics */}
            <View className='tips-section'>
              <View className='tips-header'>
                <Text className='tips-title'>{t.tips_title}</Text>
              </View>
              <View className='tips-list'>
                {t.tips.map((tip, index) => (
                  <View className='tip-item' key={index}>
                    <Text className='tip-number'>0{index + 1}</Text>
                    <View className='tip-text-wrapper'>
                      <Text className='tip-link-title'>{tip.title}</Text>
                      <Text className='tip-text'>{tip.desc}</Text>
                    </View>
                  </View>
                ))}
              </View>

              {/* Hero Tip moved to "More from Hero" section below */}
            </View>

            {/* More from Hero: guide + related apps */}
            <View className='more-from-hero-section'>
              <Text className='more-hero-title'>{t.more_hero_title}</Text>
              {t.more_hero.map((item, idx) => (
                <View
                  key={idx}
                  className='more-hero-card'
                  onClick={() => {
                    const urls = [
                      'https://pslehero.org/p3-high-ability-identification-guide.html',
                      'https://play.google.com/store/apps/details?id=com.pslehero.app',
                      'https://play.google.com/store/apps/details?id=com.singaporeprimarymath.app'
                    ]
                    if (idx === 0) {
                      handleOpenGuide()
                      return
                    }
                    if (typeof window !== 'undefined') {
                      window.open(urls[idx], '_blank')
                    }
                  }}
                >
                  <Text className='more-hero-emoji'>{item.emoji}</Text>
                  <View className='more-hero-text'>
                    <Text className='more-hero-name'>{item.name}</Text>
                    <Text className='more-hero-sub'>{item.sub}</Text>
                  </View>
                  <Text className='more-hero-arrow'>›</Text>
                </View>
              ))}
            </View>

            {/* Footer */}
            <View className='footer'>
              <View className='feedback-link' onClick={handleFeedback}>
                <Text>{t.feedback}</Text>
              </View>
              <Text className='support-text'>{t.support_email}</Text>
              <View className='website-link' onClick={handleOpenWebsite}>
                <Text className='website-text'>{t.website}</Text>
              </View>
            </View>

            <View className='footer-spacer' />
          </ScrollView>
        </SwiperItem>
      </Swiper>

      {/* Floating Bottom Pagination Indicator */}
      <View className={`pagination-dots ${showHint ? 'swipe-hint-active' : ''}`}>
        {currentSwiperIndex === 1 && (
          <Text className={`swipe-hint-arrow left ${showHint ? 'swipe-hint-active' : ''}`}>‹</Text>
        )}
        <Text className='swipe-helper-text'>
          {currentSwiperIndex === 0
            ? (lang === 'en' ? 'Swipe for progress' : '滑动查看进步')
            : (lang === 'en' ? 'Swipe back to practice' : '滑回开始练习')}
        </Text>
        <View className={`dot ${currentSwiperIndex === 0 ? 'active' : ''}`} />
        <View className={`dot ${currentSwiperIndex === 1 ? 'active' : ''}`} />
        {currentSwiperIndex === 0 && (
          <Text className={`swipe-hint-arrow right ${showHint ? 'swipe-hint-active' : ''}`}>›</Text>
        )}
      </View>

      {/* Modals */}
      <ReferralModal
        isOpen={showReferral}
        onClose={() => setShowReferral(false)}
        onSuccess={refreshState}
      />
      <QuotaOverlay
        isOpen={showQuota}
        onClose={() => setShowQuota(false)}
        onUnlocked={refreshState}
      />
      <SettingsModal
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
        onLangChanged={refreshState}
      />
      {showAdConfirm && (
        <ConfirmModal
          isOpen={showAdConfirm}
          title={t.ad_confirm_title}
          content={t.ad_confirm_content}
          confirmText={t.ad_confirm_ok}
          cancelText={t.ad_confirm_cancel}
          onConfirm={handleConfirmAd}
          onCancel={() => setShowAdConfirm(false)}
        />
      )}
    </View>
  )
}
