-- Student-reported BrainActive question issues.
-- Writes are accepted only through brainactive-report-question using the service role.

CREATE TABLE IF NOT EXISTS public.brainactive_question_issue_reports (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  question_id VARCHAR(64) NOT NULL,
  issue_type VARCHAR(32) NOT NULL,
  detail TEXT,
  reported_by_device_id VARCHAR(128) NOT NULL,
  reported_on TIMESTAMPTZ NOT NULL DEFAULT now(),
  status VARCHAR(32) NOT NULL DEFAULT 'open',
  last_update_on TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT brainactive_question_issue_type_check
    CHECK (issue_type IN ('question', 'answer', 'explanation', 'image', 'other')),
  CONSTRAINT brainactive_question_issue_detail_check
    CHECK (issue_type <> 'other' OR length(trim(coalesce(detail, ''))) > 0)
);

CREATE INDEX IF NOT EXISTS idx_ba_question_issue_reports_question
  ON public.brainactive_question_issue_reports(question_id);

CREATE INDEX IF NOT EXISTS idx_ba_question_issue_reports_status
  ON public.brainactive_question_issue_reports(status);

ALTER TABLE public.brainactive_question_issue_reports ENABLE ROW LEVEL SECURITY;
