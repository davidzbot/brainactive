import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

Deno.serve(async (req) => {
  const supabaseUrl = Deno.env.get('SUPABASE_URL')
  const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')

  const supabase = createClient(supabaseUrl!, supabaseKey!)

  const { data, error } = await supabase
    .schema('brainactive')
    .from('content_pool')
    .select('*')
    .limit(1)

  return new Response(JSON.stringify({ data, error }), { 
    headers: { 'Content-Type': 'application/json' },
    status: 200 
  })
})
