import { PropsWithChildren } from 'react'
import Taro, { useLaunch } from '@tarojs/taro'
import { getLang, setLang } from '@/utils/storage'
import './styles/index.scss'

function App({ children }: PropsWithChildren<any>) {
  useLaunch(() => {
    // Detect system language on first launch
    const savedLang = getLang()
    if (!savedLang) {
      try {
        const sysLang = Taro.getSystemInfoSync().language || ''
        const isChinese = sysLang.toLowerCase().includes('zh')
        setLang(isChinese ? 'zh' : 'en')
      } catch (e) {
        setLang('en')
      }
    }
  })

  return children
}

export default App
