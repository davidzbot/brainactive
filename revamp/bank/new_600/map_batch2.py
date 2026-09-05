import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
d = json.load(open(r"C:\Projects\brainactive-android\revamp\bank\new_600\brainactive_new_600_upload.json", encoding="utf-8"))
keys = {
    "GRID": ["cat starts at the centre (row 2, column 2)", "dog starts at the bottom-left corner",
             "robot starts at row 1, column 1", "centre square is blocked", "fountain at row 2, column 2"],
    "CLOCK": ["minute hand points to 12", "hour hand points to 3", "spinner arrow points to 6",
              "dial points to 2", "3:00 (minute hand up"],
    "NETLBL": ["Which two faces are opposite", "Which face is opposite the heart",
               "opposite the frog", "does the star NOT touch", "heart is on top and the star faces front",
               "moon faces front and the sun faces back"],
    "FILL22": ["2-by-2 grid of small squares fills up"],
    "DOT4": ["dot that moves clockwise: top, right, bottom"],
}
for group, phrases in keys.items():
    print(f"== {group}")
    for q in d["questions"]:
        if any(p in q["question"] for p in phrases):
            print(" ", q["id"], "|", q["question"][:70], "| img:", q.get("image_path"))
