"""Fix 6 short explanations in the question bank."""
import json, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

JSON_PATH = r'C:\Projects\brainactive-android\revamp\bank\new_600\brainactive_new_600_20260905.json'

with open(JSON_PATH, encoding='utf-8') as f:
    data = json.load(f)

FIXES = {
    "NEW_SOL_021": "Ali started with 10 marbles and gave away 3. To find how many Ali has now, subtract: 10 - 3 = 7. Ali has 7 marbles left.",
    "NEW_SOL_022": "Mei started with 15 stickers and received 5 more from her brother. To find the new total, add: 15 + 5 = 20. Mei now has 20 stickers.",
    "NEW_SOL_023": "The box started with 20 apples and 8 were sold (taken away). To find how many remain, subtract: 20 - 8 = 12. There are 12 apples left.",
    "NEW_SOL_025": "Sara ran in two parts: first 60 metres, then 25 more metres. To find the total distance, add both parts: 60 + 25 = 85 m. Sara ran 85 metres in total.",
    "NEW_SOL_046": "The pins form rows of 1, 2, 3 and 4. To find the total, add all rows: 1 + 2 + 3 + 4 = 10. There are 10 pins in total.",
    "NEW_VER_008": "Each letter is converted to its position in the alphabet (P=16, I=9, G=7), then added together: 16 + 9 + 7 = 32. PIG is coded as 32.",
}

fixed = 0
for q in data['questions']:
    if q['id'] in FIXES:
        old = q['explanation']
        q['explanation'] = FIXES[q['id']]
        print(f"Fixed {q['id']}: '{old}' -> '{q['explanation']}'")
        fixed += 1

with open(JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

print(f"\nFixed {fixed} explanations. File updated.")
