"""
roadmap_data.py
----------------
Questionnaire definition, the curated library of FREE resources, and the
phase templates used to assemble a personalized roadmap.

All resources are free to access at the time of writing (free tier / course
audit) and require NO coding for the learner.
"""

import math

# --------------------------------------------------------------------------- #
# Questionnaire — 6 questions
# --------------------------------------------------------------------------- #
QUESTIONS = [
    {
        "id": "role",
        "title": "What best describes your role?",
        "help": "We use this to frame examples in language you already speak.",
        "multi": False,
        "options": [
            ("pm", "📋 Project Manager", "Plans, schedules, delivery on time & budget"),
            ("dm", "🚚 Delivery / Program Manager", "Oversees teams, outcomes & stakeholders"),
            ("product", "🧭 Product / Business lead", "Owns strategy, roadmap & value"),
            ("other", "👤 Other leadership role", "Experienced, non-technical manager"),
        ],
    },
    {
        "id": "goal",
        "title": "Why do you want to learn AI?",
        "help": "Pick the one that matters most right now.",
        "multi": False,
        "options": [
            ("lead", "🎯 Lead / manage AI projects", "Run AI initiatives with confidence"),
            ("talk", "🗣️ Talk to technical teams", "Understand what engineers & data scientists mean"),
            ("strategy", "♟️ Make better strategic decisions", "Spot opportunities, risks & realistic scope"),
            ("career", "📈 Stay relevant & grow my career", "Future-proof my skills"),
            ("curious", "💡 Genuinely understand how it works", "From curiosity, no coding wanted"),
        ],
    },
    {
        "id": "level",
        "title": "How familiar are you with AI today?",
        "help": "Be honest — there are no wrong answers.",
        "multi": False,
        "options": [
            ("none", "🌱 Complete beginner", "I mostly know AI from the news"),
            ("buzz", "📰 I know the buzzwords", "Heard of ML, LLMs, ChatGPT — but it's fuzzy"),
            ("user", "🤖 I use AI tools", "I use ChatGPT/Copilot but don't know the 'why'"),
            ("some", "🧠 I get the basics", "I can hold a conversation; want depth & structure"),
        ],
    },
    {
        "id": "time",
        "title": "How much time can you give each week?",
        "help": "We'll size the roadmap so it fits your real life.",
        "multi": False,
        "options": [
            ("low", "⏳ 1–2 hours", "Busy — small, steady steps"),
            ("mid", "🕒 3–5 hours", "A solid evening or two per week"),
            ("high", "🚀 6+ hours", "I want to move fast"),
        ],
    },
    {
        "id": "style",
        "title": "How do you learn best?",
        "help": "Choose all that apply.",
        "multi": True,
        "options": [
            ("video", "🎬 Watching videos", "Visual, narrated explanations"),
            ("read", "📖 Reading", "Articles, guides & short books"),
            ("course", "🎓 Structured courses", "Step-by-step with a clear path"),
            ("hands", "🛠️ Trying tools myself", "Learn by clicking & experimenting (still no coding)"),
        ],
    },
    {
        "id": "interest",
        "title": "Which topics interest you most?",
        "help": "Choose all that apply — we'll prioritize these.",
        "multi": True,
        "options": [
            ("genai", "✨ Generative AI & ChatGPT", "How tools like ChatGPT actually work"),
            ("prompt", "💬 Prompting & everyday AI tools", "Get more done with AI at work"),
            ("concepts", "⚙️ How AI/ML works under the hood", "Concepts, not code"),
            ("strategy", "📊 AI strategy & use-cases", "Where AI creates business value"),
            ("ethics", "⚖️ Risk, ethics & governance", "Responsible & safe AI"),
            ("managing", "🧩 Managing AI projects", "Delivery, teams, data & MLOps basics"),
        ],
    },
]

# --------------------------------------------------------------------------- #
# Resource library
#   type: course | video | read | tool
# --------------------------------------------------------------------------- #
RESOURCES = {
    "elementsofai": {
        "title": "Elements of AI",
        "url": "https://www.elementsofai.com/",
        "type": "course",
        "desc": "The famous free university course (Helsinki) explaining what AI is and isn't — built for non-technical people. No coding.",
        "tags": ["~30 hrs, self-paced", "Beginner"],
    },
    "ai_for_everyone": {
        "title": "AI for Everyone — Andrew Ng (Coursera, audit free)",
        "url": "https://www.coursera.org/learn/ai-for-everyone",
        "type": "course",
        "desc": "The single best non-technical AI course for managers. Click 'Audit' to take it free. Covers what AI can/can't do and how to run AI projects.",
        "tags": ["~6 hrs", "Audit = free", "For managers"],
    },
    "google_genai_intro": {
        "title": "Introduction to Generative AI — Google (YouTube)",
        "url": "https://www.youtube.com/watch?v=G2fqAlgmoPo",
        "type": "video",
        "desc": "A short, clear explainer of generative AI from Google. Great first watch.",
        "tags": ["~22 min", "Beginner"],
    },
    "ms_ai_beginners": {
        "title": "AI for Beginners — Microsoft",
        "url": "https://microsoft.github.io/AI-For-Beginners/",
        "type": "read",
        "desc": "A free, structured curriculum. Read the concept lessons and skip the code labs — the explanations stand on their own.",
        "tags": ["Self-paced", "Concepts"],
    },
    "crash_course_ai": {
        "title": "Crash Course: Artificial Intelligence (YouTube)",
        "url": "https://www.youtube.com/playlist?list=PL8dPuuaLjXtO65LeD2p4_Sb5XQ51par_b",
        "type": "video",
        "desc": "Friendly, animated series covering the big ideas of AI without math overload.",
        "tags": ["Playlist", "Beginner"],
    },
    "three_blue_one_brown": {
        "title": "But what is a neural network? — 3Blue1Brown (YouTube)",
        "url": "https://www.youtube.com/watch?v=aircAruvnKk",
        "type": "video",
        "desc": "Gorgeous visual intuition for how neural networks 'think'. Watch for the pictures, not the math.",
        "tags": ["~19 min", "Visual", "Concepts"],
    },
    "llm_explained": {
        "title": "Intro to Large Language Models — Andrej Karpathy (YouTube)",
        "url": "https://www.youtube.com/watch?v=zjkBMFhNj_g",
        "type": "video",
        "desc": "A clear 1-hour talk on how ChatGPT-style models work, from an AI leader. Accessible to smart non-experts.",
        "tags": ["~1 hr", "Concepts"],
    },
    "prompt_guide": {
        "title": "Prompt Engineering Guide (free)",
        "url": "https://www.promptingguide.ai/",
        "type": "read",
        "desc": "A free, practical guide to writing better prompts. Skim the intro and the basic techniques.",
        "tags": ["Reference", "Practical"],
    },
    "google_workspace_learning": {
        "title": "Google — Prompting tips & AI-at-work guides",
        "url": "https://workspace.google.com/learning-center/",
        "type": "read",
        "desc": "Free, practical prompting and AI-at-work tips you can apply immediately in tools you already use.",
        "tags": ["Practical", "At work"],
    },
    "chatgpt_try": {
        "title": "Try ChatGPT yourself (free tier)",
        "url": "https://chat.openai.com/",
        "type": "tool",
        "desc": "Hands-on: ask it to summarize a document, draft a status update, or explain a concept. Best way to build intuition.",
        "tags": ["Hands-on", "Free tier"],
    },
    "claude_try": {
        "title": "Try Claude yourself (free tier)",
        "url": "https://claude.ai/",
        "type": "tool",
        "desc": "Another leading AI assistant. Compare how it answers the same prompt vs. ChatGPT to feel the differences.",
        "tags": ["Hands-on", "Free tier"],
    },
    "hbr_ai": {
        "title": "Harvard Business Review — AI articles (free monthly reads)",
        "url": "https://hbr.org/topic/subject/ai-and-machine-learning",
        "type": "read",
        "desc": "Business-focused AI thinking. HBR gives a few free articles per month — perfect for strategy framing.",
        "tags": ["Strategy", "Business"],
    },
    "pmi_ai": {
        "title": "PMI — AI resources for project professionals",
        "url": "https://www.pmi.org/",
        "type": "read",
        "desc": "Project Management Institute material on AI's impact on delivery and the PM role. Free articles & some courses.",
        "tags": ["For PMs", "Delivery"],
    },
    "responsible_ai": {
        "title": "Google — Responsible AI practices",
        "url": "https://ai.google/responsibility/responsible-ai-practices/",
        "type": "read",
        "desc": "Plain-language overview of fairness, safety and accountability in AI systems.",
        "tags": ["Ethics", "Governance"],
    },
    "nist_ai_rmf": {
        "title": "NIST AI Risk Management Framework (overview)",
        "url": "https://www.nist.gov/itl/ai-risk-management-framework",
        "type": "read",
        "desc": "The reference framework for managing AI risk. Read the overview to speak credibly about governance.",
        "tags": ["Risk", "Governance"],
    },
    "mlops_explained": {
        "title": "What is MLOps? — plain-English explainer (YouTube)",
        "url": "https://www.youtube.com/watch?v=ZVWg18AXXuE",
        "type": "video",
        "desc": "How AI/ML projects actually get built, shipped and maintained — the lifecycle a manager should know.",
        "tags": ["Delivery", "Lifecycle"],
    },
    "ml_canvas": {
        "title": "Machine Learning Canvas (free template)",
        "url": "https://www.ownml.co/machine-learning-canvas",
        "type": "tool",
        "desc": "A one-page template to scope an AI use-case with your team — like a Business Model Canvas for ML.",
        "tags": ["Template", "Use-cases"],
    },
}

# --------------------------------------------------------------------------- #
# Phase templates
# --------------------------------------------------------------------------- #
PHASE_TEMPLATES = [
    ("foundations", "Foundations",
     "Build a clear mental model of what AI is, what it can and can't do — in plain English."),
    ("howitworks", "How it actually works",
     "Understand the 'why' behind AI and modern tools like ChatGPT, without any math or code."),
    ("handson", "Hands-on with AI tools",
     "Build real intuition by using AI tools yourself and learning to prompt well."),
    ("applied", "Apply it to your work",
     "Connect AI to strategy, use-cases, delivery and responsible use in your role."),
]

TYPE_ICON = {"course": "🎓", "video": "🎬", "read": "📖", "tool": "🛠️"}
TYPE_LABEL = {"course": "Course", "video": "Video", "read": "Read", "tool": "Try it"}


# --------------------------------------------------------------------------- #
# Roadmap builder
# --------------------------------------------------------------------------- #
def build_roadmap(answers: dict) -> dict:
    """Turn the user's answers into an ordered list of phases with resources."""
    level = answers.get("level")
    interests = answers.get("interest", []) or []
    styles = answers.get("style", []) or []
    time = answers.get("time")
    goal = answers.get("goal")
    role = answers.get("role")

    likes_video = "video" in styles
    likes_read = "read" in styles
    likes_hands = "hands" in styles

    buckets = {key: [] for key, _, _ in PHASE_TEMPLATES}

    def push(phase_key, res_key):
        if res_key in RESOURCES and res_key not in buckets[phase_key]:
            buckets[phase_key].append(res_key)

    # Phase 1 — Foundations (everyone)
    push("foundations", "ai_for_everyone")
    if level in ("none", "buzz"):
        push("foundations", "elementsofai")
    if likes_video:
        push("foundations", "google_genai_intro")
    if level == "none" and likes_video:
        push("foundations", "crash_course_ai")

    # Phase 2 — How it works
    if "concepts" in interests or level in ("some", "user"):
        push("howitworks", "three_blue_one_brown")
        push("howitworks", "llm_explained")
    if "genai" in interests:
        push("howitworks", "llm_explained")
    if likes_read:
        push("howitworks", "ms_ai_beginners")
    if not buckets["howitworks"]:
        push("howitworks", "three_blue_one_brown")

    # Phase 3 — Hands-on
    push("handson", "chatgpt_try")
    if likes_hands:
        push("handson", "claude_try")
    if "prompt" in interests or "genai" in interests:
        push("handson", "prompt_guide")
        push("handson", "google_workspace_learning")
    if len(buckets["handson"]) < 2:
        push("handson", "prompt_guide")

    # Phase 4 — Applied
    if "strategy" in interests or goal == "strategy":
        push("applied", "hbr_ai")
        push("applied", "ml_canvas")
    if "managing" in interests or goal == "lead" or role in ("pm", "dm"):
        push("applied", "pmi_ai")
        push("applied", "mlops_explained")
        push("applied", "ml_canvas")
    if "ethics" in interests:
        push("applied", "responsible_ai")
        push("applied", "nist_ai_rmf")
    if not buckets["applied"]:
        push("applied", "hbr_ai")
        push("applied", "ml_canvas")

    phases = []
    for key, title, goal_text in PHASE_TEMPLATES:
        res = [RESOURCES[k] for k in buckets[key]]
        if res:
            phases.append({"title": title, "goal": goal_text, "resources": res})

    total = sum(len(p["resources"]) for p in phases)
    per_week = {"high": 4.0, "mid": 2.5, "low": 1.3}.get(time, 2.0)
    weeks = max(3, math.ceil(total / per_week))

    return {"phases": phases, "total": total, "weeks": weeks}
