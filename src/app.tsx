import { PropsWithChildren } from 'react'
import { useLaunch } from '@tarojs/taro'
import { getLang, setLang } from '@/utils/storage'
import './styles/index.scss'

function App({ children }: PropsWithChildren<any>) {
  useLaunch(() => {
    // Initialize default language if not set
    if (!getLang()) {
      setLang('en')
    }
  })

  return children
}

export default App
