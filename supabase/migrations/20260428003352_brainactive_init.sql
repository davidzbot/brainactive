-- -----------------------------------------------------------------------------
-- BrainActive Supabase Setup (Replicated from brain-plan)
-- Supports Dual Language (EN/ZH) for Static Data
-- -----------------------------------------------------------------------------

-- 0. Schema
create schema if not exists brainactive;

-- 1. user_profile
create table if not exists brainactive.user_profile (
  user_id uuid primary key references auth.users(id) on delete cascade,
  referral_code text unique not null,
  created_at timestamptz default now()
);

create index if not exists idx_user_profile_referral_code
on brainactive.user_profile(referral_code);

-- 2. referrals
create table if not exists brainactive.referrals (
  id bigserial primary key,
  referrer_user_id uuid not null references auth.users(id) on delete cascade,
  referred_user_id uuid unique not null references auth.users(id) on delete cascade,
  created_at timestamptz default now()
);

create index if not exists idx_referrals_referrer
on brainactive.referrals(referrer_user_id);

-- 3. content_pool (Bilingual Support)
create table if not exists brainactive.content_pool (
  id bigserial primary key,
  type text not null,                -- 'city', 'sentence', 'name', 'tip'
  value text not null,               -- string or JSON string
  language text not null default 'en', -- 'en' or 'zh'
  difficulty int null,               -- optional: 1 (easy), 2 (normal), 3 (pro)
  is_active boolean default true,
  created_at timestamptz default now()
);

create index if not exists idx_content_pool_type_lang_active
on brainactive.content_pool(type, language)
where is_active = true;

-- ------------------------
-- Permissions
-- ------------------------
GRANT USAGE ON SCHEMA brainactive TO anon, authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA brainactive TO anon, authenticated;
GRANT INSERT, UPDATE ON ALL TABLES IN SCHEMA brainactive TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA brainactive TO anon, authenticated;

-- ------------------------
-- RLS (Row Level Security)
-- ------------------------
alter table brainactive.user_profile enable row level security;
alter table brainactive.referrals enable row level security;
alter table brainactive.content_pool enable row level security;

-- content: public read
create policy "public read content"
on brainactive.content_pool
for select
to anon, authenticated
using (is_active = true);

-- user_profile: self access
create policy "user profile select own"
on brainactive.user_profile
for select
to authenticated
using (auth.uid() = user_id);

create policy "user profile insert own"
on brainactive.user_profile
for insert
to authenticated
with check (auth.uid() = user_id);

-- ------------------------
-- Auth Triggers
-- ------------------------

-- Function to handle new user signup for brainactive
create or replace function brainactive.handle_new_user()
returns trigger as $$
declare
  new_code text;
  code_exists boolean;
begin
  loop
    new_code := upper(substring(md5(random()::text) from 1 for 6));
    select exists(select 1 from brainactive.user_profile where referral_code = new_code) into code_exists;
    exit when not code_exists;
  end loop;

  insert into brainactive.user_profile (user_id, referral_code)
  values (new.id, new_code);
  return new;
end;
$$ language plpgsql security definer;

-- Trigger to call the function on auth.users insert
create or replace trigger on_auth_user_created_brainactive
  after insert on auth.users
  for each row execute procedure brainactive.handle_new_user();

-- referrals: insert + read
create policy "insert referral"
on brainactive.referrals
for insert
to authenticated
with check (auth.uid() = referred_user_id);

create policy "read own referrals"
on brainactive.referrals
for select
to authenticated
using (
  auth.uid() = referrer_user_id
  or auth.uid() = referred_user_id
);

-- ------------------------
-- Initial Data (Dual Language)
-- ------------------------

-- 1. Insert Names (English - Humor & Pro)
INSERT INTO brainactive.content_pool (type, value, language) VALUES
('name', 'Professor Snape', 'en'), ('name', 'Captain Jack', 'en'), ('name', 'Dr. Strange', 'en'),
('name', 'Sherlock Holmes', 'en'), ('name', 'Wonder Woman', 'en'), ('name', 'Iron Man', 'en'),
('name', 'Elon Musk', 'en'), ('name', 'Master Yoda', 'en'), ('name', 'SpongeBob SquarePants', 'en'),
('name', 'Gordon Ramsay', 'en'), ('name', 'Rick Sanchez', 'en'), ('name', 'Walter White', 'en');

-- 2. Insert Names (Chinese)
INSERT INTO brainactive.content_pool (type, value, language) VALUES
('name', '张大伯', 'zh'), ('name', '王大妈', 'zh'), ('name', '李老师', 'zh'),
('name', '诸葛亮', 'zh'), ('name', '孙悟空', 'zh'), ('name', '曹操', 'zh');

-- 3. Insert Cities (English - Exotic & Fun)
INSERT INTO brainactive.content_pool (type, value, language) VALUES
('city', 'Hogwarts', 'en'), ('city', 'Gotham City', 'en'), ('city', 'Wakanda', 'en'),
('city', 'Silicon Valley', 'en'), ('city', 'Bermuda Triangle', 'en'), ('city', 'Mount Everest', 'en'),
('city', 'Tokyo', 'en'), ('city', 'Paris', 'en'), ('city', 'New York', 'en');

-- 4. Insert Cities (Chinese)
INSERT INTO brainactive.content_pool (type, value, language) VALUES
('city', '北京', 'zh'), ('city', '上海', 'zh'), ('city', '广州', 'zh'),
('city', '香港', 'zh'), ('city', '台北', 'zh'), ('city', '拉萨', 'zh');

-- 5. Insert Sentences (English - Humorous/Relatable)
INSERT INTO brainactive.content_pool (type, value, language) VALUES
('sentence', '{"t": "My cat is judging my life choices again", "w": "My cat is judging my life choises again"}', 'en'),
('sentence', '{"t": "I came into this room and forgot why", "w": "I came into this room and forgot whyy"}', 'en'),
('sentence', '{"t": "Coffee: because adulting is hard without it", "w": "Cofee: because adulting is hard without it"}', 'en'),
('sentence', '{"t": "I put the pro in procrastination today", "w": "I put the pro in procrustination today"}', 'en');

-- 6. Insert Sentences (Chinese)
INSERT INTO brainactive.content_pool (type, value, language) VALUES
('sentence', '{"t": "今天早上去市场买新鲜蔬菜", "w": "今天早上去市厂买新鲜蔬菜"}', 'zh'),
('sentence', '{"t": "下午在公园慢慢散步放松心情", "w": "下午在公圆慢慢散步放松心情"}', 'zh');

-- 7. Insert Tips (English)
INSERT INTO brainactive.content_pool (type, value, language) VALUES
('tip', 'Use it or lose it! Your brain isn''t a museum piece 🧠', 'en'),
('tip', 'Hydrate! A dry brain is basically a raisin in a skull 💧', 'en'),
('tip', 'Move a bit! Don''t let your brain enter Infinite Loading mode ⚡', 'en');

-- 8. Insert Tips (Chinese)
INSERT INTO brainactive.content_pool (type, value, language) VALUES
('tip', '大脑不用，会慢慢''生锈'' 🧠', 'zh'),
('tip', '多喝水，不然脑子容易''卡顿中…''', 'zh');
