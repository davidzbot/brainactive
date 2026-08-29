import re, glob, os, sys

mig = 'C:/Projects/brainactive-android/supabase/migrations/20260829000000_brainactive_schema.sql'
raw = open(mig, encoding='utf-8').read()
lines = raw.splitlines()

# 1) Strip -- comments, then split into statements by ';'
no_comment_lines = []
for l in lines:
    # remove trailing comment
    idx = l.find('--')
    no_comment_lines.append(l[:idx] if idx != -1 else l)
stripped = '\n'.join(no_comment_lines)

# mathhero/psle must NOT appear outside comments
if re.search(r'mathhero|psle', stripped.lower()):
    print('FAIL: mathhero/psle referenced outside a comment (real statement):')
    for i, l in enumerate(stripped.splitlines(), 1):
        if re.search(r'mathhero|psle', l.lower()):
            print('   L', i, l.strip())
    sys.exit(1)
else:
    print('OK: no mathhero/psle reference in actual statements (only a doc comment, if any).')

# split into statements
stmts = [s.strip() for s in stripped.split(';') if s.strip()]

problems = []
allowed = []

def is_ba_table(s):
    return bool(re.search(r'\bbrainactive_[a-z_]+\b', s.lower()))

for s in stmts:
    low = s.lower()
    # DROP
    if re.search(r'^\s*drop\b', low):
        problems.append('DROP found: ' + s[:80])
    # GRANT
    if low.startswith('grant '):
        if 'brainactive_' not in low:
            problems.append('GRANT not scoped to brainactive_*: ' + s[:90])
        else:
            allowed.append('GRANT ok: ' + s[:90])
    # ALTER TABLE
    if low.startswith('alter table'):
        if 'brainactive_' not in low:
            problems.append('ALTER TABLE not on brainactive_*: ' + s[:90])
        else:
            allowed.append('ALTER ok: ' + s[:90])
    # CREATE TABLE / INDEX / VIEW
    for kw in ('create table', 'create index', 'create unique index', 'create view'):
        if low.startswith(kw):
            if 'brainactive_' not in low:
                problems.append(kw + ' not on brainactive_*: ' + s[:90])
            else:
                allowed.append(kw + ' ok: ' + s[:60])
    # CREATE POLICY: must be on a brainactive_* table OR a storage.objects policy scoped to brainactive-assets
    if low.startswith('create policy'):
        on_ba = is_ba_table(s)
        on_storage_ours = ('storage.objects' in low) and ("'brainactive-assets'" in s or '"brainactive-assets"' in s or 'brainactive-assets' in low)
        if on_ba:
            allowed.append('POLICY ok (brainactive_ table): ' + s.splitlines()[0][:80])
        elif on_storage_ours:
            allowed.append('POLICY ok (storage.objects scoped to brainactive-assets): ' + s.splitlines()[0][:80])
        else:
            problems.append('CREATE POLICY not scoped to brainactive_ or our bucket: ' + s[:90])
    # storage.buckets: only INSERT with brainactive-assets id
    if 'storage.buckets' in low:
        if 'brainactive-assets' not in low:
            problems.append('storage.buckets statement not for brainactive-assets: ' + s[:90])
        else:
            allowed.append('storage.buckets ok (brainactive-assets only): ' + s.splitlines()[0][:80])

# Schema-wide grants (re-check across full stripped text)
if re.search(r'grant\s+.*\bon\s+all\s+(tables|sequences)\s+in\s+schema', stripped.lower()):
    problems.append('Schema-wide GRANT ALL ON ALL TABLES/SEQUENCES IN SCHEMA still present.')
if re.search(r'grant\s+usage\s+on\s+schema\s+public', stripped.lower()):
    problems.append('Broad GRANT USAGE ON SCHEMA public still present.')

# Catalog what the migration touches
creates = [s.splitlines()[0][:70] for s in stmts if s.lower().startswith('create table')]
print('\n--- CREATE TABLE statements (new BrainActive tables) ---')
for c in creates: print('   ', c)

print('\n--- ALLOWED statements summary ---')
for a in allowed: print('   ', a)

print('\n--- PROBLEMS ---')
print('   NONE. Migration is BrainActive-only.' if not problems else '')
for p in problems: print('   !!', p)

print('\nRESULT:', 'PASS' if not problems else 'FAIL')
sys.exit(1 if problems else 0)
