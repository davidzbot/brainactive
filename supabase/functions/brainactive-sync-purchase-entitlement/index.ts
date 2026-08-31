import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type, x-device-id',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Max-Age': '86400',
}

function standardResponse(success: boolean, data: any = null, error: any = null, status = 200) {
  return new Response(JSON.stringify({
    success,
    ...(success ? { data } : {
      error: {
        code: error?.code || 'UNKNOWN_ERROR',
        message: error?.message || 'Something went wrong',
        source: 'brainactive-sync-purchase-entitlement',
      },
    }),
  }), {
    headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    status,
  })
}

function generateReferralCode() {
  return `BA${crypto.randomUUID().replace(/-/g, '').slice(0, 10).toUpperCase()}`
}

Deno.serve(async req => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: corsHeaders })
  if (req.method !== 'POST') {
    return standardResponse(false, null, { code: 'METHOD_NOT_ALLOWED', message: 'Only POST is supported' }, 405)
  }

  try {
    const userId = req.headers.get('x-device-id')?.trim() || ''
    const body = await req.json().catch(() => ({}))
    const productId = typeof body?.product_id === 'string' ? body.product_id.trim() : ''
    const expiryDate = typeof body?.expiry_date === 'string' ? body.expiry_date.trim() : ''
    const transactionId = typeof body?.transaction_id === 'string' ? body.transaction_id.trim() : null

    if (!userId || userId === 'unknown-device' || userId.length > 128) {
      return standardResponse(false, null, { code: 'AUTH_MISSING_ID', message: 'Valid x-device-id is required' }, 400)
    }
    if (productId !== 'brainactive_pro') {
      return standardResponse(false, null, { code: 'INVALID_PRODUCT', message: 'Unsupported subscription product' }, 400)
    }
    const expiry = new Date(expiryDate)
    if (!expiryDate || Number.isNaN(expiry.getTime()) || expiry.getTime() <= Date.now()) {
      return standardResponse(false, null, { code: 'INVALID_EXPIRY', message: 'A future subscription expiry is required' }, 400)
    }

    const supabaseUrl = Deno.env.get('SUPABASE_URL') || ''
    const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || ''
    if (!supabaseUrl || !serviceRoleKey) {
      return standardResponse(false, null, { code: 'SERVER_CONFIG_ERROR', message: 'Entitlement service is not configured' }, 500)
    }

    const supabase = createClient(supabaseUrl, serviceRoleKey)
    const now = new Date().toISOString()
    const { data: profile, error: profileError } = await supabase
      .from('brainactive_profiles')
      .select('user_id')
      .eq('user_id', userId)
      .maybeSingle()

    if (profileError) throw profileError

    const values = {
      is_pro: true,
      pro_expiry: expiry.toISOString(),
      updated_at: now,
    }
    const write = profile
      ? await supabase.from('brainactive_profiles').update(values).eq('user_id', userId)
      : await supabase.from('brainactive_profiles').insert({
          user_id: userId,
          referral_code: generateReferralCode(),
          ...values,
          created_at: now,
        })

    if (write.error) throw write.error

    console.info('[brainactive-sync-purchase-entitlement] Updated profile', {
      productId,
      transactionId,
      expiry: expiry.toISOString(),
    })
    return standardResponse(true, {
      user_id: userId,
      is_pro: true,
      pro_expiry: expiry.toISOString(),
    })
  } catch (error: any) {
    console.error('[brainactive-sync-purchase-entitlement] Failed:', error?.message || 'unknown error')
    return standardResponse(false, null, { code: 'SYNC_FAILED', message: 'Could not update BrainActive entitlement' }, 500)
  }
})
