/**
 * Storage abstraction layer - replaces wx storage APIs
 * Usage: import { getStorage, setStorage } from '@/utils/storage'
 */

const isBrowser = typeof window !== 'undefined'

/**
 * Get value from storage
 * Handles both JSON strings and plain strings properly
 */
export function getStorage(key: string): any {
  if (isBrowser) {
    const value = localStorage.getItem(key)
    if (value) {
      try {
        return JSON.parse(value)
      } catch {
        // Return plain string if not JSON
        return value
      }
    }
    return null
  }
  // Node/server fallback (for SSR)
  return null
}

/**
 * Set value to storage
 * Automatically handles serialization for arrays/objects
 */
export function setStorage(key: string, value: any): void {
  if (isBrowser) {
    // Handle null/undefined by removing the key
    if (value === null || value === undefined) {
      localStorage.removeItem(key)
      return
    }
    // Serialize arrays/objects, keep strings as-is for simplicity
    const serialized = typeof value === 'string' ? value : JSON.stringify(value)
    localStorage.setItem(key, serialized)
  }
}

/**
 * Remove item from storage
 */
export function removeStorage(key: string): void {
  if (isBrowser) {
    localStorage.removeItem(key)
  }
}

/**
 * Clear all storage
 */
export function clearStorage(): void {
  if (isBrowser) {
    localStorage.clear()
  }
}

/**
 * Get or generate a persistent device_id (alias for user_id on Android)
 */
export function getDeviceId(): string {
  return getUserId()
}

/**
 * Reset device_id for testing (Debug Only)
 */
export function resetDeviceId(): string {
  removeStorage('user_id')
  return getUserId()
}

/**
 * Get user_id (Standardized for Android monetization)
 */
export function getUserId(): string {
  let userId = getStorage('user_id')
  if (!userId) {
    // Generate a UUID-v4 like string
    userId = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0
      const v = c == 'x' ? r : (r & 0x3 | 0x8)
      return v.toString(16)
    })
    setStorage('user_id', userId)
  }
  return userId
}

/**
 * Get language preference
 */
export function getLang(): string | null {
  return getStorage('lang')
}

/**
 * Set language preference
 */
export function setLang(lang: string): void {
  setStorage('lang', lang)
}