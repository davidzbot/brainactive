-- ------------------------
-- Harden Security for brainactive schema
-- ------------------------

-- 1. Revoke overly permissive grants
REVOKE ALL ON ALL TABLES IN SCHEMA brainactive FROM anon, authenticated;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA brainactive FROM anon, authenticated;
REVOKE ALL ON SCHEMA brainactive FROM anon, authenticated;

-- 2. Grant USAGE on schema
GRANT USAGE ON SCHEMA brainactive TO anon, authenticated;

-- 3. content_pool: Read-only for everyone
GRANT SELECT ON brainactive.content_pool TO anon, authenticated;

-- 4. user_profile: SELECT, INSERT, UPDATE
-- RLS already protects these, but we shouldn't grant more than needed
GRANT SELECT, INSERT, UPDATE ON brainactive.user_profile TO authenticated;
-- anon might need to check if a referral code exists during registration flow? 
-- But usually handle_new_user is security definer.
GRANT SELECT ON brainactive.user_profile TO anon; 

-- 5. referrals: SELECT, INSERT
GRANT SELECT, INSERT ON brainactive.referrals TO authenticated;

-- 6. Sequences (needed for inserts)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA brainactive TO authenticated;

-- ------------------------
-- Ensure RLS is active and correct
-- ------------------------
ALTER TABLE brainactive.content_pool ENABLE ROW LEVEL SECURITY;
ALTER TABLE brainactive.user_profile ENABLE ROW LEVEL SECURITY;
ALTER TABLE brainactive.referrals ENABLE ROW LEVEL SECURITY;

-- Drop existing if we want to be clean, but usually better to create if not exists or replace
-- For brevity, we assume the init migration did its job, we just double check logic.

-- Content pool should ONLY allow select where is_active = true
DROP POLICY IF EXISTS "public read content" ON brainactive.content_pool;
CREATE POLICY "public read content"
ON brainactive.content_pool
FOR SELECT
TO anon, authenticated
USING (is_active = true);
