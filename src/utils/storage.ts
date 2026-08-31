/**
 * BrainActive Storage Abstraction Layer
 * Adapts Math Hero storage architecture with isolated 'ba_' namespace.
 */

const isBrowser = typeof window !== 'undefined'
const BA_PREFIX = 'ba_'

type StorageListener = (key: string, value: any) => void
const listeners = new Map<string, Set<StorageListener>>()

export function onStorageChange(key: string, listener: StorageListener): () => void {
  if (!listeners.has(key)) listeners.set(key, new Set())
  listeners.get(key)!.add(listener)
  return () => listeners.get(key)?.delete(listener)
}

export function offStorageChange(key: string, listener: StorageListener): void {
  listeners.get(key)?.delete(listener)
}

function notifyStorageChange(key: string, value: any): void {
  listeners.get(key)?.forEach(fn => fn(key, value))
}

function deserialize(value: string): any {
  try {
    return JSON.parse(value)
  } catch {
    return value
  }
}

export function getStorage(key: string): any {
  if (isBrowser) {
    const value = localStorage.getItem(BA_PREFIX + key)
    if (value !== null) return deserialize(value)
    return null
  }
  return null
}

export function setStorage(key: string, value: any): void {
  if (isBrowser) {
    if (value === null || value === undefined) {
      localStorage.removeItem(BA_PREFIX + key)
      notifyStorageChange(key, null)
      return
    }
    const serialized = typeof value === 'string' ? value : JSON.stringify(value)
    localStorage.setItem(BA_PREFIX + key, serialized)
    notifyStorageChange(key, value)
  }
}

export function removeStorage(key: string): void {
  if (isBrowser) {
    localStorage.removeItem(BA_PREFIX + key)
    notifyStorageChange(key, null)
  }
}

// -------------------------------------------------------------
// Stable Device ID / User ID
// -------------------------------------------------------------
export function getDeviceId(): string {
  let id = getStorage('device_id')
  if (!id) {
    id = 'ba_usr_' + Math.random().toString(36).substring(2, 12) + '_' + Date.now().toString(36)
    setStorage('device_id', id)
  }
  return id
}

export function getUserId(): string {
  return getDeviceId()
}

// -------------------------------------------------------------
// SGT Calendar Day (Singapore Time = UTC+8)
// -------------------------------------------------------------
export function getLogicalSgtDay(): string {
  const d = new Date()
  const utc = d.getTime() + d.getTimezoneOffset() * 60000
  const sgt = new Date(utc + 8 * 3600000)
  return sgt.toISOString().split('T')[0]
}

// -------------------------------------------------------------
// Daily Usage & Free Rounds Limit
// Model: 1 free round + up to 3 rewarded-ad rounds (max 4 rounds / 20 questions per day)
// Sequence: 1 free -> 2 ad -> 3 ad -> 4 ad -> stop (Pro = unlimited)
// -------------------------------------------------------------
export const FREE_ROUNDS_PER_DAY = 1
export const MAX_AD_ROUNDS_PER_DAY = 3
export const MAX_TOTAL_DAILY_ROUNDS = FREE_ROUNDS_PER_DAY + MAX_AD_ROUNDS_PER_DAY

export interface DailyUsage {
  date: string
  roundsCompleted: number
  bonusRounds: number // Max 3 per day
  totalQuestions: number
}

export function getDailyUsage(): DailyUsage {
  const today = getLogicalSgtDay()
  const stored = getStorage('daily_usage')
  if (!stored || stored.date !== today) {
    const fresh: DailyUsage = {
      date: today,
      roundsCompleted: 0,
      bonusRounds: 0,
      totalQuestions: 0
    }
    setStorage('daily_usage', fresh)
    return fresh
  }
  return stored
}

export function incrementDailyRounds(questionCount = 5): DailyUsage {
  const usage = getDailyUsage()
  usage.roundsCompleted += 1
  usage.totalQuestions += questionCount
  setStorage('daily_usage', usage)
  return usage
}

export function canWatchAdForRound(): boolean {
  if (isPro()) return false
  const usage = getDailyUsage()
  return usage.bonusRounds < MAX_AD_ROUNDS_PER_DAY
}

export function unlockBonusRound(): DailyUsage {
  const usage = getDailyUsage()
  if (usage.bonusRounds < MAX_AD_ROUNDS_PER_DAY) {
    usage.bonusRounds += 1
    setStorage('daily_usage', usage)
  }
  return usage
}

export function canStartPractice(): boolean {
  if (isPro()) return true
  const usage = getDailyUsage()
  const allowedRounds = FREE_ROUNDS_PER_DAY + usage.bonusRounds
  return usage.roundsCompleted < allowedRounds
}

export function getRemainingFreeRounds(): number {
  if (isPro()) return 999
  const usage = getDailyUsage()
  const totalAllowed = FREE_ROUNDS_PER_DAY + usage.bonusRounds
  return Math.max(0, totalAllowed - usage.roundsCompleted)
}

export function isDailyMaxReached(): boolean {
  if (isPro()) return false
  const usage = getDailyUsage()
  return usage.roundsCompleted >= MAX_TOTAL_DAILY_ROUNDS
}

// -------------------------------------------------------------
// Streak Tracking
// -------------------------------------------------------------
export interface StreakState {
  streak: number
  lastActiveDate: string
}

export function getStreak(): number {
  const state: StreakState = getStorage('streak_state') || { streak: 0, lastActiveDate: '' }
  const today = getLogicalSgtDay()
  if (!state.lastActiveDate) return 0
  
  const lastDate = new Date(state.lastActiveDate)
  const currDate = new Date(today)
  const diffDays = Math.round((currDate.getTime() - lastDate.getTime()) / (1000 * 3600 * 24))
  
  if (diffDays <= 1) {
    return state.streak
  }
  return 0 // Streak broken if skipped a day
}

export function markStreakActive(): number {
  const today = getLogicalSgtDay()
  const state: StreakState = getStorage('streak_state') || { streak: 0, lastActiveDate: '' }
  
  if (state.lastActiveDate === today) {
    return state.streak // already counted today
  }
  
  if (!state.lastActiveDate) {
    state.streak = 1
  } else {
    const lastDate = new Date(state.lastActiveDate)
    const currDate = new Date(today)
    const diffDays = Math.round((currDate.getTime() - lastDate.getTime()) / (1000 * 3600 * 24))
    if (diffDays === 1) {
      state.streak += 1
    } else {
      state.streak = 1
    }
  }
  
  state.lastActiveDate = today
  setStorage('streak_state', state)
  return state.streak
}

// -------------------------------------------------------------
// Pro Status & Entitlements
// -------------------------------------------------------------
export function isPro(): boolean {
  // Check direct Pro expiry
  const proExp = getStorage('pro_expiry')
  if (proExp) {
    const expTime = new Date(proExp).getTime()
    if (expTime > Date.now()) return true
  }
  
  // Check the locally observed Google Play subscription state first. The native
  // purchase bridge may omit expiryTimeMillis for an otherwise valid purchase.
  if (getSubscriptionActive()) return true

  // Check subscription expiry
  const subExp = getStorage('subscription_expiry')
  if (subExp) {
    const expTime = new Date(subExp).getTime()
    if (expTime > Date.now()) return true
  }
  
  return false
}

export function setProExpiry(dateStr: string | null): void {
  setStorage('pro_expiry', dateStr)
}

export function getProExpiry(): string | null {
  return getStorage('pro_expiry')
}

export function setSubscriptionExpiry(dateStr: string | null): void {
  setStorage('subscription_expiry', dateStr)
}

export function getSubscriptionExpiry(): string | null {
  return getStorage('subscription_expiry')
}

export function setSubscriptionActive(active: boolean): void {
  setStorage('subscription_active', active ? 'true' : 'false')
}

export function getSubscriptionActive(): boolean {
  return getStorage('subscription_active') === 'true'
}

// -------------------------------------------------------------
// Wrong Questions (Review Mistakes Bank)
// -------------------------------------------------------------
export function saveWrongQuestion(q: any): void {
  const list: any[] = getStorage('wrong_questions') || []
  if (!list.some(item => item.id === q.id)) {
    list.unshift(q)
    setStorage('wrong_questions', list.slice(0, 50)) // cap at 50 recent
  }
}

export function getWrongQuestions(): any[] {
  return getStorage('wrong_questions') || []
}

export function clearWrongQuestions(): void {
  removeStorage('wrong_questions')
}

// -------------------------------------------------------------
// Quiz History
// -------------------------------------------------------------
export function saveQuizAttempt(attempt: {
  date: string
  score: number
  total: number
  topic?: string
  level?: string
  timeSpentSec: number
}): void {
  const history: any[] = getStorage('quiz_history') || []
  history.unshift(attempt)
  setStorage('quiz_history', history.slice(0, 30))
}

export function getQuizHistory(): any[] {
  return getStorage('quiz_history') || []
}

// -------------------------------------------------------------
// Referral State
// -------------------------------------------------------------
export function getReferralCode(): string {
  let code = getStorage('referral_code')
  if (!code) {
    code = getDeviceId().slice(-6).toUpperCase()
    setStorage('referral_code', code)
  }
  return code
}

export function setReferralCode(code: string): void {
  setStorage('referral_code', code)
}

// -------------------------------------------------------------
// Language (EN / ZH)
// -------------------------------------------------------------
export function getLang(): 'en' | 'zh' {
  return (getStorage('lang') as 'en' | 'zh') || 'en'
}

export function setLang(lang: 'en' | 'zh'): void {
  setStorage('lang', lang)
}