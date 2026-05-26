"""
grammar_cards.py — Standalone grammar reference module.
All rules stored as data structures; import and display as flashcard-style review.
"""

from typing import Dict, List


# ---------------------------------------------------------------------------
# Future Forms
# ---------------------------------------------------------------------------

FUTURE_FORMS: List[Dict] = [
    {
        "name": "WILL",
        "structure": "Subject + will + base verb",
        "negative": "Subject + will not (won't) + base verb",
        "question": "Will + subject + base verb?",
        "uses": [
            "Spontaneous decisions made at the moment of speaking",
            "Promises",
            "Opinion-based predictions (I think / I believe / I'm sure...)",
        ],
        "examples": [
            "I think AI will replace many entry-level jobs.",
            "I'll help you with that report right now.",
            "She will definitely pass the certification exam.",
            "I believe the software will be ready by Friday.",
        ],
        "trigger_words": ["I think", "I believe", "I'm sure", "probably", "maybe"],
        "warning": "Do NOT use 'will' inside time clauses (after when/before/after/as soon as/if).",
    },
    {
        "name": "BE GOING TO",
        "structure": "Subject + am/is/are + going to + base verb",
        "negative": "Subject + am/is/are + not going to + base verb",
        "question": "Am/Is/Are + subject + going to + base verb?",
        "uses": [
            "Prior plans and intentions (decided before speaking)",
            "Evidence-based predictions (you can see proof now)",
        ],
        "examples": [
            "I am going to graduate in December.",
            "She is going to apply for the data science position.",
            "Look at those dark clouds — it is going to rain.",
            "We are going to launch the app next quarter.",
        ],
        "trigger_words": ["I plan to", "I intend to", "I have decided to"],
        "warning": None,
    },
    {
        "name": "PRESENT SIMPLE (future meaning)",
        "structure": "Subject + base verb (+ -s/-es for he/she/it)",
        "negative": "Subject + do/does + not + base verb",
        "question": "Do/Does + subject + base verb?",
        "uses": [
            "ONLY for fixed, official schedules and timetables (calendars, transport, events)",
        ],
        "examples": [
            "The train leaves at 9:00 AM tomorrow.",
            "The conference starts on Monday.",
            "The exam begins at 8:30 AM.",
            "Our flight departs at 6:15 PM.",
        ],
        "trigger_words": ["timetable", "schedule", "calendar", "departs", "leaves", "starts", "begins"],
        "warning": "Only use for external, fixed schedules — NOT for personal plans.",
    },
    {
        "name": "PRESENT CONTINUOUS (future meaning)",
        "structure": "Subject + am/is/are + verb-ing",
        "negative": "Subject + am/is/are + not + verb-ing",
        "question": "Am/Is/Are + subject + verb-ing?",
        "uses": [
            "Confirmed personal arrangements (booked, agreed, or organized in advance)",
        ],
        "examples": [
            "I am meeting the client tomorrow at 10 AM.",
            "We are presenting our project on Thursday.",
            "She is starting her internship next week.",
            "They are attending the tech summit on Friday.",
        ],
        "trigger_words": ["tomorrow", "next week", "on [day]", "this evening"],
        "warning": "There must be a prior arrangement — not just a plan in your head.",
    },
]


# ---------------------------------------------------------------------------
# Future Time Clauses — The Golden Rule
# ---------------------------------------------------------------------------

FUTURE_TIME_CLAUSES: Dict = {
    "title": "FUTURE TIME CLAUSES — THE GOLDEN RULE",
    "rule": (
        "After time conjunctions (when / before / after / as soon as / until / once / if), "
        "you MUST use Present Simple — even when the meaning is future."
    ),
    "conjunctions": ["when", "before", "after", "as soon as", "until", "once", "if"],
    "correct_examples": [
        "As soon as you get to the city, call me.",
        "When she finishes the report, she will send it.",
        "Before the meeting starts, review the slides.",
        "I will contact you after I arrive at the office.",
        "Once he completes the course, he is going to apply for a promotion.",
    ],
    "incorrect_examples": [
        "As soon as you will get to the city, call me.  [WRONG — no will after as soon as]",
        "When she will finish the report, she will send it.  [WRONG — no will after when]",
        "Before the meeting will start, review the slides.  [WRONG]",
    ],
    "memory_tip": (
        "Think: the time clause describes a condition, not a promise. "
        "Only the MAIN clause can carry 'will' or 'be going to'."
    ),
}


# ---------------------------------------------------------------------------
# Comparatives and Superlatives
# ---------------------------------------------------------------------------

COMPARATIVES_SUPERLATIVES: Dict = {
    "title": "COMPARATIVES AND SUPERLATIVES",
    "sections": [
        {
            "type": "Short adjectives (1 syllable)",
            "comparative": "adjective + -er + than",
            "superlative": "the + adjective + -est",
            "examples": [
                {"adj": "fast", "comp": "faster than", "sup": "the fastest"},
                {"adj": "safe", "comp": "safer than", "sup": "the safest"},
                {"adj": "hard", "comp": "harder than", "sup": "the hardest"},
                {"adj": "long", "comp": "longer than", "sup": "the longest"},
            ],
        },
        {
            "type": "Long adjectives (2+ syllables)",
            "comparative": "more + adjective + than",
            "superlative": "the most + adjective",
            "examples": [
                {"adj": "innovative", "comp": "more innovative than", "sup": "the most innovative"},
                {"adj": "demanding", "comp": "more demanding than", "sup": "the most demanding"},
                {"adj": "efficient", "comp": "more efficient than", "sup": "the most efficient"},
                {"adj": "complex", "comp": "more complex than", "sup": "the most complex"},
            ],
        },
        {
            "type": "Irregulars",
            "comparative": "(see examples)",
            "superlative": "(see examples)",
            "examples": [
                {"adj": "good", "comp": "better than", "sup": "the best"},
                {"adj": "bad", "comp": "worse than", "sup": "the worst"},
                {"adj": "far", "comp": "farther/further than", "sup": "the farthest/furthest"},
                {"adj": "little", "comp": "less than", "sup": "the least"},
                {"adj": "many/much", "comp": "more than", "sup": "the most"},
            ],
        },
        {
            "type": "Equality",
            "comparative": "just as + adjective + as",
            "superlative": "N/A",
            "examples": [
                {"adj": "reliable", "comp": "just as reliable as", "sup": "—"},
                {"adj": "accurate", "comp": "just as accurate as", "sup": "—"},
            ],
        },
    ],
    "tech_examples": [
        "Cloud computing is more scalable than traditional servers.",
        "Cybersecurity is one of the most demanding fields in tech.",
        "AI developers work longer hours than UX designers.",
        "Machine learning is just as important as data analysis.",
        "This algorithm is the fastest we have tested so far.",
        "Remote work is more flexible than office-based work.",
    ],
}


# ---------------------------------------------------------------------------
# Cohesion — Connectors and Time Expressions
# ---------------------------------------------------------------------------

COHESION: Dict = {
    "title": "COHESION — CONNECTORS AND TIME EXPRESSIONS",
    "connectors": [
        {
            "word": "and",
            "function": "Addition",
            "example": "I am studying programming and I am going to take a cloud certification.",
        },
        {
            "word": "because",
            "function": "Cause / Reason",
            "example": "I chose this career because technology is the future.",
        },
        {
            "word": "but",
            "function": "Contrast",
            "example": "The course is difficult, but I will complete it.",
        },
        {
            "word": "so",
            "function": "Consequence / Result",
            "example": "The internship starts on Monday, so I am preparing my documents.",
        },
        {
            "word": "however",
            "function": "Contrast (formal)",
            "example": "The deadline is tight; however, we will deliver on time.",
        },
        {
            "word": "therefore",
            "function": "Consequence (formal)",
            "example": "The system failed; therefore, we are going to reboot the server.",
        },
    ],
    "time_expressions": [
        "soon", "next semester", "next week", "next month", "next year",
        "then", "before", "after", "later", "in the future",
        "by the end of the year", "in December", "on Monday",
        "this afternoon", "tomorrow", "eventually",
    ],
}


# ---------------------------------------------------------------------------
# Writing Checklist (Part IV criteria)
# ---------------------------------------------------------------------------

WRITING_CHECKLIST: Dict = {
    "title": "PART IV — WRITING CHECKLIST",
    "word_count": {"min": 70, "max": 90},
    "required_elements": [
        {
            "id": "will",
            "label": "Will (spontaneous decision / promise / opinion prediction)",
            "example": "I think AI will transform the industry.",
            "points": 2,
        },
        {
            "id": "be_going_to",
            "label": "Be going to (prior plan / evidence prediction)",
            "example": "I am going to complete my internship in June.",
            "points": 2,
        },
        {
            "id": "present_simple_schedule",
            "label": "Present Simple with schedule marker (timetable/fixed event)",
            "example": "The program starts on September 1st.",
            "points": 1,
        },
        {
            "id": "present_continuous",
            "label": "Present Continuous (confirmed personal arrangement)",
            "example": "I am presenting my project next Thursday.",
            "points": 2,
        },
        {
            "id": "connectors",
            "label": "At least 2 connectors (and / because / but / so / however / therefore)",
            "example": "I love coding, but the deadlines are challenging.",
            "points": 2,
        },
        {
            "id": "time_expressions",
            "label": "At least 1 future time expression",
            "example": "next semester, soon, in December, later",
            "points": 1,
        },
    ],
    "action_verbs": [
        "develop", "implement", "design", "analyze", "integrate",
        "optimize", "collaborate", "present", "complete", "launch",
        "manage", "create", "build", "deploy", "test",
    ],
}


# ---------------------------------------------------------------------------
# Listening Tips (Part II)
# ---------------------------------------------------------------------------

LISTENING_TIPS: Dict = {
    "title": "PART II — LISTENING COMPREHENSION TIPS",
    "key_listening_targets": [
        "Names, roles, and responsibilities of speakers",
        "Comparative forms: more..., -er than, the most, the -est",
        "Superlative forms used to describe extremes",
        "Numbers, percentages, and statistics",
        "Cause-and-effect relationships",
        "Contrast signals: but, however, on the other hand",
    ],
    "common_comparatives_in_audio": [
        "most demanding", "more innovative", "longer hours",
        "better salary", "faster growth", "more flexible",
        "the highest", "the lowest", "the best", "the worst",
    ],
    "strategies": [
        "First listen: get the general topic and number of speakers.",
        "Second listen: focus on specific details and comparatives.",
        "Write key words during listening — do not write full sentences.",
        "Pay attention to intonation — stress often falls on the compared item.",
    ],
}


def get_all_cards() -> List[Dict]:
    """Return all grammar cards as a flat list for iteration."""
    return [
        *FUTURE_FORMS,
        FUTURE_TIME_CLAUSES,
        COMPARATIVES_SUPERLATIVES,
        COHESION,
        WRITING_CHECKLIST,
        LISTENING_TIPS,
    ]


# ---------------------------------------------------------------------------
# Practice exercise data (imported by exam_assistant.py)
# ---------------------------------------------------------------------------

READING_TEXTS: List[Dict] = [
    {
        "title": "The Rise of Cybersecurity Professionals",
        "text": (
            "Cybersecurity has become one of the most critical fields in the technology sector. "
            "As digital threats grow more sophisticated, organizations are hiring specialists who "
            "can protect networks, analyze vulnerabilities, and respond to incidents. "
            "A cybersecurity analyst monitors systems daily, while an ethical hacker tests defenses "
            "by simulating attacks. Security architects design the overall protection framework. "
            "These roles require collaboration: analysts report findings to architects, who then "
            "update the strategy. The field is more demanding than many others in tech, offering "
            "some of the highest salaries and fastest career growth."
        ),
        "questions": [
            "What is the main idea of this text?",
            "What does a cybersecurity analyst do every day?",
            "How does an ethical hacker differ from a security architect?",
            "Why do cybersecurity professionals collaborate?",
            "What are two advantages of a cybersecurity career?",
        ],
        "answers": [
            "Cybersecurity is a critical, growing field requiring specialists with distinct roles.",
            "A cybersecurity analyst monitors systems daily.",
            "An ethical hacker tests defenses by simulating attacks; an architect designs the framework.",
            "Analysts report findings to architects who then update the protection strategy.",
            "High salaries and fast career growth.",
        ],
    },
    {
        "title": "Artificial Intelligence in Software Development",
        "text": (
            "Artificial intelligence is transforming how developers write and review code. "
            "AI-powered tools can suggest completions, detect bugs, and generate entire functions "
            "from natural language descriptions. Some developers argue that AI assistants make "
            "programming more accessible than ever before, while others believe the most innovative "
            "solutions still come from human creativity. Data scientists work alongside software "
            "engineers to train the models that power these tools. Project managers coordinate "
            "timelines, ensuring that AI integration does not delay product launches. "
            "The collaboration between technical and non-technical roles is just as important "
            "as the technology itself."
        ),
        "questions": [
            "What is the main purpose of AI tools in software development?",
            "What do data scientists do in this context?",
            "What is the role of project managers according to the text?",
            "What comparison does the text make about AI and human creativity?",
            "Identify a connector word and explain its function.",
        ],
        "answers": [
            "AI tools suggest code completions, detect bugs, and generate functions.",
            "Data scientists train the models that power AI development tools.",
            "Project managers coordinate timelines to avoid delays in product launches.",
            "Some argue AI is more accessible than before; others say humans are still more innovative.",
            "'While' (contrast), 'and' (addition) — accept any correctly identified connector.",
        ],
    },
]

FILL_IN_BLANK_COMPARATIVE: List[Dict] = [
    {
        "sentence": "Cloud storage is ________ (flexible) than a local hard drive.",
        "answer": "more flexible",
        "rule": "Long adjective -> more + adj",
    },
    {
        "sentence": "This new processor is ________ (fast) than the previous model.",
        "answer": "faster",
        "rule": "Short adjective -> adj + -er",
    },
    {
        "sentence": "Cybersecurity is one of ________ (demanding) careers in technology.",
        "answer": "the most demanding",
        "rule": "Long adjective superlative -> the most + adj",
    },
    {
        "sentence": "The old software had ________ (bad) performance than the update.",
        "answer": "worse",
        "rule": "Irregular: bad -> worse",
    },
    {
        "sentence": "AI is ________ (innovative) field in modern industry.",
        "answer": "the most innovative",
        "rule": "Superlative of long adjective",
    },
    {
        "sentence": "Remote work is just ________ (productive) ________ office work.",
        "answer": "as productive as",
        "rule": "Equality: just as + adj + as",
    },
]

FILL_IN_BLANK_FUTURE: List[Dict] = [
    {
        "sentence": "I ________ (attend) the cloud seminar next Friday. [confirmed plan]",
        "answer": "am attending",
        "rule": "Confirmed personal arrangement -> Present Continuous",
    },
    {
        "sentence": "I think automation ________ (change) the job market. [opinion prediction]",
        "answer": "will change",
        "rule": "Opinion-based prediction -> will",
    },
    {
        "sentence": "She ________ (graduate) in December. She applied for her diploma. [prior plan]",
        "answer": "is going to graduate",
        "rule": "Prior plan/intention -> be going to",
    },
    {
        "sentence": "The registration deadline ________ (close) on July 15th. [schedule]",
        "answer": "closes",
        "rule": "Official timetable -> Present Simple",
    },
    {
        "sentence": "As soon as he ________ (finish) the report, he will submit it. [time clause]",
        "answer": "finishes",
        "rule": "After 'as soon as' -> Present Simple (NOT will finish)",
    },
    {
        "sentence": "When the system ________ (restart), all processes will reset. [time clause]",
        "answer": "restarts",
        "rule": "After 'when' -> Present Simple (NOT will restart)",
    },
]

ERROR_CORRECTION: List[Dict] = [
    {
        "sentence": "Before she will submit the project, she needs to run tests.",
        "error": "'will submit' after 'before'",
        "correction": "Before she submits the project, she needs to run tests.",
        "rule": "Time clause after 'before' -> Present Simple",
    },
    {
        "sentence": "As soon as the update will install, the app will work faster.",
        "error": "'will install' after 'as soon as'",
        "correction": "As soon as the update installs, the app will work faster.",
        "rule": "Time clause after 'as soon as' -> Present Simple",
    },
    {
        "sentence": "When she will finish her degree, she is going to apply for a senior role.",
        "error": "'will finish' after 'when'",
        "correction": "When she finishes her degree, she is going to apply for a senior role.",
        "rule": "Time clause after 'when' -> Present Simple",
    },
    {
        "sentence": "I will call you after I will get back from the conference.",
        "error": "'will get' after 'after'",
        "correction": "I will call you after I get back from the conference.",
        "rule": "Time clause after 'after' -> Present Simple",
    },
    {
        "sentence": "Once the team will complete the sprint, we will review performance.",
        "error": "'will complete' after 'once'",
        "correction": "Once the team completes the sprint, we will review performance.",
        "rule": "Time clause after 'once' -> Present Simple",
    },
]

MODEL_PARAGRAPHS: List[Dict] = [
    {
        "title": "Career in Software Engineering",
        "text": (
            "I am currently studying software engineering, and I am going to graduate next semester. "
            "I am meeting my academic advisor on Thursday to finalize my electives. "
            "I think technology will create many new opportunities for professionals like me. "
            "The enrollment deadline closes on October 15th, so I need to register soon. "
            "After I finish my degree, I will apply for a junior developer position. "
            "I believe this career will be both challenging and rewarding."
        ),
        "score": 10,
        "notes": [
            "WILL: 'technology will create' (prediction) / 'I will apply' (plan)",
            "BE GOING TO: 'I am going to graduate' (prior plan)",
            "PRESENT SIMPLE: 'closes on October 15th' (official schedule)",
            "PRESENT CONTINUOUS: 'I am meeting my advisor on Thursday' (arrangement)",
            "CONNECTORS: 'and', 'so'",
            "TIME EXPRESSION: 'next semester', 'soon', 'on Thursday'",
        ],
    },
    {
        "title": "AI and the Future of Cybersecurity",
        "text": (
            "Cybersecurity is one of the most demanding fields in technology today. "
            "I am going to start an intensive certification course because I want to become a security analyst. "
            "Our first training session begins on Monday, and I am preparing my study schedule. "
            "I think AI will help analysts detect threats faster than ever before. "
            "After I complete the course, I will look for internships in the sector. "
            "Eventually, I am going to specialize in ethical hacking."
        ),
        "score": 10,
        "notes": [
            "WILL: 'AI will help' (prediction) / 'I will look for' (future decision)",
            "BE GOING TO: 'I am going to start' / 'I am going to specialize' (prior plans)",
            "PRESENT SIMPLE: 'begins on Monday' (fixed schedule)",
            "PRESENT CONTINUOUS: 'I am preparing my study schedule' (current arrangement)",
            "CONNECTORS: 'because', 'and'",
            "TIME EXPRESSION: 'on Monday', 'Eventually'",
        ],
    },
    {
        "title": "Plans for a Technology Internship",
        "text": (
            "Next month, I am starting a data science internship at a technology company. "
            "I am going to work on real machine learning projects, so I have been reviewing Python libraries. "
            "The internship orientation begins on June 2nd, and I am attending the welcome session that day. "
            "I believe this experience will improve my analytical skills significantly. "
            "When I finish the internship, I will update my portfolio with the projects I develop there."
        ),
        "score": 10,
        "notes": [
            "WILL: 'will improve my skills' (prediction) / 'I will update my portfolio'",
            "BE GOING TO: 'I am going to work on real projects' (prior intention)",
            "PRESENT SIMPLE: 'begins on June 2nd' (official schedule)",
            "PRESENT CONTINUOUS: 'I am starting an internship' / 'I am attending the session'",
            "CONNECTORS: 'so', 'and'",
            "TIME EXPRESSION: 'Next month', 'on June 2nd', 'that day'",
        ],
    },
]
