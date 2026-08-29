# -*- coding: utf-8 -*-
"""Build the local BrainActive P3 High Ability question bank (100).

Phases:
 1. Convert frozen baseline v0.4.1 (old schema) -> new bank schema.
 2. Convert verbal extension v0.5 (old schema) -> new bank schema (separate file + in bank).
 3. Author 40 new questions (Num9/Log9/Vis8/Pat11/PS3) deterministically.
 4. Assemble revamp/bank/brainactive_p3_question_bank.json (100).

NO DB, NO Supabase, NO production code. JSON is the temporary source of truth.
"""
import json
import os

ROOT = r"C:\Projects\brainactive-android\revamp"
BASE = os.path.join(ROOT, "pilot", "brainactive_p3_high_ability_pilot.json")
VERBAL_V05 = os.path.join(ROOT, "pilot", "brainactive_p3_verbal_extension_v05.json")
BANK = os.path.join(ROOT, "bank")
QUESTIONS_DIR = os.path.join(BANK, "questions")

LEVEL_DIFF = {"Explore": "easy", "Think": "medium", "Challenge": "hard", "Master": "expert"}
DOMAIN_OF = {
    "numerical_reasoning": "numerical_reasoning",
    "logical_reasoning": "logical_reasoning",
    "verbal_reasoning": "verbal_reasoning",
    "visual_spatial": "visual_spatial",
    "pattern_abstract": "pattern_abstract",
    "problem_solving": "problem_solving",
}


def conv_old(q, qa_status):
    """Convert an old-schema question to the new bank schema."""
    lvl = q.get("level") or q.get("difficulty")
    cat = q.get("category")
    domain = DOMAIN_OF.get(cat, cat)
    vid = q["id"]
    out = {
        "id": vid,
        "domain": domain,
        "skill": q.get("skill_code") or q.get("skill"),
        "archetype": q.get("subcategory") or q.get("skill"),
        "level": lvl,
        "difficulty": LEVEL_DIFF.get(lvl, "medium"),
        "question_type": "multiple_choice",
        "question": q["question"],
        "options": q["options"],
        "answer": q["answer"],
        "explanation": q.get("explanation", ""),
        "reasoning": q.get("thinking_skill") or q.get("why_level", ""),
        "visual_required": bool(q.get("visual_required")),
        "visual_spec": q.get("visual_spec"),
        "image_path": ("brainactive/p3/%s.svg" % vid) if q.get("visual_required") else None,
        "tags": q.get("tags", []),
        "qa_status": qa_status,
        "provenance": {
            "basis": "BrainActive curriculum research",
            "archetype": q.get("subcategory") or q.get("skill"),
            "source_inspiration": q.get("source_inspiration", ""),
            "original": True,
        },
    }
    return out


def mc(domain, skill, archetype, level, question, opts, answer,
       explanation, reasoning, tags, source_inspiration,
       visual_required=False, visual_spec=None):
    options = [{"id": chr(65 + i), "text": t} for i, t in enumerate(opts)]
    return {
        "domain": domain,
        "skill": skill,
        "archetype": archetype,
        "level": level,
        "difficulty": LEVEL_DIFF[level],
        "question_type": "multiple_choice",
        "question": question,
        "options": options,
        "answer": answer,
        "explanation": explanation,
        "reasoning": reasoning,
        "visual_required": visual_required,
        "visual_spec": visual_spec,
        "image_path": None,  # filled after id assigned
        "tags": tags,
        "qa_status": "ai_generated_not_approved",
        "provenance": {
            "basis": "BrainActive curriculum research",
            "archetype": archetype,
            "source_inspiration": source_inspiration,
            "original": True,
        },
    }


# ---------------------------------------------------------------------------
# NEW 40 QUESTIONS
# ---------------------------------------------------------------------------
NEW = []

# --- Numerical Reasoning (1.x) : 9 ---
NEW.append(mc("numerical_reasoning", "1.1", "number_sequence", "Explore",
    "Find the next number: 2, 4, 8, 16, ___?",
    ["24", "32", "30", "64"],
    "B",
    "Each number is double the previous one (x2). 16 x 2 = 32.",
    "Spotting a constant doubling rule.",
    ["p3", "high_ability", "numerical", "pattern"], "Deterministic generator 1.1 (doubling)."))

NEW.append(mc("numerical_reasoning", "1.1", "interleaved_sequence", "Think",
    "Find the next number: 1, 3, 2, 6, 3, 9, 4, ___?",
    ["12", "15", "7", "8"],
    "A",
    "Two woven sequences. Odd positions: 1, 2, 3, 4 (+1). Even positions: 3, 6, 9, 12 (+3). The missing 8th term is the next even-position term: 12.",
    "Splitting two interleaved sequences and continuing the even track.",
    ["p3", "high_ability", "numerical", "pattern"], "Deterministic generator 1.1 (interleaved)."))

NEW.append(mc("numerical_reasoning", "1.1", "growing_difference", "Think",
    "Find the next number: 3, 5, 8, 12, 17, ___?",
    ["22", "23", "24", "21"],
    "B",
    "Gaps between terms grow by 1: +2, +3, +4, +5. Next gap is +6, so 17 + 6 = 23.",
    "Finding a second-order (growing) difference.",
    ["p3", "high_ability", "numerical", "pattern"], "Deterministic generator 1.1 (growing diff)."))

NEW.append(mc("numerical_reasoning", "1.1", "alternating_rule", "Challenge",
    "Find the next number: 1, 2, 4, 5, 10, ___?",
    ["11", "20", "21", "10"],
    "A",
    "The rule alternates +1, then x2: 1->2 (+1), 2->4 (x2), 4->5 (+1), 5->10 (x2). After the x2 step the next step is +1, so 10 + 1 = 11.",
    "Holding an alternating +1 / x2 rule across steps.",
    ["p3", "high_ability", "numerical", "pattern"], "Deterministic generator 1.1 (alternating).",
    ))
# fix: alternation +1,x2,... gives after 10 the next is +1 = 11. Keep answer A=11.

NEW.append(mc("numerical_reasoning", "1.2", "number_analogy", "Explore",
    "3 is to 6 as 4 is to ___?",
    ["8", "7", "9", "12"],
    "A",
    "Relation: x2. 3 x 2 = 6, so 4 x 2 = 8.",
    "Applying a single-operation (x2) relation.",
    ["p3", "high_ability", "numerical", "analogy"], "Deterministic generator 1.2."))

NEW.append(mc("numerical_reasoning", "1.2", "compound_rule_analogy", "Think",
    "5 is to 11 as 6 is to ___?",
    ["12", "13", "14", "17"],
    "B",
    "Rule: x2 then +1. 5 -> 11; so 6 -> (6 x 2) + 1 = 13. Distractors use x2 only (12) or x2+2 (14).",
    "Inferring and testing a two-part rule (x2 then +1).",
    ["p3", "high_ability", "numerical", "analogy"], "Deterministic generator 1.2."))

NEW.append(mc("numerical_reasoning", "1.2", "compound_rule_analogy", "Challenge",
    "2 is to 3 as 8 is to ___?",
    ["16", "15", "17", "14"],
    "B",
    "Rule: x2 then -1. 2 -> 3; so 8 -> (8 x 2) - 1 = 15. Distractors use x2 (16) or x2+1 (17).",
    "Inferring a less obvious two-part rule (x2 then -1) and applying it.",
    ["p3", "high_ability", "numerical", "analogy"], "Deterministic generator 1.2."))

NEW.append(mc("numerical_reasoning", "1.3", "weight_system", "Think",
    "A triangle and a square together weigh 9. A square and a circle together weigh 11. A triangle and a circle together weigh 8. Which shape is heaviest?",
    ["Triangle", "Square", "Circle", "All equal"],
    "B",
    "Add the three pair-weights: each shape counted twice = 28, so one of each = 14. Circle = 14 - 9 = 5, square = 14 - 8 = 6, triangle = 14 - 11 = 3. The square (6) is heaviest.",
    "Solving a small system by combining equations.",
    ["p3", "high_ability", "numerical", "deduction"], "Deterministic generator 1.3 (system)."))

NEW.append(mc("numerical_reasoning", "1.4", "chained_comparison", "Think",
    "Ravi has 4 more marbles than Sam. Sam has 3 fewer than Tom. Tom has 12. Who has the most?",
    ["Ravi", "Sam", "Tom", "All equal"],
    "A",
    "Tom = 12. Sam = 12 - 3 = 9. Ravi = 9 + 4 = 13. Ravi (13) > Tom (12) > Sam (9).",
    "Chaining several comparisons into a full order.",
    ["p3", "high_ability", "numerical", "logic"], "Deterministic generator 1.4."))

# --- Logical Reasoning (2.x) : 9 ---
NEW.append(mc("logical_reasoning", "2.1", "linear_order", "Explore",
    "P and Q are taller than R. Q is shorter than P. Order them from tallest to shortest.",
    ["P, Q, R", "Q, P, R", "R, P, Q", "P, R, Q"],
    "A",
    "P is tallest (P > Q and P > R). Q is shorter than P but taller than R, so P > Q > R.",
    "Building a linear order from two transitive clues.",
    ["p3", "high_ability", "logical", "ordering"], "Deterministic generator 2.1."))

NEW.append(mc("logical_reasoning", "2.1", "merge_partial_orders", "Think",
    "Four runners race. A beats B. B beats C. D beats A. Order them from fastest to slowest.",
    ["D, A, B, C", "A, D, B, C", "D, B, A, C", "A, B, C, D"],
    "A",
    "D beats A, and A beats B, and B beats C, so D > A > B > C. Fastest to slowest: D, A, B, C.",
    "Merging two partial orderings into one total order.",
    ["p3", "high_ability", "logical", "ordering"], "Deterministic generator 2.1."))

NEW.append(mc("logical_reasoning", "2.2", "seating_constraint", "Think",
    "Ali, Ben, Cai and Dee sit in a row of four. Ali is at the left end. Cai is in the middle. Ben is not next to Ali. Who sits second from the left?",
    ["Dee", "Ben", "Cai", "Ali"],
    "A",
    "Seats: 1 Ali, 3 Cai. Seats 2 and 4 are Ben and Dee. Ben is not next to Ali (seat 2 is next to Ali), so Ben is seat 4 and Dee is seat 2. Second from left = Dee.",
    "Placing fixed positions, then applying a negative constraint.",
    ["p3", "high_ability", "logical", "constraint"], "Deterministic generator 2.2."))

NEW.append(mc("logical_reasoning", "2.2", "multi_clue_assignment", "Challenge",
    "Three boxes are red, blue and green. Each holds one thing: a ball, a coin or a key. The blue box holds the coin. The red box does not hold the ball. What is in the green box?",
    ["ball", "coin", "key", "cannot tell"],
    "A",
    "Blue = coin, so red and green share ball and key. Red does not hold the ball, so red = key and green = ball.",
    "Multi-clue assignment (constraint satisfaction).",
    ["p3", "high_ability", "logical", "constraint"], "Deterministic generator 2.2."))

NEW.append(mc("logical_reasoning", "2.3", "modus_tollens", "Think",
    "If a number is even, it is coloured blue. The number 7 is NOT blue. What can we conclude?",
    ["7 is not even", "7 is even", "7 is blue", "cannot tell"],
    "A",
    "Rule: even -> blue. 7 is not blue, so by the contrapositive 7 is not even. You cannot tell its colour otherwise.",
    "Using the contrapositive (must-be-true from a negation).",
    ["p3", "high_ability", "logical", "deduction"], "Deterministic generator 2.3."))

NEW.append(mc("logical_reasoning", "2.3", "chained_conditionals", "Challenge",
    "If it is hot, we swim. If we swim, we are happy. It is hot. What MUST be true?",
    ["We are happy", "It is cold", "We do not swim", "We are sad"],
    "A",
    "Hot -> swim -> happy. Since it is hot, we swim and we are happy. The only MUST-be-true option is 'we are happy'.",
    "Chaining two conditional rules to a conclusion.",
    ["p3", "high_ability", "logical", "deduction"], "Deterministic generator 2.3."))

NEW.append(mc("logical_reasoning", "2.4", "figure_classification", "Think",
    "Which shape does NOT belong?  A triangle  B square  C circle  D rectangle",
    ["triangle", "square", "circle", "rectangle"],
    "C",
    "Triangle, square and rectangle are polygons with straight sides. The circle is the only curved shape, so it does not belong.",
    "Finding the property three share (straight sides) and the odd one.",
    ["p3", "high_ability", "logical", "classification"], "Deterministic generator 2.4."))

NEW.append(mc("logical_reasoning", "2.5", "syllogism", "Think",
    "All cats are animals. All animals are living things. Which MUST be true?",
    ["All cats are living things", "All living things are cats", "All animals are cats", "Cats are not living"],
    "A",
    "Every cat is an animal, and every animal is living, so every cat is living. The others reverse the direction of the rules.",
    "Chaining set inclusions (transitive).",
    ["p3", "high_ability", "logical", "syllogism"], "Deterministic generator 2.5."))

NEW.append(mc("logical_reasoning", "2.5", "syllogism_particular", "Challenge",
    "Some squares are red. All red things are small. Which MUST be true?",
    ["Some squares are small", "All squares are small", "All small things are squares", "No squares are small"],
    "A",
    "The red squares are squares AND red; all red things are small, so those squares are small. Thus SOME squares are small. 'All squares are small' need not be true.",
    "Chaining a particular quantifier with a universal one without over-generalising.",
    ["p3", "high_ability", "logical", "syllogism"], "Deterministic generator 2.5."))

# --- Visual & Spatial (4.x) : 8 ---
NEW.append(mc("visual_spatial", "4.1", "single_rotation", "Explore",
    "An arrow points UP. It is rotated 90 degrees clockwise. Which way does it point now?",
    ["right", "down", "left", "up"],
    "A",
    "One 90-degree clockwise turn moves UP to RIGHT.",
    "Mentally rotating a shape one step.",
    ["p3", "high_ability", "spatial", "rotation"], "Deterministic visual 4.1.",
    visual_required=True,
    visual_spec={"type": "rotation_sequence", "start": "up", "steps": 1}))

NEW.append(mc("visual_spatial", "4.1", "two_step_rotation", "Think",
    "An arrow points UP. It is rotated 90 degrees clockwise twice. Which way does it point now?",
    ["down", "right", "left", "up"],
    "A",
    "Two 90-degree clockwise turns = 180 degrees, so UP becomes DOWN.",
    "Tracking rotation across two steps.",
    ["p3", "high_ability", "spatial", "rotation"], "Deterministic visual 4.1.",
    visual_required=True,
    visual_spec={"type": "rotation_sequence", "start": "up", "steps": 2}))

NEW.append(mc("visual_spatial", "4.2", "mirror_reflection", "Think",
    "The letter 'p' is reflected in a vertical mirror (left-right flip). Which letter does the reflection look like?",
    ["q", "p", "b", "d"],
    "A",
    "A vertical (left-right) mirror flips 'p' so its bowl moves to the left, making it look like 'q'.",
    "Mirror reflection across a vertical axis.",
    ["p3", "high_ability", "spatial", "reflection"], "Deterministic visual 4.2.",
    visual_required=True,
    visual_spec={"type": "reflection", "axis": "vertical", "source": "p", "result": "q"}))

NEW.append(mc("visual_spatial", "4.2", "mirror_reflection", "Think",
    "The letter 'd' is reflected in a vertical mirror (left-right flip). Which letter does the reflection look like?",
    ["b", "d", "p", "q"],
    "A",
    "A vertical mirror flips 'd' so its bowl moves to the left, making it look like 'b'.",
    "Mirror reflection across a vertical axis (reverse case).",
    ["p3", "high_ability", "spatial", "reflection"], "Deterministic visual 4.2.",
    visual_required=True,
    visual_spec={"type": "reflection", "axis": "vertical", "source": "d", "result": "b"}))

NEW.append(mc("visual_spatial", "4.3", "cube_net", "Think",
    "A cube net: centre square A, with B above A, C below A, D left of A, E right of A, and F below C. Folded with A as the front face, which square is the BACK face (opposite the front)?",
    ["F", "B", "C", "E"],
    "A",
    "Fold A as front: D = left, E = right, B = top, C = bottom, and the remaining square F folds to the back. The face opposite front (A) is the back = F.",
    "Folding a net to find the opposite face.",
    ["p3", "high_ability", "spatial", "net"], "Deterministic visual 4.3.",
    visual_required=True,
    visual_spec={"type": "cube_net", "layout": [["", "B", ""], ["D", "A", "E"], ["", "C", ""], ["", "F", ""]], "front": "A", "back": "F"}))

NEW.append(mc("visual_spatial", "4.4", "rotation_3d", "Challenge",
    "A cube has a dot on its TOP face and a star on its RIGHT face. You rotate it 90 degrees to the LEFT around the vertical axis. Where is the star now?",
    ["front", "right", "top", "left"],
    "A",
    "Rotating around the vertical axis to the left turns the right face to the front. The top face (dot) stays on top. The star moves from right to front.",
    "3D rotation around the vertical axis (side faces move, top stays).",
    ["p3", "high_ability", "spatial", "rotation", "challenge"], "Deterministic visual 4.4.",
    visual_required=True,
    visual_spec={"type": "rotation_3d", "axis": "vertical", "marks": {"top": "dot", "right": "star"}, "rotation": "left 90", "star_after": "front"}))

NEW.append(mc("visual_spatial", "4.5", "position", "Explore",
    "In a 3-by-3 grid, the star is in the top-left square. The circle is directly below the star. The square is to the right of the circle. Where is the square?",
    ["middle row, middle column", "top-left", "bottom-right", "top-right"],
    "A",
    "Top-left is row1 col1. Directly below = row2 col1 (circle). To the right of the circle = row2 col2 (square). So the square is in the middle row, middle column.",
    "Tracking positions on a grid from relative clues.",
    ["p3", "high_ability", "spatial", "position"], "Authored 4.5 (text-based grid)."))

NEW.append(mc("visual_spatial", "4.5", "position", "Think",
    "A is to the left of B. C is above A. D is to the right of C. Which letter is in the top-right position?",
    ["D", "A", "B", "C"],
    "A",
    "Place A left of B (same row). C above A (col1, row above). D right of C (col2, row above). The top-right position is D.",
    "Combining left/right and above/below clues on a grid.",
    ["p3", "high_ability", "spatial", "position"], "Authored 4.5 (text-based grid)."))

# --- Pattern & Abstract (5.x) : 11 ---
NEW.append(mc("pattern_abstract", "5.1", "count_sequence", "Explore",
    "Groups of dots: 1, then 2, then 4, then 8. How many dots come next?",
    ["16", "10", "12", "9"],
    "A",
    "Each group has twice as many dots as the previous group: 1, 2, 4, 8, so 8 x 2 = 16.",
    "Continuing a doubling count sequence.",
    ["p3", "high_ability", "pattern", "sequence"], "Deterministic visual 5.1.",
    visual_required=True,
    visual_spec={"type": "count_sequence", "counts": [1, 2, 4, 8], "next": 16}))

NEW.append(mc("pattern_abstract", "5.1", "rotation_transformation", "Think",
    "A red triangle points UP. Each step it rotates 90 degrees clockwise AND its colour alternates red, blue, red... Step 1: red triangle up. Step 2: blue square right. Step 3: red pentagon down. What is Step 4?",
    ["blue hexagon pointing left", "blue hexagon pointing up", "pentagon pointing left", "blue hexagon pointing down"],
    "A",
    "Two rules: rotate 90 CW (up -> right -> down -> left) and alternate colour red/blue (red, blue, red, so next is blue). Step 4 = blue hexagon pointing left.",
    "Integrating a rotation rule with a colour rule.",
    ["p3", "high_ability", "pattern", "transformation"], "Deterministic visual 5.1.",
    visual_required=True,
    visual_spec={"type": "rotation_transform_sequence", "rules": ["rotate 90 CW", "alternate colour red/blue"],
                 "step1": "triangle up red(3)", "step2": "square right blue(4)",
                 "step3": "pentagon down red(5)", "step4": "hexagon left blue(6)"}))

NEW.append(mc("pattern_abstract", "5.2", "analogy_matrix", "Explore",
    "Top-left is a red square. Top-right is a blue square (colour flipped). Bottom-left is a red circle. Following the same change (flip colour, keep shape), what should the bottom-right be?",
    ["blue circle", "red circle", "blue square", "red square"],
    "A",
    "Change from top-left to top-right is 'flip colour, keep shape'. Apply the same to bottom-left (red circle): red -> blue, shape stays circle = blue circle.",
    "Mapping a transformation across a 2x2 matrix.",
    ["p3", "high_ability", "pattern", "matrix"], "Deterministic visual 5.2.",
    visual_required=True,
    visual_spec={"type": "analogy_matrix", "rows": 2, "cols": 2, "rule": "flip colour red<->blue, keep shape",
                 "cells": [["red square", "blue square"], ["red circle", "?"]]}))

NEW.append(mc("pattern_abstract", "5.2", "analogy_matrix", "Think",
    "Top-left is a red circle. Top-right is a blue circle with a dot (flip colour AND add a dot). Bottom-left is a red square. Following the same change, what should the bottom-right be?",
    ["blue square with a dot", "red square with a dot", "blue square", "blue circle with a dot"],
    "A",
    "Rule: flip colour red->blue AND add a dot, shape stays. Bottom-left red square -> blue square with a dot.",
    "Mapping two simultaneous changes across a 2x2 matrix.",
    ["p3", "high_ability", "pattern", "matrix"], "Deterministic visual 5.2.",
    visual_required=True,
    visual_spec={"type": "analogy_matrix", "rows": 2, "cols": 2, "rule": "flip colour AND add a dot, keep shape",
                 "cells": [["red circle", "blue circle+dot"], ["red square", "?"]]}))

NEW.append(mc("pattern_abstract", "5.2", "matrix_3x3", "Think",
    "Complete the 3x3 matrix. DOWN each column: add one dot (1 -> 2 -> 3). ACROSS each row: colour changes red -> blue -> green. Top-left is a red square with 1 dot. The bottom-right cell is ___?",
    ["green square with 3 dots", "red square with 3 dots", "green square with 2 dots", "blue square with 3 dots"],
    "A",
    "Down column 3 the dots go 1 -> 2 -> 3. Across row 3 the colour goes red -> blue -> green. So bottom-right = green square with 3 dots.",
    "Completing a 3x3 matrix with row and column rules.",
    ["p3", "high_ability", "pattern", "matrix"], "Deterministic visual 5.2.",
    visual_required=True,
    visual_spec={"type": "matrix_3x3",
                 "cells": [["red square 1", "blue square 1", "green square 1"],
                           ["red square 2", "blue square 2", "green square 2"],
                           ["red square 3", "blue square 3", "?"]],
                 "col_rule": "add one dot down the column",
                 "row_rule": "colour changes red->blue->green across the row",
                 "answer": "green square 3"}))

NEW.append(mc("pattern_abstract", "5.2", "matrix_3x3", "Challenge",
    "Complete the 3x3 matrix. DOWN each column: add 2 dots (1 -> 3 -> 5). ACROSS each row: colour changes red -> blue -> green. Top-left is a red circle with 1 dot. The bottom-right cell is ___?",
    ["green circle with 5 dots", "red circle with 5 dots", "green circle with 3 dots", "blue circle with 5 dots"],
    "A",
    "Down column 3 the dots go 1 -> 3 -> 5. Across row 3 the colour goes red -> blue -> green. So bottom-right = green circle with 5 dots.",
    "Completing a 3x3 matrix where the column rule is +2 dots.",
    ["p3", "high_ability", "pattern", "matrix", "challenge"], "Deterministic visual 5.2.",
    visual_required=True,
    visual_spec={"type": "matrix_3x3",
                 "cells": [["red circle 1", "blue circle 1", "green circle 1"],
                           ["red circle 3", "blue circle 3", "green circle 3"],
                           ["red circle 5", "blue circle 5", "?"]],
                 "col_rule": "add 2 dots down the column",
                 "row_rule": "colour changes red->blue->green across the row",
                 "answer": "green circle 5"}))

NEW.append(mc("pattern_abstract", "5.3", "figure_odd_one_out", "Explore",
    "Four figures: A triangle with 1 dot, B triangle with 2 dots, C triangle with 3 dots, D square with 1 dot. Which does not belong?",
    ["D", "A", "B", "C"],
    "A",
    "A, B and C are triangles (only the dot count changes). D is the only square, so it does not belong by shape.",
    "SPONCS odd-one-out by shape.",
    ["p3", "high_ability", "pattern", "odd_one_out"], "Deterministic visual 5.3.",
    visual_required=True,
    visual_spec={"type": "odd_one_out", "dimension": "shape",
                 "items": [{"id": "A", "shape": "triangle", "dots": 1},
                           {"id": "B", "shape": "triangle", "dots": 2},
                           {"id": "C", "shape": "triangle", "dots": 3},
                           {"id": "D", "shape": "square", "dots": 1}]}))

NEW.append(mc("pattern_abstract", "5.3", "figure_odd_one_out", "Think",
    "Four figures: A red triangle, B red triangle, C blue triangle, D red triangle. Which does not belong?",
    ["C", "A", "B", "D"],
    "A",
    "Three of the four are red triangles. C is the only blue one, so by colour C is the odd one out (shape alone is a trap).",
    "Odd-one-out by colour, not shape.",
    ["p3", "high_ability", "pattern", "odd_one_out"], "Deterministic visual 5.3.",
    visual_required=True,
    visual_spec={"type": "odd_one_out", "dimension": "colour",
                 "items": [{"id": "A", "shape": "triangle", "dots": 0, "colour": "red"},
                           {"id": "B", "shape": "triangle", "dots": 0, "colour": "red"},
                           {"id": "C", "shape": "triangle", "dots": 0, "colour": "blue"},
                           {"id": "D", "shape": "triangle", "dots": 0, "colour": "red"}]}))

NEW.append(mc("pattern_abstract", "5.3", "figure_odd_one_out", "Challenge",
    "Four figures: A red circle, B blue circle, C red square, D green circle. Which does not belong?",
    ["C", "A", "B", "D"],
    "A",
    "A, B and D are circles (only colour changes). C is the only square, so by shape C is the odd one out (checking shape, not colour).",
    "Two-dimension odd-one-out; the true split is by shape.",
    ["p3", "high_ability", "pattern", "odd_one_out"], "Deterministic visual 5.3.",
    visual_required=True,
    visual_spec={"type": "odd_one_out", "dimension": "shape",
                 "items": [{"id": "A", "shape": "circle", "dots": 0, "colour": "red"},
                           {"id": "B", "shape": "circle", "dots": 0, "colour": "blue"},
                           {"id": "C", "shape": "square", "dots": 0, "colour": "red"},
                           {"id": "D", "shape": "circle", "dots": 0, "colour": "green"}]}))

NEW.append(mc("pattern_abstract", "5.4", "figure_analogy", "Explore",
    "A small circle changes into a small square (the SHAPE changes, size stays the same). Using the same change, a large triangle changes into a ___?",
    ["large square", "large triangle", "small square", "large circle"],
    "A",
    "The change is 'change shape circle -> square', size stays the same. Small circle -> small square, so large triangle -> large square.",
    "Mapping a single feature (shape) in a figure analogy.",
    ["p3", "high_ability", "pattern", "analogy"], "Deterministic visual 5.4.",
    visual_required=True,
    visual_spec={"type": "shape_analogy", "rule": "change shape circle->square, keep size",
                 "pair1": {"small_circle": "small_square"}, "pair2": {"large_triangle": "?"}}))

NEW.append(mc("pattern_abstract", "5.4", "figure_analogy", "Think",
    "A small red circle changes into a large blue circle (size flips AND colour flips red<->blue, shape stays). Using the same change, a small blue square changes into a ___?",
    ["large red square", "small red square", "large blue square", "large blue circle"],
    "A",
    "Two changes: size small->large, and colour flips (red->blue, so blue->red). Shape stays the same. So small blue square -> large red square.",
    "Mapping two transformations at once (size + colour).",
    ["p3", "high_ability", "pattern", "analogy"], "Deterministic visual 5.4.",
    visual_required=True,
    visual_spec={"type": "shape_analogy", "rule": "flip size AND flip colour (red<->blue), keep shape",
                 "pair1": {"small_red_circle": "large_blue_circle"}, "pair2": {"small_blue_square": "?"}}))

# --- Problem Solving & Heuristics (6.x) : 3 ---
NEW.append(mc("problem_solving", "6.3", "before_after", "Think",
    "Ben has 3 more marbles than Ali. Ben gives Ali 1 marble. Now who has more marbles, and by how many?",
    ["Ben, by 1", "Ali, by 1", "They are equal", "Ben, by 3"],
    "A",
    "Originally Ben leads by 3. When Ben gives Ali 1, Ben loses 1 and Ali gains 1, so the gap shrinks by 2 (3 - 2 = 1). Ben still has 1 more.",
    "Constant-difference under a transfer (gap shrinks by twice the amount moved).",
    ["p3", "high_ability", "heuristics", "before_after"], "Authored 6.3."))

NEW.append(mc("problem_solving", "6.4", "draw_diagram", "Think",
    "Five trees are planted in a straight line, 2 metres apart. How long is the row from the first tree to the last tree?",
    ["8 m", "10 m", "5 m", "6 m"],
    "A",
    "Draw a diagram: with 5 trees there are 4 gaps between them. Each gap is 2 m, so the row is 4 x 2 = 8 m. (Not 5 x 2.)",
    "Drawing a diagram to count the gaps, not the objects.",
    ["p3", "high_ability", "heuristics", "draw_diagram"], "Authored 6.4."))

NEW.append(mc("problem_solving", "6.5", "make_list", "Think",
    "How many two-letter codes can you make using the letters A, B and C if you may repeat a letter (e.g. AA, AB)?",
    ["9", "6", "8", "12"],
    "A",
    "List them systematically: AA, AB, AC, BA, BB, BC, CA, CB, CC = 9 codes. (3 choices for the first letter x 3 for the second = 9.)",
    "Making an organised list of all possibilities.",
    ["p3", "high_ability", "heuristics", "make_list"], "Authored 6.5."))


# ---------------------------------------------------------------------------
# ASSEMBLE
# ---------------------------------------------------------------------------
def main():
    base = json.load(open(BASE))
    verbal = json.load(open(VERBAL_V05))

    bank_qs = [conv_old(q, "validated_baseline_v041") for q in base["questions"]]
    verbal_new = [conv_old(q, "ai_generated_not_approved") for q in verbal["questions"]]

    # assign ids + image_path to the 40 new questions
    new_qs = []
    for i, q in enumerate(NEW, start=51):
        qid = "BA_P3_%04d" % i  # BA_P3_0051 .. BA_P3_0090
        q["id"] = qid
        if q["visual_required"]:
            q["image_path"] = "brainactive/p3/%s.svg" % qid
        new_qs.append(q)

    all_qs = bank_qs + verbal_new + new_qs

    bank = {
        "dataset": {
            "name": "BrainActive P3 High Ability",
            "version": "0.5-local",
            "status": "development",
            "target": "Singapore Primary 3 High Ability",
            "question_count": len(all_qs),
            "disclaimer": "Local development content bank. Original reasoning-practice items inspired by BrainActive curriculum research (MOE 2026 HAL context, GEP General Ability verbal archetypes, CogAT, UK 11+ VR/NVR). Not affiliated with or predictive of any MOE/GEP assessment. Not a mock exam. Not English tuition. JSON is the temporary source of truth; not production-approved.",
            "gates": "No DB, no Supabase, no production app code, no publish. AI1 QA + human review required before any import.",
            "composition": {
                "baseline_v041": len(bank_qs),
                "verbal_extension_v05": len(verbal_new),
                "new_generated": len(new_qs),
                "total": len(all_qs),
            },
        },
        "questions": all_qs,
    }

    os.makedirs(QUESTIONS_DIR, exist_ok=True)
    # separate extension file (new schema) for the verbal 10
    ext_file = {
        "dataset": verbal.get("dataset"),
        "questions": verbal_new,
    }
    json.dump(ext_file, open(os.path.join(QUESTIONS_DIR, "verbal_extension_v05.json"), "w"),
              ensure_ascii=False, indent=2)
    json.dump(bank, open(os.path.join(BANK, "brainactive_p3_question_bank.json"), "w"),
              ensure_ascii=False, indent=2)
    print("bank questions:", len(all_qs),
          "| baseline", len(bank_qs), "verbal", len(verbal_new), "new", len(new_qs))


if __name__ == "__main__":
    main()
