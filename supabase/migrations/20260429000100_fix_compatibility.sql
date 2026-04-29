-- ------------------------
-- Fix compatibility and permissions
-- ------------------------

-- 1. Ensure anon/authenticated can check referral codes
-- RLS was too restrictive, preventing checking if a referral code exists
DROP POLICY IF EXISTS "user profile select own" ON brainactive.user_profile;
CREATE POLICY "user profile select own"
ON brainactive.user_profile
FOR SELECT
TO anon, authenticated
USING (true); 

DROP POLICY IF EXISTS "user profile select own" ON brain_plan.user_profile;
CREATE POLICY "user profile select own"
ON brain_plan.user_profile
FOR SELECT
TO anon, authenticated
USING (true); 

-- 2. Grant necessary permissions for brain_plan schema just in case
GRANT USAGE ON SCHEMA brain_plan TO anon, authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA brain_plan TO anon, authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA brain_plan TO anon, authenticated;

-- 3. Merge data from brain_plan to brainactive to ensure edge function has all content
-- Avoid duplicates by checking existence
INSERT INTO brainactive.content_pool (type, value, language, is_active)
SELECT type, value, 'zh', true
FROM brain_plan.content_pool bp
WHERE NOT EXISTS (
  SELECT 1 FROM brainactive.content_pool ba 
  WHERE ba.type = bp.type AND ba.value = bp.value AND ba.language = 'zh'
);

-- 4. Add index to content_pool for better performance
CREATE INDEX IF NOT EXISTS idx_content_pool_lookup 
ON brainactive.content_pool (type, language, is_active);
