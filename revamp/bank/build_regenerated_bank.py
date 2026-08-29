"""
Generator and Validator for 275 Regenerated Questions (BrainActive P3)
Skills: 1.3, 1.4, 2.2, 2.3, 3.6, 6.3, 6.4, 6.5, 6.6
"""

import json
import random
import re
import os

def create_option_list(correct_text, distractor_texts, shuffle=True):
    """Creates exactly 4 options A-D with distinct texts and returns (options, answer_id)."""
    assert len(distractor_texts) >= 3, f"Need at least 3 distractors, got {distractor_texts}"
    # pick 3 unique distractors that are not equal to correct_text
    unique_distractors = []
    for d in distractor_texts:
        if str(d) != str(correct_text) and str(d) not in unique_distractors:
            unique_distractors.append(str(d))
        if len(unique_distractors) == 3:
            break
    assert len(unique_distractors) == 3, f"Could not find 3 unique distractors for {correct_text} from {distractor_texts}"
    
    all_choices = [str(correct_text)] + unique_distractors
    if shuffle:
        random.shuffle(all_choices)
    
    options = []
    answer_id = None
    letters = ['A', 'B', 'C', 'D']
    for idx, choice in enumerate(all_choices):
        opt_id = letters[idx]
        options.append({"id": opt_id, "text": choice})
        if choice == str(correct_text):
            answer_id = opt_id
            
    assert answer_id is not None
    assert len(options) == 4
    assert len(set(opt['text'] for opt in options)) == 4
    return options, answer_id

def generate_skill_1_3():
    """Skill 1.3: Weight / Balance System (40 questions).
    Given pairs (A+B, B+C, A+C), deduce individual weights or extremes.
    All weights must be distinct!
    """
    questions = []
    shape_sets = [
        ("triangle", "square", "circle"),
        ("star", "diamond", "oval"),
        ("heart", "crescent", "cross"),
        ("pentagon", "hexagon", "octagon"),
        ("cube", "cylinder", "cone"),
        ("red block", "blue block", "yellow block"),
        ("gold coin", "silver coin", "bronze coin"),
        ("apple", "orange", "pear"),
        ("ruby", "sapphire", "emerald"),
        ("pyramid", "sphere", "prism")
    ]
    
    # 40 distinct triples of weights (w1, w2, w3) all distinct
    distinct_weight_triples = [
        (3, 5, 7), (2, 4, 9), (3, 6, 8), (4, 5, 7), (2, 5, 8),
        (3, 4, 9), (5, 6, 8), (3, 7, 10), (4, 6, 9), (2, 7, 9),
        (4, 7, 8), (3, 8, 9), (5, 7, 11), (2, 6, 11), (4, 8, 10),
        (3, 5, 12), (6, 7, 9), (4, 9, 11), (5, 8, 12), (3, 9, 10),
        (2, 8, 13), (5, 9, 10), (4, 6, 13), (6, 8, 11), (3, 7, 12),
        (5, 7, 10), (2, 9, 12), (4, 10, 11), (6, 9, 10), (3, 6, 13),
        (5, 8, 11), (4, 7, 12), (6, 7, 11), (2, 10, 13), (7, 8, 10),
        (3, 8, 11), (5, 9, 12), (4, 8, 13), (6, 8, 13), (7, 9, 11)
    ]
    
    levels = ["Think"] * 20 + ["Explore"] * 10 + ["Challenge"] * 10
    difficulties = ["medium"] * 20 + ["easy"] * 10 + ["hard"] * 10
    
    for i in range(40):
        w1, w2, w3 = distinct_weight_triples[i]
        s1, s2, s3 = shape_sets[i % len(shape_sets)]
        
        # pairs
        sum12 = w1 + w2
        sum23 = w2 + w3
        sum13 = w1 + w3
        total = w1 + w2 + w3
        
        weights = {s1: w1, s2: w2, s3: w3}
        heaviest = max(weights, key=weights.get)
        lightest = min(weights, key=weights.get)
        
        # Vary question type:
        # 0: Which is heaviest?
        # 1: Which is lightest?
        # 2: What is the weight of s2?
        # 3: What is the total weight of all three?
        q_type = i % 4
        
        if q_type == 0:
            question_text = (
                f"A {s1} and a {s2} together weigh {sum12} kg. "
                f"A {s2} and a {s3} together weigh {sum23} kg. "
                f"A {s1} and a {s3} together weigh {sum13} kg. "
                f"Which shape is the heaviest?"
            )
            correct = heaviest
            distractors = [s for s in [s1, s2, s3, "cannot tell"] if s != correct]
            explanation = (
                f"Adding all three pairs gives 2 × ({s1} + {s2} + {s3}) = {sum12} + {sum23} + {sum13} = {2 * total} kg. "
                f"So all three shapes together weigh {total} kg. "
                f"Then: {s1} = {total} − {sum23} = {w1} kg, {s2} = {total} − {sum13} = {w2} kg, and {s3} = {total} − {sum12} = {w3} kg. "
                f"Comparing the weights ({w1} kg, {w2} kg, {w3} kg), the heaviest is the {heaviest} ({weights[heaviest]} kg)."
            )
            reasoning = "Solving a 3-variable balance system by summing pair equations and subtracting."
        elif q_type == 1:
            question_text = (
                f"A {s1} and a {s2} together weigh {sum12} g. "
                f"A {s2} and a {s3} together weigh {sum23} g. "
                f"A {s1} and a {s3} together weigh {sum13} g. "
                f"Which shape is the lightest?"
            )
            correct = lightest
            distractors = [s for s in [s1, s2, s3, "cannot tell"] if s != correct]
            explanation = (
                f"The sum of all three pairs is {sum12} + {sum23} + {sum13} = {2 * total} g, which is double the total weight. "
                f"Total weight of all three shapes = {total} g. "
                f"Individual weights: {s1} = {total} − {sum23} = {w1} g, {s2} = {total} − {sum13} = {w2} g, {s3} = {total} − {sum12} = {w3} g. "
                f"Comparing the weights ({w1} g, {w2} g, {w3} g), the lightest is the {lightest} ({weights[lightest]} g)."
            )
            reasoning = "Solving a 3-variable balance system to identify the minimum weight."
        elif q_type == 2:
            question_text = (
                f"A {s1} and a {s2} weigh {sum12} units together. "
                f"A {s2} and a {s3} weigh {sum23} units together. "
                f"A {s1} and a {s3} weigh {sum13} units together. "
                f"What is the weight of one {s2}?"
            )
            correct = f"{w2} units"
            distractor_nums = [w1, w3, total - w2, w2 + 1, w2 - 1]
            distractors = [f"{d} units" for d in distractor_nums if d != w2][:3]
            explanation = (
                f"Summing the three pair weights gives 2 × ({s1} + {s2} + {s3}) = {sum12} + {sum23} + {sum13} = {2 * total} units. "
                f"Thus, one of each shape totals {total} units. "
                f"Since {s1} + {s3} = {sum13} units, the {s2} weighs {total} − {sum13} = {w2} units."
            )
            reasoning = "Finding an individual shape weight from three pairwise sums."
        else:
            question_text = (
                f"On a balance scale, a {s1} and a {s2} balance {sum12} kg. "
                f"A {s2} and a {s3} balance {sum23} kg. "
                f"A {s1} and a {s3} balance {sum13} kg. "
                f"What is the total weight of one {s1}, one {s2}, and one {s3} together?"
            )
            correct = f"{total} kg"
            distractor_nums = [2 * total, total - 2, total + 2, sum12 + sum23]
            distractors = [f"{d} kg" for d in distractor_nums if d != total][:3]
            explanation = (
                f"Each shape appears exactly twice across the three pair measurements. "
                f"Adding the three pairs gives 2 × ({s1} + {s2} + {s3}) = {sum12} + {sum23} + {sum13} = {2 * total} kg. "
                f"Dividing by 2 gives the total weight of all three shapes: {2 * total} ÷ 2 = {total} kg."
            )
            reasoning = "Deducing the sum of three items by taking half of their pairwise sums."

        options, answer_id = create_option_list(correct, distractors)
        
        q_obj = {
            "domain": "numerical_reasoning",
            "skill": "1.3",
            "archetype": "weight_system",
            "level": levels[i],
            "difficulty": difficulties[i],
            "question_type": "multiple_choice",
            "question": question_text,
            "options": options,
            "answer": answer_id,
            "explanation": explanation,
            "reasoning": reasoning,
            "tags": ["p3", "high_ability", "numerical", "deduction", "balance_system"],
            "visual_required": False,
            "visual_spec": None
        }
        questions.append(q_obj)
        
    return questions

def generate_skill_1_4():
    """Skill 1.4: Chain Comparison (20 questions).
    Given chained relative comparisons, find extremes or specific values.
    All quantities must be strictly distinct!
    """
    questions = []
    scenarios = [
        ("game cards", "cards"), ("stickers", "stickers"), ("marbles", "marbles"),
        ("stamps", "stamps"), ("coloured ribbons", "ribbons"), ("coins", "coins"),
        ("wooden beads", "beads"), ("pencils", "pencils"), ("origami stars", "stars"),
        ("storybooks", "books"), ("seashells", "shells"), ("badges", "badges"),
        ("erasers", "erasers"), ("bookmarks", "bookmarks"), ("toy cars", "cars"),
        ("balloons", "balloons"), ("magnets", "magnets"), ("crayons", "crayons"),
        ("building blocks", "blocks"), ("paper clips", "clips")
    ]
    name_triples = [
        ("Ali", "Ben", "Cai"), ("Dan", "Eve", "Fay"), ("Gil", "Han", "Ivy"),
        ("Jay", "Ken", "Leo"), ("Mia", "Nora", "Owen"), ("Pam", "Roy", "Sam"),
        ("Tina", "Uma", "Vera"), ("Will", "Xan", "Yip"), ("Zack", "Amy", "Bob"),
        ("Chloe", "Dave", "Ella"), ("Fred", "Gina", "Hugo"), ("Iris", "Jack", "Kira"),
        ("Luke", "Maya", "Noah"), ("Olga", "Paul", "Quin"), ("Rita", "Seth", "Toby"),
        ("Una", "Vince", "Wren"), ("Alex", "Beth", "Cole"), ("Dora", "Eric", "Finn"),
        ("Gwen", "Hank", "Ivan"), ("Jade", "Kurt", "Lily")
    ]
    
    levels = ["Think"] * 10 + ["Explore"] * 5 + ["Challenge"] * 5
    difficulties = ["medium"] * 10 + ["easy"] * 5 + ["hard"] * 5
    
    # Pre-defined non-tied configs: (anchor_val, diff1, diff2, type)
    # n1 relative to n2, n2 relative to n3 (anchor n3)
    configs = [
        (15, 4, 6, "more_fewer"),   # Dan=15, Cai=15-6=9, Ben=9+4=13 -> (13, 9, 15)
        (20, 5, 3, "fewer_more"),   # Dan=20, Cai=20+3=23, Ben=23-5=18 -> (18, 23, 20)
        (12, 7, 2, "more_more"),    # Dan=12, Cai=12+2=14, Ben=14+7=21 -> (21, 14, 12)
        (25, 6, 8, "fewer_fewer"),  # Dan=25, Cai=25-8=17, Ben=17-6=11 -> (11, 17, 25)
        (18, 3, 5, "more_fewer"),   # Dan=18, Cai=18-5=13, Ben=13+3=16 -> (16, 13, 18)
        (14, 8, 4, "fewer_more"),   # Dan=14, Cai=14+4=18, Ben=18-8=10 -> (10, 18, 14)
        (16, 5, 4, "more_more"),    # Dan=16, Cai=16+4=20, Ben=20+5=25 -> (25, 20, 16)
        (30, 9, 7, "fewer_fewer"),  # Dan=30, Cai=30-7=23, Ben=23-9=14 -> (14, 23, 30)
        (22, 6, 4, "more_fewer"),   # Dan=22, Cai=22-4=18, Ben=18+6=24 -> (24, 18, 22)
        (17, 3, 8, "fewer_more"),   # Dan=17, Cai=17+8=25, Ben=25-3=22 -> (22, 25, 17)
        (10, 6, 5, "more_more"),    # Dan=10, Cai=10+5=15, Ben=15+6=21 -> (21, 15, 10)
        (28, 7, 5, "fewer_fewer"),  # Dan=28, Cai=28-5=23, Ben=23-7=16 -> (16, 23, 28)
        (19, 8, 3, "more_fewer"),   # Dan=19, Cai=19-3=16, Ben=16+8=24 -> (24, 16, 19)
        (15, 4, 7, "fewer_more"),   # Dan=15, Cai=15+7=22, Ben=22-4=18 -> (18, 22, 15)
        (13, 5, 6, "more_more"),    # Dan=13, Cai=13+6=19, Ben=19+5=24 -> (24, 19, 13)
        (32, 8, 10, "fewer_fewer"), # Dan=32, Cai=32-10=22, Ben=22-8=14 -> (14, 22, 32)
        (21, 7, 5, "more_fewer"),   # Dan=21, Cai=21-5=16, Ben=16+7=23 -> (23, 16, 21)
        (16, 5, 9, "fewer_more"),   # Dan=16, Cai=16+9=25, Ben=25-5=20 -> (20, 25, 16)
        (11, 4, 8, "more_more"),    # Dan=11, Cai=11+8=19, Ben=19+4=23 -> (23, 19, 11)
        (35, 11, 6, "fewer_fewer")  # Dan=35, Cai=35-6=29, Ben=29-11=18 -> (18, 29, 35)
    ]
    
    for i in range(20):
        p1, p2, p3 = name_triples[i]
        _, item_name = scenarios[i]
        anchor, d1, d2, rel_type = configs[i]
        
        # Calculate counts
        # p3 = anchor
        # p2 = p3 rel2 d2
        # p1 = p2 rel1 d1
        if rel_type == "more_fewer":
            val3 = anchor
            val2 = anchor - d2
            val1 = val2 + d1
            rel1_text = f"{p1} has {d1} more {item_name} than {p2}"
            rel2_text = f"{p2} has {d2} fewer {item_name} than {p3}"
        elif rel_type == "fewer_more":
            val3 = anchor
            val2 = anchor + d2
            val1 = val2 - d1
            rel1_text = f"{p1} has {d1} fewer {item_name} than {p2}"
            rel2_text = f"{p2} has {d2} more {item_name} than {p3}"
        elif rel_type == "more_more":
            val3 = anchor
            val2 = anchor + d2
            val1 = val2 + d1
            rel1_text = f"{p1} has {d1} more {item_name} than {p2}"
            rel2_text = f"{p2} has {d2} more {item_name} than {p3}"
        else: # fewer_fewer
            val3 = anchor
            val2 = anchor - d2
            val1 = val2 - d1
            rel1_text = f"{p1} has {d1} fewer {item_name} than {p2}"
            rel2_text = f"{p2} has {d2} fewer {item_name} than {p3}"
            
        counts = {p1: val1, p2: val2, p3: val3}
        assert len(set(counts.values())) == 3, f"Tie detected in skill 1.4 item {i}: {counts}"
        
        most_person = max(counts, key=counts.get)
        fewest_person = min(counts, key=counts.get)
        
        q_ask_type = i % 3
        if q_ask_type == 0:
            question_text = (
                f"{rel1_text}. {rel2_text}. {p3} has {val3} {item_name}. "
                f"Who has the most {item_name}?"
            )
            correct = most_person
            distractors = [p for p in [p1, p2, p3, "cannot tell"] if p != correct]
            explanation = (
                f"Start with {p3}: {p3} = {val3}. "
                f"From the clues: {p2} = {val2} {item_name}, and {p1} = {val1} {item_name}. "
                f"Comparing the amounts ({p1}: {val1}, {p2}: {val2}, {p3}: {val3}), {most_person} has the most ({counts[most_person]} {item_name})."
            )
        elif q_ask_type == 1:
            question_text = (
                f"{rel1_text}. {rel2_text}. {p3} has {val3} {item_name}. "
                f"Who has the fewest {item_name}?"
            )
            correct = fewest_person
            distractors = [p for p in [p1, p2, p3, "cannot tell"] if p != correct]
            explanation = (
                f"Find each person's amount step by step: "
                f"{p3} = {val3}. "
                f"{p2} = {val2}. "
                f"{p1} = {val1}. "
                f"Comparing {val1}, {val2}, and {val3}, {fewest_person} has the fewest ({counts[fewest_person]} {item_name})."
            )
        else:
            question_text = (
                f"{rel1_text}. {rel2_text}. {p3} has {val3} {item_name}. "
                f"How many {item_name} does {p1} have?"
            )
            correct = f"{val1} {item_name}"
            distractor_nums = [val2, val3, val1 + 2, val1 - 2, val2 + d1]
            distractors = [f"{d} {item_name}" for d in distractor_nums if d != val1][:3]
            explanation = (
                f"{p3} has {val3} {item_name}. "
                f"Next, find {p2}'s amount: {p2} = {val2} {item_name}. "
                f"Then, find {p1}'s amount: {p1} = {val1} {item_name}."
            )

        options, answer_id = create_option_list(correct, distractors)
        q_obj = {
            "domain": "numerical_reasoning",
            "skill": "1.4",
            "archetype": "chain_comparison",
            "level": levels[i],
            "difficulty": difficulties[i],
            "question_type": "multiple_choice",
            "question": question_text,
            "options": options,
            "answer": answer_id,
            "explanation": explanation,
            "reasoning": "Chaining relative comparison clues step-by-step to find an exact count or extreme.",
            "tags": ["p3", "high_ability", "numerical", "comparison", "ordering"],
            "visual_required": False,
            "visual_spec": None
        }
        questions.append(q_obj)
        
    return questions

def generate_skill_2_2():
    """Skill 2.2: Logical Constraint Placement (40 questions).
    Place 4-5 people in positions.
    CRITICAL RULE: NEVER ask for a position whose occupant is directly given in the clues!
    Every question must require deductive inference.
    """
    questions = []
    
    # 40 completely distinct scenarios and name sets
    scenarios_2_2 = [
        # (names, context, t_type, ask_desc, ask_seat)
        (["Ali", "Ben", "Cai", "Dan"], "sit in a cinema row with seats 1 to 4 from left to right", 0, "Who sits in seat 2?", 2),
        (["Eve", "Fay", "Gil", "Han"], "are seated in a classroom row from seat 1 (left) to seat 4 (right)", 0, "Who sits in seat 3?", 3),
        (["Ina", "Jay", "Ken", "Leo"], "sit on a park bench with four numbered spots 1 to 4 from left to right", 0, "Who sits in spot 2?", 2),
        (["Mia", "Nora", "Owen", "Pam"], "are seated in four consecutive bus seats (1 to 4)", 0, "Who sits in seat 3?", 3),
        (["Roy", "Sam", "Tina", "Uma"], "sit at a computer lab row (stations 1 to 4 from left to right)", 0, "Who sits in station 2?", 2),
        (["Amy", "Bob", "Chloe", "Dave"], "are sitting in four front-row theater seats 1 to 4", 0, "Who sits in seat 3?", 3),
        (["Ella", "Fred", "Gina", "Hugo"], "sit in a library study booth with 4 chairs in a row", 0, "Who sits in chair 2?", 2),
        (["Ivy", "Jack", "Kira", "Luke"], "are seated in four auditorium chairs numbered 1 to 4", 0, "Who sits in chair 3?", 3),
        (["Maya", "Noah", "Olga", "Paul"], "sit in four consecutive train seats 1 to 4", 0, "Who sits in seat 2?", 2),
        (["Quin", "Rita", "Seth", "Toby"], "are sitting on a wooden bench at spots 1 to 4", 0, "Who sits in spot 3?", 3),
        
        (["Alex", "Beth", "Cole", "Dora"], "are seated in desks 1 to 4 from left to right", 1, "Who sits in desk 2?", 2),
        (["Eric", "Finn", "Gwen", "Hank"], "sit in a row of four reading chairs (1 to 4)", 1, "Who sits in chair 1?", 1),
        (["Ivan", "Jade", "Kurt", "Lily"], "are seated in four concert seats from left to right", 1, "Who sits in seat 2?", 2),
        (["Mark", "Nina", "Oscar", "Penny"], "sit in four consecutive exam desks numbered 1 to 4", 1, "Who sits in desk 1?", 1),
        (["Ross", "Sara", "Tom", "Una"], "are sitting in four cafe chairs in a row", 1, "Who sits in chair 2?", 2),
        (["Vince", "Wendy", "Xavier", "Yara"], "sit in a row of four stadium seats (1 to 4)", 1, "Who sits in seat 1?", 1),
        (["Zack", "Anna", "Boris", "Celia"], "are seated in four music room chairs", 1, "Who sits in chair 2?", 2),
        (["Dean", "Emma", "Felix", "Grace"], "sit in four chairs arranged in a line from 1 to 4", 1, "Who sits in chair 1?", 1),
        (["Harry", "Isla", "Jacob", "Kate"], "are seated at four cafeteria spots from left to right", 1, "Who sits in spot 2?", 2),
        (["Leo", "Mila", "Nico", "Olive"], "sit in four laboratory seats numbered 1 to 4", 1, "Who sits in seat 1?", 1),
        
        (["Peter", "Quinn", "Rose", "Sean"], "competed in a 100m sprint race", 2, "Who finished in 1st place?", "1st"),
        (["Tara", "Umar", "Vicky", "Walter"], "took part in a swimming race", 2, "Who finished in 3rd place?", "3rd"),
        (["Xander", "Yasmine", "Zane", "Alice"], "competed in a cycling time trial", 2, "Who finished in 1st place?", "1st"),
        (["Brian", "Clara", "David", "Emily"], "ran in a cross-country race", 2, "Who finished in 3rd place?", "3rd"),
        (["Frank", "Gloria", "Henry", "Iris"], "competed in an obstacle course race", 2, "Who finished in 1st place?", "1st"),
        (["James", "Kelly", "Liam", "Megan"], "competed in a 200m track race", 2, "Who finished in 3rd place?", "3rd"),
        (["Nathan", "Olivia", "Patrick", "Queen"], "took part in a school math race", 2, "Who finished in 1st place?", "1st"),
        (["Ryan", "Sophia", "Thomas", "Ursula"], "competed in a roller-skating race", 2, "Who finished in 3rd place?", "3rd"),
        (["Victor", "Willa", "Xeno", "Yvonne"], "raced in a friendly sprint", 2, "Who finished in 1st place?", "1st"),
        (["Zara", "Adam", "Bella", "Chris"], "competed in a 50m freestyle swim", 2, "Who finished in 3rd place?", "3rd"),
        
        (["Daisy", "Ethan", "Flora", "George"], "are standing in a queue for ice cream", 3, "Who is 2nd in line?", "2nd"),
        (["Hannah", "Ian", "Julia", "Kevin"], "are lining up at the school canteen", 3, "Who is 4th in line?", "4th"),
        (["Laura", "Max", "Naomi", "Oliver"], "are queued up at the library counter", 3, "Who is 2nd in line?", "2nd"),
        (["Paige", "Quentin", "Ruby", "Simon"], "are standing in line to board the school bus", 3, "Who is 4th in line?", "4th"),
        (["Talia", "Uri", "Valerie", "Wyatt"], "are lined up to buy cinema tickets", 3, "Who is 2nd in line?", "2nd"),
        (["Xena", "Yosef", "Zelda", "Aaron"], "are standing in a queue at the art room", 3, "Who is 4th in line?", "4th"),
        (["Brooke", "Caleb", "Diana", "Eli"], "are waiting in line for a ride at the theme park", 3, "Who is 2nd in line?", "2nd"),
        (["Faith", "Gavin", "Hope", "Isaac"], "are lining up to return their sports equipment", 3, "Who is 4th in line?", "4th"),
        (["Joy", "Keith", "Luna", "Milo"], "are queued up at the bookshop register", 3, "Who is 2nd in line?", "2nd"),
        (["Nora", "Orson", "Pippa", "Quinn"], "are standing in a line for the water fountain", 3, "Who is 4th in line?", "4th")
    ]
    
    levels = ["Think"] * 20 + ["Explore"] * 10 + ["Challenge"] * 10
    difficulties = ["medium"] * 20 + ["easy"] * 10 + ["hard"] * 10
    
    for i, item in enumerate(scenarios_2_2):
        names, context, t_type, ask_phrase, target_val = item
        n1, n2, n3, n4 = names
        
        if t_type == 0:
            # Order: 1: n4, 2: n2, 3: n3, 4: n1
            correct = n2 if target_val == 2 else n3
            question_text = (
                f"{n1}, {n2}, {n3}, and {n4} {context}. "
                f"{n4} sits in position 1 at the left end. {n2} is not at either end. "
                f"{n3} sits immediately to the right of {n2}. {ask_phrase}"
            )
            explanation = (
                f"Position 1 is occupied by {n4}. "
                f"Since {n2} is not at either end and {n3} sits immediately to the right of {n2}, "
                f"{n2} and {n3} must occupy positions 2 and 3 respectively (with {n2} in 2 and {n3} in 3). "
                f"This leaves position 4 for {n1}. Therefore, {correct} sits in position {target_val}."
            )
        elif t_type == 1:
            # Order: 1: n4, 2: n3, 3: n2, 4: n1
            correct = n3 if target_val == 2 else n4
            question_text = (
                f"{n1}, {n2}, {n3}, and {n4} {context}. "
                f"{n1} sits in position 4 at the far right. {n2} sits immediately to the left of {n1}. "
                f"{n4} sits somewhere to the left of {n3}. {ask_phrase}"
            )
            explanation = (
                f"Position 4 is {n1}. {n2} sits immediately to the left of {n1}, placing {n2} in position 3. "
                f"Positions 1 and 2 remain for {n4} and {n3}. "
                f"Since {n4} is to the left of {n3}, {n4} is in position 1 and {n3} in position 2. "
                f"Full order: 1:{n4}, 2:{n3}, 3:{n2}, 4:{n1}. Thus, {correct} is in position {target_val}."
            )
        elif t_type == 2:
            # Race order: 1st: n3, 2nd: n2, 3rd: n1, 4th: n4
            correct = n3 if target_val == "1st" else n1
            question_text = (
                f"{n1}, {n2}, {n3}, and {n4} {context}. There were no ties. "
                f"{n2} finished in 2nd place. {n1} finished immediately after {n3}. "
                f"{n4} did not finish in 1st place. {ask_phrase}"
            )
            explanation = (
                f"{n2} is 2nd. {n1} finished immediately after {n3}, so {n3} and {n1} must occupy adjacent places. "
                f"With 2nd place taken by {n2}, the pair {n3} and {n1} must be 3rd and 4th or 1st and 3rd? "
                f"Since {n1} is immediately after {n3}, {n3} must be 1st and {n1} 3rd (separated by 2nd) or {n3} is 3rd and {n1} is 4th. "
                f"If {n3} were 3rd and {n1} 4th, 1st place would be {n4}, but the clue states {n4} did not finish 1st! "
                f"Thus, {n3} is 1st, {n2} is 2nd, {n1} is 3rd, and {n4} is 4th. "
                f"Therefore, {correct} finished in {target_val} place."
            )
        else:
            # Queue order: 1st: n1, 2nd: n4, 3rd: n2, 4th: n3
            correct = n4 if target_val == "2nd" else n3
            question_text = (
                f"{n1}, {n2}, {n3}, and {n4} {context}. "
                f"{n1} is 1st in line. {n3} is standing behind {n2}. "
                f"{n4} is standing immediately between {n1} and {n2}. "
                f"{ask_phrase}"
            )
            explanation = (
                f"{n1} is 1st. {n4} is immediately between {n1} and {n2}, placing {n4} 2nd and {n2} 3rd. "
                f"Since {n3} is behind {n2}, {n3} must be 4th in line. "
                f"Queue order: 1st:{n1}, 2nd:{n4}, 3rd:{n2}, 4th:{n3}. So {correct} is {target_val} in line."
            )

        distractors = [p for p in [n1, n2, n3, n4] if p != correct]
        opts, ans = create_option_list(correct, distractors)
        q_obj = {
            "domain": "logical_reasoning",
            "skill": "2.2",
            "archetype": "constraint_placement",
            "level": levels[i],
            "difficulty": difficulties[i],
            "question_type": "multiple_choice",
            "question": question_text,
            "options": opts,
            "answer": ans,
            "explanation": explanation,
            "reasoning": "Applying multiple spatial and logical constraints to deduce unstated positions.",
            "tags": ["p3", "high_ability", "logical", "deduction", "constraint", "seating"],
            "visual_required": False,
            "visual_spec": None
        }
        questions.append(q_obj)
        
    return questions

def generate_skill_2_3():
    """Skill 2.3: Conditional / Contrapositive (35 questions).
    Include Contrapositive (15), Modus Ponens (10), Transitive Chain (10).
    CRITICAL FIX: In contrapositive 'not Q', ensure the subject genuinely satisfies 'not Q' in reality!
    """
    questions = []
    
    levels = ["Think"] * 17 + ["Explore"] * 9 + ["Challenge"] * 9
    difficulties = ["medium"] * 17 + ["easy"] * 9 + ["hard"] * 9
    
    # 15 Contrapositive questions
    contra_data = [
        ("a number is a multiple of 4", "it is coloured blue", "15", "is not blue", "15 is not a multiple of 4",
         ["15 is a multiple of 4", "15 is blue", "15 is an even number"]),
        ("a shape is a rectangle", "it has exactly 4 sides", "A circle", "does not have exactly 4 sides", "A circle is not a rectangle",
         ["A circle is a rectangle", "A circle has 4 sides", "All shapes are circles"]),
        ("a number is a multiple of 5", "its last digit is 0 or 5", "37", "does not have a last digit of 0 or 5", "37 is not a multiple of 5",
         ["37 is a multiple of 5", "37 ends in 5", "37 is divisible by 10"]),
        ("a polygon is a triangle", "it has exactly 3 vertices", "Figure G", "does not have exactly 3 vertices", "Figure G is not a triangle",
         ["Figure G is a triangle", "Figure G has 3 vertices", "Figure G is a circle"]),
        ("it is a rainy afternoon", "Ben carries an umbrella", "On Tuesday afternoon", "Ben does not carry an umbrella", "Tuesday afternoon is not rainy",
         ["Tuesday afternoon is rainy", "Ben carries an umbrella on Tuesday", "It rains every Tuesday"]),
        ("a number is a multiple of 6", "it is an even number", "21", "is not an even number", "21 is not a multiple of 6",
         ["21 is a multiple of 6", "21 is an even number", "21 is divisible by 12"]),
        ("an animal is a bird", "it has feathers", "A dolphin", "does not have feathers", "A dolphin is not a bird",
         ["A dolphin is a bird", "A dolphin has feathers", "All animals are birds"]),
        ("a card has a star symbol", "it belongs in Box A", "Card #9", "does not belong in Box A", "Card #9 does not have a star symbol",
         ["Card #9 has a star symbol", "Card #9 belongs in Box A", "All cards have stars"]),
        ("a number is divisible by 10", "it ends in 0", "54", "does not end in 0", "54 is not divisible by 10",
         ["54 is divisible by 10", "54 ends in 0", "54 is a multiple of 100"]),
        ("an integer is odd", "it cannot be divided by 2 without a remainder", "8", "can be divided by 2 without a remainder", "8 is not an odd integer",
         ["8 is an odd integer", "8 has a remainder when divided by 2", "All integers are odd"]),
        ("a vehicle is a bicycle", "it has exactly 2 wheels", "A car", "does not have exactly 2 wheels", "A car is not a bicycle",
         ["A car is a bicycle", "A car has 2 wheels", "All vehicles are bicycles"]),
        ("a number is greater than 50", "it is marked with a red tag", "The number 28", "is not marked with a red tag", "The number 28 is not greater than 50",
         ["The number 28 is greater than 50", "The number 28 has a red tag", "All numbers are marked red"]),
        ("a day is Sunday", "the library is closed", "On Friday", "the library is not closed", "Friday is not Sunday",
         ["Friday is Sunday", "The library is closed on Friday", "The library is never open"]),
        ("a student scores full marks", "they receive a gold badge", "Lucas", "did not receive a gold badge", "Lucas did not score full marks",
         ["Lucas scored full marks", "Lucas received a gold badge", "All students received gold badges"]),
        ("a shape is a square", "all 4 of its sides are equal in length", "Shape X", "does not have all 4 sides equal in length", "Shape X is not a square",
         ["Shape X is a square", "Shape X has 4 equal sides", "Shape X is a circle"])
    ]
    
    # 10 Modus Ponens questions
    ponens_data = [
        ("a shape is a pentagon", "it has exactly 5 sides", "Shape P is a pentagon", "Shape P has exactly 5 sides",
         ["Shape P has 6 sides", "Shape P is not a pentagon", "Shape P has 4 sides"]),
        ("a number is a multiple of 8", "it is divisible by 4", "The number 32 is a multiple of 8", "32 is divisible by 4",
         ["32 is not divisible by 4", "32 is not a multiple of 8", "32 is an odd number"]),
        ("an animal is an insect", "it has 6 legs", "A ladybug is an insect", "A ladybug has 6 legs",
         ["A ladybug has 8 legs", "A ladybug is not an insect", "A ladybug has 4 legs"]),
        ("a number is prime and greater than 2", "it must be odd", "17 is a prime number greater than 2", "17 must be odd",
         ["17 must be even", "17 is not prime", "17 is divisible by 2"]),
        ("a student is in the school choir", "they attend practice on Wednesdays", "Maya is in the school choir", "Maya attends practice on Wednesdays",
         ["Maya does not attend practice on Wednesdays", "Maya is not in the choir", "Maya attends practice on Fridays"]),
        ("a figure is a cube", "it has exactly 6 flat faces", "Block C is a cube", "Block C has exactly 6 flat faces",
         ["Block C has 8 flat faces", "Block C is not a cube", "Block C has 5 flat faces"]),
        ("a number ends in 0", "it is a multiple of 5", "The number 80 ends in 0", "80 is a multiple of 5",
         ["80 is not a multiple of 5", "80 does not end in 0", "80 is an odd number"]),
        ("an angle is a right angle", "it measures exactly 90 degrees", "Angle K is a right angle", "Angle K measures exactly 90 degrees",
         ["Angle K measures 45 degrees", "Angle K is not a right angle", "Angle K measures 180 degrees"]),
        ("a fruit is a citrus fruit", "it contains citric acid", "A lemon is a citrus fruit", "A lemon contains citric acid",
         ["A lemon does not contain citric acid", "A lemon is not a fruit", "All fruits are lemons"]),
        ("a polygon is an octagon", "it has 8 straight sides", "Tile T is an octagon", "Tile T has 8 straight sides",
         ["Tile T has 6 straight sides", "Tile T is not an octagon", "Tile T has 10 straight sides"])
    ]
    
    # 10 Transitive Chain questions
    chain_data = [
        ("If it is sunny on Saturday, Ken goes to the swimming pool. If Ken goes to the swimming pool, he wears his blue goggles. It is sunny on Saturday.",
         "Ken wears his blue goggles",
         ["Ken does not go to the pool", "Ken wears red goggles", "It is not sunny on Saturday"]),
        ("If a number is a multiple of 12, it is a multiple of 6. If a number is a multiple of 6, it is an even number. The number 36 is a multiple of 12.",
         "36 is an even number",
         ["36 is an odd number", "36 is not a multiple of 6", "36 is not divisible by 3"]),
        ("If Zoe finishes her homework early, she reads a book. If Zoe reads a book, she learns new vocabulary words. Zoe finishes her homework early today.",
         "Zoe learns new vocabulary words",
         ["Zoe does not read a book", "Zoe does not finish her homework", "Zoe watches television"]),
        ("If an animal is a robin, it is a bird. If an animal is a bird, it has wings. Chirpy is a robin.",
         "Chirpy has wings",
         ["Chirpy is not a bird", "Chirpy does not have wings", "Chirpy cannot fly"]),
        ("If a shape is a square, it is a rectangle. If a shape is a rectangle, it has 4 right angles. Shape S is a square.",
         "Shape S has 4 right angles",
         ["Shape S is not a rectangle", "Shape S has only 2 right angles", "Shape S has 3 sides"]),
        ("If a student joins the chess club, they receive a club badge. If a student receives a club badge, they can enter the tournament. Liam joins the chess club.",
         "Liam can enter the tournament",
         ["Liam does not receive a club badge", "Liam cannot enter the tournament", "Liam leaves the chess club"]),
        ("If a plant receives enough sunlight, it makes food. If a plant makes food, it grows healthy green leaves. Plant A receives enough sunlight.",
         "Plant A grows healthy green leaves",
         ["Plant A does not make food", "Plant A wilts", "Plant A receives no sunlight"]),
        ("If a number is a multiple of 20, it is a multiple of 10. If a number is a multiple of 10, its last digit is 0. The number 60 is a multiple of 20.",
         "60 has a last digit of 0",
         ["60 is not a multiple of 10", "60 ends in 5", "60 is an odd number"]),
        ("If David saves $10 this week, he buys a model airplane kit. If David buys a model airplane kit, he builds it on Sunday. David saves $10 this week.",
         "David builds the model airplane kit on Sunday",
         ["David does not buy the kit", "David does not save $10", "David sells his kit"]),
        ("If a polygon is a regular hexagon, all 6 of its sides are equal. If all 6 sides are equal, its perimeter is 6 times one side. Shape H is a regular hexagon with side length 3 cm.",
         "Shape H has a perimeter of 18 cm",
         ["Shape H has unequal sides", "Shape H has a perimeter of 12 cm", "Shape H has 5 sides"])
    ]
    
    idx = 0
    # Process 15 contrapositive
    for item in contra_data:
        rule_p, rule_q, subj, not_q, correct, dist = item
        q_text = f"Rule: If {rule_p}, then {rule_q}. Given: {subj} {not_q}. What must be true?"
        exp = (
            f"The given rule is: '{rule_p} → {rule_q}'. "
            f"We are given that {subj} {not_q} (the opposite of the conclusion). "
            f"By the logical rule of contrapositive (if Not Q, then Not P), we can validly conclude that: {correct}."
        )
        opts, ans = create_option_list(correct, dist)
        q_obj = {
            "domain": "logical_reasoning",
            "skill": "2.3",
            "archetype": "conditional_contrapositive",
            "level": levels[idx],
            "difficulty": difficulties[idx],
            "question_type": "multiple_choice",
            "question": q_text,
            "options": opts,
            "answer": ans,
            "explanation": exp,
            "reasoning": "Applying the contrapositive deduction rule (If P then Q; Not Q therefore Not P).",
            "tags": ["p3", "high_ability", "logical", "conditional", "contrapositive"],
            "visual_required": False,
            "visual_spec": None
        }
        questions.append(q_obj)
        idx += 1
        
    # Process 10 modus ponens
    for item in ponens_data:
        rule_p, rule_q, premise, correct, dist = item
        q_text = f"Rule: If {rule_p}, then {rule_q}. Given: {premise}. What can we conclude?"
        exp = (
            f"The rule states: 'If {rule_p}, then {rule_q}'. "
            f"Since {premise} satisfies the condition (P is true), by direct deduction (Modus Ponens), "
            f"the result must follow: {correct}."
        )
        opts, ans = create_option_list(correct, dist)
        q_obj = {
            "domain": "logical_reasoning",
            "skill": "2.3",
            "archetype": "conditional_contrapositive",
            "level": levels[idx],
            "difficulty": difficulties[idx],
            "question_type": "multiple_choice",
            "question": q_text,
            "options": opts,
            "answer": ans,
            "explanation": exp,
            "reasoning": "Applying direct conditional deduction (Modus Ponens: If P then Q; P therefore Q).",
            "tags": ["p3", "high_ability", "logical", "conditional", "deduction"],
            "visual_required": False,
            "visual_spec": None
        }
        questions.append(q_obj)
        idx += 1
        
    # Process 10 transitive chains
    for item in chain_data:
        scenario, correct, dist = item
        q_text = f"{scenario} What must be true?"
        exp = (
            f"Following the chain of conditions step by step leads directly to the conclusion. "
            f"Therefore, the statement that must be true is: '{correct}'."
        )
        opts, ans = create_option_list(correct, dist)
        q_obj = {
            "domain": "logical_reasoning",
            "skill": "2.3",
            "archetype": "conditional_contrapositive",
            "level": levels[idx],
            "difficulty": difficulties[idx],
            "question_type": "multiple_choice",
            "question": q_text,
            "options": opts,
            "answer": ans,
            "explanation": exp,
            "reasoning": "Applying a transitive conditional reasoning chain (P → Q → R; P therefore R).",
            "tags": ["p3", "high_ability", "logical", "conditional", "transitive_chain"],
            "visual_required": False,
            "visual_spec": None
        }
        questions.append(q_obj)
        idx += 1
        
    return questions

def generate_skill_3_6():
    """Skill 3.6: Verbal Letter Pattern (20 questions).
    Clean single letter options A-Z.
    Correct modulo 26 math: ((pos - 1) % 26) + 1.
    """
    questions = []
    
    levels = ["Think"] * 10 + ["Explore"] * 5 + ["Challenge"] * 5
    difficulties = ["medium"] * 10 + ["easy"] * 5 + ["hard"] * 5
    
    def l2n(ch): return ord(ch) - ord('A') + 1
    def n2l(n): return chr(((n - 1) % 26) + ord('A'))
    
    patterns = [
        # (type, seq_str, gaps_desc, last_letter_char, next_gap_val, distractor_letters)
        ("constant", ["B", "D", "F", "H"], "Each step moves 2 letters forward (+2).", "H", 2, ["I", "K", "G"]),
        ("constant", ["C", "F", "I", "L"], "Each step moves 3 letters forward (+3).", "L", 3, ["M", "N", "P"]),
        ("constant", ["A", "E", "I", "M"], "Each step moves 4 letters forward (+4).", "M", 4, ["N", "P", "R"]),
        ("alternating", ["D", "F", "I", "K"], "The gaps alternate between +2 and +3.", "K", 3, ["L", "M", "O"]),
        ("alternating", ["B", "C", "F", "G"], "The gaps alternate between +1 and +3.", "G", 3, ["H", "I", "K"]),
        ("constant", ["E", "H", "K", "N"], "Each step moves 3 letters forward (+3).", "N", 3, ["O", "P", "M"]),
        ("growing", ["A", "C", "F", "J"], "The gaps grow by 1 each step (+2, +3, +4, ...).", "J", 5, ["N", "P", "M"]),
        ("forward_back", ["P", "S", "R", "U"], "The gaps alternate between +3 and -1.", "U", -1, ["U", "V", "X"]),
        ("alternating", ["G", "I", "L", "N"], "The gaps alternate between +2 and +3.", "N", 3, ["O", "P", "M"]),
        ("constant", ["F", "J", "N", "R"], "Each step moves 4 letters forward (+4).", "R", 4, ["S", "T", "U"]),
        
        ("wrap_constant", ["W", "Y", "B", "D"], "Each step moves 2 letters forward (wrapping past Z back to A).", "D", 2, ["E", "C", "G"]),
        ("forward_back", ["U", "X", "W", "Z"], "The gaps alternate between +3 and -1.", "Z", -1, ["A", "B", "W"]),
        ("growing", ["B", "D", "G", "K"], "The gaps grow by 1 each step (+2, +3, +4, ...).", "K", 5, ["O", "N", "M"]),
        ("forward_back", ["T", "X", "V", "Z"], "The gaps alternate between +4 and -2.", "Z", -2, ["Y", "W", "V"]),
        ("wrap_forward_back", ["Y", "B", "A", "D"], "The gaps alternate between +3 and -1 (wrapping past Z).", "D", -1, ["G", "E", "F"]),
        
        ("growing", ["C", "E", "H", "L"], "The gaps grow by 1 each step (+2, +3, +4, ...).", "L", 5, ["P", "O", "R"]),
        ("wrap_forward_back", ["V", "Y", "X", "B"], "The gaps alternate between +3 and -1 (wrapping past Z).", "B", -1, ["C", "E", "D"]),
        ("wrap_forward_back", ["X", "B", "Z", "D"], "The gaps alternate between +4 and -2 (wrapping past Z).", "D", -2, ["F", "E", "G"]),
        ("growing", ["D", "F", "I", "M"], "The gaps grow by 1 each step (+2, +3, +4, ...).", "M", 5, ["S", "Q", "T"]),
        ("wrap_forward_back", ["Z", "C", "B", "E"], "The gaps alternate between +3 and -1 (wrapping past Z).", "E", -1, ["G", "H", "F"])
    ]
    
    for i, p_info in enumerate(patterns):
        p_type, seq, desc, last_char, next_gap, dist_letters = p_info
        
        last_pos = l2n(last_char)
        next_pos = last_pos + next_gap
        correct_letter = n2l(next_pos)
        
        seq_str = ", ".join(seq) + ", ___"
        q_text = f"A letter pattern goes: {seq_str}. {desc} What comes next?"
        
        # Build explanation step string
        step_strs = []
        for s_idx in range(len(seq) - 1):
            c1, c2 = seq[s_idx], seq[s_idx + 1]
            pos1, pos2 = l2n(c1), l2n(c2)
            step_strs.append(f"{c1}({pos1})→{c2}({pos2})")
            
        full_steps = " ".join(step_strs)
        exp = (
            f"Tracking letter positions: {full_steps}. "
            f"Following the rule, the next step from {last_char}({last_pos}) applies a shift of {next_gap:+d}, "
            f"yielding position {last_pos} + ({next_gap:+d}) = {next_pos} → {correct_letter}."
        )
        
        # Check distractors are clean single A-Z letters
        opts, ans = create_option_list(correct_letter, dist_letters)
        q_obj = {
            "domain": "verbal_reasoning",
            "skill": "3.6",
            "archetype": "letter_series",
            "level": levels[i],
            "difficulty": difficulties[i],
            "question_type": "multiple_choice",
            "question": q_text,
            "options": opts,
            "answer": ans,
            "explanation": exp,
            "reasoning": "Finding the rule in a letter series and applying the correct next gap position.",
            "tags": ["p3", "high_ability", "verbal", "letter_pattern", "sequence"],
            "visual_required": False,
            "visual_spec": None
        }
        questions.append(q_obj)
        
    return questions

def generate_skill_6_3():
    """Skill 6.3: Problem Solving - Before/After Transfer (30 questions).
    Heuristic: transfer changes gap by 2 * transfer_amount.
    Diverse characters, items, and operations.
    """
    questions = []
    
    levels = ["Think"] * 15 + ["Explore"] * 8 + ["Challenge"] * 7
    difficulties = ["medium"] * 15 + ["easy"] * 8 + ["hard"] * 7
    
    scenarios = [
        ("Amy", "Ben", "stickers", 24, 16, 3, "Amy gives Ben"),       # A=21, B=19 -> Amy by 2
        ("Chloe", "Dave", "marbles", 30, 20, 4, "Chloe gives Dave"),   # C=26, D=24 -> Chloe by 2
        ("Ella", "Fred", "sweets", 18, 10, 2, "Fred gives Ella"),      # E=20, F=8 -> Ella by 12
        ("Gina", "Hugo", "coins", 25, 15, 5, "Gina gives Hugo"),       # G=20, H=20 -> They have the same amount
        ("Ivy", "Jack", "books", 14, 8, 2, "Ivy gives Jack"),          # I=12, J=10 -> Ivy by 2
        ("Kira", "Luke", "beads", 32, 20, 6, "Kira gives Luke"),       # K=26, L=26 -> They have the same amount
        ("Maya", "Noah", "cards", 40, 28, 4, "Maya gives Noah"),       # M=36, N=32 -> Maya by 4
        ("Olga", "Paul", "stamps", 22, 14, 3, "Paul gives Olga"),      # O=25, P=11 -> Olga by 14
        ("Rita", "Seth", "pencils", 19, 11, 3, "Rita gives Seth"),     # R=16, S=14 -> Rita by 2
        ("Tina", "Uma", "ribbons", 28, 16, 4, "Tina gives Uma"),       # T=24, U=20 -> Tina by 4
        ("Vera", "Will", "origami cranes", 35, 25, 5, "Will gives Vera"), # V=40, W=20 -> Vera by 20
        ("Xan", "Yip", "toy cars", 16, 10, 2, "Xan gives Yip"),        # X=14, Y=12 -> Xan by 2
        ("Zack", "Bob", "badges", 27, 15, 6, "Zack gives Bob"),        # Z=21, B=21 -> They have the same amount
        ("Cai", "Dan", "erasers", 20, 12, 2, "Dan gives Cai"),         # C=22, D=10 -> Cai by 12
        ("Eve", "Fay", "bookmarks", 33, 21, 4, "Eve gives Fay"),       # E=29, F=25 -> Eve by 4
        ("Gil", "Han", "paper clips", 45, 31, 5, "Gil gives Han"),     # G=40, H=36 -> Gil by 4
        ("Ina", "Jay", "seashells", 26, 18, 3, "Ina gives Jay"),       # I=23, J=21 -> Ina by 2
        ("Ken", "Leo", "balloons", 15, 9, 2, "Leo gives Ken"),         # K=17, L=7 -> Ken by 10
        ("Mia", "Nora", "crayons", 36, 24, 6, "Mia gives Nora"),       # M=30, N=30 -> They have the same amount
        ("Owen", "Pam", "magnets", 29, 17, 4, "Owen gives Pam"),       # O=25, P=21 -> Owen by 4
        ("Roy", "Sam", "building blocks", 50, 34, 8, "Roy gives Sam"), # R=42, S=42 -> They have the same amount
        ("Toby", "Una", "buttons", 23, 15, 3, "Una gives Toby"),       # T=26, U=12 -> Toby by 14
        ("Vince", "Wren", "colouring pens", 31, 19, 5, "Vince gives Wren"), # V=26, W=24 -> Vince by 2
        ("Alex", "Beth", "stickers", 42, 30, 4, "Alex gives Beth"),    # A=38, B=34 -> Alex by 4
        ("Cole", "Dora", "game tokens", 34, 22, 4, "Cole gives Dora"), # C=30, D=26 -> Cole by 4
        ("Eric", "Finn", "marbles", 25, 13, 4, "Eric gives Finn"),     # E=21, F=17 -> Eric by 4
        ("Gwen", "Hank", "sweets", 38, 26, 6, "Gwen gives Hank"),      # G=32, H=32 -> They have the same amount
        ("Ivan", "Jade", "stamps", 27, 17, 3, "Jade gives Ivan"),      # I=30, J=14 -> Ivan by 16
        ("Kurt", "Lily", "cards", 44, 32, 4, "Kurt gives Lily"),       # K=40, L=36 -> Kurt by 4
        ("Mark", "Nina", "beads", 30, 18, 5, "Mark gives Nina")        # M=25, N=23 -> Mark by 2
    ]
    
    for i in range(30):
        p1, p2, item, init1, init2, transfer, action = scenarios[i]
        
        # initial gap
        init_gap = init1 - init2
        
        if "gives" in action:
            giver = action.split(" gives ")[0]
            receiver = action.split(" gives ")[1]
            if giver == p1:
                fin1 = init1 - transfer
                fin2 = init2 + transfer
            else:
                fin1 = init1 + transfer
                fin2 = init2 - transfer
        
        if fin1 > fin2:
            gap = fin1 - fin2
            correct = f"{p1}, by {gap}"
            distractors = [
                f"{p2}, by {gap}",
                f"{p1}, by {init_gap}",
                f"They have the same amount",
                f"{p1}, by {gap + 2}"
            ]
        elif fin2 > fin1:
            gap = fin2 - fin1
            correct = f"{p2}, by {gap}"
            distractors = [
                f"{p1}, by {gap}",
                f"{p2}, by {init_gap}",
                f"They have the same amount",
                f"{p2}, by {gap + 2}"
            ]
        else:
            correct = "They have the same amount"
            distractors = [
                f"{p1}, by {transfer}",
                f"{p2}, by {transfer}",
                f"{p1}, by {2 * transfer}",
                f"{p2}, by {2 * transfer}"
            ]
            
        q_text = (
            f"{p1} has {init1} {item} and {p2} has {init2} {item}. "
            f"{action} {transfer} {item}. "
            f"Now who has more {item}, and by how many?"
        )
        exp = (
            f"Initially: {p1} = {init1}, {p2} = {init2} (initial difference = {init1 - init2}). "
            f"After the transfer: {p1} has {fin1} {item} and {p2} has {fin2} {item}. "
            f"Comparing the new amounts ({fin1} vs {fin2}), the result is: {correct}."
        )
        
        opts, ans = create_option_list(correct, distractors)
        q_obj = {
            "domain": "problem_solving",
            "skill": "6.3",
            "archetype": "before_after_transfer",
            "level": levels[i],
            "difficulty": difficulties[i],
            "question_type": "multiple_choice",
            "question": q_text,
            "options": opts,
            "answer": ans,
            "explanation": exp,
            "reasoning": "Applying the transfer heuristic: a transfer of N items between two people changes their difference by 2N.",
            "tags": ["p3", "high_ability", "problem_solving", "before_after", "transfer", "heuristic"],
            "visual_required": False,
            "visual_spec": None
        }
        questions.append(q_obj)
        
    return questions

def generate_skill_6_4():
    """Skill 6.4: Problem Solving - Draw a Diagram (Count Gaps) (30 questions).
    Line: N objects -> (N-1) gaps. Total = (N-1) * gap.
    Circle: N objects -> N gaps. Total = N * gap.
    """
    questions = []
    
    levels = ["Think"] * 15 + ["Explore"] * 8 + ["Challenge"] * 7
    difficulties = ["medium"] * 15 + ["easy"] * 8 + ["hard"] * 7
    
    # 20 Line problems + 10 Circle problems
    line_configs = [
        ("fence posts", "a straight fence", 7, 3, "m", "length of the fence from the first to the last post"),
        ("trees", "a straight garden path", 9, 4, "m", "distance from the first tree to the last tree"),
        ("lamp posts", "a straight street", 11, 5, "m", "distance between the first and the last lamp post"),
        ("flags", "a straight race track", 8, 6, "m", "distance from the first flag to the eighth flag"),
        ("dominoes", "a straight row", 10, 2, "cm", "distance from the first domino to the last domino"),
        ("bus stops", "a straight bus route", 6, 500, "m", "total distance from the first stop to the sixth stop"),
        ("beads", "a straight wire", 12, 3, "cm", "distance from the first bead to the twelfth bead"),
        ("steps", "a straight staircase", 15, 20, "cm", "total horizontal span from the bottom step to the top step"),
        ("traffic cones", "a straight lane", 8, 4, "m", "total distance from the first cone to the last cone"),
        ("wooden stakes", "a straight garden plot", 13, 2, "m", "distance from the first stake to the thirteenth stake"),
        ("milestones", "a straight trail", 5, 800, "m", "distance from the 1st milestone to the 5th milestone"),
        ("streetlights", "a straight bridge", 7, 12, "m", "length of the bridge between the first and seventh streetlight"),
        ("plant pots", "a straight balcony edge", 9, 30, "cm", "distance from the first pot to the ninth pot"),
        ("red balloons", "a straight string", 6, 25, "cm", "distance from the first balloon to the last balloon"),
        ("pegs", "a straight clothesline", 14, 15, "cm", "distance between the first peg and the fourteenth peg"),
        ("solar lights", "a straight walkway", 10, 3, "m", "distance from the first light to the tenth light"),
        ("stepping stones", "a straight lawn path", 11, 40, "cm", "distance from the first stone to the eleventh stone"),
        ("banner poles", "a straight road", 8, 10, "m", "distance from the first pole to the eighth pole"),
        ("chairs", "a straight row on stage", 12, 50, "cm", "distance from the first chair to the twelfth chair"),
        ("coloured markers", "a straight border", 16, 5, "m", "distance from the first marker to the sixteenth marker")
    ]
    
    circle_configs = [
        ("bushes", "a circular pond", 8, 3, "m", "total distance around the pond"),
        ("lamp posts", "a circular roundabout", 10, 6, "m", "total perimeter around the roundabout"),
        ("trees", "a circular running track", 12, 25, "m", "total length around the track"),
        ("chairs", "a round table", 6, 2, "m", "circumference around the table"),
        ("flowers", "a circular flowerbed", 15, 4, "m", "total distance around the flowerbed"),
        ("beads", "a closed circular necklace", 20, 2, "cm", "total length of the necklace"),
        ("stepping stones", "a circular fountain", 9, 3, "m", "distance all the way around the fountain"),
        ("lanterns", "a circular courtyard wall", 8, 5, "m", "total distance around the courtyard"),
        ("posts", "a circular horse arena", 14, 10, "m", "total distance around the arena"),
        ("flags", "a circular festival ring", 16, 8, "m", "total boundary length around the ring")
    ]
    
    idx = 0
    # Line questions (20)
    for item in line_configs:
        obj, setting, n, gap, unit, q_phrase = item
        gaps_count = n - 1
        total_len = gaps_count * gap
        
        q_text = (
            f"{n} {obj} are placed evenly along {setting}, with a distance of {gap} {unit} between every two consecutive {obj}. "
            f"What is the {q_phrase}?"
        )
        correct = f"{total_len} {unit}"
        distractor_vals = [n * gap, (n - 2) * gap, total_len + 2 * gap, total_len - 2 * gap, n * gap + gap]
        distractors = [f"{d} {unit}" for d in distractor_vals if f"{d} {unit}" != correct and d > 0]
        exp = (
            f"Draw a diagram: along a straight line, {n} {obj} create exactly {n} − 1 = {gaps_count} equal intervals (gaps). "
            f"Each gap is {gap} {unit}. "
            f"Total distance = {gaps_count} × {gap} {unit} = {total_len} {unit}."
        )
        opts, ans = create_option_list(correct, distractors)
        q_obj = {
            "domain": "problem_solving",
            "skill": "6.4",
            "archetype": "draw_diagram_gaps",
            "level": levels[idx],
            "difficulty": difficulties[idx],
            "question_type": "multiple_choice",
            "question": q_text,
            "options": opts,
            "answer": ans,
            "explanation": exp,
            "reasoning": "Using the 'draw a diagram / count gaps' heuristic for objects in a line: Gaps = N - 1.",
            "tags": ["p3", "high_ability", "problem_solving", "draw_diagram", "intervals", "heuristic"],
            "visual_required": False,
            "visual_spec": None
        }
        questions.append(q_obj)
        idx += 1
        
    # Circle questions (10)
    for item in circle_configs:
        obj, setting, n, gap, unit, q_phrase = item
        gaps_count = n
        total_len = gaps_count * gap
        
        q_text = (
            f"{n} {obj} are spaced equally around {setting}, with {gap} {unit} between each adjacent pair. "
            f"What is the {q_phrase}?"
        )
        correct = f"{total_len} {unit}"
        distractor_vals = [(n - 1) * gap, (n + 1) * gap, total_len + 2 * gap, total_len - 2 * gap]
        distractors = [f"{d} {unit}" for d in distractor_vals if f"{d} {unit}" != correct and d > 0]
        exp = (
            f"Draw a diagram: around a closed circle or loop, the number of gaps equals the number of objects. "
            f"With {n} {obj}, there are exactly {n} equal gaps. "
            f"Total distance = {n} × {gap} {unit} = {total_len} {unit}."
        )
        opts, ans = create_option_list(correct, distractors)
        q_obj = {
            "domain": "problem_solving",
            "skill": "6.4",
            "archetype": "draw_diagram_gaps",
            "level": levels[idx],
            "difficulty": difficulties[idx],
            "question_type": "multiple_choice",
            "question": q_text,
            "options": opts,
            "answer": ans,
            "explanation": exp,
            "reasoning": "Using the 'draw a diagram / count gaps' heuristic for objects in a loop: Gaps = N.",
            "tags": ["p3", "high_ability", "problem_solving", "draw_diagram", "intervals", "circle", "heuristic"],
            "visual_required": False,
            "visual_spec": None
        }
        questions.append(q_obj)
        idx += 1
        
    return questions

def generate_skill_6_5():
    """Skill 6.5: Problem Solving - Make a List (Organised Counting) (30 questions).
    Systematic listing across varied scenario types.
    """
    questions = []
    
    levels = ["Think"] * 15 + ["Explore"] * 8 + ["Challenge"] * 7
    difficulties = ["medium"] * 15 + ["easy"] * 8 + ["hard"] * 7
    
    counting_puzzles = [
        # 1. 2-digit numbers from {2, 5, 8} without repetition: 3*2 = 6
        ("How many different 2-digit numbers can you form using the digits 2, 5, and 8 without repeating any digit?",
         "6", ["9", "3", "8"],
         "List systematically by tens digit: 25, 28 (2 numbers); 52, 58 (2 numbers); 82, 85 (2 numbers). Total = 3 × 2 = 6 numbers."),
         
        # 2. 2-letter codes from {A, B, C, D} with repetition allowed: 4*4 = 16
        ("How many different 2-letter codes can be made using the letters A, B, C, and D if letters can be repeated?",
         "16", ["12", "8", "24"],
         "List systematically: First letter has 4 choices (A, B, C, D) and second letter has 4 choices. Total = 4 × 4 = 16 codes."),
         
        # 3. Outfits: 3 shirts and 4 shorts: 3*4 = 12
        ("Mei has 3 shirts (red, blue, green) and 4 pairs of shorts (black, white, grey, navy). How many different outfits of 1 shirt and 1 pair of shorts can she make?",
         "12", ["7", "10", "14"],
         "List systematically: Each of the 3 shirts can be paired with any of the 4 shorts. Total = 3 × 4 = 12 outfits."),
         
        # 4. Handshakes among 4 people: 4*3/2 = 6
        ("Four friends (Ali, Ben, Cai, and Dan) each shake hands with every other friend exactly once. How many handshakes take place in total?",
         "6", ["8", "12", "4"],
         "List pairs systematically: Ali-Ben, Ali-Cai, Ali-Dan (3); Ben-Cai, Ben-Dan (2); Cai-Dan (1). Total = 3 + 2 + 1 = 6 handshakes."),
         
        # 5. 3-letter codes from {X, Y, Z} without repetition: 3*2*1 = 6
        ("How many different 3-letter words (real or made-up) can you form using the letters X, Y, and Z using each letter exactly once?",
         "6", ["9", "3", "27"],
         "List systematically: XYZ, XZY, YXZ, YZX, ZXY, ZYX. There are 6 different arrangements."),
         
        # 6. Meal combos: 2 mains, 3 drinks, 2 desserts: 2*3*2 = 12
        ("A set meal allows you to choose 1 main dish, 1 drink, and 1 dessert. The menu offers 2 mains, 3 drinks, and 2 desserts. How many different meal combinations can you choose?",
         "12", ["7", "10", "18"],
         "Organised counting: Multiply the number of choices for each course: 2 (mains) × 3 (drinks) × 2 (desserts) = 12 combinations."),
         
        # 7. Ways to pay 40 cents using 10-cent and 20-cent coins
        ("How many different ways can you pay exactly 40 cents using only 10-cent and 20-cent coins?",
         "3", ["2", "4", "5"],
         "List combinations systematically by number of 20-cent coins: (1) Two 20¢ coins; (2) One 20¢ and two 10¢ coins; (3) Four 10¢ coins. Total = 3 ways."),
         
        # 8. Choose 2 captains from 5 students: 5*4/2 = 10
        ("A teacher wants to choose 2 captains from a group of 5 students (A, B, C, D, E). How many different pairs of captains can be chosen?",
         "10", ["20", "5", "15"],
         "List pairs systematically: AB, AC, AD, AE (4); BC, BD, BE (3); CD, CE (2); DE (1). Total = 4 + 3 + 2 + 1 = 10 pairs."),
         
        # 9. 2-digit EVEN numbers from {1, 2, 3, 4} with no repetition: ends in 2 or 4 -> 3*2 = 6
        ("How many 2-digit EVEN numbers can be formed using the digits 1, 2, 3, and 4 without repeating any digit?",
         "6", ["8", "4", "12"],
         "An even number must end in 2 or 4. If ending in 2: 12, 32, 42 (3 numbers). If ending in 4: 14, 24, 34 (3 numbers). Total = 3 + 3 = 6 even numbers."),
         
        # 10. Handshakes among 5 people: 5*4/2 = 10
        ("At a chess club meeting, 5 members each play exactly one game against every other member. How many games are played altogether?",
         "10", ["20", "15", "8"],
         "List all pairings systematically: Player 1 plays 4 games; Player 2 plays 3 remaining games; Player 3 plays 2 games; Player 4 plays 1 game. Total = 4 + 3 + 2 + 1 = 10 games."),
         
        # 11. 3-digit numbers from {1, 2, 3} with repetition allowed: 3^3 = 27
        ("How many different 3-digit numbers can be formed using only the digits 1, 2, and 3 if digits CAN be repeated?",
         "27", ["9", "18", "12"],
         "There are 3 choices for the hundreds digit, 3 choices for the tens digit, and 3 choices for the ones digit: 3 × 3 × 3 = 27 numbers."),
         
        # 12. 2-digit numbers greater than 50 from {3, 5, 7, 9} no repeat: tens in {5,7,9} -> 3*3 = 9
        ("How many 2-digit numbers greater than 50 can be formed using the digits 3, 5, 7, and 9 without repeating any digit?",
         "9", ["12", "6", "8"],
         "The tens digit must be 5, 7, or 9 (3 choices). For each tens digit, there are 3 remaining choices for the ones digit. Total = 3 × 3 = 9 numbers (53, 57, 59, 73, 75, 79, 93, 95, 97)."),
         
        # 13. Paths on a 2x2 grid (from top-left to bottom-right, moving only right and down): 6 paths
        ("On a 2 × 2 grid of squares, how many different paths lead from the top-left corner to the bottom-right corner if you can only move Right and Down along grid lines?",
         "6", ["4", "8", "5"],
         "Every path consists of 2 Right (R) and 2 Down (D) steps: RRDD, RDRD, RDDR, DRRD, DRDR, DDRR. Listing them systematically gives 6 paths."),
         
        # 14. Ways to make 50 cents using 10c, 20c, 50c
        ("How many different combinations of 10-cent, 20-cent, and 50-cent coins total exactly 50 cents?",
         "4", ["3", "5", "6"],
         "List by 50¢ and 20¢ coins: (1) One 50¢; (2) Two 20¢ + one 10¢; (3) One 20¢ + three 10¢; (4) Five 10¢ coins. Total = 4 ways."),
         
        # 15. Ice cream cones: 1 cone type (waffle/sugar) x 1 flavour (vanilla, chocolate, strawberry) x 1 topping (sprinkles, nuts): 2*3*2 = 12
        ("An ice cream shop offers 2 types of cones, 3 flavours of ice cream, and 2 choices of toppings. How many different single-scoop ice cream treats with 1 topping can you create?",
         "12", ["7", "8", "18"],
         "List choices systematically: 2 (cone types) × 3 (flavours) × 2 (toppings) = 12 different ice cream treats."),
         
        # 16. Photo arrangement of 3 children in a row: 3! = 6
        ("In how many different orders can 3 children (Sam, Toby, and Uma) stand in a straight line for a photograph?",
         "6", ["3", "9", "8"],
         "List all orders: Sam-Toby-Uma, Sam-Uma-Toby, Toby-Sam-Uma, Toby-Uma-Sam, Uma-Sam-Toby, Uma-Toby-Sam. Total = 6 arrangements."),
         
        # 17. 2-digit ODD numbers from {2, 4, 5, 7} with no repeat: ones digit in {5, 7} -> 3*2 = 6
        ("How many 2-digit ODD numbers can you make using the digits 2, 4, 5, and 7 without repeating any digit?",
         "6", ["8", "4", "12"],
         "The units digit must be odd (5 or 7). If units is 5: 25, 45, 75 (3 numbers). If units is 7: 27, 47, 57 (3 numbers). Total = 3 + 3 = 6 odd numbers."),
         
        # 18. Choosing 2 books from 4 different books: 4*3/2 = 6
        ("Lucas wants to borrow 2 books from a shelf of 4 different books (A, B, C, D). How many different selections of 2 books can he borrow?",
         "6", ["8", "12", "4"],
         "List all pairs: AB, AC, AD (3); BC, BD (2); CD (1). Total = 3 + 2 + 1 = 6 selections."),
         
        # 19. 2-letter codes from {P, Q, R} without repetition: 3*2 = 6
        ("How many 2-letter codes can be made from the letters P, Q, and R if no letter can be used more than once in a code?",
         "6", ["9", "3", "8"],
         "List them: PQ, PR, QP, QR, RP, RQ. There are 6 codes."),
         
        # 20. Ways to form a sum of 7 by rolling two standard 6-sided dice: (1,6),(2,5),(3,4),(4,3),(5,2),(6,1) = 6
        ("When rolling two standard 6-sided dice (a red die and a blue die), in how many different ways can the two numbers add up to 7?",
         "6", ["5", "7", "8"],
         "List the pairs (Red, Blue): (1,6), (2,5), (3,4), (4,3), (5,2), (6,1). Total = 6 ways."),
         
        # 21. 3-digit numbers from {4, 7} with repetition allowed: 2^3 = 8
        ("How many different 3-digit numbers can be formed using ONLY the digits 4 and 7 (repetition is allowed)?",
         "8", ["6", "9", "4"],
         "List systematically: 444, 447, 474, 477, 744, 747, 774, 777. Total = 2 × 2 × 2 = 8 numbers."),
         
        # 22. Matching pairs: 3 boys and 3 girls pair up for a dance: 1 boy and 1 girl pair: 3*3 = 9 possible pairs
        ("How many different boy-girl dance pairs can be formed from a group of 3 boys and 3 girls?",
         "9", ["6", "12", "3"],
         "Each of the 3 boys can be paired with any of the 3 girls: 3 × 3 = 9 possible pairs."),
         
        # 23. Ways to pay 30 cents using only 10-cent and 20-cent coins
        ("How many different ways can you make exactly 30 cents using only 10-cent and 20-cent coins?",
         "2", ["3", "4", "1"],
         "List combinations: (1) One 20¢ + one 10¢; (2) Three 10¢ coins. Total = 2 ways."),
         
        # 24. 3-digit numbers with digits summing to 4 (using digits > 0): 112, 121, 211, 130?, digits > 0: 112, 121, 211, 220?
        # Let's do: How many 2-digit numbers have digits that add up to 6?
        # 15, 24, 33, 42, 51, 60 = 6 numbers
        ("How many 2-digit numbers have digits that add up to 6?",
         "6", ["5", "7", "4"],
         "List systematically starting from tens digit 1 to 6: 15, 24, 33, 42, 51, 60. Total = 6 numbers."),
         
        # 25. How many 2-digit numbers have digits that add up to 5?
        # 14, 23, 32, 41, 50 = 5 numbers
        ("How many 2-digit numbers have digits that add up to 5?",
         "5", ["4", "6", "3"],
         "List systematically by tens digit: 14, 23, 32, 41, 50. Total = 5 numbers."),
         
        # 26. Triangular tournament matches: 6 teams each play each other once: 6*5/2 = 15
        ("In a school soccer tournament with 6 teams, every team plays against every other team once. How many matches are played in total?",
         "15", ["12", "18", "30"],
         "List systematically: Team 1 plays 5 games; Team 2 plays 4 remaining; Team 3 plays 3; Team 4 plays 2; Team 5 plays 1. Total = 5 + 4 + 3 + 2 + 1 = 15 matches."),
         
        # 27. Arranging 4 books on a shelf where Math book is always on the far left: 3! = 6
        ("Four books (Math, Science, English, Art) are placed on a shelf in a row. If the Math book must always be on the far left, in how many different orders can all four books be arranged?",
         "6", ["24", "4", "8"],
         "The Math book is fixed in position 1. The remaining 3 positions can be filled by Science, English, and Art in 3 × 2 × 1 = 6 different ways."),
         
        # 28. Choose 1 main and 1 side from 4 mains and 3 sides: 4*3 = 12
        ("A cafeteria lunch menu has 4 main dishes and 3 side dishes. How many different lunches containing 1 main dish and 1 side dish can you choose?",
         "12", ["7", "14", "9"],
         "Multiply choices: 4 (mains) × 3 (sides) = 12 different lunch combinations."),
         
        # 29. 2-digit numbers using {1, 3, 5, 7} that are less than 50, no repeat: tens in {1, 3} -> 2*3 = 6
        ("How many 2-digit numbers less than 50 can be formed using the digits 1, 3, 5, and 7 without repeating any digit?",
         "6", ["8", "4", "12"],
         "The tens digit must be 1 or 3 (2 choices). For each, there are 3 remaining choices for the ones digit. List: 13, 15, 17, 31, 35, 37. Total = 6 numbers."),
         
        # 30. Ways to form a sum of 8 by rolling two standard 6-sided dice: (2,6), (3,5), (4,4), (5,3), (6,2) = 5
        ("When rolling two standard 6-sided dice, in how many different ways can the two rolled numbers sum to 8?",
         "5", ["6", "4", "7"],
         "List all pairs (Die 1, Die 2): (2,6), (3,5), (4,4), (5,3), (6,2). Total = 5 ways.")
    ]
    
    for i, item in enumerate(counting_puzzles):
        q_text, correct, distractors, exp = item
        opts, ans = create_option_list(correct, distractors)
        q_obj = {
            "domain": "problem_solving",
            "skill": "6.5",
            "archetype": "make_a_list",
            "level": levels[i],
            "difficulty": difficulties[i],
            "question_type": "multiple_choice",
            "question": q_text,
            "options": opts,
            "answer": ans,
            "explanation": exp,
            "reasoning": "Using the 'make an organised list' heuristic to systematically count all valid possibilities.",
            "tags": ["p3", "high_ability", "problem_solving", "make_a_list", "counting", "combinatorics", "heuristic"],
            "visual_required": False,
            "visual_spec": None
        }
        questions.append(q_obj)
        
    return questions

def generate_skill_6_6():
    """Skill 6.6: Problem Solving - Pattern Application (Discover & Apply a Rule) (30 questions).
    Show 3 clear examples that determine a unique mathematical rule, then ask for a new input.
    Must use wide variety of rules (at least 10+ distinct rules).
    """
    questions = []
    
    levels = ["Think"] * 15 + ["Explore"] * 8 + ["Challenge"] * 7
    difficulties = ["medium"] * 15 + ["easy"] * 8 + ["hard"] * 7
    
    rule_configs = [
        # (rule_name, func, str_rule, [(in1, out1), (in2, out2), (in3, out3)], query_in, distractors)
        ("x2 + 1", lambda x: x * 2 + 1, "output = (input × 2) + 1", [(2, 5), (3, 7), (4, 9)], 7, [13, 14, 16]),
        ("x3 - 1", lambda x: x * 3 - 1, "output = (input × 3) − 1", [(2, 5), (3, 8), (4, 11)], 6, [16, 18, 15]),
        ("x2 - 1", lambda x: x * 2 - 1, "output = (input × 2) − 1", [(3, 5), (4, 7), (5, 9)], 8, [14, 16, 17]),
        ("x3 + 2", lambda x: x * 3 + 2, "output = (input × 3) + 2", [(1, 5), (2, 8), (3, 11)], 5, [16, 18, 15]),
        ("x^2 + 1", lambda x: x * x + 1, "output = (input × input) + 1", [(2, 5), (3, 10), (4, 17)], 5, [24, 25, 27]),
        ("x^2 - 1", lambda x: x * x - 1, "output = (input × input) − 1", [(2, 3), (3, 8), (4, 15)], 6, [34, 36, 37]),
        ("(x + 2) * 2", lambda x: (x + 2) * 2, "output = (input + 2) × 2", [(1, 6), (2, 8), (3, 10)], 6, [14, 18, 15]),
        ("x4 - 3", lambda x: x * 4 - 3, "output = (input × 4) − 3", [(1, 1), (2, 5), (3, 9)], 5, [16, 18, 15]),
        ("x*(x+1)", lambda x: x * (x + 1), "output = input × (input + 1)", [(2, 6), (3, 12), (4, 20)], 5, [25, 35, 28]),
        ("x5 - 2", lambda x: x * 5 - 2, "output = (input × 5) − 2", [(2, 8), (3, 13), (4, 18)], 6, [26, 30, 27]),
        
        ("(x + 1) * 3", lambda x: (x + 1) * 3, "output = (input + 1) × 3", [(1, 6), (2, 9), (3, 12)], 5, [16, 20, 15]),
        ("x2 + 3", lambda x: x * 2 + 3, "output = (input × 2) + 3", [(2, 7), (3, 9), (4, 11)], 8, [18, 20, 17]),
        ("x3 - 2", lambda x: x * 3 - 2, "output = (input × 3) − 2", [(2, 4), (3, 7), (4, 10)], 7, [18, 20, 21]),
        ("x4 + 1", lambda x: x * 4 + 1, "output = (input × 4) + 1", [(1, 5), (2, 9), (3, 13)], 6, [24, 26, 23]),
        ("(x - 1) * 4", lambda x: (x - 1) * 4, "output = (input − 1) × 4", [(2, 4), (3, 8), (4, 12)], 7, [20, 28, 22]),
        ("x2 + 5", lambda x: x * 2 + 5, "output = (input × 2) + 5", [(1, 7), (2, 9), (3, 11)], 7, [17, 20, 18]),
        ("x3 + 3", lambda x: x * 3 + 3, "output = (input × 3) + 3", [(1, 6), (2, 9), (3, 12)], 6, [18, 22, 20]),
        ("x^2 + 2", lambda x: x * x + 2, "output = (input × input) + 2", [(1, 3), (2, 6), (3, 11)], 5, [25, 26, 28]),
        ("(x + 3) * 2", lambda x: (x + 3) * 2, "output = (input + 3) × 2", [(1, 8), (2, 10), (3, 12)], 6, [16, 20, 17]),
        ("x5 + 1", lambda x: x * 5 + 1, "output = (input × 5) + 1", [(1, 6), (2, 11), (3, 16)], 4, [20, 22, 19]),
        
        ("x*(x-1)", lambda x: x * (x - 1), "output = input × (input − 1)", [(2, 2), (3, 6), (4, 12)], 6, [24, 36, 28]),
        ("(x + 1)^2", lambda x: (x + 1) * (x + 1), "output = (input + 1) × (input + 1)", [(1, 4), (2, 9), (3, 16)], 4, [20, 24, 26]),
        ("x4 - 1", lambda x: x * 4 - 1, "output = (input × 4) − 1", [(2, 7), (3, 11), (4, 15)], 6, [22, 24, 25]),
        ("x3 + 4", lambda x: x * 3 + 4, "output = (input × 3) + 4", [(1, 7), (2, 10), (3, 13)], 5, [18, 20, 17]),
        ("x2 + 7", lambda x: x * 2 + 7, "output = (input × 2) + 7", [(1, 9), (2, 11), (3, 13)], 6, [17, 20, 18]),
        ("(x - 1) * 5 + 2", lambda x: (x - 1) * 5 + 2, "output = (input − 1) × 5 + 2", [(2, 7), (3, 12), (4, 17)], 6, [25, 29, 26]),
        ("x6 - 3", lambda x: x * 6 - 3, "output = (input × 6) − 3", [(1, 3), (2, 9), (3, 15)], 5, [25, 30, 26]),
        ("(x + 4) * 2", lambda x: (x + 4) * 2, "output = (input + 4) × 2", [(1, 10), (2, 12), (3, 14)], 5, [16, 20, 17]),
        ("x4 - 2", lambda x: x * 4 - 2, "output = (input × 4) − 2", [(2, 6), (3, 10), (4, 14)], 6, [20, 24, 21]),
        ("x2 + 6", lambda x: x * 2 + 6, "output = (input × 2) + 6", [(1, 8), (2, 10), (3, 12)], 7, [18, 22, 19])
    ]
    
    machine_names = [
        "A number machine", "A magic box", "A number pattern machine", "A math robot",
        "A secret code machine", "A number transformer", "A math puzzle box", "A function machine",
        "A number processor", "A calculation device"
    ]
    
    for i, cfg in enumerate(rule_configs):
        r_name, func, r_str, examples, q_in, dists = cfg
        m_name = machine_names[i % len(machine_names)]
        
        ex_str = ", ".join(f"{inp} → {out}" for inp, out in examples)
        correct_val = func(q_in)
        correct_text = str(correct_val)
        dist_texts = [str(d) for d in dists]
        
        q_text = (
            f"{m_name} changes numbers following a secret rule: {ex_str}. "
            f"If the input is {q_in}, what number comes out?"
        )
        
        ex_proofs = ", ".join(f"{inp} follows {r_str.replace('input', str(inp))} = {out}" for inp, out in examples)
        exp = (
            f"Discover the rule by testing the examples: {ex_proofs}. "
            f"The rule is: {r_str}. "
            f"Applying this rule to the input {q_in}: {r_str.replace('input', str(q_in))} = {correct_val}."
        )
        
        opts, ans = create_option_list(correct_text, dist_texts)
        q_obj = {
            "domain": "problem_solving",
            "skill": "6.6",
            "archetype": "pattern_application",
            "level": levels[i],
            "difficulty": difficulties[i],
            "question_type": "multiple_choice",
            "question": q_text,
            "options": opts,
            "answer": ans,
            "explanation": exp,
            "reasoning": "Discovering a functional algebraic/arithmetic rule from input-output examples and applying it to a new value.",
            "tags": ["p3", "high_ability", "problem_solving", "pattern_application", "function_rule", "heuristic"],
            "visual_required": False,
            "visual_spec": None
        }
        questions.append(q_obj)
        
    return questions

def main():
    q_1_3 = generate_skill_1_3()
    q_1_4 = generate_skill_1_4()
    q_2_2 = generate_skill_2_2()
    q_2_3 = generate_skill_2_3()
    q_3_6 = generate_skill_3_6()
    q_6_3 = generate_skill_6_3()
    q_6_4 = generate_skill_6_4()
    q_6_5 = generate_skill_6_5()
    q_6_6 = generate_skill_6_6()
    
    all_questions = q_1_3 + q_1_4 + q_2_2 + q_2_3 + q_3_6 + q_6_3 + q_6_4 + q_6_5 + q_6_6
    
    print(f"Generated {len(all_questions)} questions in total.")
    counts = {
        "1.3": len(q_1_3),
        "1.4": len(q_1_4),
        "2.2": len(q_2_2),
        "2.3": len(q_2_3),
        "3.6": len(q_3_6),
        "6.3": len(q_6_3),
        "6.4": len(q_6_4),
        "6.5": len(q_6_5),
        "6.6": len(q_6_6)
    }
    for sk, c in counts.items():
        print(f"  Skill {sk}: {c}")
        
    # Rigorous QA checks
    assert len(all_questions) == 275, f"Expected 275 questions, got {len(all_questions)}"
    
    required_keys = {
        "domain", "skill", "archetype", "level", "difficulty",
        "question_type", "question", "options", "answer",
        "explanation", "reasoning", "tags", "visual_required", "visual_spec"
    }
    forbidden_keys = {"id", "qa_status", "provenance", "image_path"}
    
    for idx, q in enumerate(all_questions):
        # Key check
        q_keys = set(q.keys())
        assert q_keys == required_keys, f"Q#{idx} key mismatch: {q_keys ^ required_keys}"
        for fk in forbidden_keys:
            assert fk not in q, f"Q#{idx} contains forbidden key {fk}"
            
        # Options check
        assert len(q["options"]) == 4, f"Q#{idx} options count != 4"
        opt_ids = [opt["id"] for opt in q["options"]]
        assert opt_ids == ["A", "B", "C", "D"], f"Q#{idx} opt ids != A-D: {opt_ids}"
        opt_texts = [opt["text"] for opt in q["options"]]
        assert len(set(opt_texts)) == 4, f"Q#{idx} duplicate option texts: {opt_texts}"
        
        # Answer check
        assert q["answer"] in ["A", "B", "C", "D"], f"Q#{idx} answer invalid: {q['answer']}"
        ans_idx = ord(q["answer"]) - ord('A')
        chosen_opt_text = q["options"][ans_idx]["text"]
        assert len(chosen_opt_text.strip()) > 0, f"Q#{idx} chosen option text is empty"
        
        # Skill 3.6 letter check
        if q["skill"] == "3.6":
            for opt in q["options"]:
                txt = opt["text"]
                assert len(txt) == 1 and txt.isupper() and txt.isalpha(), f"Q#{idx} 3.6 invalid letter option: '{txt}'"
                
        # Clean names check (no trailing digits like Ben1)
        for opt in q["options"]:
            assert not re.search(r'[A-Za-z]+\d+', opt["text"]), f"Q#{idx} option has trailing digit: {opt['text']}"
            
        # Visual check
        assert q["visual_required"] is False, f"Q#{idx} visual_required is not False"
        assert q["visual_spec"] is None, f"Q#{idx} visual_spec is not None"
        
    print("All 275 questions passed strict validation!")
    
    # Save output to bank/regenerated_questions.json and workspace root regenerated_questions.json
    out_paths = [
        "c:/Projects/brainactive-android/revamp/bank/regenerated_questions.json",
        "c:/Projects/brainactive-android/regenerated_questions.json"
    ]
    for p in out_paths:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(all_questions, f, indent=2, ensure_ascii=False)
        print(f"Wrote {len(all_questions)} questions to {p}")

if __name__ == "__main__":
    main()
