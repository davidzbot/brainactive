-- 0. Schema
create schema if not exists brain_plan;

-- 1. user_profile
create table if not exists brain_plan.user_profile (
  user_id uuid primary key references auth.users(id) on delete cascade,
  referral_code text unique not null,
  created_at timestamptz default now()
);

create index if not exists idx_user_profile_referral_code
on brain_plan.user_profile(referral_code);

-- 2. referrals
create table if not exists brain_plan.referrals (
  id bigserial primary key,
  referrer_user_id uuid not null references auth.users(id) on delete cascade,
  referred_user_id uuid unique not null references auth.users(id) on delete cascade,
  created_at timestamptz default now()
);

create index if not exists idx_referrals_referrer
on brain_plan.referrals(referrer_user_id);

-- 3. content_pool (SIMPLIFIED)
create table if not exists brain_plan.content_pool (
  id bigserial primary key,
  type text not null,          -- 'city', 'sentence', 'name'
  value text not null,         -- simple string or JSON string
  difficulty int null,         -- optional
  is_active boolean default true,
  created_at timestamptz default now()
);

create index if not exists idx_content_pool_type_active
on brain_plan.content_pool(type)
where is_active = true;

-- ------------------------
-- Permissions
-- ------------------------
GRANT USAGE ON SCHEMA brain_plan TO anon, authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA brain_plan TO anon, authenticated;
GRANT INSERT, UPDATE ON ALL TABLES IN SCHEMA brain_plan TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA brain_plan TO anon, authenticated;

-- ------------------------
-- RLS
-- ------------------------
alter table brain_plan.user_profile enable row level security;
alter table brain_plan.referrals enable row level security;
alter table brain_plan.content_pool enable row level security;

-- content: public read
create policy "public read content"
on brain_plan.content_pool
for select
to anon, authenticated
using (is_active = true);

-- user_profile: self access
create policy "user profile select own"
on brain_plan.user_profile
for select
to authenticated
using (auth.uid() = user_id);

create policy "user profile insert own"
on brain_plan.user_profile
for insert
to authenticated
with check (auth.uid() = user_id);

-- ------------------------
-- Auth Triggers
-- ------------------------

-- Function to handle new user signup
create or replace function brain_plan.handle_new_user()
returns trigger as $$
declare
  new_code text;
  code_exists boolean;
begin
  -- Generate a unique 6-character referral code
  loop
    new_code := upper(substring(md5(random()::text) from 1 for 6));
    select exists(select 1 from brain_plan.user_profile where referral_code = new_code) into code_exists;
    exit when not code_exists;
  end loop;

  insert into brain_plan.user_profile (user_id, referral_code)
  values (new.id, new_code);
  return new;
end;
$$ language plpgsql security definer;

-- Trigger to call the function on auth.users insert
create or replace trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure brain_plan.handle_new_user();

-- referrals: insert + read
create policy "insert referral"
on brain_plan.referrals
for insert
to authenticated
with check (auth.uid() = referred_user_id);

create policy "read own referrals"
on brain_plan.referrals
for select
to authenticated
using (
  auth.uid() = referrer_user_id
  or auth.uid() = referred_user_id
);

-- ------------------------
-- Initial Data (content_pool)
-- ------------------------

-- 1. Insert Cities
INSERT INTO brain_plan.content_pool (type, value) VALUES
('city', '北京'), ('city', '上海'), ('city', '广州'), ('city', '深圳'), ('city', '成都'),
('city', '杭州'), ('city', '南京'), ('city', '重庆'), ('city', '西安'), ('city', '武汉'),
('city', '苏黎世'), ('city', '伦敦'), ('city', '巴黎'), ('city', '东京'), ('city', '纽约'),
('city', '悉尼'), ('city', '新加坡'), ('city', '柏林'), ('city', '吉隆坡'), ('city', '曼谷'),
('city', '首尔'), ('city', '台北'), ('city', '香港'), ('city', '澳门'), ('city', '拉萨'),
('city', '乌鲁木齐'), ('city', '哈尔滨'), ('city', '青岛'), ('city', '大连'), ('city', '厦门');

-- 2. Insert Names
INSERT INTO brain_plan.content_pool (type, value) VALUES
('name', '张大伯'), ('name', '王大妈'), ('name', '李老师'), ('name', '赵班长'), ('name', '孙医生'),
('name', '陈会计'), ('name', '刘叔叔'), ('name', '周奶奶'), ('name', '谢师傅'), ('name', '谭大姐'),
('name', '刘备'), ('name', '关羽'), ('name', '张飞'), ('name', '诸葛亮'), ('name', '曹操'),
('name', '孙权'), ('name', '周瑜'), ('name', '司马懿'), ('name', '孙悟空'), ('name', '唐僧'),
('name', '猪八戒'), ('name', '沙僧'), ('name', '宋江'), ('name', '林冲'), ('name', '武松');

-- 3. Insert Sentences (Stored as JSON strings)
INSERT INTO brain_plan.content_pool (type, value) VALUES
('sentence', '{"t": "今天早上去市场买新鲜蔬菜", "w": "今天早上去市厂买新鲜蔬菜"}'),
('sentence', '{"t": "下午在公园慢慢散步放松心情", "w": "下午在公圆慢慢散步放松心情"}'),
('sentence', '{"t": "晚上和朋友一起聊天喝茶", "w": "晚上和明友一起聊天喝茶"}'),
('sentence', '{"t": "周末带家人出去吃饭放松", "w": "周末带家人出去契饭放松"}'),
('sentence', '{"t": "早上锻炼身体让精神更好", "w": "早上锻陈身体让精神更好"}'),
('sentence', '{"t": "晚饭后散步有助于健康", "w": "晚饭后散步有助干健康"}'),
('sentence', '{"t": "读书可以提升记忆能力", "w": "读书可以提升记意能力"}'),
('sentence', '{"t": "规律作息让大脑更清醒", "w": "规律作息让大脑更情醒"}'),
('sentence', '{"t": "坚持运动能增强身体素质", "w": "坚持运动能增虽身体素质"}'),
('sentence', '{"t": "多吃水果蔬菜对身体有益", "w": "多吃水果梳菜对身体有益"}');
