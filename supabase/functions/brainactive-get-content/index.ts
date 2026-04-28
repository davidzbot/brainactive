import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

function standardResponse(success: boolean, data: any = null, error: any = null) {
  return new Response(
    JSON.stringify({ success, data, error }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: success ? 200 : 400 }
  )
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    // Initialize client with brainactive schema
    const supabase = createClient(supabaseUrl, supabaseKey, {
      db: { schema: 'brainactive' }
    })

    const url = new URL(req.url)
    const type = url.searchParams.get('type')
    const lang = url.searchParams.get('lang') || 'en'
    const limit = parseInt(url.searchParams.get('limit') || '10')

    let query = supabase
      .from('content_pool')
      .select('type, value, language')
      .eq('is_active', true)
      .eq('language', lang)

    if (type) {
      query = query.eq('type', type)
    }

    const { data: content, error } = await query

    if (error) throw error

    // Shuffle in memory
    const shuffled = (content || [])
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }

    const selected = shuffled.slice(0, limit)

    return standardResponse(true, selected)
  } catch (error) {
    return standardResponse(false, null, { code: 'SERVER_ERROR', message: error.message })
  }
})
