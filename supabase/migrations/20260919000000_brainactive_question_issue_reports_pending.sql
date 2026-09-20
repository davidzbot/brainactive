-- Admin dashboard Pending Issues view for BrainActive.
-- Read by C:\Projects\vercel\admin.html (loadPendingIssues) with the anon key
-- as view public.brainactive_question_issue_reports_pending.
-- Same read-only pattern as question_issue_reports_pending / math_question_issue_reports_pending:
-- view runs with owner privileges, RLS on the base report table is bypassed
-- for the view WITHOUT changing any RLS policy. No device/user columns exposed.
-- Output columns intentionally match admin.html VIEW_COLS:
--   question_id,issue,reported_on,status,school,subject,question_number,question_text
-- (+ id, last_update_on for debugging; PostgREST can select a subset).

create or replace view public.brainactive_question_issue_reports_pending as
select
  r.id,
  r.question_id,
  trim(concat_ws(': ', r.issue_type, nullif(trim(r.detail), ''))) as issue,
  r.reported_on,
  r.status,
  r.last_update_on,
  r.question_id as question_number,
  q.question as question_text,
  q.topic as subject,
  q.domain as school
from public.brainactive_question_issue_reports r
left join public.brainactive_questions q on q.id = r.question_id
where r.status = 'open'
order by r.reported_on desc;

grant select on public.brainactive_question_issue_reports_pending to anon;
