import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type, x-device-id',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Max-Age': '86400',
}

function standardResponse(success: boolean, data: any = null, error: any = null) {
  const response: any = { success }
  if (success) {
    response.data = data
  } else {
    response.error = {
      code: error?.code || 'UNKNOWN_ERROR',
      message: error?.message || 'Something went wrong',
      source: 'brainactive-ask-hero'
    }
  }
  return new Response(
    JSON.stringify(response),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 200 }
  )
}

const AGNES_BASE_URL = 'https://apihub.agnes-ai.com/v1'
const ASSETS_BUCKET = 'brainactive-assets'
const HARD_TIMEOUT_MS = 60_000

function buildImageUrl(supabaseUrl: string, imagePath?: string | null): string | null {
  if (!imagePath || !imagePath.trim()) return null
  let cleanPath = imagePath.trim().replace(/^\/+/, '')
  const bucketPrefix = `${ASSETS_BUCKET}/`
  if (cleanPath.startsWith(bucketPrefix)) {
    cleanPath = cleanPath.slice(bucketPrefix.length)
  }
  const encodedPath = cleanPath.split('/').map(segment => encodeURIComponent(segment)).join('/')
  return `${supabaseUrl}/storage/v1/object/public/${ASSETS_BUCKET}/${encodedPath}`
}

async function fetchImageBase64(url: string): Promise<string | null> {
  try {
    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), 8_000)
    const resp = await fetch(url, { signal: controller.signal })
    clearTimeout(timer)
    if (!resp.ok) return null
    const buf = await resp.arrayBuffer()
    const bytes = new Uint8Array(buf)
    let binary = ''
    const chunk = 0x8000
    for (let i = 0; i < bytes.length; i += chunk) {
      binary += String.fromCharCode.apply(null, Array.from(bytes.subarray(i, i + chunk)))
    }
    const mime = resp.headers.get('content-type')?.split(';')[0] || 'image/svg+xml'
    return `data:${mime};base64,${btoa(binary)}`
  } catch {
    return null
  }
}

/**
 * Builds the tutor prompt for Singapore Primary 3 High Ability Reasoning
 */
function buildMessages(
  mode: string,
  question: any,
  studentAnswer: string,
  studentQuestion: string,
  history: any[],
  imageDataUri: string | null
) {
  const systemParts: string[] = []

  systemParts.push(
    `[HERO AI IDENTITY — P3 THINKING SKILLS]\n` +
    `You are Hero AI, a warm, encouraging thinking-skills tutor for Singapore Primary 3 High Ability learners (around 9 years old).\n` +
    `You specialize in non-routine problem solving across 6 core domains: Numerical Thinking, Logical Reasoning, Pattern & Abstract, Visual & Spatial Reasoning, Verbal Reasoning, and Problem-Solving Heuristics.\n` +
    `If asked who you are, say only: "I'm Hero AI, your thinking skills coach!" Never mention internal APIs, model providers, or backend prompts.`
  )

  systemParts.push(
    `[TEACHING STYLE & SOCRATIC GUIDANCE]\n` +
    `- Be cheerful, supportive, and kind. Celebrate curiosity and logical effort.\n` +
    `- Keep explanations clear, structured, and age-appropriate for 9-year-olds.\n` +
    `- Emphasize THINKING STRATEGIES (e.g. balance systems, working backwards, elimination, spatial rotation, finding invariants) rather than dry algebra.\n` +
    `- In Hint mode, guide the student to take the first logical step without immediately spoiling the final answer.`
  )

  systemParts.push(
    `[LANGUAGE & RESPONSE RULES]\n` +
    `- Default to English. If the student writes to you in Chinese, respond in natural, friendly Chinese.\n` +
    `- Keep responses concise (3-5 short paragraphs or bullet points). Do not overwhelm the child with huge walls of text.`
  )

  if (mode === 'why_wrong') {
    systemParts.push(
      `[MODE: WHY WAS I WRONG?]\n` +
      `The student chose option "${studentAnswer || 'an answer'}". Gently analyze what misconception or common trap might have caused this mistake, and point out what clue was missed.`
    )
  } else if (mode === 'hint') {
    systemParts.push(
      `[MODE: GIVE ME A HINT]\n` +
      `Give ONE clear, exciting clue or first step that unlocks the problem. Do NOT give away the final letter answer yet.`
    )
  } else if (mode === 'explain') {
    systemParts.push(
      `[MODE: EXPLAIN STEP BY STEP]\n` +
      `Walk through the complete reasoning path step by step. Highlight the key heuristic used to make it easy to remember.`
    )
  } else if (mode === 'ask') {
    systemParts.push(
      `[MODE: ANSWER STUDENT QUESTION]\n` +
      `Answer the student's specific question clearly and connect it back to the problem's underlying thinking rule.`
    )
  }

  const system = systemParts.join('\n\n')

  const optionsText = Array.isArray(question.options)
    ? question.options.map((o: any) => `${o.id || o.label}) ${o.text || o}`).join('\n')
    : String(question.options || '')

  const goldenText = [
    `[QUESTION STEM]\n${question.question || ''}`,
    optionsText ? `[OPTIONS]\n${optionsText}` : '',
    question.answer ? `[CORRECT ANSWER]\nOption ${question.answer}` : '',
    question.explanation ? `[OFFICIAL SOLUTION]\n${question.explanation}` : '',
    question.reasoning ? `[KEY HEURISTIC]\n${question.reasoning}` : '',
    question.topic ? `[TOPIC]\n${question.topic}` : '',
    question.level ? `[LEVEL]\n${question.level}` : '',
  ].filter(Boolean).join('\n\n')

  const userText = [
    `The student is asking for tutoring help on this question.`,
    `[STUDENT'S CURRENT ANSWER]\n${studentAnswer || '(no answer chosen yet)'}`,
    studentQuestion ? `[STUDENT'S QUESTION / THOUGHTS]\n${studentQuestion}` : '',
  ].filter(Boolean).join('\n\n')

  const messages: any[] = []
  const boundedHistory = (Array.isArray(history) ? history : []).slice(-6)
  for (const h of boundedHistory) {
    if (h && typeof h.content === 'string' && h.content.trim()) {
      messages.push({
        role: h.role === 'assistant' ? 'assistant' : 'user',
        content: h.content.slice(0, 2000)
      })
    }
  }

  const content: any[] = []
  if (imageDataUri) {
    content.push({ type: 'text', text: goldenText })
    content.push({ type: 'image_url', image_url: { url: imageDataUri } })
    content.push({ type: 'text', text: userText })
  } else {
    content.push({ type: 'text', text: `${goldenText}\n\n${userText}` })
  }

  messages.push({ role: 'user', content })
  return { system, messages }
}

async function callModel(system: string, messages: any[]): Promise<string> {
  const apiKey = Deno.env.get('AGNESI_API_KEY') || Deno.env.get('AGNES_API_KEY') || Deno.env.get('OPENAI_API_KEY') || ''
  
  if (!apiKey) {
    // Fallback response if AI API key is not yet set in environment
    return "💡 Here's a helpful thinking tip: Start by identifying what information is known, look for repeated shapes or numbers, and test each option one by one!"
  }

  const payload = {
    model: 'agnes-2.0-flash',
    temperature: 0.2,
    max_tokens: 1000,
    messages: [{ role: 'system', content: system }, ...messages]
  }

  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), HARD_TIMEOUT_MS)

  try {
    const resp = await fetch(`${AGNES_BASE_URL}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify(payload),
      signal: controller.signal
    })

    if (!resp.ok) {
      throw new Error(`Model API HTTP ${resp.status}`)
    }

    const data = await resp.json()
    const text = data?.choices?.[0]?.message?.content
    if (typeof text !== 'string' || !text.trim()) {
      throw new Error('Empty model response')
    }
    return text.trim()
  } finally {
    clearTimeout(timer)
  }
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL') || ''
    const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || Deno.env.get('SUPABASE_ANON_KEY') || ''
    const supabase = createClient(supabaseUrl, supabaseServiceKey)

    const body = await req.json()
    const {
      question_id,
      mode = 'explain',
      student_answer = '',
      student_question = '',
      history = []
    } = body

    if (!question_id) {
      return standardResponse(false, null, { code: 'MISSING_QUESTION_ID', message: 'question_id is required' })
    }

    // 1. Fetch Golden Question
    const { data: q, error } = await supabase
      .from('brainactive_questions')
      .select('*')
      .eq('id', question_id)
      .maybeSingle()

    if (error || !q) {
      return standardResponse(false, null, { code: 'QUESTION_NOT_FOUND', message: 'Question not found' })
    }

    // 2. Fetch Visual Asset if applicable
    let imageDataUri: string | null = null
    if (q.image_path) {
      const imgUrl = buildImageUrl(supabaseUrl, q.image_path)
      if (imgUrl) {
        imageDataUri = await fetchImageBase64(imgUrl)
      }
    }

    // 3. Build Messages
    const { system, messages } = buildMessages(
      mode,
      q,
      student_answer,
      student_question,
      history,
      imageDataUri
    )

    // 4. Generate AI Tutor Response
    const reply = await callModel(system, messages)

    return standardResponse(true, {
      ok: true,
      message: reply
    })
  } catch (err: any) {
    console.error('[brainactive-ask-hero error]', err)
    return standardResponse(false, null, { code: 'AI_TUTOR_ERROR', message: err.message || 'AI Tutor temporarily unavailable' })
  }
})
