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
      source: 'brainactive-get-content'
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

    const url = new URL(req.url)
    const lang = url.searchParams.get('lang') || 'en'
    const type = url.searchParams.get('type') || ''
    const limit = parseInt(url.searchParams.get('limit') || '20', 10)

    let query = supabase
      .schema('brainactive')
      .from('content_pool')
      .select('*')
      .eq('is_active', true)

    if (type) {
      query = query.eq('type', type)
    }
    if (lang) {
      query = query.eq('language', lang)
    }

    query = query.limit(Math.max(1, Math.min(limit || 20, 100)))

    const { data, error } = await query
    if (error) throw error

    return standardResponse(true, data || [])
  } catch (err: any) {
    return standardResponse(false, null, { code: 'CONTENT_FETCH_FAILED', message: err.message }, 500)
  }
})
