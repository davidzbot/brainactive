import React, { useState, useEffect, useRef } from 'react'
import { View, Text, Button, Image, ScrollView } from '@tarojs/components'
import Taro, { useRouter } from '@tarojs/taro'
import {
  getDeviceId,
  saveWrongQuestion,
  saveQuizAttempt,
  incrementDailyRounds,
  markStreakActive,
  getLang
} from '@/utils/storage'
import {
  getBrainActiveQuestions,
  submitBrainActiveAttempt,
  getBrainActiveAssetUrl
} from '@/utils/request'
import ConfirmModal from '@/components/ConfirmModal'
import AskHeroButton from '@/components/AskHero/AskHeroButton'
import AskHeroPanel from '@/components/AskHero/AskHeroPanel'
import './index.scss'

export default function QuizContent() {
  const router = useRouter()
  const mode = (router.params.mode as any) || 'quick_test'
  const topicFilter = router.params.topic || ''
  const levelFilter = router.params.level || ''
  const lang = getLang() || 'en'

  const [loading, setLoading] = useState(true)
  const [questions, setQuestions] = useState<any[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [selectedOptionId, setSelectedOptionId] = useState<string | null>(null)
  const [isAnswerSubmitted, setIsAnswerSubmitted] = useState(false)
  const [attempts, setAttempts] = useState<any[]>([])
  const [secondsSpent, setSecondsSpent] = useState(0)
  const [showExitConfirm, setShowExitConfirm] = useState(false)
  const [showAskHero, setShowAskHero] = useState(false)

  const timerRef = useRef<any>(null)
  const questionStartTime = useRef(Date.now())

  // Load questions
  useEffect(() => {
    async function loadQuiz() {
      try {
        setLoading(true)
        const limit = mode === 'quick_test' ? 5 : 10
        const fetched = await getBrainActiveQuestions({
          mode,
          topic: topicFilter,
          level: levelFilter,
          limit
        })

        if (fetched && fetched.length > 0) {
          setQuestions(fetched)
        } else {
          // Local fallback candidate sample if offline
          setQuestions([
            {
              id: 'BA_P3_0001',
              domain: 'numerical_reasoning',
              topic: 'Numerical Thinking',
              skill: '1.3',
              archetype: 'weight_system',
              level: 'Think',
              question: 'A triangle and a square together weigh 11 kg. A square and a circle together weigh 9 kg. A triangle and a circle together weigh 8 kg. Which shape is the heaviest?',
              options: [
                { id: 'A', text: 'triangle' },
                { id: 'B', text: 'square' },
                { id: 'C', text: 'circle' },
                { id: 'D', text: 'cannot tell' }
              ],
              answer: 'B',
              explanation: 'Add all three pair-weights: 2 × (tri + sq + circ) = 11 + 9 + 8 = 28 kg, so all three total 14 kg. Circle = 14 − 11 = 3, Triangle = 14 − 9 = 5, Square = 14 − 8 = 6 kg. Square (6 kg) is the heaviest.',
              reasoning: 'Solving a 3-variable balance system by summing pairs and subtracting.'
            }
          ])
        }
        setLoading(false)
        questionStartTime.current = Date.now()
      } catch (err: any) {
        console.error('Failed to load quiz:', err)
        setLoading(false)
      }
    }

    loadQuiz()

    timerRef.current = setInterval(() => {
      setSecondsSpent(s => s + 1)
    }, 1000)

    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [mode, topicFilter, levelFilter])

  const currentQ = questions[currentIndex]

  const handleSelectOption = (optId: string) => {
    if (isAnswerSubmitted) return
    setSelectedOptionId(optId)
    setIsAnswerSubmitted(true)

    const isCorrect = optId === currentQ.answer
    const timeSpentMs = Date.now() - questionStartTime.current

    const attempt = {
      question_id: currentQ.id,
      selected_answer: optId,
      is_correct: isCorrect,
      time_spent_ms: timeSpentMs,
      topic: currentQ.topic || currentQ.domain,
      level: currentQ.level
    }

    setAttempts(prev => [...prev, attempt])

    if (!isCorrect) {
      saveWrongQuestion(currentQ)
    }
  }

  const handleNext = async () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(i => i + 1)
      setSelectedOptionId(null)
      setIsAnswerSubmitted(false)
      questionStartTime.current = Date.now()
    } else {
      // Finished Quiz
      if (timerRef.current) clearInterval(timerRef.current)

      const finalAttempts = attempts.length === questions.length
        ? attempts
        : [...attempts, {
            question_id: currentQ.id,
            selected_answer: selectedOptionId,
            is_correct: selectedOptionId === currentQ.answer,
            time_spent_ms: Date.now() - questionStartTime.current,
            topic: currentQ.topic,
            level: currentQ.level
          }]
      const correctCount = finalAttempts.filter(a => a.is_correct).length

      // Save local streak and round
      if (mode === 'quick_test') {
        incrementDailyRounds(questions.length)
        markStreakActive()
      }

      saveQuizAttempt({
        date: new Date().toISOString(),
        score: correctCount,
        total: questions.length,
        topic: topicFilter || 'General Thinking',
        level: levelFilter || 'Mixed',
        timeSpentSec: secondsSpent
      })

      // Submit to backend
      try {
        await submitBrainActiveAttempt({
          user_id: getDeviceId(),
          attempts: finalAttempts,
          mode
        })
      } catch (e) {
        console.warn('Attempt submit background sync notice:', e)
      }

      Taro.redirectTo({
        url: `/pages/result/index?score=${correctCount}&total=${questions.length}&time=${secondsSpent}`
      })
    }
  }

  const handleExit = () => {
    setShowExitConfirm(true)
  }

  if (loading) {
    return (
      <View className="quiz-container loading-state">
        <Text className="loading-text">Preparing your thinking quest<Text className="loading-dots">...</Text></Text>
      </View>
    )
  }

  if (!currentQ) {
    return (
      <View className="quiz-container empty-state">
        <Text className="empty-text">No questions available right now. Try again shortly.</Text>
        <Button className="btn-back" onClick={() => Taro.navigateBack()}>Back to Home</Button>
      </View>
    )
  }

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60)
    const s = secs % 60
    return `${m}:${s < 10 ? '0' : ''}${s}`
  }

  return (
    <View className="quiz-container">
      {/* Top Header */}
      <View className="quiz-header">
        <View className="exit-btn" onClick={handleExit}>
          <Text className="exit-icon">✕</Text>
        </View>

        {/* Topic, Level and Q number */}
        <View className="meta-badges">
          <Text className="topic-badge">{currentQ.topic || 'Reasoning'}</Text>
          <Text className="dot-sep">•</Text>
          <Text className="level-badge">{currentQ.level || 'Think'}</Text>
          <Text className="dot-sep">•</Text>
          <Text className="q-num-badge">{currentIndex + 1}/{questions.length}</Text>
        </View>

        <View className="timer-badge">
          <Text className="timer-text">⏱ {formatTime(secondsSpent)}</Text>
        </View>
      </View>

      {/* Progress Bar */}
      <View className="progress-bar-container">
        <View
          className="progress-fill"
          style={{ width: `${((currentIndex + 1) / questions.length) * 100}%` }}
        />
      </View>

      {/* Scrollable Question Content */}
      <ScrollView scrollY className="question-scroll-body">
        <View className="question-card">
          <Text className="question-text">{currentQ.question}</Text>

          {/* Visual Asset if required */}
          {currentQ.visual_required && currentQ.image_path && (
            <Image
              className="question-image"
              src={getBrainActiveAssetUrl(currentQ.image_path) || ''}
              mode="aspectFit"
            />
          )}
        </View>

        {/* Options List */}
        <View className="options-container">
          {currentQ.options.map((opt: any) => {
            const isSelected = selectedOptionId === opt.id
            const isCorrect = opt.id === currentQ.answer

            let optionClass = 'option-card'
            if (isAnswerSubmitted) {
              if (isCorrect) optionClass += ' correct'
              else if (isSelected && !isCorrect) optionClass += ' wrong'
            } else if (isSelected) {
              optionClass += ' selected'
            }

            return (
              <View
                key={opt.id}
                className={optionClass}
                onClick={() => handleSelectOption(opt.id)}
              >
                <View className="opt-id-circle">
                  <Text className="opt-id-text">{opt.id}</Text>
                </View>
                <Text className="opt-text">{opt.text}</Text>
              </View>
            )
          })}
        </View>

        {/* Ask Hero AI Tutor Button */}
        <AskHeroButton
          lang={lang}
          onClick={() => setShowAskHero(true)}
        />

        {/* Explanation and Reasoning Reveal */}
        {isAnswerSubmitted && (
          <View className="explanation-card">
            <View className="exp-header">
              <Text className="exp-badge">
                {selectedOptionId === currentQ.answer
                  ? '✅ Well done! Here\'s the reasoning:'
                  : 'Not this time — here\'s how to think it through:'}
              </Text>
            </View>
            <Text className="exp-body">{currentQ.explanation}</Text>
            {currentQ.reasoning && (
              <View className="reasoning-box">
                <Text className="reasoning-label">💡 Thinking Strategy:</Text>
                <Text className="reasoning-text">{currentQ.reasoning}</Text>
              </View>
            )}
          </View>
        )}
      </ScrollView>

      {/* Ask Hero AI Interactive Panel */}
      <AskHeroPanel
        questionId={currentQ.id}
        studentAnswer={selectedOptionId || ''}
        lang={lang}
        hasVisualQuestion={Boolean(currentQ.visual_required || currentQ.image_path)}
        visible={showAskHero}
        onClose={() => setShowAskHero(false)}
      />

      {/* Bottom Action Footer */}
      {isAnswerSubmitted && (
        <View className="bottom-action-bar">
          <Button className="btn-next-action" onClick={handleNext}>
            {currentIndex < questions.length - 1 ? 'Continue →' : 'See My Results →'}
          </Button>
        </View>
      )}

      {/* Exit Confirmation */}
      <ConfirmModal
        isOpen={showExitConfirm}
        title="Leave this round?"
        content="Your progress in this practice round will not be saved."
        confirmText="Leave"
        cancelText="Stay"
        onConfirm={() => Taro.navigateBack()}
        onCancel={() => setShowExitConfirm(false)}
      />
    </View>
  )
}
