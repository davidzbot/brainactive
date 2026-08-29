SELECT 'questions_total' AS k, count(*)::text AS v FROM public.brainactive_questions
UNION ALL SELECT 'questions_active', count(*)::text FROM public.brainactive_questions WHERE is_active
UNION ALL SELECT 'qa_ai_gen', count(*)::text FROM public.brainactive_questions WHERE qa_status='ai_generated_not_approved'
UNION ALL SELECT 'qa_regen', count(*)::text FROM public.brainactive_questions WHERE qa_status='regenerated_pending_ai1'
UNION ALL SELECT 'qa_validated', count(*)::text FROM public.brainactive_questions WHERE qa_status='validated_baseline_v041'
UNION ALL SELECT 'rls_on', count(*)::text FROM pg_tables t
  JOIN pg_class c ON c.relname=t.tablename AND c.relnamespace=(SELECT oid FROM pg_namespace WHERE nspname='public')
  WHERE t.schemaname='public' AND t.tablename LIKE 'brainactive_%' AND c.relrowsecurity;
