import { useEffect, useRef, useState } from 'react'
import { View, Text, Button, Textarea } from '@tarojs/components'
import { reportBrainActiveQuestionIssue, BrainActiveQuestionIssueType } from '@/utils/request'
import './index.scss'

interface Props {
  questionId: string
  lang: 'en' | 'zh'
  onClose: () => void
}

const ISSUE_OPTIONS: Array<{ key: BrainActiveQuestionIssueType; labelEn: string; labelZh: string }> = [
  { key: 'question', labelEn: 'Question is wrong', labelZh: '题目有误' },
  { key: 'answer', labelEn: 'Answer is wrong', labelZh: '答案有误' },
  { key: 'explanation', labelEn: 'Explanation is wrong', labelZh: '解析有误' },
  { key: 'image', labelEn: 'Image is wrong', labelZh: '图片有误' },
  { key: 'other', labelEn: 'Something else', labelZh: '其他' },
]

const stopTouch = (event: any) => {
  event?.stopPropagation?.()
}

export default function ReportQuestionModal({ questionId, lang, onClose }: Props) {
  const [selectedKey, setSelectedKey] = useState<BrainActiveQuestionIssueType | null>(null)
  const [detail, setDetail] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [submitFailed, setSubmitFailed] = useState(false)
  const [needsDetail, setNeedsDetail] = useState(false)
  const closeTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const isZh = lang === 'zh'

  const strings = {
    title: isZh ? '反馈题目问题' : 'Report question issue',
    subtitle: isZh ? '这道题有什么问题？' : 'What seems to be wrong with this question?',
    placeholder: isZh ? '告诉我们你注意到的内容…' : 'Tell us what you noticed…',
    needsDetail: isZh ? '请再告诉我们一些内容，方便我们核实。' : 'Tell us a little more so we can check it.',
    cancel: isZh ? '取消' : 'Cancel',
    send: isZh ? '发送反馈' : 'Send report',
    sending: isZh ? '发送中…' : 'Sending…',
    failed: isZh ? '反馈发送失败，请重试。' : 'The report could not be sent. Please try again.',
    thanksTitle: isZh ? '感谢你的反馈！' : 'Thanks for letting us know!',
    thanksDesc: isZh ? '我们会查看这道题。' : 'We’ll check this question.',
  }

  useEffect(() => () => {
    if (closeTimerRef.current) clearTimeout(closeTimerRef.current)
  }, [])

  const handleSend = async () => {
    if (submitting || !selectedKey) return
    if (selectedKey === 'other' && !detail.trim()) {
      setNeedsDetail(true)
      return
    }

    setSubmitting(true)
    setSubmitFailed(false)
    setNeedsDetail(false)
    try {
      const response = await reportBrainActiveQuestionIssue({
        question_id: questionId,
        issue_type: selectedKey,
        detail: detail.trim() || undefined,
      })
      if (response?.success === false) throw new Error(response?.error?.message || 'Report failed')
      setSubmitted(true)
      closeTimerRef.current = setTimeout(onClose, 1800)
    } catch (error) {
      console.error('[BRAINACTIVE_REPORT_QUESTION]', error)
      setSubmitFailed(true)
    } finally {
      setSubmitting(false)
    }
  }

  if (submitted) {
    return (
      <View className='report-modal-overlay' onTouchStart={stopTouch} onTouchMove={stopTouch} onTouchEnd={stopTouch}>
        <View className='report-modal-content report-modal-content--thanks' onClick={stopTouch}>
          <Text className='report-thanks-icon'>✓</Text>
          <Text className='report-thanks-title'>{strings.thanksTitle}</Text>
          <Text className='report-thanks-desc'>{strings.thanksDesc}</Text>
        </View>
      </View>
    )
  }

  return (
    <View className='report-modal-overlay' onTouchStart={stopTouch} onTouchMove={stopTouch} onTouchEnd={stopTouch}>
      <View className='report-modal-content' onClick={stopTouch}>
        <View className='report-modal-header'>
          <Text className='report-modal-title'>{strings.title}</Text>
          <Text className='report-modal-desc'>{strings.subtitle}</Text>
        </View>

        <View className='report-options'>
          {ISSUE_OPTIONS.map(option => (
            <View
              key={option.key}
              className={`report-option ${selectedKey === option.key ? 'selected' : ''}`}
              onClick={() => {
                setSelectedKey(option.key)
                setNeedsDetail(false)
              }}
            >
              <View className={`report-option-radio ${selectedKey === option.key ? 'checked' : ''}`} />
              <Text className='report-option-text'>{isZh ? option.labelZh : option.labelEn}</Text>
            </View>
          ))}
        </View>

        {selectedKey === 'other' && (
          <View className='report-detail-wrap'>
            <Textarea
              className='report-detail-input'
              placeholder={strings.placeholder}
              value={detail}
              maxlength={300}
              onInput={event => setDetail(event.detail.value)}
            />
            {needsDetail && <Text className='report-detail-required'>{strings.needsDetail}</Text>}
          </View>
        )}

        {submitFailed && <Text className='report-error'>{strings.failed}</Text>}

        <Button className='report-btn-send' onClick={handleSend} disabled={submitting || !selectedKey}>
          {submitting ? strings.sending : strings.send}
        </Button>
        <View className='report-btn-cancel' onClick={() => !submitting && onClose()}>
          <Text>{strings.cancel}</Text>
        </View>
      </View>
    </View>
  )
}
