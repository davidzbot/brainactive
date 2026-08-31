import React, { useState, useRef, useEffect } from 'react'
import { View, Text, Button, Textarea, ScrollView } from '@tarojs/components'
import { askBrainActiveHero, AskHeroResult } from '@/utils/request'
import AskHeroMessage from '../AskHeroMessage'
import './index.scss'

interface Props {
  questionId: string
  questionData?: any
  studentAnswer: string
  lang?: 'en' | 'zh'
  hasVisualQuestion?: boolean
  visible?: boolean
  onClose: () => void
  onReportQuestion?: () => void
}

type Mode = 'why_wrong' | 'hint' | 'explain' | 'ask'

interface ChatItem {
  role: 'user' | 'assistant'
  content: string
}

const MODE_OPTIONS: { key: Mode; icon: string; labelEn: string; labelZh: string }[] = [
  { key: 'why_wrong', icon: '🤔', labelEn: 'Why was I wrong?', labelZh: '我为什么错了？' },
  { key: 'hint', icon: '💡', labelEn: 'Give me a hint', labelZh: '给我一个提示' },
  { key: 'explain', icon: '📖', labelEn: 'Explain step-by-step', labelZh: '详细讲解' },
  { key: 'ask', icon: '✍️', labelEn: 'Ask my own question', labelZh: '问我想问的' },
]

export default function AskHeroPanel({
  questionId,
  questionData,
  studentAnswer,
  lang = 'en',
  hasVisualQuestion = false,
  visible = true,
  onClose,
  onReportQuestion,
}: Props) {
  const isZh = lang === 'zh'
  const hasAnswer = Boolean(studentAnswer.trim())

  const strings = {
    title: isZh ? '问问 Hero AI' : 'Ask Hero AI',
    subtitle: isZh
      ? 'Hero AI 陪你一步一步探索这道思维题的解题思路。'
      : 'Hero AI guides you step-by-step through Singapore P3 thinking skills.',
    visualNote: isZh ? 'Hero AI 也能看这道题里的图形。' : 'Hero AI can also look at the diagram in this question.',
    modePrompt: isZh ? '你想怎样学习这道题？' : 'How would you like Hero AI to help?',
    thinking: isZh ? 'Hero AI 正在思考…' : 'Hero AI is thinking…',
    followupPlaceholder: isZh ? '问问 Hero 别的思考问题…' : 'Ask Hero another thinking question…',
    send: isZh ? '发送' : 'Send',
    sending: isZh ? '思考中…' : 'Sending…',
    retry: isZh ? '再试一次' : 'Try again',
    close: isZh ? '关闭' : 'Close',
    failed: isZh ? '😴 Hero AI 正在休息，请稍后再试。' : '😴 Hero AI is taking a quick rest. Please try again shortly.',
    startOver: isZh ? '重新开始' : 'Start over',
    report: isZh ? '反馈题目问题' : 'Report question issue',
  }

  const [chat, setChat] = useState<ChatItem[]>([])
  const [mode, setMode] = useState<Mode | null>(null)
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [failed, setFailed] = useState(false)
  const [lastPayload, setLastPayload] = useState<any>(null)
  const scrollRef = useRef<any>(null)
  const busyRef = useRef(false)

  useEffect(() => {
    if (scrollRef.current && scrollRef.current.scrollTo) {
      scrollRef.current.scrollTo({ scrollTop: 99999, animated: true })
    }
  }, [chat, loading])

  const runAskHero = async (payload: any) => {
    if (busyRef.current) return
    busyRef.current = true
    setLoading(true)
    setFailed(false)
    setLastPayload(payload)

    try {
      const res: AskHeroResult = await askBrainActiveHero(payload)
      if (res.ok && res.message) {
        setChat(prev => [...prev, { role: 'assistant', content: res.message || '' }])
      } else {
        setFailed(true)
      }
    } catch {
      setFailed(true)
    } finally {
      busyRef.current = false
      setLoading(false)
    }
  }

  const handleModeSelect = (m: Mode) => {
    if (busyRef.current) return
    setMode(m)
    setInput('')
    if (m === 'ask') return

    const userBubble: ChatItem = {
      role: 'user',
      content: isZh
        ? (MODE_OPTIONS.find(o => o.key === m)?.labelZh || m)
        : (MODE_OPTIONS.find(o => o.key === m)?.labelEn || m),
    }
    setChat(prev => [...prev, userBubble])
    const payload = {
      question_id: questionId,
      question_data: questionData,
      mode: m,
      student_answer: studentAnswer,
      history: [...chat, userBubble].map(({ role, content }) => ({ role, content })),
    }
    runAskHero(payload)
  }

  const handleAskSubmit = () => {
    if (busyRef.current) return
    const text = input.trim()
    if (!text) return
    const userBubble: ChatItem = { role: 'user', content: text }
    setInput('')
    setChat(prev => [...prev, userBubble])
    const payload = {
      question_id: questionId,
      question_data: questionData,
      mode: 'ask' as Mode,
      student_answer: studentAnswer,
      student_question: text,
      history: [...chat, userBubble].map(({ role, content }) => ({ role, content })),
    }
    runAskHero(payload)
  }

  const handleRetry = () => {
    if (lastPayload && !busyRef.current) runAskHero(lastPayload)
  }

  const handleStartOver = () => {
    setChat([])
    setMode(null)
    setInput('')
    setFailed(false)
    setLastPayload(null)
  }

  if (!visible) return null

  const showModePicker = chat.length === 0 && mode === null
  const showInitialAskInput = mode === 'ask' && chat.length === 0
  const showFollowupInput = chat.length > 0 && !loading

  return (
    <View className='ask-hero-overlay' onClick={onClose} onTouchStart={(e) => e.stopPropagation()} onTouchMove={(e) => e.stopPropagation()} onTouchEnd={(e) => e.stopPropagation()}>
      <View className='ask-hero-content' onClick={(e) => e.stopPropagation()} onTouchStart={(e) => e.stopPropagation()} onTouchMove={(e) => e.stopPropagation()} onTouchEnd={(e) => e.stopPropagation()}>
        {/* Header */}
        <View className='ask-hero-header'>
          <View className='ask-hero-title-wrap'>
            <View className='ask-hero-title-mark'>
              <Text className='mark-letter'>H</Text>
            </View>
            <View className='title-box'>
              <Text className='ask-hero-title'>{strings.title}</Text>
              <Text className='ask-hero-desc'>{strings.subtitle}</Text>
              {hasVisualQuestion && (
                <Text className='ask-hero-visual-note'>🖼️ {strings.visualNote}</Text>
              )}
            </View>
          </View>
          <View className='ask-hero-close' onClick={onClose}>✕</View>
        </View>

        {/* Scrollable Chat / Mode Picker */}
        <ScrollView className='ask-hero-body' scrollY ref={scrollRef} scrollWithAnimation>
          {showModePicker && (
            <View className='ask-hero-mode-picker'>
              <Text className='ask-hero-mode-prompt'>{strings.modePrompt}</Text>
              {MODE_OPTIONS.map(option => (
                <View
                  key={option.key}
                  className='ask-hero-mode-option'
                  onClick={() => handleModeSelect(option.key)}
                >
                  <Text className='ask-hero-mode-icon'>{option.icon}</Text>
                  <Text className='ask-hero-mode-text'>
                    {option.key === 'why_wrong' && !hasAnswer
                      ? (isZh ? '帮我开始这道题' : 'Help me get started')
                      : (isZh ? option.labelZh : option.labelEn)}
                  </Text>
                </View>
              ))}
            </View>
          )}

          {chat.length > 0 && (
            <View className='ask-hero-chat'>
              {chat.map((item, idx) => (
                <AskHeroMessage key={idx} role={item.role} content={item.content} lang={lang} />
              ))}
              {loading && (
                <View className='ask-hero-loading'>
                  <View className='ask-hero-loading-dots'>
                    <View className='dot' /><View className='dot' /><View className='dot' />
                  </View>
                  <Text className='ask-hero-loading-text'>{strings.thinking}</Text>
                </View>
              )}
              {failed && !loading && (
                <View className='ask-hero-failed'>
                  <Text className='ask-hero-failed-text'>{strings.failed}</Text>
                  <Button className='ask-hero-failed-retry' onClick={handleRetry}>{strings.retry}</Button>
                </View>
              )}
            </View>
          )}

          {showInitialAskInput && (
            <View className='ask-hero-followup'>
              <Textarea
                className='ask-hero-input'
                placeholder={strings.followupPlaceholder}
                value={input}
                maxlength={500}
                onInput={(e) => setInput(e.detail.value)}
              />
              <Button className='ask-hero-send' onClick={handleAskSubmit} disabled={!input.trim()}>
                {strings.send}
              </Button>
            </View>
          )}

          {showFollowupInput && (
            <View className='ask-hero-followup'>
              <Textarea
                className='ask-hero-input'
                placeholder={strings.followupPlaceholder}
                value={input}
                maxlength={500}
                onInput={(e) => setInput(e.detail.value)}
              />
              <Button className='ask-hero-send' onClick={handleAskSubmit} disabled={!input.trim()}>
                {loading ? strings.sending : strings.send}
              </Button>
            </View>
          )}
        </ScrollView>

        {/* Footer */}
        <View className='ask-hero-footer'>
          <View className='ask-hero-footer-left'>
            {chat.length > 0 && (
              <View className='ask-hero-start-over' onClick={handleStartOver}>
                <Text className='ask-hero-start-over-text'>{strings.startOver}</Text>
              </View>
            )}
            {onReportQuestion && (
              <View className='ask-hero-report' onClick={onReportQuestion}>
                <Text>{strings.report}</Text>
              </View>
            )}
          </View>
          <View className='ask-hero-close-footer' onClick={onClose}>
            <Text>{strings.close}</Text>
          </View>
        </View>
      </View>
    </View>
  )
}
