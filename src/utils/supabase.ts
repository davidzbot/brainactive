import Taro, { request } from '@tarojs/taro'
import { getStorage, setStorage } from './storage'

const SUPABASE_URL = 'https://mqpunjvdrkqvionsjosl.supabase.co'
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1xcHVuanZkcmtxdmlvbnNqb3NsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY0NTk5MTYsImV4cCI6MjA5MjAzNTkxNn0.QLjWtVdGvFgTajL5Q51MoAbLyV46inSFsIGtAJBDXbE'

export async function fetchBrainActiveContent(type?: string, lang: string = 'en', limit: number = 20) {
  // Debug: Simulate API failure
  if (getStorage('simulate_api_fail')) {
    console.warn('Simulating API failure')
    setStorage('simulate_api_fail', false)
    return null
  }

  try {
    const res = await request({
      url: `${SUPABASE_URL}/functions/v1/brainactive-get-content?lang=${lang}&limit=${limit}${type ? `&type=${type}` : ''}`,
      method: 'GET',
      header: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
        'apikey': SUPABASE_ANON_KEY
      },
      timeout: 10000 // 10s timeout
    })

    if (res.statusCode === 200 && res.data && res.data.success) {
      return res.data.data
    }
    
    // Log non-critical errors but don't crash
    if (res.statusCode !== 200) {
      console.error(`Supabase API error: ${res.statusCode}`, res.data)
    }
    
    return null
  } catch (e) {
    // Basic error safety: prevent blank screen by returning null (triggers local fallback)
    console.error('Supabase request failed', e)
    return null
  }
}
