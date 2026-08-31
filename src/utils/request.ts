/**
 * BrainActive API Request Layer
 * Reuses Math Hero request architecture adapted strictly for BrainActive endpoints.
 * Completely isolated from MathHero/PSLE backend tables and functions.
 */

import Taro from '@tarojs/taro'
import { getDeviceId } from './storage'

const SUPABASE_URL = 'https://mqpunjvdrkqvionsjosl.supabase.co'
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1xcHVuanZkcmtxdmlvbnNqb3NsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY0NTk5MTYsImV4cCI6MjA5MjAzNTkxNn0.65Yda6PICedefQLGex5OuS1IOFNeJaHgBuG3mGfoI3s'
const BRAINACTIVE_ASSETS_BUCKET = 'brainactive-assets'

export function getBrainActiveAssetUrl(imagePath?: string | null): string | null {
  if (!imagePath || !imagePath.trim()) return null
  let cleanPath = imagePath.trim().replace(/^\/+/, '')
  const bucketPrefix = `${BRAINACTIVE_ASSETS_BUCKET}/`
  if (cleanPath.startsWith(bucketPrefix)) {
    cleanPath = cleanPath.slice(bucketPrefix.length)
  }
  const encodedPath = cleanPath.split('/').map(segment => encodeURIComponent(segment)).join('/')
  return `${SUPABASE_URL}/storage/v1/object/public/${BRAINACTIVE_ASSETS_BUCKET}/${encodedPath}`
}

export interface RequestOptions {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  header?: Record<string, string>
  timeout?: number
}

export async function request<T = any>(options: RequestOptions): Promise<any> {
  const fullUrl = options.url.startsWith('http') 
    ? options.url 
    : `${SUPABASE_URL}${options.url}`

  const defaultHeaders = {
    'Content-Type': 'application/json',
    'apikey': SUPABASE_ANON_KEY,
    'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
    'x-device-id': getDeviceId()
  }

  try {
    const res = await Taro.request({
      url: fullUrl,
      method: options.method || 'GET',
      data: options.data,
      header: { ...defaultHeaders, ...(options.header || {}) },
      timeout: options.timeout || 10000
    })

    if (res.statusCode >= 200 && res.statusCode < 300) {
      return res.data
    }
    throw new Error(res.data?.error?.message || `HTTP ${res.statusCode}`)
  } catch (err: any) {
    console.error(`[BrainActive API] Error on ${fullUrl}:`, err.message)
    throw err
  }
}

// 1. Fetch BrainActive Questions
export async function getBrainActiveQuestions(params: {
  mode?: 'quick_test' | 'pro_practice' | 'retry'
  topic?: string
  level?: string
  limit?: number
  ids?: string[]
}): Promise<any[]> {
  const query = new URLSearchParams()
  if (params.mode) query.set('mode', params.mode)
  if (params.topic) query.set('topic', params.topic)
  if (params.level) query.set('level', params.level)
  if (params.limit) query.set('limit', String(params.limit))
  if (params.ids && params.ids.length > 0) query.set('ids', params.ids.join(','))

  const url = `/functions/v1/brainactive-get-questions?${query.toString()}`
  const res = await request({ url, method: 'GET' })
  return res?.data || []
}

// 2. Submit BrainActive Attempt
export async function submitBrainActiveAttempt(payload: {
  user_id: string
  attempts: Array<{
    question_id: string
    selected_answer: string
    is_correct: boolean
    time_spent_ms?: number
    topic?: string
    level?: string
  }>
  session_id?: string
  mode?: string
}): Promise<any> {
  const url = '/functions/v1/brainactive-submit-attempt'
  const res = await request({ url, method: 'POST', data: payload })
  return res?.data || null
}

// 3. Get BrainActive Progress & Entitlement
export async function getBrainActiveProgress(userId: string): Promise<any> {
  const url = `/functions/v1/brainactive-get-progress?user_id=${encodeURIComponent(userId)}`
  const res = await request({ url, method: 'GET' })
  return res?.data || null
}

// 4. Apply BrainActive Referral Code
export async function applyBrainActiveReferral(userId: string, referralCode: string): Promise<any> {
  const url = '/functions/v1/brainactive-apply-referral'
  const res = await request({
    url,
    method: 'POST',
    data: { user_id: userId, referral_code: referralCode }
  })
  return res?.data || null
}

// 5. Ask Hero AI Tutor
export interface AskHeroPayload {
  question_id: string
  question_data?: any
  mode: 'why_wrong' | 'hint' | 'explain' | 'ask'
  student_answer?: string
  student_question?: string
  history?: Array<{ role: 'user' | 'assistant'; content: string }>
}

export type BrainActiveQuestionIssueType = 'question' | 'answer' | 'explanation' | 'image' | 'other'

export async function reportBrainActiveQuestionIssue(payload: {
  question_id: string
  issue_type: BrainActiveQuestionIssueType
  detail?: string
}): Promise<any> {
  return request({
    url: '/functions/v1/brainactive-report-question',
    method: 'POST',
    data: payload,
  })
}

export interface AskHeroResult {
  ok: boolean
  message?: string
  reason?: string
}

export async function askBrainActiveHero(payload: AskHeroPayload): Promise<AskHeroResult> {
  try {
    const res = await request({
      url: '/functions/v1/brainactive-ask-hero',
      method: 'POST',
      data: payload,
      timeout: 30000
    })
    return res?.data || res || { ok: false, reason: 'NO_DATA' }
  } catch (err: any) {
    console.error('[Ask Hero AI Error]', err)
    return {
      ok: true,
      message: "💡 Here's a thinking tip: Look carefully at the relationships between parts of the question. Try testing each option step-by-step!"
    }
  }
}
