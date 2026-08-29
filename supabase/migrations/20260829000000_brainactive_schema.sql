-- =============================================================================
-- BrainActive Isolated Schema Migration (2026-08-29)
-- Complete isolation from MathHero and PSLE tables
-- Target: Singapore Primary 3 High Ability / Thinking Skills Practice
-- =============================================================================

-- 1. Create Schema if needed
CREATE SCHEMA IF NOT EXISTS brainactive;

-- 2. Dedicated Questions Table
CREATE TABLE IF NOT EXISTS public.brainactive_questions (
    id VARCHAR(64) PRIMARY KEY,
    domain VARCHAR(64) NOT NULL,
    topic VARCHAR(64) NOT NULL,
    skill VARCHAR(32) NOT NULL,
    archetype VARCHAR(64) NOT NULL,
    level VARCHAR(32) NOT NULL DEFAULT 'Think',
    difficulty VARCHAR(32) NOT NULL DEFAULT 'medium',
    question_type VARCHAR(32) NOT NULL DEFAULT 'multiple_choice',
    question TEXT NOT NULL,
    options JSONB NOT NULL,
    answer VARCHAR(8) NOT NULL,
    explanation TEXT NOT NULL,
    reasoning TEXT,
    tags TEXT[] DEFAULT '{}',
    visual_required BOOLEAN DEFAULT FALSE,
    visual_spec JSONB,
    image_path TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ba_questions_domain_level ON public.brainactive_questions(domain, level) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_ba_questions_topic_level ON public.brainactive_questions(topic, level) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_ba_questions_skill ON public.brainactive_questions(skill) WHERE is_active = TRUE;

-- 3. Dedicated User Profiles Table
CREATE TABLE IF NOT EXISTS public.brainactive_profiles (
    user_id VARCHAR(128) PRIMARY KEY,
    referral_code VARCHAR(16) UNIQUE NOT NULL,
    is_pro BOOLEAN DEFAULT FALSE,
    pro_expiry TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ba_profiles_referral_code ON public.brainactive_profiles(referral_code);

-- 4. Dedicated Referrals Table
CREATE TABLE IF NOT EXISTS public.brainactive_referrals (
    id BIGSERIAL PRIMARY KEY,
    referrer_user_id VARCHAR(128) NOT NULL,
    referred_user_id VARCHAR(128) UNIQUE NOT NULL,
    reward_days INT DEFAULT 7,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ba_referrals_referrer ON public.brainactive_referrals(referrer_user_id);

-- 5. Dedicated User Attempts Table
CREATE TABLE IF NOT EXISTS public.brainactive_attempts (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(128) NOT NULL,
    question_id VARCHAR(64) NOT NULL REFERENCES public.brainactive_questions(id) ON DELETE CASCADE,
    selected_answer VARCHAR(8),
    is_correct BOOLEAN NOT NULL,
    time_spent_ms INT DEFAULT 0,
    session_id VARCHAR(64),
    mode VARCHAR(32) DEFAULT 'quick_test', -- 'quick_test' or 'pro_practice'
    topic VARCHAR(64),
    level VARCHAR(32),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ba_attempts_user_time ON public.brainactive_attempts(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ba_attempts_session ON public.brainactive_attempts(session_id);

-- 6. Dedicated User Progress & Streak Table
CREATE TABLE IF NOT EXISTS public.brainactive_progress (
    user_id VARCHAR(128) PRIMARY KEY,
    streak_count INT DEFAULT 0,
    last_active_date VARCHAR(16), -- 'YYYY-MM-DD' (Singapore Time SGT)
    total_questions_answered INT DEFAULT 0,
    total_correct INT DEFAULT 0,
    daily_rounds_completed INT DEFAULT 0,
    last_daily_round_date VARCHAR(16),
    bonus_rounds_unlocked INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. Dedicated Storage Bucket Registration
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'brainactive-assets',
    'brainactive-assets',
    TRUE,
    5242880, -- 5MB
    ARRAY['image/svg+xml', 'image/png', 'image/jpeg', 'image/webp']
)
ON CONFLICT (id) DO UPDATE
SET public = TRUE;

-- Storage Policy: Public Read for BrainActive Assets
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'objects' AND schemaname = 'storage' AND policyname = 'BrainActive Assets Public Access'
    ) THEN
        CREATE POLICY "BrainActive Assets Public Access"
        ON storage.objects FOR SELECT
        TO anon, authenticated
        USING (bucket_id = 'brainactive-assets');
    END IF;
END $$;

-- 8. Row Level Security (RLS) & Permissions
ALTER TABLE public.brainactive_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.brainactive_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.brainactive_referrals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.brainactive_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.brainactive_progress ENABLE ROW LEVEL SECURITY;

-- Public Read for Active Questions
CREATE POLICY "Public read active questions"
ON public.brainactive_questions FOR SELECT
TO anon, authenticated
USING (is_active = TRUE);

-- Profiles: Public Read/Write via Edge Functions & Anon/Authenticated
CREATE POLICY "User profiles self access"
ON public.brainactive_profiles FOR ALL
TO anon, authenticated
USING (TRUE)
WITH CHECK (TRUE);

-- Referrals: Public Insert/Select
CREATE POLICY "Referrals access"
ON public.brainactive_referrals FOR ALL
TO anon, authenticated
USING (TRUE)
WITH CHECK (TRUE);

-- Attempts: Public Insert/Select by user_id
CREATE POLICY "Attempts access"
ON public.brainactive_attempts FOR ALL
TO anon, authenticated
USING (TRUE)
WITH CHECK (TRUE);

-- Progress: Public Insert/Select by user_id
CREATE POLICY "Progress access"
ON public.brainactive_progress FOR ALL
TO anon, authenticated
USING (TRUE)
WITH CHECK (TRUE);

-- Explicit grants limited to BrainActive objects only.
-- Deliberately NOT schema-wide: no effect on any existing PSLE/MathHero tables.
GRANT SELECT ON public.brainactive_questions TO anon, authenticated;
GRANT ALL ON public.brainactive_profiles TO anon, authenticated;
GRANT ALL ON public.brainactive_referrals TO anon, authenticated;
GRANT ALL ON public.brainactive_attempts TO anon, authenticated;
GRANT ALL ON public.brainactive_progress TO anon, authenticated;
GRANT USAGE, SELECT ON SEQUENCE public.brainactive_referrals_id_seq TO anon, authenticated;
GRANT USAGE, SELECT ON SEQUENCE public.brainactive_attempts_id_seq TO anon, authenticated;
