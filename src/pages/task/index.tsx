import React, { useState, useEffect, useRef } from 'react'
import { View, Text, Button } from '@tarojs/components'
import Taro, { useLoad, showToast, showModal, reLaunch, navigateTo } from '@tarojs/taro'
import { getStorage, getLang } from '@/utils/storage'
import { setSafeTitle } from '@/utils/common'
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
  const [totalSteps] = useState(3)
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

    // Correctly track daily usage
    try {
      const { incrementDailyUsage } = require('@/utils/common')
      incrementDailyUsage(diff)
    } catch (e) {
      console.warn('Usage tracking failed', e)
    }

    // Initialize tasks immediately with local data so user isn't blocked
    initTasks()
    
    // Fetch remote content for Android (H5/Capacitor)
    if (process.env.TARO_ENV === 'h5') {
      setLoading(true)
      const lang = getLang()
      
      // Safety timeout to prevent infinite loading screen
      const safetyTimer = setTimeout(() => {
        setLoading(false)
        console.warn('TASK: Loading cleared by safety timeout')
      }, 5000)

      try {
        console.log('TASK: Starting remote data load...')
        const results = await Promise.allSettled([
          fetchBrainActiveContent('name', lang, 20),
          fetchBrainActiveContent('city', lang, 20),
          fetchBrainActiveContent('sentence', lang, 10)
        ])
        
        const names = results[0].status === 'fulfilled' ? results[0].value : []
        const cities = results[1].status === 'fulfilled' ? results[1].value : []
        const sentences = results[2].status === 'fulfilled' ? results[2].value : []

        console.log('TASK: Results settled', { 
          namesCount: names.length, 
          citiesCount: cities.length, 
          sentencesCount: sentences.length 
        })
        
        if (names.length > 0 || cities.length > 0 || sentences.length > 0) {
          setRemoteData({
            names: names.map(i => i.value),
            cities: cities.map(i => i.value),
            sentences: sentences.map(i => {
              try {
                return typeof i.value === 'string' ? JSON.parse(i.value) : i.value
              } catch(e) {
                return { t: i.value, w: i.value }
              }
            })
          })
          console.log('TASK: Remote data load SUCCESS')
        } else {
          console.log('TASK: Remote data empty, using FALLBACK')
        }

        // Handle hardware back button
        try {
          const { App } = require('@capacitor/app')
          App.addListener('backButton', () => {
            goBack()
          })
        } catch (e) {
          // ignore
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
    if (taskQueue.length > 0 && currentStep <= totalSteps) {
      runTask()
    }
    return () => {
      timersRef.current.forEach(t => clearTimeout(t))
      if (lockTimerRef.current) clearTimeout(lockTimerRef.current)
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
    const tasks = shuffle(allTasks).slice(0, 3)
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

    if (!targetArray || targetArray.length === 0) {
      taskNumber()
    }
  }

  useEffect(() => {
    updateInstruction()
  }, [taskType, showMemoryPhase, mathProblem, sequenceMode])

  const updateInstruction = () => {
    if (showMemoryPhase) {
      if (taskType === 4) {
        setInstruction(t('task.remember_sentences')) 
      } else if (taskType === 1 && mathProblem) {
        setInstruction(t('task.remember_numbers'))
      } else if (taskType === 0) {
        setInstruction(t('task.remember_names'))
      } else if (taskType === 3) {
        setInstruction(t('task.remember_cities'))
      } else {
        setInstruction(t('task.remember_names'))
      }
    } else {
      if (mathProblem) {
        const opParts = mathProblem.op.split(' ... ')
        if (opParts.length === 2) {
          setInstruction(`🧮 ${opParts[0]} ... ${opParts[1]} = ?`)
        } else {
          setInstruction(`🧮 ${mathProblem.op} = ?`)
        }
      } else if (sequenceMode) {
        setInstruction(t('task.order_them'))
      } else {
        setInstruction(t('task.pick_them'))
      }
    }
  }

  const getPool = (type: 'names' | 'cities' | 'sentences') => {
    if (remoteData[type] && remoteData[type].length > 0) {
      return remoteData[type]
    }
    return dataUtils[type]
  }

  const taskName = () => {
    const pool = shuffle([...getPool('names')])
    let targetCount = 1
    if (difficulty === 'normal') targetCount = 3
    if (difficulty === 'pro') targetCount = 4

    const targets = pool.slice(0, targetCount).map((n: string) => ({ display: n, _key: n }))
    const distractors = pool.slice(targetCount, targetCount + (difficulty === 'pro' ? 6 : 5)).map((n: string) => ({ display: n, _key: n }))
    
    setTargetArray(targets)
    setOptions(shuffle([...targets, ...distractors]))
    setSequenceMode(difficulty !== 'easy')
  }

  const taskCity = () => {
    const pool = shuffle([...getPool('cities')])
    let targetCount = 1
    if (difficulty === 'normal') targetCount = 3
    if (difficulty === 'pro') targetCount = 4

    const targets = pool.slice(0, targetCount).map((c: string) => ({ display: c, _key: c }))
    const distractors = pool.slice(targetCount, targetCount + (difficulty === 'pro' ? 6 : 5)).map((c: string) => ({ display: c, _key: c }))
    
    setTargetArray(targets)
    setOptions(shuffle([...targets, ...distractors]))
    setSequenceMode(difficulty !== 'easy')
  }

  const taskNumber = () => {
    const diff = difficulty
    if (diff === 'normal' || diff === 'pro') {
      const isPro = diff === 'pro'
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
      let iterations = 0
      while(optVals.length < 6 && iterations < 50) {
        iterations++
        let d = result + (Math.floor(Math.random() * (isPro ? 100 : 40)) - (isPro ? 50 : 20))
        if (!optVals.includes(d) && d > 0) optVals.push(d)
      }
      while(optVals.length < 6) {
        let d = Math.floor(Math.random() * (isPro ? 2000 : 150)) + 1
        if (!optVals.includes(d)) optVals.push(d)
      }

      let opStr = `${n1} ${op1} ${n2}`
      if (isPro) opStr = `${n1} ${op1} ${n2} ${op2} ${n3}`

      setTargetArray(targets)
      setOptions(shuffle(optVals).map((o: number) => ({ display: String(o), _key: String(o) })))
      setMathProblem({ op: opStr, res: result })
      setSequenceMode(false)
    } else {
      const n = Math.floor(Math.random() * 900 + 100)
      const taskItem: TaskItem = { display: String(n), _key: String(n) }
      setTargetArray([taskItem])
      setOptions(shuffle([n, n+5, n-3, n+10]).map((o: number) => ({ display: String(o), _key: String(o) })))
    }
  }

  const taskColorShape = () => {
    const colors = [
      { name: 'Red', nameZh: '红', hex: '#ef4444' },
      { name: 'Blue', nameZh: '蓝', hex: '#3b82f6' },
      { name: 'Green', nameZh: '绿', hex: '#22c55e' },
      { name: 'Yellow', nameZh: '黄', hex: '#eab308' },
      { name: 'Purple', nameZh: '紫', hex: '#a855f7' }
    ]
    const shapes = [
      { name: 'Circle', nameZh: '圆形', class: 'circle' },
      { name: 'Square', nameZh: '方形', class: 'square' },
      { name: 'Triangle', nameZh: '三角形', class: 'triangle' },
      { name: 'Star', nameZh: '星形', class: 'star' }
    ]
    
    let pool: TaskItem[] = []
    const isZh = getLang() === 'zh'
    
    colors.forEach(c => {
      shapes.forEach(s => {
        pool.push({
          colorHex: c.hex,
          shapeClass: s.class,
          display: isZh ? c.nameZh + s.nameZh : c.name + ' ' + s.name,
          _key: c.name + s.name,
          isShapeObj: true 
        })
      })
    })
    
    let targetCount = 1
    let optionCount = 4
    if (difficulty === 'normal') { targetCount = 2; optionCount = 6 }
    if (difficulty === 'pro') { targetCount = 3; optionCount = 8 }
    
    const shuffled = shuffle(pool)
    const targets = shuffled.slice(0, targetCount)
    const distractors = shuffled.slice(targetCount, optionCount)
    
    setTargetArray(targets)
    setOptions(shuffle([...targets, ...distractors]))
    setSequenceMode(difficulty !== 'easy')
  }

  const taskSentence = () => {
    const pool = shuffle([...getPool('sentences')])
    
    let targetCount = 1
    if (difficulty === 'normal') targetCount = 2
    if (difficulty === 'pro') targetCount = 3

    const targets = pool.slice(0, targetCount)
    const targetArrayItems: TaskItem[] = targets.map((s: any) => ({ display: s.t, _key: s.t }))
    
    let opts: TaskItem[] = []
    targets.forEach((s: any) => {
      opts.push({ display: s.t, _key: s.t })
      opts.push({ display: s.w, _key: 'typo_' + s.t })
    })
    
    let distractorCount = 2
    if (difficulty === 'normal') distractorCount = 2
    if (difficulty === 'pro') distractorCount = 3

    const otherSentences = pool.slice(targetCount, targetCount + distractorCount)
    otherSentences.forEach((s: any) => {
      opts.push({ display: s.t, _key: s.t })
    })

    setTargetArray(targetArrayItems)
    setOptions(shuffle(opts))
    setSequenceMode(difficulty !== 'easy')
  }

  const skipMemory = () => {
    setShowMemoryPhase(false)
  }

  const backToMemory = () => {
    setShowMemoryPhase(true)
    setSelectedOptions([])
    setAnsweringLock(false)
  }

  const selectOption = (item: TaskItem) => {
    if (answeringLock) return
    const val = item._key
    let selected = [...selectedOptions]

    if (selected.includes(val)) {
      selected = selected.filter(i => i !== val)
    } else {
      selected.push(val)
    }
    setSelectedOptions(selected)

    let targetReq = targetArray.length
    if (mathProblem) targetReq = 1

    if (selected.length >= targetReq) {
      setAnsweringLock(true)
      let correct = false
      if (mathProblem) {
        correct = val == String(mathProblem.res)
      } else if (sequenceMode) {
        const targetKeys = targetArray.map(t => t._key)
        correct = selected.every((v, i) => v === targetKeys[i])
      } else {
        const targetKeys = targetArray.map(t => t._key)
        correct = targetKeys.every(t => selected.includes(t))
      }
      setSafeTimeout(() => { if (correct) { success() } else { fail() } }, 300)
    }
  }

  const showCustomToast = async (msg: string) => {
    try {
      const { Toast } = require('@capacitor/toast')
      await Toast.show({ text: msg, duration: 'short', position: 'center' })
    } catch (e) {
      showToast({ title: msg, icon: 'none' })
    }
  }

  const success = () => {
    const newCombo = combo + 1
    const points = 10 + newCombo * 2
    setCombo(newCombo)
    setScore(score + points)
    showCustomToast(`+${points}`)
    next()
  }

  const fail = () => {
    setCombo(0)
    setAnsweringLock(false)
    setSelectedOptions([])
    showCustomToast(getLang() === 'zh' ? '再想想 👀' : 'Try Again 👀')
  }

  const next = () => {
    if (lockTimerRef.current) clearTimeout(lockTimerRef.current)
    lockTimerRef.current = setSafeTimeout(() => {
      if (answeringLock) {
        setAnsweringLock(false)
      }
    }, 5000)

    if (currentStep < totalSteps) {
      setSafeTimeout(async () => {
        try {
          setCurrentStep(currentStep + 1)
        } catch (e) {
          console.error('runTask error:', e)
          setAnsweringLock(false)
          await showModal({
            title: 'Error',
            content: 'Task load failed',
            showCancel: false,
          })
          reLaunch({ url: '/pages/home/index' })
        }
      }, 600)
    } else {
      const time = Math.round((Date.now() - startTime) / 1000)
      const url = `/pages/result/index?time=${time}&score=${score}`
      navigateTo({ url })
    }
  }

  const goBack = async () => {
    let confirm = false
    if (process.env.TARO_ENV === 'h5') {
      try {
        const { Dialog } = require('@capacitor/dialog')
        const { value } = await Dialog.confirm({
          title: t('task.exit_confirm'),
          message: t('task.exit_msg'),
        })
        confirm = value
      } catch (e) {
        confirm = window.confirm(t('task.exit_msg'))
      }
    } else {
      const res = await showModal({
        title: t('task.exit_confirm'),
        content: t('task.exit_msg'),
      })
      confirm = res.confirm
    }

    if (confirm) {
      reLaunch({ url: '/pages/home/index' })
    }
  }

  const renderTargetItem = (item: TaskItem, index: number) => {
    if (item.isShapeObj && item.colorHex) {
      return (
        <View key={index} className="target-shape" style={{ backgroundColor: item.colorHex }}>
          <Text className="shape-text">{item.display}</Text>
        </View>
      )
    }
    return (
      <View key={index} className="target-item">
        <Text className="target-text">{item.display}</Text>
      </View>
    )
  }

  const renderOptionItem = (item: TaskItem, index: number) => {
    const isSelected = selectedOptions.includes(item._key)
    
    if (item.isShapeObj && item.colorHex) {
      return (
        <View 
          key={index}
          className={`option-shape ${isSelected ? 'selected' : ''}`}
          style={{ backgroundColor: item.colorHex }}
          onClick={() => selectOption(item)}
        >
          <Text className="shape-text">{item.display}</Text>
        </View>
      )
    }
    
    return (
      <View 
        key={index}
        className={`option-item ${isSelected ? 'selected' : ''}`}
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

      <View className="instruction">
        <Text className="instruction-text">{instruction}</Text>
      </View>

      {showMemoryPhase ? (
        <View className="memory-phase">
          <View className="target-grid">
            {targetArray.map((item, index) => renderTargetItem(item, index))}
          </View>
          <Button className="continue-btn" onClick={skipMemory}>
            {t('task.got_it')}
          </Button>
          <Button className="back-btn" onClick={backToMemory}>
            ← {t('task.back')}
          </Button>
        </View>
      ) : (
        <View className="answer-phase">
          <View className="options-grid">
            {options.map((item, index) => renderOptionItem(item, index))}
          </View>
        </View>
      )}

      <View className="exit-btn" onClick={goBack}>
        <Text>{t('task.exit')}</Text>
      </View>
    </View>
  )
}
