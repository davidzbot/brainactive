/**
 * Google Play In-App Review — isolated, production-safe helper.
 *
 * Design constraints (do not weaken without review):
 * - Prompt shape: Quick Test completion on the Result page ONLY. Never called
 *   from question answering, navigation, submission, scoring, or loading paths.
 * - New users AND updating users start at zero: the counter key below never
 *   existed before, so historical usage alone can never trigger a request.
 * - A request being INITIATED is all we record (Play never reports whether the
 *   dialog was shown or a review submitted). Cooldown starts at initiation.
 * - Every failure path resolves silently; the learning flow is never blocked.
 */
import { Capacitor } from '@capacitor/core'
import { InAppReview } from '@capacitor-community/in-app-review'
import { getStorage, setStorage } from './storage'

// Questions completed in NEW Quick Test sessions since the (re)start of the
// current cycle. 10 questions ~= 2 x 5-question Quick Tests.
const REVIEW_QUESTIONS_THRESHOLD = 10
const REVIEW_COUNT_KEY = 'inapp_review_questions'
// ISO timestamp of the last INITIATED review request. Absent = never requested.
const REVIEW_TS_KEY = 'lastReviewRequestAt'

// Guards against double-counting when the Result page effect re-fires for the
// same session (same result signature). Module lifetime only, never persisted.
let lastHandledResultKey: string | null = null

export interface ReviewStore {
  get: (key: string) => any
  set: (key: string, value: any) => void
}

export interface ReviewRequest {
  /** Quick Test mode value seen on this Result page (e.g. 'quick_test'). */
  mode?: string
  /** Total questions of the just-finished session. */
  totalQuestions?: number | string
  /** True only for a NEW qualifying Quick Test session (never retry/pro). */
  isQuickMode: boolean
  /** Opaque per-session signature (score|total|time). */
  resultKey: string
  store?: ReviewStore
  nowMs?: number
  requestReview?: () => Promise<unknown>
}

function defaultStore(): ReviewStore {
  return {
    get: (key: string) => getStorage(key),
    set: (key: string, value: any) => setStorage(key, value),
  }
}

/** Native Play review request. Resolves silently on every failure path. */
export async function requestPlayReview(): Promise<void> {
  try {
    if (Capacitor.getPlatform() !== 'android') return
    await InAppReview.requestReview()
  } catch {
    // Play quotas, debug builds, missing plugin, unsupported device:
    // the learning flow continues untouched.
  }
}

/**
 * Add whole calendar months with month-end clamping
 * (e.g. Nov 30 + 3 months = Feb 28/29, not Mar 2/3).
 */
export function addCalendarMonths(fromMs: number, months: number): number {
  const d = new Date(fromMs)
  const day = d.getDate()
  const target = new Date(d.getFullYear(), d.getMonth() + months, 1)
  const lastDay = new Date(target.getFullYear(), target.getMonth() + 1, 0).getDate()
  target.setDate(Math.min(day, lastDay))
  target.setHours(d.getHours(), d.getMinutes(), d.getSeconds(), d.getMilliseconds())
  return target.getTime()
}

function readCount(store: ReviewStore): number {
  const raw = Number(store.get(REVIEW_COUNT_KEY))
  if (!Number.isFinite(raw) || raw < 0) return 0
  return Math.floor(raw)
}

function readLastRequestMs(store: ReviewStore): number | null {
  const raw = store.get(REVIEW_TS_KEY)
  if (raw === null || raw === undefined || raw === '') return null
  const ms = new Date(raw).getTime()
  return Number.isFinite(ms) ? ms : null
}

/**
 * Maybe count this Result page toward review eligibility and, when due,
 * initiate ONE native review request (fire-and-forget safe).
 *
 * Returns a status string for diagnostics/tests; never throws.
 * Possible outcomes: 'skipped-mode' | 'duplicate' | 'counted' | 'requested' | 'cooldown' | 'error'.
 */
export function maybeRequestInAppReview(req: ReviewRequest): string {
  try {
    if (!req.isQuickMode) return 'skipped-mode'
    if (req.resultKey && req.resultKey === lastHandledResultKey) return 'duplicate'
    if (req.resultKey) lastHandledResultKey = req.resultKey

    const store = req.store || defaultStore()
    const nowMs = typeof req.nowMs === 'number' ? req.nowMs : Date.now()
    const answered = Math.max(0, Math.floor(Number(req.totalQuestions) || 0))
    const next = readCount(store) + answered
    store.set(REVIEW_COUNT_KEY, next)
    if (next < REVIEW_QUESTIONS_THRESHOLD) return 'counted'

    const last = readLastRequestMs(store)
    if (last !== null && nowMs < addCalendarMonths(last, 3)) return 'cooldown'

    // Initiate: record timestamp + reset cycle BEFORE the async native call.
    // Google Play independently decides whether to show anything.
    store.set(REVIEW_TS_KEY, new Date(nowMs).toISOString())
    store.set(REVIEW_COUNT_KEY, 0)
    const run = req.requestReview || requestPlayReview
    void Promise.resolve()
      .then(() => run())
      .catch(() => {})
    return 'requested'
  } catch {
    // Unexpected internal error: never surface it; treat as not-eligible so
    // the Result page flow continues untouched.
    return 'error'
  }
}
