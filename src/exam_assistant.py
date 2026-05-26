"""
exam_assistant.py — Interactive English 3 Exam Assistant (CLI, stdlib only).
Menu-driven tool covering all 4 exam parts. Data lives in grammar_cards.py.
"""

import re
import sys
import random
from typing import Dict, List, Tuple

try:
    import grammar_cards as gc
except ImportError:
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    import grammar_cards as gc


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

W = 62

def hr(char: str = "=") -> None:
    print(char * W)

def title_box(text: str) -> None:
    hr()
    print(f"  {text}")
    hr("-")

def section(text: str) -> None:
    print(f"\n  [{text}]\n  " + "-" * (len(text) + 2))

def pause() -> None:
    input("\n  Press ENTER to continue...")

def wrap(text: str, indent: int = 2) -> None:
    pad = " " * indent
    words, line = text.split(), []
    for w in words:
        if sum(len(x) + 1 for x in line) + len(w) > W - indent:
            print(pad + " ".join(line))
            line = [w]
        else:
            line.append(w)
    if line:
        print(pad + " ".join(line))


# ---------------------------------------------------------------------------
# 1. Grammar Reference
# ---------------------------------------------------------------------------

def show_grammar_reference() -> None:
    while True:
        print()
        title_box("GRAMMAR REFERENCE")
        menu = [
            "Future Forms (Will / Be Going To / Pres. Simple / Pres. Continuous)",
            "Future Time Clauses — The Golden Rule",
            "Comparatives and Superlatives",
            "Cohesion: Connectors and Time Expressions",
            "Writing Checklist (Part IV)",
            "Listening Tips (Part II)",
            "Back to Main Menu",
        ]
        for i, opt in enumerate(menu, 1):
            print(f"    {i}. {opt}")
        ch = input("\n  Choose (1-7): ").strip()
        if ch == "7":
            break
        handlers = [None, _ref_future_forms, _ref_time_clauses,
                    _ref_comparatives, _ref_cohesion, _ref_checklist, _ref_listening]
        if ch.isdigit() and 1 <= int(ch) <= 6:
            handlers[int(ch)]()
        else:
            print("  Invalid option.")


def _ref_future_forms() -> None:
    for f in gc.FUTURE_FORMS:
        hr()
        print(f"\n  ** {f['name']} **\n")
        print(f"  Structure : {f['structure']}")
        print(f"  Negative  : {f['negative']}")
        print(f"  Question  : {f['question']}")
        section("Uses")
        for u in f["uses"]:
            print(f"    + {u}")
        section("Examples")
        for ex in f["examples"]:
            print(f"    > {ex}")
        if f["trigger_words"]:
            print(f"\n  Triggers: {', '.join(f['trigger_words'])}")
        if f["warning"]:
            print(f"\n  WARNING: {f['warning']}")
        print()
    pause()


def _ref_time_clauses() -> None:
    d = gc.FUTURE_TIME_CLAUSES
    hr()
    print(f"\n  ** {d['title']} **\n")
    wrap(d["rule"])
    print(f"\n  Conjunctions: {', '.join(d['conjunctions'])}")
    section("Correct")
    for ex in d["correct_examples"]:
        print(f"    OK > {ex}")
    section("Incorrect")
    for ex in d["incorrect_examples"]:
        print(f"    NO > {ex}")
    print(f"\n  TIP: {d['memory_tip']}")
    hr()
    pause()


def _ref_comparatives() -> None:
    d = gc.COMPARATIVES_SUPERLATIVES
    hr()
    print(f"\n  ** {d['title']} **\n")
    for sec in d["sections"]:
        print(f"  Type: {sec['type']}")
        print(f"    Comparative : {sec['comparative']}")
        print(f"    Superlative : {sec['superlative']}")
        for ex in sec["examples"]:
            print(f"      {ex['adj']:15} -> {ex['comp']:28} | {ex['sup']}")
        print()
    section("Tech Examples")
    for ex in d["tech_examples"]:
        print(f"    > {ex}")
    hr()
    pause()


def _ref_cohesion() -> None:
    d = gc.COHESION
    hr()
    print(f"\n  ** {d['title']} **\n")
    section("Connectors")
    for c in d["connectors"]:
        print(f"    {c['word']:12} [{c['function']}]")
        print(f"               Ex: {c['example']}\n")
    section("Time Expressions")
    print("    " + " | ".join(d["time_expressions"]))
    hr()
    pause()


def _ref_checklist() -> None:
    d = gc.WRITING_CHECKLIST
    hr()
    print(f"\n  ** {d['title']} **\n")
    wc = d["word_count"]
    print(f"  Word count: {wc['min']}–{wc['max']} words\n")
    for el in d["required_elements"]:
        pts = el["points"]
        print(f"  [{pts} pt{'s' if pts > 1 else ' '}] {el['label']}")
        print(f"         Ex: {el['example']}\n")
    total = sum(e["points"] for e in d["required_elements"])
    print(f"  Total: {total} points")
    print(f"\n  Action verbs: {', '.join(d['action_verbs'])}")
    hr()
    pause()


def _ref_listening() -> None:
    d = gc.LISTENING_TIPS
    hr()
    print(f"\n  ** {d['title']} **\n")
    section("What to Listen For")
    for t in d["key_listening_targets"]:
        print(f"    - {t}")
    section("Common Comparatives in Audio")
    print("    " + " | ".join(d["common_comparatives_in_audio"]))
    section("Strategies")
    for s in d["strategies"]:
        print(f"    {s}")
    hr()
    pause()


# ---------------------------------------------------------------------------
# 2. Practice Generator
# ---------------------------------------------------------------------------

def run_practice_generator() -> None:
    while True:
        print()
        title_box("PRACTICE GENERATOR")
        menu = [
            "Reading Comprehension (tech text + questions)",
            "Comparative / Superlative fill-in-the-blank",
            "Future Forms fill-in-the-blank",
            "Error Correction — Future Time Clauses",
            "Back to Main Menu",
        ]
        for i, o in enumerate(menu, 1):
            print(f"    {i}. {o}")
        ch = input("\n  Choose (1-5): ").strip()
        if ch == "5":
            break
        elif ch == "1":
            _practice_reading()
        elif ch == "2":
            _practice_drills(gc.FILL_IN_BLANK_COMPARATIVE, "COMPARATIVES / SUPERLATIVES")
        elif ch == "3":
            _practice_drills(gc.FILL_IN_BLANK_FUTURE, "FUTURE FORMS")
        elif ch == "4":
            _practice_error_correction()
        else:
            print("  Invalid option.")


def _practice_reading() -> None:
    td = random.choice(gc.READING_TEXTS)
    hr()
    print(f"\n  TEXT: {td['title']}\n")
    hr("-")
    wrap(td["text"])
    hr()
    print("\n  COMPREHENSION QUESTIONS:\n")
    for i, q in enumerate(td["questions"], 1):
        print(f"  {i}. {q}")
        input("     Your answer: ")
        print(f"     Model answer: {td['answers'][i-1]}\n")
    pause()


def _practice_drills(drills: List[Dict], topic: str) -> None:
    exercises = random.sample(drills, min(4, len(drills)))
    hr()
    print(f"\n  FILL-IN-THE-BLANK: {topic}\n")
    score = 0
    for i, ex in enumerate(exercises, 1):
        print(f"  {i}. {ex['sentence']}")
        ans = input("     Your answer: ").strip().lower()
        correct = ex["answer"].lower()
        if correct in ans or ans in correct:
            print(f"     Correct! ({ex['answer']})")
            score += 1
        else:
            print(f"     Correct answer: {ex['answer']}")
        print(f"     Rule: {ex['rule']}\n")
    print(f"  Score: {score}/{len(exercises)}")
    pause()


def _practice_error_correction() -> None:
    exercises = random.sample(gc.ERROR_CORRECTION, min(4, len(gc.ERROR_CORRECTION)))
    hr()
    print("\n  ERROR CORRECTION — Find the mistake in each sentence.\n")
    score = 0
    for i, ex in enumerate(exercises, 1):
        print(f"  {i}. {ex['sentence']}")
        input("     What is the error? ")
        print(f"     Error   : {ex['error']}")
        print(f"     Fixed   : {ex['correction']}")
        print(f"     Rule    : {ex['rule']}")
        got_it = input("     Did you get it right? (y/n): ").strip().lower()
        if got_it == "y":
            score += 1
        print()
    print(f"  Score: {score}/{len(exercises)}")
    pause()


# ---------------------------------------------------------------------------
# 3. Writing Assistant
# ---------------------------------------------------------------------------

_CONNECTORS = [
    "and", "because", "but", "so", "however", "therefore",
    "although", "even though", "since", "moreover", "furthermore",
]
_TIME_EXPRS = [
    "soon", "next semester", "next week", "next month", "next year",
    "then", "before", "after", "later", "in the future",
    "by the end of the year", "in december", "in january", "in february",
    "in march", "on monday", "on tuesday", "on wednesday", "on thursday",
    "on friday", "this afternoon", "tomorrow", "eventually",
    "in the coming months", "next quarter", "by then",
]
_SCHEDULE_VERBS = [
    "starts", "begins", "opens", "closes", "departs", "arrives",
    "ends", "finishes", "leaves", "runs", "takes place",
]


def _count_words(text: str) -> int:
    return len(text.split())


def _check(pattern: str, text: str) -> Tuple[bool, str]:
    found = re.findall(pattern, text, re.IGNORECASE)
    return bool(found), f"Found: {found[:2]}" if found else "Not found"


def analyze_paragraph(text: str) -> Dict:
    will_ok, will_d = _check(r"\b(will\s+\w+|won't\s+\w+)\b", text)
    bgt_ok, bgt_d = _check(r"\b(am|is|are)\s+going\s+to\s+\w+", text)

    ps_ok = any(re.search(r"\b" + v + r"\b", text, re.IGNORECASE) for v in _SCHEDULE_VERBS)
    ps_d = next((f"Marker: '{v}'" for v in _SCHEDULE_VERBS
                 if re.search(r"\b" + v + r"\b", text, re.IGNORECASE)),
                "No schedule verb (starts/begins/opens/closes...)")

    cleaned = re.sub(r"\b(am|is|are)\s+going\s+to\b", "", text, flags=re.IGNORECASE)
    pc_ok, pc_d = _check(r"\b(am|is|are)\s+\w+ing\b", cleaned)

    found_conn = [c for c in _CONNECTORS if re.search(r"\b" + c + r"\b", text, re.IGNORECASE)]
    conn_ok = len(found_conn) >= 2
    conn_d = f"Found: {found_conn}" if found_conn else "None found"

    lower = text.lower()
    found_time = [t for t in _TIME_EXPRS if t in lower]
    time_ok = bool(found_time)
    time_d = f"Found: {found_time}" if found_time else "Not found"

    wc = _count_words(text)
    limits = gc.WRITING_CHECKLIST["word_count"]
    score = (2 * will_ok + 2 * bgt_ok + ps_ok + 2 * pc_ok
             + 2 * conn_ok + time_ok)

    return {
        "word_count": wc,
        "word_count_ok": limits["min"] <= wc <= limits["max"],
        "will": (will_ok, will_d),
        "be_going_to": (bgt_ok, bgt_d),
        "present_simple_schedule": (ps_ok, ps_d),
        "present_continuous": (pc_ok, pc_d),
        "connectors": (conn_ok, conn_d, len(found_conn)),
        "time_expressions": (time_ok, time_d),
        "score": score,
    }


def print_analysis(r: Dict) -> None:
    hr()
    wc_tag = "OK" if r["word_count_ok"] else "NEEDS FIX"
    print(f"\n  Word count: {r['word_count']} [{wc_tag}] (target: 70-90)\n")
    hr("-")
    checks = [
        ("Will", r["will"], 2),
        ("Be going to", r["be_going_to"], 2),
        ("Present Simple (schedule)", r["present_simple_schedule"], 1),
        ("Present Continuous", r["present_continuous"], 2),
        ("Connectors (need 2+)", r["connectors"], 2),
        ("Time expression", r["time_expressions"], 1),
    ]
    for label, data, pts in checks:
        ok = data[0]
        detail = data[1]
        mark = "OK" if ok else "MISSING"
        earned = pts if ok else 0
        print(f"  [{mark:^7}] {label:35} ({earned}/{pts} pts)")
        print(f"           {detail}\n")
    print(f"  TOTAL SCORE: {r['score']}/10")
    _print_feedback(r)
    hr()


def _print_feedback(r: Dict) -> None:
    if r["score"] == 10 and r["word_count_ok"]:
        print("\n  Perfect! This paragraph meets all requirements.")
        return
    print("\n  What to fix:")
    if not r["word_count_ok"]:
        diff = abs(r["word_count"] - (90 if r["word_count"] > 90 else 70))
        action = "Remove" if r["word_count"] > 90 else "Add"
        print(f"    - {action} approximately {diff} word(s).")
    if not r["will"][0]:
        print("    - Add 'will + verb' for a prediction or promise.")
    if not r["be_going_to"][0]:
        print("    - Add 'am/is/are going to + verb' for a prior plan.")
    if not r["present_simple_schedule"][0]:
        print("    - Add a schedule sentence (e.g. 'The course starts on...').")
    if not r["present_continuous"][0]:
        print("    - Add 'am/is/are + verb-ing' for a confirmed arrangement.")
    if not r["connectors"][0]:
        print(f"    - Add more connectors (you have {r['connectors'][2]}, need at least 2).")
    if not r["time_expressions"][0]:
        print("    - Add a time expression (next semester, soon, in December...).")


def run_writing_assistant() -> None:
    print()
    title_box("WRITING ASSISTANT — PART IV")
    print("\n  Write your paragraph (70-90 words).")
    print("  Press ENTER twice when done.\n")
    while True:
        lines: List[str] = []
        try:
            while True:
                line = input("  > ")
                if line == "" and lines and lines[-1] == "":
                    break
                lines.append(line)
        except EOFError:
            break
        text = " ".join(l for l in lines if l.strip())
        if not text.strip():
            print("  No text entered.")
            break
        print_analysis(analyze_paragraph(text))
        if input("\n  Revise and check again? (y/n): ").strip().lower() != "y":
            break


# ---------------------------------------------------------------------------
# 4. Sample Model Paragraphs
# ---------------------------------------------------------------------------

def run_sample_writing() -> None:
    print()
    title_box("SAMPLE MODEL PARAGRAPHS — SCORE 10/10")
    for i, para in enumerate(gc.MODEL_PARAGRAPHS, 1):
        hr()
        print(f"\n  SAMPLE {i}: {para['title']}  [Score: {para['score']}/10]\n")
        hr("-")
        wrap(para["text"])
        print(f"\n  Word count: {_count_words(para['text'])}")
        section("Why it scores 10/10")
        for note in para["notes"]:
            print(f"    + {note}")
        print()
    hr()
    pause()


# ---------------------------------------------------------------------------
# Main Menu
# ---------------------------------------------------------------------------

BANNER = """
  =====================================================
   ENGLISH 3 — EXAM ASSISTANT
   Interactive CLI Preparation Tool
  ====================================================="""


def main_menu() -> None:
    while True:
        print(BANNER)
        hr("-")
        print("  MAIN MENU\n")
        opts = [
            ("1", "Grammar Reference        (all rules + examples)"),
            ("2", "Practice Generator      (drills for all parts)"),
            ("3", "Writing Assistant       (check your paragraph)"),
            ("4", "Sample Model Paragraphs (10/10 examples)"),
            ("5", "Exit"),
        ]
        for key, label in opts:
            print(f"    {key}. {label}")
        hr("-")
        ch = input("\n  Enter your choice (1-5): ").strip()
        if ch == "1":
            show_grammar_reference()
        elif ch == "2":
            run_practice_generator()
        elif ch == "3":
            run_writing_assistant()
        elif ch == "4":
            run_sample_writing()
        elif ch == "5":
            print("\n  Good luck on your exam!\n")
            sys.exit(0)
        else:
            print("  Invalid option. Please enter 1-5.")
            pause()
        print()


if __name__ == "__main__":
    main_menu()
