import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type, x-device-id',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
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
      source: 'brainactive-report-question',
    }
  }
  return new Response(JSON.stringify(response), {
    headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    status,
  })
}

const allowedIssueTypes = new Set(['question', 'answer', 'explanation', 'image', 'other'])

Deno.serve(async req => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: corsHeaders })
  if (req.method !== 'POST') {
    return standardResponse(false, null, { code: 'METHOD_NOT_ALLOWED', message: 'Only POST is supported' }, 405)
  }

  try {
    const deviceId = req.headers.get('x-device-id')?.trim() || ''
    if (!deviceId || deviceId === 'unknown-device' || deviceId.length > 128) {
      return standardResponse(false, null, { code: 'AUTH_MISSING_ID', message: 'Valid x-device-id is required' }, 400)
    }

    const body = await req.json().catch(() => ({}))
    const questionId = typeof body?.question_id === 'string' ? body.question_id.trim() : ''
    const issueType = typeof body?.issue_type === 'string' ? body.issue_type.trim() : ''
    const detail = typeof body?.detail === 'string' ? body.detail.trim() : ''

    if (!questionId || questionId.length > 64) {
      return standardResponse(false, null, { code: 'VALIDATION_ERROR', message: 'question_id must be a non-empty string of at most 64 characters' }, 400)
    }
    if (!allowedIssueTypes.has(issueType)) {
      return standardResponse(false, null, { code: 'VALIDATION_ERROR', message: 'Unsupported issue_type' }, 400)
    }
    if (detail.length > 300) {
      return standardResponse(false, null, { code: 'VALIDATION_ERROR', message: 'detail is too long' }, 400)
    }
    if (issueType === 'other' && !detail) {
      return standardResponse(false, null, { code: 'VALIDATION_ERROR', message: 'detail is required for other reports' }, 400)
    }

    const supabaseUrl = Deno.env.get('SUPABASE_URL') || ''
    const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || ''
    if (!supabaseUrl || !serviceRoleKey) {
      return standardResponse(false, null, { code: 'SERVER_CONFIG_ERROR', message: 'Report service is not configured' }, 500)
    }

    const supabase = createClient(supabaseUrl, serviceRoleKey)
    const { error } = await supabase.from('brainactive_question_issue_reports').insert({
      question_id: questionId,
      issue_type: issueType,
      detail: detail || null,
      reported_by_device_id: deviceId,
    })

    if (error) {
      console.error('[brainactive-report-question] Insert error:', error.message)
      return standardResponse(false, null, { code: 'DATABASE_ERROR', message: 'Could not save report' }, 500)
    }

    return standardResponse(true, { recorded: true })
  } catch (error: any) {
    console.error('[brainactive-report-question] Unexpected error:', error?.message)
    return standardResponse(false, null, { code: 'SERVER_ERROR', message: 'Could not save report' }, 500)
  }
})
