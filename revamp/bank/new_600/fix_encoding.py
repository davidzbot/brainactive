"""Fix encoding corruption in explanations and image paths."""
import json, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

JSON_PATH = r'C:\Projects\brainactive-android\revamp\bank\new_600\brainactive_new_600_20260905.json'

with open(JSON_PATH, encoding='utf-8') as f:
    data = json.load(f)

# Fix 1: Replace garbled math symbols in explanations
# Common corruptions from CP1252->UTF8 misread:
# × (U+00D7) -> may appear as various garbled sequences
# − (U+2212) -> may appear as various garbled sequences
# ÷ (U+00F7) -> may appear as various garbled sequences

fix_count = 0
for q in data['questions']:
    expl = q.get('explanation', '')
    original = expl
    
    # Fix common garbled patterns
    # These are the actual bytes that get misread
    expl = expl.replace('\u00d7', 'x')  # × -> x (simple ASCII)
    expl = expl.replace('\u2212', '-')  # − -> -
    expl = expl.replace('\u00f7', '/')  # ÷ -> /
    expl = expl.replace('\u2014', '-')  # — -> -
    expl = expl.replace('\u2013', '-')  # – -> -
    expl = expl.replace('\u2018', "'")  # ' -> '
    expl = expl.replace('\u2019', "'")  # ' -> '
    expl = expl.replace('\u201c', '"')  # " -> "
    expl = expl.replace('\u201d', '"')  # " -> "
    
    # Also fix any remaining high-unicode chars
    cleaned = []
    for c in expl:
        if ord(c) > 127:
            # Replace with ASCII equivalent or skip
            if c in '×':
                cleaned.append('x')
            elif c in '−–':
                cleaned.append('-')
            elif c in '÷':
                cleaned.append('/')
            elif c in '""':
                cleaned.append('"')
            elif c in "''":
                cleaned.append("'")
            elif c in '—':
                cleaned.append('-')
            else:
                cleaned.append('?')
        else:
            cleaned.append(c)
    expl = ''.join(cleaned)
    
    if expl != original:
        q['explanation'] = expl
        fix_count += 1

# Fix 2: Image paths - change p3/ to images/
path_fixes = 0
for q in data['questions']:
    ip = q.get('image_path') or ''
    if ip.startswith('p3/'):
        q['image_path'] = ip.replace('p3/', 'images/', 1)
        path_fixes += 1

# Save
with open(JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

print(f"Fixed {fix_count} explanations with encoding issues")
print(f"Fixed {path_fixes} image paths")

# Verify no non-ASCII remains in explanations
remaining = 0
for q in data['questions']:
    expl = q.get('explanation', '')
    for c in expl:
        if ord(c) > 127:
            remaining += 1
            break
print(f"Questions with remaining non-ASCII in explanations: {remaining}")
