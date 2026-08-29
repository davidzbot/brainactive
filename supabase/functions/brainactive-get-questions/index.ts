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
      source: 'brainactive-get-questions'
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
    const mode = url.searchParams.get('mode') || 'quick_test'
    const topic = url.searchParams.get('topic') || ''
    const level = url.searchParams.get('level') || ''
    const limit = parseInt(url.searchParams.get('limit') || (mode === 'quick_test' ? '5' : '10'), 10)
    const retryIdsParam = url.searchParams.get('ids') || ''

    if (mode === 'retry' && retryIdsParam) {
      const ids = retryIdsParam.split(',').map(id => id.trim()).filter(Boolean)
      const { data, error } = await supabase
        .from('brainactive_questions')
        .select('*')
        .in('id', ids)
        .eq('is_active', true)

      if (error) throw error
      return standardResponse(true, data || [])
    }

    let query = supabase
      .from('brainactive_questions')
      .select('*')
      .eq('is_active', true)

    if (topic && topic !== 'All') {
      query = query.eq('topic', topic)
    }

    if (level && level !== 'All') {
      query = query.eq('level', level)
    }

    // Fetch pool of candidates to sample from
    const { data: pool, error } = await query.limit(100)
    if (error) throw error

    if (!pool || pool.length === 0) {
      return standardResponse(true, [])
    }

    // Shuffle and pick requested limit
    const shuffled = [...pool].sort(() => 0.5 - Math.random())
    const selected = shuffled.slice(0, Math.min(limit, shuffled.length))

    return standardResponse(true, selected)
  } catch (err: any) {
    return standardResponse(false, null, { code: 'FETCH_FAILED', message: err.message }, 500)
  }
})
