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
      source: 'brainactive-submit-attempt'
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

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL') || ''
    const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || Deno.env.get('SUPABASE_ANON_KEY') || ''
    const supabase = createClient(supabaseUrl, supabaseServiceKey)

    const payload = await req.json()
    const {
      user_id,
      attempts, // Array of { question_id, selected_answer, is_correct, time_spent_ms, topic, level }
      session_id,
      mode = 'quick_test'
    } = payload

    if (!user_id || !Array.isArray(attempts) || attempts.length === 0) {
      return standardResponse(false, null, { code: 'INVALID_PAYLOAD', message: 'Missing user_id or attempts' }, 400)
    }

    const todaySgt = getSgtDateString()

    // 1. Insert attempts
    const attemptsToInsert = attempts.map(att => ({
      user_id,
      question_id: att.question_id,
      selected_answer: att.selected_answer,
      is_correct: !!att.is_correct,
      time_spent_ms: att.time_spent_ms || 0,
      session_id: session_id || null,
      mode,
      topic: att.topic || null,
      level: att.level || null,
      created_at: new Date().toISOString()
    }))

    const { error: insertErr } = await supabase
      .from('brainactive_attempts')
      .insert(attemptsToInsert)

    if (insertErr) {
      console.error('Failed to insert attempts:', insertErr)
    }

    // 2. Fetch existing progress
    const { data: existingProgress } = await supabase
      .from('brainactive_progress')
      .select('*')
      .eq('user_id', user_id)
      .maybeSingle()

    let streak = existingProgress?.streak_count || 0
    const lastActive = existingProgress?.last_active_date || ''
    const totalAns = (existingProgress?.total_questions_answered || 0) + attempts.length
    const correctCount = attempts.filter(a => a.is_correct).length
    const totalCorr = (existingProgress?.total_correct || 0) + correctCount

    let dailyRounds = existingProgress?.daily_rounds_completed || 0
    let lastDailyDate = existingProgress?.last_daily_round_date || ''

    if (lastDailyDate !== todaySgt) {
      dailyRounds = 1
      lastDailyDate = todaySgt
    } else {
      dailyRounds += 1
    }

    // Streak logic: check if consecutive day
    if (!lastActive) {
      streak = 1
    } else if (lastActive === todaySgt) {
      // already active today, keep streak
    } else {
      const lastDate = new Date(lastActive)
      const currDate = new Date(todaySgt)
      const diffDays = Math.round((currDate.getTime() - lastDate.getTime()) / (1000 * 3600 * 24))
      if (diffDays === 1) {
        streak += 1
      } else {
        streak = 1
      }
    }

    const progressRecord = {
      user_id,
      streak_count: streak,
      last_active_date: todaySgt,
      total_questions_answered: totalAns,
      total_correct: totalCorr,
      daily_rounds_completed: dailyRounds,
      last_daily_round_date: lastDailyDate,
      updated_at: new Date().toISOString()
    }

    const { error: upsertErr } = await supabase
      .from('brainactive_progress')
      .upsert(progressRecord, { onConflict: 'user_id' })

    if (upsertErr) {
      console.error('Failed to update progress:', upsertErr)
    }

    return standardResponse(true, {
      streak,
      daily_rounds_completed: dailyRounds,
      total_questions: totalAns,
      total_correct: totalCorr,
      session_correct: correctCount,
      session_total: attempts.length
    })
  } catch (err: any) {
    return standardResponse(false, null, { code: 'SUBMIT_FAILED', message: err.message }, 500)
  }
})
