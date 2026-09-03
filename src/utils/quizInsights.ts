export interface QuizHistoryEntry {
  score?: number
  total?: number
  topic?: string
  topicBreakdown?: Array<{
    topic?: string
    correct?: number
    total?: number
  }>
}

export interface TopicPerformance {
  topic: string
  correct: number
  total: number
  accuracy: number
}

export const WEAK_AREA_MIN_QUESTIONS = 3
export const WEAK_AREA_MAX_ACCURACY = 70

const NON_ACTIONABLE_TOPICS = new Set([
  'mixed',
  'general',
  'general thinking',
  'unknown',
  'unspecified'
])

export function aggregateQuizTopicPerformance(history: QuizHistoryEntry[]): TopicPerformance[] {
  const topicMap: Record<string, { correct: number; total: number }> = {}

  history.forEach(entry => {
    if (Array.isArray(entry.topicBreakdown) && entry.topicBreakdown.length > 0) {
      entry.topicBreakdown.forEach(breakdown => {
        const topic = String(breakdown.topic || '').trim() || 'Mixed'
        if (!topicMap[topic]) topicMap[topic] = { correct: 0, total: 0 }
        topicMap[topic].correct += Number(breakdown.correct) || 0
        topicMap[topic].total += Number(breakdown.total) || 0
      })
      return
    }

    const topic = String(entry.topic || 'General Thinking').trim() || 'General Thinking'
    if (!topicMap[topic]) topicMap[topic] = { correct: 0, total: 0 }
    topicMap[topic].correct += Number(entry.score) || 0
    topicMap[topic].total += Number(entry.total) || 5
  })

  return Object.entries(topicMap)
    .map(([topic, values]) => ({
      topic,
      correct: values.correct,
      total: values.total,
      accuracy: values.total > 0 ? Math.round((values.correct / values.total) * 100) : 0
    }))
    .sort((a, b) => b.accuracy - a.accuracy)
}

export function findMeaningfulWeakArea(history: QuizHistoryEntry[]): TopicPerformance | null {
  return aggregateQuizTopicPerformance(history)
    .filter(item =>
      item.total >= WEAK_AREA_MIN_QUESTIONS &&
      item.accuracy < WEAK_AREA_MAX_ACCURACY &&
      !NON_ACTIONABLE_TOPICS.has(item.topic.toLowerCase())
    )
    .sort((a, b) => a.accuracy - b.accuracy || b.total - a.total)[0] || null
}
