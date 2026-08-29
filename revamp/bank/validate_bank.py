# -*- coding: utf-8 -*-
"""Local structural validator for the BrainActive question bank.

Checks (per TODO): JSON parses, unique IDs, 4 options, answer exists,
no duplicate option ids, required fields, valid levels/domains,
visual_required <-> visual_spec consistency, image_path present + file exists,
SVG parses as XML, no external image refs, duplicate fingerprints.
"""
import json
import os
import re
import xml.dom.minidom as minidom

BANK = r"C:\Projects\brainactive-android\revamp\bank\brainactive_p3_question_bank.json"
IMG_DIR = r"C:\Projects\brainactive-android\revamp\bank\images"

VALID_LEVELS = {"Explore", "Think", "Challenge", "Master"}
VALID_DOMAINS = {"numerical_reasoning", "logical_reasoning", "verbal_reasoning",
                 "visual_spatial", "pattern_abstract", "problem_solving"}
REQUIRED = ["id", "domain", "skill", "archetype", "level", "question_type",
            "question", "options", "answer", "explanation", "reasoning",
            "visual_required", "visual_spec", "image_path", "tags",
            "qa_status", "provenance"]


def main():
    j = json.load(open(BANK))
    qs = j["questions"]
    issues = []
    ids = []
    fingerprints = {}

    for q in qs:
        qid = q.get("id", "<no-id>")
        ids.append(qid)
        for f in REQUIRED:
            if f not in q:
                issues.append((qid, "missing field: %s" % f))
        opts = q.get("options", [])
        opt_ids = [o.get("id") for o in opts]
        if len(opts) != 4:
            issues.append((qid, "options != 4 (%d)" % len(opts)))
        if len(set(opt_ids)) != len(opt_ids):
            issues.append((qid, "duplicate option ids"))
        ans = q.get("answer")
        if ans not in opt_ids:
            issues.append((qid, "answer not in options"))
        if q.get("level") not in VALID_LEVELS:
            issues.append((qid, "invalid level: %s" % q.get("level")))
        if q.get("domain") not in VALID_DOMAINS:
            issues.append((qid, "invalid domain: %s" % q.get("domain")))
        # visual consistency
        vr = q.get("visual_required")
        spec = q.get("visual_spec")
        ip = q.get("image_path")
        if vr and not spec:
            issues.append((qid, "visual_required but no visual_spec"))
        if not vr and spec:
            issues.append((qid, "visual_spec but not visual_required"))
        if vr and not ip:
            issues.append((qid, "visual_required but no image_path"))
        if ip:
            local = os.path.join(IMG_DIR, os.path.basename(ip))
            if not os.path.exists(local):
                issues.append((qid, "image file missing: %s" % ip))
            elif ip.endswith(".svg"):
                try:
                    minidom.parse(local)
                except Exception as e:
                    issues.append((qid, "SVG not valid XML: %s" % e))
        # no external image refs in explanation/question
        blob = (q.get("question", "") + " " + q.get("explanation", ""))
        if re.search(r"https?://|src\s*=|\.(png|jpg|jpeg)", blob, re.I):
            issues.append((qid, "possible external image ref in text"))
        # duplicate fingerprint
        fp = (q.get("question", "").strip().lower(), q.get("answer"))
        if fp in fingerprints:
            issues.append((qid, "duplicate fingerprint with %s" % fingerprints[fp]))
        else:
            fingerprints[fp] = qid

    dup_ids = len(ids) - len(set(ids))
    print("Questions: %d" % len(qs))
    print("Duplicate IDs: %d" % dup_ids)
    print("Structural issues: %d" % len(issues))
    for i in issues:
        print("  -", i)
    # quick distribution
    from collections import Counter
    dom = Counter(q["domain"] for q in qs)
    lvl = Counter(q["level"] for q in qs)
    vis = sum(1 for q in qs if q["visual_required"])
    print("By domain:", dict(dom))
    print("By level:", dict(lvl))
    print("Visual questions: %d" % vis)
    return 1 if (issues or dup_ids) else 0


if __name__ == "__main__":
    raise SystemExit(main())
