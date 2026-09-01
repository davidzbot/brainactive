import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type, x-device-id',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Max-Age': '86400',
}

function standardResponse(success: boolean, data: any = null, error: any = null, status = 200) {
  const response: any = { success }
  if (success) {
    response.data = data
  } else {
    response.error = {
      code: error?.code || 'UNKNOWN_ERROR',
      message: error?.message || 'Something went wrong',
      source: 'brainactive-get-progress'
    }
  }
  return new Response(
    JSON.stringify(response),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status }
  )
}

function getSgtDateString(): string {
  const d = new Date()
  const utc = d.getTime() + d.getTimezoneOffset() * 60000
  const sgt = new Date(utc + 8 * 3600000)
  return sgt.toISOString().split('T')[0]
}

function generateReferralCode(): string {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
  let code = ''
  for (let i = 0; i < 6; i++) {
    code += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return code
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL') || ''
    const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || Deno.env.get('SUPABASE_ANON_KEY') || ''
    const supabase = createClient(supabaseUrl, supabaseServiceKey)

    const url = new URL(req.url)
    const userId = url.searchParams.get('user_id')

    if (!userId) {
      return standardResponse(false, null, { code: 'MISSING_USER_ID', message: 'user_id is required' }, 400)
    }

    const todaySgt = getSgtDateString()

    // 1. Get or create user profile
    let { data: profile } = await supabase
      .from('brainactive_profiles')
      .select('*')
      .eq('user_id', userId)
      .maybeSingle()

    if (!profile) {
      const code = generateReferralCode()
      const { data: newProfile, error: profileErr } = await supabase
        .from('brainactive_profiles')
        .insert({
          user_id: userId,
          referral_code: code,
          is_pro: false,
          created_at: new Date().toISOString()
        })
        .select()
        .single()

      if (!profileErr) {
        profile = newProfile
      }
    }

    // 2. Get progress
    const { data: progress } = await supabase
      .from('brainactive_progress')
      .select('*')
      .eq('user_id', userId)
      .maybeSingle()

    const dailyRounds = (progress?.last_daily_round_date === todaySgt) ? (progress?.daily_rounds_completed || 0) : 0
    const bonusRounds = progress?.bonus_rounds_unlocked || 0

    // Check Pro validity — is_pro must be accompanied by a future expiry
    const now = new Date()
    const proExpiry = profile?.pro_expiry ? new Date(profile.pro_expiry) : null
    const isPro = !!(profile?.is_pro && proExpiry && proExpiry > now)

    return standardResponse(true, {
      user_id: userId,
      streak_count: progress?.streak_count || 0,
      total_questions: progress?.total_questions_answered || 0,
      total_correct: progress?.total_correct || 0,
      daily_rounds_completed: dailyRounds,
      free_rounds_limit: 1,
      bonus_rounds_unlocked: bonusRounds,
      referral_code: profile?.referral_code || '',
      is_pro: isPro,
      pro_expiry: profile?.pro_expiry || null
    })
  } catch (err: any) {
    return standardResponse(false, null, { code: 'GET_PROGRESS_FAILED', message: err.message }, 500)
  }
})
