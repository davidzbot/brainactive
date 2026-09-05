"""Normalize all explanations to one teacher voice + readable line breaks.

Voice: rotating warm openers (stable per question id).
Layout: opener, blank line, body with one step per line for 3+ sentences,
existing bullet/step lines preserved untouched. Content words unchanged.
Usage: tone_explanations.py preview | apply-db | apply-files
"""
import json, os, re, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))

OPENERS = [
    "Let's solve it together! \U0001F9E0",
    "Come, let's work this out together! \U0001F4AA",
    "Let's think this through together! \U0001F50D",
    "Good question \u2014 let's solve it together! \u2B50",
    "Let's break it down together! \U0001F9E9",
]

TITLE_DOT = "\ue000"


def opener_for(qid):
    h = sum(ord(c) * (i + 1) for i, c in enumerate(qid))
    return OPENERS[h % len(OPENERS)]


def split_sentences(seg):
    # protect titles and decimals from sentence splitting
    s = re.sub(r"\b(Mr|Mrs|Ms|Dr|St)\. ", lambda m: m.group(1) + TITLE_DOT + " ", seg)
    s = re.sub(r"(\d)\.(\d)", lambda m: m.group(1) + TITLE_DOT + m.group(2), s)
    parts = re.split(r"(?<=[.!?\u2713])\s+", s.strip())
    return [p.replace(TITLE_DOT, ".").strip() for p in parts if p.strip()]


def normalize(qid, text):
    text = (text or "").strip()
    for op in OPENERS:
        if text.startswith(op):
            return text, False  # already toned
    segments = [s.strip() for s in text.split("\n")]
    segments = [s for s in segments if s]
    if not segments:
        return text, False
    total_sentences = sum(len(split_sentences(s)) for s in segments)
    out_segs = []
    if total_sentences <= 2 and len(segments) == 1:
        out_segs = segments  # short: keep as one paragraph
    else:
        for s in segments:
            if "\n" in s:  # shouldn't happen after split, keep safe
                out_segs.append(s)
                continue
            sents = split_sentences(s)
            if len(sents) <= 1:
                out_segs.append(s)
            else:
                out_segs.append("\n".join(sents))
    # one step per line, no blank gaps inside the body
    body = re.sub(r"\n{2,}", "\n", "\n".join(out_segs)).strip()
    return opener_for(qid) + "\n\n" + body, True


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "preview"
    if mode == "preview":
        samples = [
            ("BA_P3_0001", "Gaps: +1, +2, +3, +4, +5. Each gap grows by 1, so the next gap is +6: 16 + 6 = 22."),
            ("BA_P3_X", "Add all three pair equations: 2 \u00d7 (T + S + C) = 28. So T + S + C = 14.\n- C = 14 \u2212 11 = 3\n- T = 14 \u2212 9 = 5\nSquare wins!"),
            ("BA_P3_Y", "Mrs Tan does not love reading. Every teacher loves reading. So she is not a teacher. Check the rule!"),
            ("BA_P3_Z", "Up \u2192 right \u2192 down. Two turns = 180 degrees, so down."),
        ]
        for qid, t in samples:
            print("=" * 70)
            print("IN :", repr(t))
            out, changed = normalize(qid, t)
            print("OUT:")
            print(out)
    else:
        print("use apply-db / apply-files modes via dedicated runners")
