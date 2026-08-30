import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type, x-device-id',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Max-Age': '86400',
}

const QUESTION_PAGE_SIZE = 100

function selectQuickQuizQuestions(pool: any[], limit: number) {
  const selected: any[] = []
  const selectedIds = new Set<string>()
  const seenTopics = new Set<string>()
  const seenSkills = new Set<string>()

  for (const question of pool) {
    if (selected.length >= limit) break
    const topic = String(question.topic || question.domain || '').trim()
    if (!topic || seenTopics.has(topic)) continue
    selected.push(question)
    selectedIds.add(question.id)
    seenTopics.add(topic)
    const skill = String(question.skill || '').trim()
    if (skill) seenSkills.add(skill)
  }

  for (const question of pool) {
    if (selected.length >= limit || selectedIds.has(question.id)) continue
    const skill = String(question.skill || '').trim()
    if (!skill || seenSkills.has(skill)) continue
    selected.push(question)
    selectedIds.add(question.id)
    seenSkills.add(skill)
  }

  for (const question of pool) {
    if (selected.length >= limit) break
    if (selectedIds.has(question.id)) continue
    selected.push(question)
    selectedIds.add(question.id)
  }

  return selected
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

    // Fetch the complete filtered pool so rows beyond the first page can be served.
    const pool: any[] = []
    for (let offset = 0; ; offset += QUESTION_PAGE_SIZE) {
      let pageQuery = supabase
        .from('brainactive_questions')
        .select('*')
        .eq('is_active', true)
        .order('id', { ascending: true })

      if (topic && topic !== 'All') {
        pageQuery = pageQuery.eq('topic', topic)
      }

      if (level && level !== 'All') {
        pageQuery = pageQuery.eq('level', level)
      }

      const { data: page, error } = await pageQuery.range(offset, offset + QUESTION_PAGE_SIZE - 1)
      if (error) throw error
      pool.push(...(page || []))
      if (!page || page.length < QUESTION_PAGE_SIZE) break
    }

    if (pool.length === 0) {
      return standardResponse(true, [])
    }

    const shuffled = [...pool].sort(() => 0.5 - Math.random())
    const selected = mode === 'quick_test'
      ? selectQuickQuizQuestions(shuffled, Math.min(limit, shuffled.length))
      : shuffled.slice(0, Math.min(limit, shuffled.length))

    return standardResponse(true, selected)
  } catch (err: any) {
    return standardResponse(false, null, { code: 'FETCH_FAILED', message: err.message }, 500)
  }
})
