import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type, x-device-id',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Max-Age': '86400',
}

function generateReferralCode(): string {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
  let code = ''
  for (let i = 0; i < 6; i++) {
    code += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return code
}

function standardResponse(success: boolean, data: any = null, error: any = null, status = 200) {
  const response: any = { success }
  if (success) {
    response.data = data
  } else {
    response.error = {
      code: error?.code || 'UNKNOWN_ERROR',
      message: error?.message || 'Something went wrong',
      source: 'brainactive-apply-referral'
    }
  }
  return new Response(
    JSON.stringify(response),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status }
  )
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL') || ''
    const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || Deno.env.get('SUPABASE_ANON_KEY') || ''
    const supabase = createClient(supabaseUrl, supabaseServiceKey)

    const payload = await req.json()
    const { user_id, referral_code } = payload

    if (!user_id || !referral_code) {
      return standardResponse(false, null, { code: 'INVALID_INPUT', message: 'user_id and referral_code are required' }, 400)
    }

    const cleanCode = referral_code.trim().toUpperCase()

    // 1. Find referrer profile
    const { data: referrer, error: referrerErr } = await supabase
      .from('brainactive_profiles')
      .select('*')
      .eq('referral_code', cleanCode)
      .maybeSingle()

    if (referrerErr || !referrer) {
      return standardResponse(false, null, { code: 'INVALID_CODE', message: 'Invalid referral code' }, 400)
    }

    if (referrer.user_id === user_id) {
      return standardResponse(false, null, { code: 'SELF_REFERRAL', message: 'Cannot refer yourself' }, 400)
    }

    // 2. Check if user was already referred
    const { data: existingRef } = await supabase
      .from('brainactive_referrals')
      .select('*')
      .eq('referred_user_id', user_id)
      .maybeSingle()

    if (existingRef) {
      return standardResponse(false, null, { code: 'ALREADY_REFERRED', message: 'You have already redeemed a referral code' }, 400)
    }

    // 3. Record referral
    const { error: refInsertErr } = await supabase
      .from('brainactive_referrals')
      .insert({
        referrer_user_id: referrer.user_id,
        referred_user_id: user_id,
        reward_days: 7,
        created_at: new Date().toISOString()
      })

    if (refInsertErr) throw refInsertErr

    return standardResponse(true, {
      message: 'Referral recorded — thanks for sharing BrainActive!',
      reward_days: 0
    })
  } catch (err: any) {
    return standardResponse(false, null, { code: 'REFERRAL_FAILED', message: err.message }, 500)
  }
})
