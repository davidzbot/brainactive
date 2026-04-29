import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

Deno.serve(async (req) => {
  const supabaseUrl = Deno.env.get('SUPABASE_URL')
  const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')

  console.log('SERVICE KEY EXISTS', !!supabaseKey)

  const supabase = createClient(supabaseUrl!, supabaseKey!)

  const { data, error } = await supabase
    .schema('brainactive')
    .from('content_pool')
    .select('*')
    .limit(1)

  console.log('DATA', data)
  console.log('ERROR', error)

  return new Response(JSON.stringify({ data, error, service_key_exists: !!supabaseKey }), { 
    headers: { 'Content-Type': 'application/json' },
    status: 200 
  })
})
