/**
 * BrainActive Common Utils - Migrated from Mini Program
 */

import Taro, { setNavigationBarTitle } from '@tarojs/taro'
import { getStorage, setStorage } from './storage'

/**
 * Safely set navigation bar title
 */
export function setSafeTitle(title: string): void {
  try {
    if (typeof setNavigationBarTitle === 'function') {
      setNavigationBarTitle({ title })
    } else if (Taro && typeof Taro.setNavigationBarTitle === 'function') {
      Taro.setNavigationBarTitle({ title })
    } else if (typeof document !== 'undefined') {
      document.title = title
    }
  } catch {
    if (typeof document !== 'undefined') {
      document.title = title
    }
  }
}

/**
 * Ad Unlock Logic:
 * - Each mode playable 1 time per day for free.
 * - Watching 1 ad unlocks ALL modes for 24 hours (unlimited play).
 */

export function isAdUnlocked(): boolean {
  try {
    const unlockUntil = getStorage('ad_unlock_until')
    if (!unlockUntil) return false
    return Date.now() < unlockUntil
  } catch {
    return false
  }
}

export function unlockAllModes(): void {
  try {
    const expiry = Date.now() + 24 * 60 * 60 * 1000 // 24 hours
    setStorage('ad_unlock_until', expiry)
  } catch (e) {
    console.error('Failed to save unlock status', e)
  }
}

export function getDailyUsage(mode: string): number {
  const usage = getStorage('daily_usage') || {}
  const today = formatDate(new Date())
  if (usage.date !== today) {
    return 0
  }
  return usage[mode] || 0
}

export function incrementDailyUsage(mode: string): void {
  const usage = getStorage('daily_usage') || {}
  const today = formatDate(new Date())
  if (usage.date !== today) {
    usage.date = today
    // Reset all modes
    usage.easy = 0
    usage.normal = 0
    usage.pro = 0
  }
  usage[mode] = (usage[mode] || 0) + 1
  setStorage('daily_usage', usage)
}

export function canPlayMode(mode: string): boolean {
  if (isAdUnlocked()) return true
  return getDailyUsage(mode) < 1
}

// Deprecated: isProUnlocked, unlockPro
export function isProUnlocked(): boolean {
  return isAdUnlocked()
}

export function unlockPro(): void {
  unlockAllModes()
}

export function parseDateSafe(dateStr: string | null): Date | null {
  if (!dateStr) return null
  const parts = dateStr.split('-')
  if (parts.length === 3) {
    return new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]))
  }
  return new Date(dateStr.replace(/-/g, '/'))
}

export function formatDate(date: Date): string {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}`
}