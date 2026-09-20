-- Source-backed repairs for the Brainactive question issue workflow.
-- BA_P3_0801's existing asset used W/X/V/Z while the question and visual_spec
-- use F/B/C/E. The corrected asset is uploaded to the existing ID-matched path.
update public.brainactive_questions
set qa_status = 'repaired_report_20260920',
    updated_at = now()
where id = 'BA_P3_0801'
  and question = 'A cube net: centre D, with F above, C below, B left, E right, and A below C. Folded with D as front, which square is the BACK face?'
  and answer = 'D'
  and image_path = 'p3/BA_P3_0801.svg';

update public.brainactive_question_issue_reports
set status = 'resolved',
    last_update_on = now()
where id = '6f5ca8ce-54e5-4dcc-8021-185ed61410ca'
  and question_id = 'BA_P3_0801'
  and status = 'open';

update public.brainactive_question_issue_reports
set status = 'reviewed_correct',
    last_update_on = now()
where id in (
  '6b29b1de-b41a-4a85-aa18-07ce93f12e4c',
  '718a2da8-33f3-4c56-be5c-9cd2f8a6c593',
  'ea4a21ff-71ae-4f39-9693-c8a6fa9f4fe9',
  'ffcf5865-667a-43cc-b666-73bbb07341ab'
)
  and status = 'open';

-- Proactive audit repairs: these rows reused generic visuals belonging to
-- neighboring source questions. Each now has an ID-matched, source-aligned asset.
update public.brainactive_questions
set image_path = 'p3/' || id || '.svg',
    qa_status = 'repaired_visual_audit_20260920',
    updated_at = now()
where id in (
  'BA_P3_2350', 'BA_P3_2356', 'BA_P3_2361', 'BA_P3_2375',
  'BA_P3_2389', 'BA_P3_2390', 'BA_P3_2391', 'BA_P3_2392', 'BA_P3_2393'
)
and is_active = true
and image_path in ('p3/BA_P3_2345.svg', 'p3/BA_P3_2388.svg');
