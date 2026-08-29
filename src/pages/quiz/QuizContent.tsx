import React, { useState, useEffect, useRef } from 'react'
import { View, Text, Button, Image, ScrollView } from '@tarojs/components'
import Taro, { useRouter } from '@tarojs/taro'
import {
  getDeviceId,
  saveWrongQuestion,
  saveQuizAttempt,
  incrementDailyRounds,
  markStreakActive,
  getLang,
  getWrongQuestions
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

// Curated 5-Question Fallback Round for Singapore Primary 3 Thinking Skills
const CURATED_FALLBACK_QUESTIONS = [
  {
    id: 'BA_P3_0001',
    domain: 'numerical_reasoning',
    topic: 'Numerical Thinking',
    skill: '1.3',
    archetype: 'weight_system',
    level: 'Think',
    question: 'A triangle and a square together weigh 11 kg. A square and a circle together weigh 9 kg. A triangle and a circle together weigh 8 kg. Which shape is the heaviest?',
    options: [
      { id: 'A', text: 'Triangle' },
      { id: 'B', text: 'Square' },
      { id: 'C', text: 'Circle' },
      { id: 'D', text: 'Cannot tell' }
    ],
    answer: 'B',
    explanation: 'Add all three pair equations: 2 × (Triangle + Square + Circle) = 11 + 9 + 8 = 28 kg. Therefore, Triangle + Square + Circle = 14 kg.\n- Circle = 14 − 11 = 3 kg\n- Triangle = 14 − 9 = 5 kg\n- Square = 14 − 8 = 6 kg.\nSquare (6 kg) is the heaviest.',
    reasoning: 'Balance & substitution system: Sum all pair equations to find the grand total, then subtract each pair to find each unknown shape.'
  },
  {
    id: 'BA_P3_0002',
    domain: 'logical_reasoning',
    topic: 'Logical Reasoning',
    skill: '2.1',
    archetype: 'order_deduction',
    level: 'Think',
    question: 'Four students (Alice, Ben, Chloe, Dan) ran a race. Alice finished before Ben. Chloe finished after Alice but before Dan. Ben was not the last. Who finished in 1st place?',
    options: [
      { id: 'A', text: 'Ben' },
      { id: 'B', text: 'Chloe' },
      { id: 'C', text: 'Alice' },
      { id: 'D', text: 'Dan' }
    ],
    answer: 'C',
    explanation: 'Let us list the order clues:\n1. Alice is ahead of Ben (Alice > Ben).\n2. Chloe is between Alice and Dan (Alice > Chloe > Dan).\nSince Alice is ahead of both Ben and Chloe, and no one is ahead of Alice, Alice must have finished 1st!',
    reasoning: 'Positional deduction: Chain inequalities together (Alice > Chloe > Dan and Alice > Ben) to find the unique leader.'
  },
  {
    id: 'BA_P3_0003',
    domain: 'pattern_abstract',
    topic: 'Pattern & Abstract',
    skill: '3.2',
    archetype: 'increasing_gaps',
    level: 'Think',
    question: 'Look at the number pattern: 1, 2, 4, 7, 11, 16, ( ? ). What number comes next in the sequence?',
    options: [
      { id: 'A', text: '20' },
      { id: 'B', text: '21' },
      { id: 'C', text: '22' },
      { id: 'D', text: '23' }
    ],
    answer: 'C',
    explanation: 'Examine the differences between consecutive terms:\n- 1 + 1 = 2\n- 2 + 2 = 4\n- 4 + 3 = 7\n- 7 + 4 = 11\n- 11 + 5 = 16\nThe added gap increases by 1 each time (+1, +2, +3, +4, +5, ...). The next gap is +6, so 16 + 6 = 22.',
    reasoning: 'Second-order arithmetic sequence: Analyze the sequence of differences between terms.'
  },
  {
    id: 'BA_P3_0004',
    domain: 'spatial_reasoning',
    topic: 'Visual & Spatial',
    skill: '4.1',
    archetype: 'cube_net',
    level: 'Think',
    question: 'A standard cube has faces numbered 1 to 6. In a flat cross-shaped cube net, Face 2 is in the center, Face 1 is to its left, Face 3 is to its right, Face 4 is above, and Face 5 is below with Face 6 attached to Face 5. Which face is directly opposite to Face 4 when folded into a cube?',
    options: [
      { id: 'A', text: 'Face 2' },
      { id: 'B', text: 'Face 5' },
      { id: 'C', text: 'Face 6' },
      { id: 'D', text: 'Face 1' }
    ],
    answer: 'B',
    explanation: 'When a cube net is folded, faces in a straight row or column that have exactly one face between them end up opposite to each other. In the vertical column (Face 4, Face 2, Face 5), Face 4 and Face 5 are separated by Face 2, so Face 4 is opposite Face 5.',
    reasoning: 'Cube net rule: Along any straight strip of squares, faces separated by one square fold into opposite sides.'
  },
  {
    id: 'BA_P3_0005',
    domain: 'verbal_reasoning',
    topic: 'Verbal Reasoning',
    skill: '5.1',
    archetype: 'instrument_purpose',
    level: 'Think',
    question: 'COMPASS is to DIRECTION as CLOCK is to ( ? ). Choose the word that completes the analogy best.',
    options: [
      { id: 'A', text: 'Battery' },
      { id: 'B', text: 'Alarm' },
      { id: 'C', text: 'Time' },
      { id: 'D', text: 'Hands' }
    ],
    answer: 'C',
    explanation: 'A compass is an instrument designed specifically to measure/indicate direction. Similarly, a clock is an instrument designed specifically to measure/indicate time.',
    reasoning: 'Functional relationship analogy: Instrument is paired with the physical dimension it measures.'
  }
]

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

  const [firstWrongSelections, setFirstWrongSelections] = useState<Record<string, string>>({})
  const [skippedQuestions, setSkippedQuestions] = useState<Set<string>>(new Set())
  const [swipeTranslateX, setSwipeTranslateX] = useState(0)
  const [swipeOpacity, setSwipeOpacity] = useState(1)
  const [isTransitioning, setIsTransitioning] = useState(false)
  const touchStartX = useRef(0)
  const touchStartY = useRef(0)

  const timerRef = useRef<any>(null)
  const questionStartTime = useRef(Date.now())

  // Android hardware back button handler
  useEffect(() => {
    const handleHardwareBack = () => {
      if (showAskHero) {
        setShowAskHero(false)
        return true
      }
      if (showExitConfirm) {
        setShowExitConfirm(false)
        return true
      }
      setShowExitConfirm(true)
      return true
    };

    (globalThis as any)._hardwareBackHandler = handleHardwareBack
    return () => {
      if ((globalThis as any)._hardwareBackHandler === handleHardwareBack) {
        (globalThis as any)._hardwareBackHandler = null
      }
    }
  }, [showAskHero, showExitConfirm])

  // Load questions
  useEffect(() => {
    async function loadQuiz() {
      try {
        setLoading(true)

        if (mode === 'retry') {
          const wrongList = getWrongQuestions()
          if (wrongList && wrongList.length > 0) {
            setQuestions(wrongList.slice(0, 5))
            setLoading(false)
            questionStartTime.current = Date.now()
            return
          }
        }

        const parsedLimit = router.params.limit ? parseInt(router.params.limit, 10) : (mode === 'quick_test' ? 5 : 10)
        const fetched = await getBrainActiveQuestions({
          mode,
          topic: topicFilter,
          level: levelFilter,
          limit: parsedLimit
        })

        if (fetched && fetched.length > 0) {
          setQuestions(fetched)
        } else {
          // Filter fallback questions by topic/level if specified
          let pool = [...CURATED_FALLBACK_QUESTIONS]
          if (topicFilter && topicFilter !== 'All Thinking Topics' && topicFilter !== 'All') {
            const filtered = pool.filter(q =>
              q.topic?.toLowerCase().includes(topicFilter.toLowerCase()) ||
              q.domain?.toLowerCase().includes(topicFilter.toLowerCase())
            )
            if (filtered.length > 0) pool = filtered
          }
          if (levelFilter && levelFilter !== 'All' && levelFilter !== 'Mixed') {
            const filtered = pool.filter(q => q.level?.toLowerCase() === levelFilter.toLowerCase())
            if (filtered.length > 0) pool = filtered
          }
          setQuestions(pool.slice(0, parsedLimit))
        }
        setLoading(false)
        questionStartTime.current = Date.now()
      } catch (err: any) {
        console.error('Failed to load quiz, using fallback round:', err)
        setQuestions(CURATED_FALLBACK_QUESTIONS)
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
  }, [mode, topicFilter, levelFilter, router.params.limit])

  const currentQ = questions[currentIndex]

  // Touch handlers for swipe left (next) and swipe right (prev)
  const handleTouchStart = (e: any) => {
    if (loading || isTransitioning) return
    if (e.touches && e.touches[0]) {
      touchStartX.current = e.touches[0].pageX
      touchStartY.current = e.touches[0].pageY
    }
  }

  const handleTouchMove = (e: any) => {
    if (loading || isTransitioning) return
    if (!e.touches || !e.touches[0]) return

    const deltaX = e.touches[0].pageX - touchStartX.current
    const deltaY = e.touches[0].pageY - touchStartY.current

    if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 20) {
      const moveX = deltaX * 0.45
      setSwipeTranslateX(moveX)
      setSwipeOpacity(Math.max(0.75, 1 - Math.abs(moveX) / 800))
    }
  }

  const handleTouchEnd = (e: any) => {
    if (loading || isTransitioning) return
    if (!e.changedTouches || !e.changedTouches[0]) {
      setSwipeTranslateX(0)
      setSwipeOpacity(1)
      return
    }

    const deltaX = e.changedTouches[0].pageX - touchStartX.current
    const deltaY = e.changedTouches[0].pageY - touchStartY.current

    // Trigger swipe if horizontal drag > 55px and dominantly horizontal
    if (Math.abs(deltaX) > 55 && Math.abs(deltaX) > Math.abs(deltaY) * 1.3) {
      if (deltaX < 0) {
        // Swipe Left -> Next question
        triggerNavigation('next')
      } else {
        // Swipe Right -> Prev question / exit prompt
        triggerNavigation('prev')
      }
    } else {
      setSwipeTranslateX(0)
      setSwipeOpacity(1)
    }
  }

  const handleSkipQuestion = () => {
    if (isAnswerSubmitted || isTransitioning) return
    const timeSpentMs = Date.now() - questionStartTime.current

    // Record skip as an incorrect attempt so it doesn't count toward the score
    const skipAttempt = {
      question_id: currentQ.id,
      selected_answer: '',
      is_correct: false,
      skipped: true,
      time_spent_ms: timeSpentMs,
      topic: currentQ.topic || currentQ.domain,
      level: currentQ.level,
      retry_count: 0,
      first_try_correct: false
    }
    setAttempts(prev => [...prev, skipAttempt])
    setSkippedQuestions(prev => new Set([...prev, currentQ.id]))

    Taro.showToast({
      title: lang === 'zh' ? '已跳过此题' : 'Question skipped',
      icon: 'none',
      duration: 1000
    })

    setIsTransitioning(true)
    setSwipeTranslateX(120)
    setSwipeOpacity(0)
    setTimeout(() => {
      if (currentIndex < questions.length - 1) {
        setCurrentIndex(i => i + 1)
        setSelectedOptionId(null)
        setIsAnswerSubmitted(false)
        questionStartTime.current = Date.now()
      } else {
        // Last question skipped — finish the quiz
        if (timerRef.current) clearInterval(timerRef.current)
        const allAttempts = [...attempts, skipAttempt]
        const correctCount = allAttempts.filter(a => a.is_correct).length
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
        submitBrainActiveAttempt({
          user_id: getDeviceId(),
          attempts: allAttempts,
          mode
        }).catch(e => console.warn('Attempt submit notice:', e))
        Taro.redirectTo({
          url: `/pages/result/index?score=${correctCount}&total=${questions.length}&time=${secondsSpent}`
        })
        return
      }
      setSwipeTranslateX(0)
      setSwipeOpacity(1)
      setIsTransitioning(false)
    }, 180)
  }

  const triggerNavigation = (direction: 'next' | 'prev') => {
    if (isTransitioning) return
    if (direction === 'next') {
      if (!isAnswerSubmitted) {
        setSwipeTranslateX(0)
        setSwipeOpacity(1)
        Taro.showToast({
          title: lang === 'zh' ? '请先选择一个答案 💡' : 'Please select an answer first! 💡',
          icon: 'none'
        })
        return
      }
      setIsTransitioning(true)
      setSwipeTranslateX(-120)
      setSwipeOpacity(0)
      setTimeout(() => {
        handleNext()
        setSwipeTranslateX(0)
        setSwipeOpacity(1)
        setIsTransitioning(false)
      }, 180)
    } else {
      // Swipe RIGHT → skip current question (don't go back, don't corrupt score)
      setSwipeTranslateX(0)
      setSwipeOpacity(1)
      handleSkipQuestion()
    }
  }

  const handleSelectOption = (optId: string) => {
    if (isAnswerSubmitted) return

    // Check if clicked the same option that already failed on 1st try
    if (firstWrongSelections[currentQ.id] === optId) {
      Taro.showToast({
        title: lang === 'zh' ? '请尝试选择其他选项' : 'Try another selection',
        icon: 'none'
      })
      return
    }

    const isCorrect = optId === currentQ.answer
    const timeSpentMs = Date.now() - questionStartTime.current
    const hasFailedBefore = firstWrongSelections[currentQ.id] !== undefined

    // 2nd Try Chance Handling:
    // If wrong on FIRST try, give the student a 2nd chance!
    if (!isCorrect && !hasFailedBefore) {
      setFirstWrongSelections(prev => ({
        ...prev,
        [currentQ.id]: optId
      }))

      // Save question to wrong questions bank for future review
      saveWrongQuestion(currentQ)

      // Show encouraging feedback
      Taro.showToast({
        title: lang === 'zh' ? '加油！再试一次，你一定可以！💪' : 'Good try! Try again, you can do it! 💪',
        icon: 'none',
        duration: 2000
      })
      return
    }

    // Otherwise: Correct on 1st try, Correct on 2nd try, or Wrong on 2nd try
    setSelectedOptionId(optId)
    setIsAnswerSubmitted(true)

    const attempt = {
      question_id: currentQ.id,
      selected_answer: optId,
      is_correct: isCorrect,
      time_spent_ms: timeSpentMs,
      topic: currentQ.topic || currentQ.domain,
      level: currentQ.level,
      retry_count: hasFailedBefore ? 1 : 0,
      first_try_correct: isCorrect && !hasFailedBefore
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

      // Only append the current question's attempt if it hasn't been recorded yet
      // (it won't be in attempts if the user answered it but it's the last question)
      const alreadyRecorded = attempts.some(a => a.question_id === currentQ.id)
      const finalAttempts = alreadyRecorded
        ? attempts
        : [...attempts, {
            question_id: currentQ.id,
            selected_answer: selectedOptionId,
            is_correct: selectedOptionId === currentQ.answer,
            time_spent_ms: Date.now() - questionStartTime.current,
            topic: currentQ.topic,
            level: currentQ.level,
            retry_count: 0,
            first_try_correct: selectedOptionId === currentQ.answer
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

  const handleConfirmExit = () => {
    setShowExitConfirm(false)
    Taro.reLaunch({ url: '/pages/home/index' }).catch(() => {
      Taro.navigateBack().catch(() => {})
    })
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
        <Button className="btn-back" onClick={handleConfirmExit}>Back to Home</Button>
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
      {/* Top Header with Exit, Home, Meta Badges & Timer */}
      <View className="quiz-header">
        <View className="nav-actions-left">
          <View className="exit-btn" onClick={handleExit}>
            <Text className="exit-icon">✕</Text>
          </View>
          <View className="home-top-btn" onClick={handleExit}>
            <Text className="home-top-icon">⌂</Text>
          </View>
        </View>

        {/* Topic, Level and Q number */}
        <View className="meta-badges">
          <Text className="topic-badge">{currentQ.topic || 'Reasoning'}</Text>
          <Text className="dot-sep">•</Text>
          <Text className="level-badge">{currentQ.level || 'Think'}</Text>
          <Text className="dot-sep">•</Text>
          <Text className="q-num-badge">{currentIndex + 1} / {questions.length}</Text>
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

      {/* Scrollable Question Content with Swipe Gesture Support */}
      <ScrollView
        scrollY
        className="question-scroll-body"
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        style={{
          transform: `translateX(${swipeTranslateX}px)`,
          opacity: swipeOpacity,
          transition: isTransitioning ? 'all 0.18s ease-out' : 'none'
        }}
      >
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
            const isFirstWrongTry = firstWrongSelections[currentQ.id] === opt.id

            let optionClass = 'option-card'
            if (isAnswerSubmitted) {
              if (isCorrect) optionClass += ' correct'
              else if (isSelected && !isCorrect) optionClass += ' wrong'
            } else if (isFirstWrongTry) {
              optionClass += ' first-wrong-try'
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

        {/* Action Row: Ask Hero AI Button + Skip + Bottom Home Link */}
        <View className="quiz-action-row">
          <AskHeroButton
            lang={lang}
            onClick={() => setShowAskHero(true)}
          />
          {!isAnswerSubmitted && (
            <View className="skip-btn" onClick={handleSkipQuestion}>
              <Text className="skip-btn-text">{lang === 'zh' ? '跳过 ›' : 'Skip ›'}</Text>
            </View>
          )}
          <View className="global-home-bottom-link" onClick={handleExit}>
            <Text className="bottom-home-icon">⌂</Text>
          </View>
        </View>

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

      {/* Exit Confirmation Modal */}
      <ConfirmModal
        isOpen={showExitConfirm}
        title="Leave this practice round?"
        content="Your progress in this 5-question round will not be saved."
        confirmText="Leave to Home"
        cancelText="Stay"
        onConfirm={handleConfirmExit}
        onCancel={() => setShowExitConfirm(false)}
      />
    </View>
  )
}

