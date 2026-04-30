import Taro, { request } from '@tarojs/taro'
import { getStorage, setStorage } from './storage'

const SUPABASE_URL = 'https://mqpunjvdrkqvionsjosl.supabase.co'
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1xcHVuanZkcmtxdmlvbnNqb3NsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY0NTk5MTYsImV4cCI6MjA5MjAzNTkxNn0.QLjWtVdGvFgTajL5Q51MoAbLyV46inSFsIGtAJBDXbE'

export async function fetchBrainActiveContent(type?: string, lang: string = 'en', limit: number = 20): Promise<any[]> {
  const url = `${SUPABASE_URL}/functions/v1/brainactive-get-content?lang=${lang}&limit=${limit}${type ? `&type=${type}` : ''}`

  const fetchPromise = request({
    url,
    method: 'GET',
    header: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
      'apikey': SUPABASE_ANON_KEY
    },
    timeout: 8000
  })

  const timeoutPromise = new Promise((_, reject) => {
    setTimeout(() => reject(new Error('TIMEOUT')), 10000)
  })

  try {
    const res: any = await Promise.race([fetchPromise, timeoutPromise])

    if (res.statusCode === 200 && res.data && res.data.success) {
      return Array.isArray(res.data.data) ? res.data.data : []
    }
    
    return []
  } catch (e) {
    return []
  }
}
