import React, { useState, useEffect, useRef } from 'react'
import { View, Text, Button } from '@tarojs/components'
import Taro, { useLoad, showToast, showModal, reLaunch, navigateTo } from '@tarojs/taro'
import { getStorage, getLang } from '@/utils/storage'
import { setSafeTitle, incrementDailyUsage } from '@/utils/common'
import { dataUtils } from '@/utils/data'
import { fetchBrainActiveContent } from '@/utils/supabase'
import { t } from '@/utils/i18n'
import './index.scss'

interface TaskItem {
  display: string
  _key: string
  colorHex?: string
  shapeClass?: string
  isShapeObj?: boolean
}

export default function TrainingPage() {
  const [currentStep, setCurrentStep] = useState(1)
  const [totalSteps] = useState(5)
  const [showMemoryPhase, setShowMemoryPhase] = useState(true)
  const [instruction, setInstruction] = useState('')
  const [taskQueue, setTaskQueue] = useState<number[]>([])
  const [options, setOptions] = useState<TaskItem[]>([])
  const [targetArray, setTargetArray] = useState<TaskItem[]>([])
  const [selectedOptions, setSelectedOptions] = useState<string[]>([])
  const [startTime, setStartTime] = useState(0)
  const [difficulty, setDifficulty] = useState('easy')
  const [score, setScore] = useState(0)
  const [combo, setCombo] = useState(0)
  const [answeringLock, setAnsweringLock] = useState(false)
  const [taskType, setTaskType] = useState(0)
  const [mathProblem, setMathProblem] = useState<{ op: string, res: number } | null>(null)
  const [sequenceMode, setSequenceMode] = useState(false)
  const [remoteData, setRemoteData] = useState<any>({ names: [], cities: [], sentences: [] })
  const [loading, setLoading] = useState(true)
  
  const timersRef = useRef<any[]>([])
  const lockTimerRef = useRef<any>(null)
  const hasPromptedExitRef = useRef(false)
  const lastPromptTimeRef = useRef(0)

  useLoad(async (loadOptions) => {
    let diff = loadOptions.difficulty || getStorage('lastDifficulty') || 'easy'
    if (!['easy', 'normal', 'pro'].includes(diff)) {
      diff = 'easy'
    }
    
    setDifficulty(diff)
    setStartTime(Date.now())
    setScore(0)
    setCombo(0)
    
    setSafeTitle(t('task.title'))
    incrementDailyUsage(diff)
    initTasks()
    
    if (process.env.TARO_ENV === 'h5') {
      setLoading(true)
      const lang = getLang() || 'en'
      const safetyTimer = setTimeout(() => setLoading(false), 5000)

      try {
        const results = await Promise.allSettled([
          fetchBrainActiveContent('name', lang, 20),
          fetchBrainActiveContent('city', lang, 20),
          fetchBrainActiveContent('sentence', lang, 10)
        ])
        
        const names = results[0].status === 'fulfilled' ? results[0].value : []
        const cities = results[1].status === 'fulfilled' ? results[1].value : []
        const sentences = results[2].status === 'fulfilled' ? results[2].value : []

        if (names.length > 0 || cities.length > 0 || sentences.length > 0) {
          setRemoteData({
            names: names.map(i => i.value),
            cities: cities.map(i => i.value),
            sentences: sentences.map(i => {
              try {
                return typeof i.value === 'string' ? JSON.parse(i.value) : i.value
              } catch {
                return { t: i.value, w: i.value }
              }
            })
          })
        }
      } catch (e) {
        console.error('TASK: Initial load exception', e)
      } finally {
        clearTimeout(safetyTimer)
        setLoading(false)
      }
    } else {
      setLoading(false)
    }
  })

  useEffect(() => {
    let backListener: any = null
    const setupBack = async () => {
      try {
        const { App } = require('@capacitor/app')
        backListener = await App.addListener('backButton', () => {
          // Debounce check: Don't prompt if already prompted within last 2s
          const now = Date.now()
          if (hasPromptedExitRef.current && (now - lastPromptTimeRef.current < 2000)) {
             return 
          }
          goBack()
        })
      } catch { }
    }
    setupBack()

    if (taskQueue.length > 0 && currentStep <= totalSteps) {
      runTask()
    }
    return () => {
      timersRef.current.forEach(t => clearTimeout(t))
      if (lockTimerRef.current) clearTimeout(lockTimerRef.current)
      if (backListener) backListener.remove()
    }
  }, [currentStep, taskQueue]) 

  const setSafeTimeout = (fn: () => void, delay: number) => {
    const timer = setTimeout(fn, delay)
    timersRef.current.push(timer)
    return timer
  }

  const shuffle = <T,>(arr: T[]): T[] => {
    let newArr = [...arr]
    for (let i = newArr.length - 1; i > 0; i--) {
      let j = Math.floor(Math.random() * (i + 1));
      [newArr[i], newArr[j]] = [newArr[j], newArr[i]]
    }
    return newArr
  }

  const initTasks = () => {
    const allTasks = [0, 1, 2, 3, 4]
    const tasks = shuffle(allTasks)
    setTaskQueue(tasks)
  }

  const runTask = () => {
    if (lockTimerRef.current) {
      clearTimeout(lockTimerRef.current)
      lockTimerRef.current = null
    }
    const type = taskQueue[currentStep - 1]
    setTaskType(type)
    setShowMemoryPhase(true)
    setSelectedOptions([])
    setAnsweringLock(false)
    setSequenceMode(false)
    setMathProblem(null)

    switch(type) {
      case 0: taskName(); break
      case 1: taskNumber(); break
      case 2: taskColorShape(); break
      case 3: taskCity(); break
      case 4: taskSentence(); break
    }
  }

  useEffect(() => {
    updateInstruction()
  }, [taskType, showMemoryPhase, mathProblem, sequenceMode])

  const updateInstruction = () => {
    if (showMemoryPhase) {
      switch (taskType) {
        case 0: setInstruction(t(sequenceMode ? 'task.remember_names_seq' : 'task.remember_names')); break
        case 1: setInstruction(t(mathProblem ? 'task.remember_numbers_calc' : 'task.remember_numbers')); break
        case 2: setInstruction(t(sequenceMode ? 'task.remember_colorshapes_seq' : 'task.remember_colorshapes')); break
        case 3: setInstruction(t(sequenceMode ? 'task.remember_cities_seq' : 'task.remember_cities')); break
        case 4: setInstruction(t(sequenceMode ? 'task.remember_sentences_seq' : 'task.remember_sentences')); break
        default: setInstruction(t('task.remember_names'))
      }
    } else {
      if (mathProblem) {
        const isZh = getLang() === 'zh'
        const opParts = mathProblem.op.split(' ')
        let maskedOp = ''
        let numCount = 1
        opParts.forEach(p => {
          if (!isNaN(parseInt(p))) {
            maskedOp += isZh ? `(数字 ${numCount})` : `(number ${numCount})`
            numCount++
          } else {
            maskedOp += ` ${p} `
          }
        })
        setInstruction(`🧮 ${maskedOp} = ?`)
      } else if (sequenceMode) {
        setInstruction(`🔢 ${t('task.order_them')}`)
      } else {
        setInstruction(`🎯 ${t('task.pick_them')}`)
      }
    }
  }

  const getPool = (type: 'names' | 'cities' | 'sentences') => {
    if (remoteData[type] && remoteData[type].length > 0) return remoteData[type]
    return dataUtils[type]
  }

  const taskName = () => {
    setTaskType(0); setMathProblem(null)
    const pool = shuffle([...getPool('names')])
    let targetCount = difficulty === 'easy' ? 1 : (difficulty === 'normal' ? 3 : 4)
    const targets = pool.slice(0, targetCount).map((n: string) => ({ display: n, _key: n }))
    const distractors = pool.slice(targetCount, targetCount + (difficulty === 'pro' ? 6 : 5)).map((n: string) => ({ display: n, _key: n }))
    setTargetArray(targets); setOptions(shuffle([...targets, ...distractors]))
    setSequenceMode(difficulty !== 'easy')
  }

  const taskCity = () => {
    setTaskType(3); setMathProblem(null)
    const pool = shuffle([...getPool('cities')])
    let targetCount = difficulty === 'easy' ? 1 : (difficulty === 'normal' ? 3 : 4)
    const targets = pool.slice(0, targetCount).map((c: string) => ({ display: c, _key: c }))
    const distractors = pool.slice(targetCount, targetCount + (difficulty === 'pro' ? 6 : 5)).map((c: string) => ({ display: c, _key: c }))
    setTargetArray(targets); setOptions(shuffle([...targets, ...distractors]))
    setSequenceMode(difficulty !== 'easy')
  }

  const taskNumber = () => {
    setTaskType(1)
    if (difficulty !== 'easy') {
      const isPro = difficulty === 'pro'
      let n1 = Math.floor(Math.random() * (isPro ? 900 : 80) + 10)
      let n2 = Math.floor(Math.random() * (isPro ? 900 : 80) + 10)
      let n3 = isPro ? Math.floor(Math.random() * 90 + 10) : 0
      const op1 = Math.random() > 0.5 ? '+' : '-'
      const op2 = Math.random() > 0.5 ? '+' : '-'
      let result = op1 === '+' ? n1 + n2 : n1 - n2
      const targets: TaskItem[] = [{ display: String(n1), _key: 'n1' }, { display: String(n2), _key: 'n2' }]
      if (isPro) {
        result = op2 === '+' ? result + n3 : result - n3
        targets.push({ display: String(n3), _key: 'n3' })
      }
      let optVals = [result]
      while(optVals.length < 6) {
        let d = result + (Math.floor(Math.random() * (isPro ? 100 : 40)) - (isPro ? 50 : 20))
        if (!optVals.includes(d) && d > 0) optVals.push(d)
        if (optVals.length >= 6) break
        let r = Math.floor(Math.random() * (isPro ? 2000 : 150)) + 1
        if (!optVals.includes(r)) optVals.push(r)
      }
      setTargetArray(targets)
      setOptions(shuffle(optVals).map((o: number) => ({ display: String(o), _key: String(o) })))
      setMathProblem({ op: isPro ? `${n1} ${op1} ${n2} ${op2} ${n3}` : `${n1} ${op1} ${n2}`, res: result })
      setSequenceMode(false)
    } else {
      const n = Math.floor(Math.random() * 900 + 100)
      setTargetArray([{ display: String(n), _key: String(n) }])
      setOptions(shuffle([n, n+5, n-3, n+10]).map((o: number) => ({ display: String(o), _key: String(o) })))
      setMathProblem(null); setSequenceMode(false)
    }
  }

  const taskColorShape = () => {
    setTaskType(2); setMathProblem(null)
    const isZh = getLang() === 'zh'
    const colors = [
      { name: 'Red', nameZh: '红', hex: '#ef4444' }, { name: 'Blue', nameZh: '蓝', hex: '#3b82f6' },
      { name: 'Green', nameZh: '绿', hex: '#22c55e' }, { name: 'Yellow', nameZh: '黄', hex: '#eab308' },
      { name: 'Purple', nameZh: '紫', hex: '#a855f7' }
    ]
    const shapes = [
      { name: 'Circle', nameZh: '圆形', class: 'circle' }, { name: 'Square', nameZh: '方形', class: 'square' },
      { name: 'Triangle', nameZh: '三角形', class: 'triangle' }, { name: 'Star', nameZh: '星形', class: 'star' }
    ]
    let pool: TaskItem[] = []
    colors.forEach(c => shapes.forEach(s => {
      pool.push({
        colorHex: c.hex, shapeClass: s.class, isShapeObj: true,
        display: isZh ? c.nameZh + s.nameZh : c.name + ' ' + s.name,
        _key: c.name + s.name
      })
    }))
    let targetCount = difficulty === 'easy' ? 1 : (difficulty === 'normal' ? 2 : 3)
    const shuffledPool = shuffle([...pool])
    const targets = shuffledPool.slice(0, targetCount)
    const distractors = shuffledPool.slice(targetCount, targetCount + (difficulty === 'pro' ? 5 : 3))
    setTargetArray(targets); setOptions(shuffle([...targets, ...distractors]))
    setSequenceMode(difficulty !== 'easy')
  }

  const taskSentence = () => {
    setTaskType(4); setMathProblem(null)
    const pool = shuffle([...getPool('sentences')])
    let targetCount = difficulty === 'easy' ? 1 : (difficulty === 'normal' ? 2 : 3)
    const targets = pool.slice(0, targetCount)
    let opts: TaskItem[] = []
    targets.forEach((s: any) => {
      opts.push({ display: s.t, _key: s.t })
      opts.push({ display: s.w, _key: 'typo_' + s.t })
    })
    const otherSentences = pool.slice(targetCount, targetCount + (difficulty === 'pro' ? 3 : 2))
    otherSentences.forEach((s: any) => opts.push({ display: s.t, _key: s.t }))
    setTargetArray(targets.map((s: any) => ({ display: s.t, _key: s.t })))
    setOptions(shuffle(opts)); setSequenceMode(difficulty !== 'easy')
  }

  const skipMemory = () => setShowMemoryPhase(false)
  const backToMemory = () => { setShowMemoryPhase(true); setSelectedOptions([]); setAnsweringLock(false) }

  const selectOption = (item: TaskItem) => {
    if (answeringLock) return
    const val = item._key
    let selected = [...selectedOptions]
    if (selected.includes(val)) selected = selected.filter(i => i !== val)
    else selected.push(val)
    setSelectedOptions(selected)

    let targetReq = mathProblem ? 1 : targetArray.length
    if (selected.length >= targetReq) {
      setAnsweringLock(true)
      let correct = false
      if (mathProblem) correct = val == String(mathProblem.res)
      else if (sequenceMode) {
        const targetKeys = targetArray.map(t => t._key)
        correct = selected.every((v, i) => v === targetKeys[i])
      } else {
        const targetKeys = targetArray.map(t => t._key)
        correct = targetKeys.every(t => selected.includes(t))
      }
      setSafeTimeout(() => { if (correct) success(); else fail() }, 300)
    }
  }

  const success = () => {
    const newCombo = combo + 1
    const points = 10 + newCombo * 2
    setCombo(newCombo); setScore(score + points)
    showCustomToast(`+${points}`); next()
  }

  const fail = () => {
    setCombo(0); setAnsweringLock(false); setSelectedOptions([])
    showCustomToast(getLang() === 'zh' ? '再想想 👀' : 'Try Again 👀')
  }

  const next = () => {
    if (lockTimerRef.current) clearTimeout(lockTimerRef.current)
    lockTimerRef.current = setSafeTimeout(() => { if (answeringLock) setAnsweringLock(false) }, 5000)

    if (currentStep < totalSteps) {
      setSafeTimeout(() => setCurrentStep(currentStep + 1), 600)
    } else {
      const time = Math.round((Date.now() - startTime) / 1000)
      navigateTo({ url: `/pages/result/index?time=${time}&score=${score}` })
    }
  }

  const goBack = async () => {
    hasPromptedExitRef.current = true
    lastPromptTimeRef.current = Date.now()
    const res = await showModal({ title: t('task.exit_confirm'), content: t('task.exit_msg') })
    if (res.confirm) reLaunch({ url: '/pages/home/index' })
    else hasPromptedExitRef.current = false
  }

  const showCustomToast = async (msg: string) => {
    try {
      const { Toast } = require('@capacitor/toast')
      await Toast.show({ text: msg, duration: 'short', position: 'center' })
    } catch { showToast({ title: msg, icon: 'none' }) }
  }

  const renderTargetItem = (item: TaskItem, index: number) => {
    if (item.isShapeObj && item.colorHex) {
      return <View key={index} className={`target-shape ${item.shapeClass}`} style={{ backgroundColor: item.colorHex }} />
    }
    return (
      <View key={index} className={`target-item ${taskType === 4 ? 'is-sentence' : ''} ${taskType === 1 ? 'is-number' : ''}`}>
        <Text className="target-text">{item.display}</Text>
      </View>
    )
  }

  const renderOptionItem = (item: TaskItem, index: number) => {
    const isSelected = selectedOptions.includes(item._key)
    const isColorShapeAns = item.isShapeObj && taskType === 2
    return (
      <View 
        key={index}
        className={`option-item ${isSelected ? 'selected' : ''} ${taskType === 4 ? 'is-sentence' : ''} ${isColorShapeAns ? 'is-colorshape-ans' : ''} ${taskType === 1 ? 'is-number' : ''}`}
        onClick={() => selectOption(item)}
      >
        <Text className="option-text">{item.display}</Text>
      </View>
    )
  }

  return (
    <View className="training-container">
      {loading && (
        <View className="loading-overlay">
          <View className="loading-spinner"></View>
          <Text className="loading-text">{t('task.loading')}</Text>
        </View>
      )}
      
      {/* Top Bar Section */}
      <View className="header">
        <View className="step-indicator">
          <Text className="step-text">Lv {currentStep} / {totalSteps}</Text>
        </View>
        <View className="score-display">
          <Text className="score-label">{t('result.score')}</Text>
          <Text className="score-value">{score}</Text>
          {combo > 0 && <Text className="combo-badge">🔥{combo}</Text>}
        </View>
      </View>

      <View className="main-stage">
        {/* Stage Label */}
        <View className="stage-clarity">
          <Text className="stage-text">{t(showMemoryPhase ? 'task.step_memorize' : 'task.step_answer')}</Text>
        </View>

        {/* Question Text */}
        <View className={`instruction ${taskType === 4 ? 'is-sentence' : ''}`}>
          <Text className="instruction-text">{instruction}</Text>
        </View>

        {/* Core Stimulus / Interaction Area */}
        <View className="interaction-area">
          {showMemoryPhase ? (
            <View className="memory-phase">
              <View className="target-grid">
                {targetArray.map((item, index) => renderTargetItem(item, index))}
              </View>
              <Button className="continue-btn" onClick={skipMemory}>
                {t('task.got_it')}
              </Button>
            </View>
          ) : (
            <View className="answer-phase">
              <View className="options-grid">
                {options.map((item, index) => renderOptionItem(item, index))}
              </View>
              <Button className="back-btn" onClick={backToMemory}>
                ← {t('task.back')}
              </Button>
            </View>
          )}
        </View>
      </View>

      <View className="exit-btn" onClick={goBack}>
        <Text>{t('task.exit')}</Text>
      </View>
    </View>
  )
}
