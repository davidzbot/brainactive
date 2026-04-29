import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

function standardResponse(success: boolean, data: any = null, error: any = null) {
  return new Response(
    JSON.stringify({ success, data, error }),
    { 
      headers: { 
        ...corsHeaders, 
        'Content-Type': 'application/json',
        'X-Content-Type-Options': 'nosniff',
        'Content-Security-Policy': "default-src 'none'"
      }, 
      status: success ? 200 : 400 
    }
  )
}

Deno.serve(async (req) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  // Only allow GET
  if (req.method !== 'GET') {
    return standardResponse(false, null, { code: 'METHOD_NOT_ALLOWED', message: 'Only GET is allowed' })
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL')
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')

    if (!supabaseUrl || !supabaseKey) {
      throw new Error('Missing environment variables')
    }

    // Initialize client with brainactive schema
    const supabase = createClient(supabaseUrl, supabaseKey, {
      db: { schema: 'brainactive' }
    })

    const url = new URL(req.url)
    const type = url.searchParams.get('type')
    const lang = url.searchParams.get('lang') || 'en'
    const limitParam = url.searchParams.get('limit')
    const limit = Math.min(Math.max(parseInt(limitParam || '10'), 1), 100)

    // Validation
    const allowedTypes = ['city', 'sentence', 'name', 'tip']
    if (type && !allowedTypes.includes(type)) {
      return standardResponse(false, null, { code: 'INVALID_TYPE', message: 'Invalid content type' })
    }

    const allowedLangs = ['en', 'zh']
    if (!allowedLangs.includes(lang)) {
       return standardResponse(false, null, { code: 'INVALID_LANG', message: 'Invalid language' })
    }

    let query = supabase
      .from('content_pool')
      .select('type, value, language')
      .eq('is_active', true)
      .eq('language', lang)

    if (type) {
      query = query.eq('type', type)
    }

    // Limit the database query to prevent large data transfers
    const { data: content, error } = await query.limit(200)

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
    console.error(`[Error] ${error.message}`)
    return standardResponse(false, null, { code: 'SERVER_ERROR', message: 'An internal error occurred' })
  }
})
