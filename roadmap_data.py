"""
roadmap_data.py
----------------
Questionnaire, curated resource library, phase templates, and roadmap builder.

Resource library rebuilt around six learning pillars for delivery/project
managers who need to LEAD AI projects — not build them:

  1. AI History & Background       — where AI came from, why it matters now
  2. AI Concepts & How It Works    — plain-English mental models
  3. AI Use Cases & Frameworks     — business value, patterns, canvas tools
  4. AI Project Lifecycle          — CRISP-DM, MLOps basics, team roles
  5. AI Project Management         — planning, risk, stakeholders, delivery
  6. AI Strategy, Ethics & Team    — leadership, governance, responsible AI

All resources are free (free tier / audit) and require NO coding.
URLs verified as of June 2025.
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
            ("pm",      "📋 Project Manager",            "Plans, schedules, delivery on time & budget"),
            ("dm",      "🚚 Delivery / Program Manager", "Oversees teams, outcomes & stakeholders"),
            ("product", "🧭 Product / Business Lead",    "Owns strategy, roadmap & value"),
            ("other",   "👤 Other leadership role",      "Experienced, non-technical manager"),
        ],
    },
    {
        "id": "goal",
        "title": "Why do you want to learn AI?",
        "help": "Pick the one that matters most right now.",
        "multi": False,
        "options": [
            ("lead",     "🎯 Lead / manage AI projects",        "Run AI initiatives with confidence"),
            ("talk",     "🗣️ Talk to technical teams",          "Understand what engineers & data scientists mean"),
            ("strategy", "♟️ Make better strategic decisions",  "Spot opportunities, risks & realistic scope"),
            ("career",   "📈 Stay relevant & grow my career",   "Future-proof my skills"),
            ("curious",  "💡 Genuinely understand how AI works","From curiosity, no coding wanted"),
        ],
    },
    {
        "id": "level",
        "title": "How familiar are you with AI today?",
        "help": "Be honest — there are no wrong answers.",
        "multi": False,
        "options": [
            ("none", "🌱 Complete beginner",    "I mostly know AI from the news"),
            ("buzz", "📰 I know the buzzwords", "Heard of ML, LLMs, ChatGPT — but it's fuzzy"),
            ("user", "🤖 I use AI tools",       "I use ChatGPT/Copilot but don't know the 'why'"),
            ("some", "🧠 I get the basics",     "I can hold a conversation; want depth & structure"),
        ],
    },
    {
        "id": "time",
        "title": "How much time can you give each week?",
        "help": "We'll size the roadmap so it fits your real life.",
        "multi": False,
        "options": [
            ("low",  "⏳ 1–2 hours", "Busy — small, steady steps"),
            ("mid",  "🕒 3–5 hours", "A solid evening or two per week"),
            ("high", "🚀 6+ hours",  "I want to move fast"),
        ],
    },
    {
        "id": "style",
        "title": "How do you learn best?",
        "help": "Choose all that apply.",
        "multi": True,
        "options": [
            ("video",  "🎬 Watching videos",        "Visual, narrated explanations"),
            ("read",   "📖 Reading",                "Articles, guides & short books"),
            ("course", "🎓 Structured courses",     "Step-by-step with a clear path"),
            ("hands",  "🛠️ Trying tools myself",    "Learn by clicking & experimenting (no coding)"),
        ],
    },
    {
        "id": "interest",
        "title": "Which topics interest you most?",
        "help": "Choose all that apply — we'll prioritize these.",
        "multi": True,
        "options": [
            ("history",   "📜 History & background of AI",      "Where AI came from and why it matters now"),
            ("concepts",  "⚙️ How AI/ML works",                 "Plain-English mental models, no math"),
            ("usecases",  "💼 AI use cases & business value",   "Where AI creates impact across industries"),
            ("lifecycle", "🔄 AI project lifecycle",            "CRISP-DM, MLOps, team roles, data pipelines"),
            ("managing",  "🧩 Managing & delivering AI projects","Planning, risk, stakeholders, delivery"),
            ("strategy",  "♟️ AI strategy, ethics & team",      "Leadership, governance & responsible AI"),
        ],
    },
]

# --------------------------------------------------------------------------- #
# Resource library — 6 pillars, all free, no coding
# --------------------------------------------------------------------------- #
RESOURCES = {

    # ── PILLAR 1: AI History & Background ────────────────────────────────────
    "history_elements": {
        "title": "Elements of AI — History & Foundations",
        "url": "https://www.elementsofai.com/",
        "type": "course",
        "desc": (
            "University of Helsinki's landmark free course. Chapter 1 covers AI history "
            "from the 1950s Turing Test to today's deep learning era — no coding, no math. "
            "Audit free."
        ),
        "tags": ["~15 hrs", "Beginner", "Audit free"],
    },
    "history_ibm_exec": {
        "title": "GenAI for Executives — AI History & Business Value (IBM, Coursera)",
        "url": "https://www.coursera.org/learn/generative-ai-for-executives-business-leaders-introduction",
        "type": "course",
        "desc": (
            "IBM's short course for leaders covers key events in AI history and why "
            "generative AI matters for business today. No prior AI background needed. Audit free."
        ),
        "tags": ["~3 hrs", "For executives", "Audit free"],
    },

    # ── PILLAR 2: AI Concepts & How It Works ─────────────────────────────────
    "concepts_ai_everyone": {
        "title": "AI for Everyone — Andrew Ng (DeepLearning.AI, Coursera)",
        "url": "https://www.coursera.org/learn/ai-for-everyone",
        "type": "course",
        "desc": (
            "The #1 non-technical AI course for managers (51,000+ reviews, 4.8 stars). "
            "Covers what AI can/can't do, ML intuition, and how to run AI projects. Audit free."
        ),
        "tags": ["~6 hrs", "Audit free", "Top-rated"],
    },
    "concepts_genai_everyone": {
        "title": "Generative AI for Everyone — Andrew Ng (DeepLearning.AI, Coursera)",
        "url": "https://www.coursera.org/learn/generative-ai-for-everyone",
        "type": "course",
        "desc": (
            "Andrew Ng's follow-up focused specifically on LLMs and GenAI. Covers how "
            "ChatGPT-style tools work, what they're good for, and real limitations. Audit free."
        ),
        "tags": ["~4 hrs", "Audit free", "GenAI focus"],
    },
    "concepts_google_intro": {
        "title": "Introduction to Generative AI — Google Cloud (Coursera)",
        "url": "https://www.coursera.org/learn/introduction-to-generative-ai",
        "type": "course",
        "desc": (
            "Google's 1-hour micro-course: what generative AI is, how it differs from "
            "traditional ML, and where it applies. Perfect first watch before longer courses."
        ),
        "tags": ["~1 hr", "Beginner", "Free"],
    },
    "concepts_llm_google": {
        "title": "Introduction to Large Language Models — Google Cloud (Coursera)",
        "url": "https://www.coursera.org/learn/introduction-to-large-language-models",
        "type": "course",
        "desc": (
            "Google's micro-course explaining what LLMs are, how prompt tuning works, "
            "and key use cases — no technical background needed. Free to audit."
        ),
        "tags": ["~1 hr", "LLMs", "Free"],
    },
    "concepts_ibm_foundations": {
        "title": "AI Foundations for Everyone Specialisation (IBM, Coursera)",
        "url": "https://www.coursera.org/specializations/ai-foundations-for-everyone",
        "type": "course",
        "desc": (
            "IBM's 4-course series covering AI concepts, applications, and no-code hands-on "
            "exercises including building a chatbot without writing a single line of code. Audit free."
        ),
        "tags": ["~40 hrs", "No-code hands-on", "Audit free"],
    },

    # ── PILLAR 3: AI Use Cases & Frameworks ──────────────────────────────────
    "usecase_ml_canvas": {
        "title": "Machine Learning Canvas (Free Template)",
        "url": "https://www.ownml.co/machine-learning-canvas",
        "type": "tool",
        "desc": (
            "A one-page canvas to scope any AI/ML initiative — like a Business Model Canvas "
            "for AI projects. Use it with your team to align on data, predictions, and outcomes."
        ),
        "tags": ["Template", "Use-case scoping", "Free"],
    },
    "usecase_hbr": {
        "title": "Harvard Business Review — AI & Machine Learning Articles",
        "url": "https://hbr.org/topic/subject/ai-and-machine-learning",
        "type": "read",
        "desc": (
            "HBR's AI topic hub: strategy articles, transformation case studies, and "
            "leadership perspectives on AI. A few free articles each month — bookmark it."
        ),
        "tags": ["Strategy", "Case studies", "Business"],
    },
    "usecase_mckinsey": {
        "title": "McKinsey — State of AI Reports & Use Case Library",
        "url": "https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai",
        "type": "read",
        "desc": (
            "McKinsey's annual AI survey and use case research. The use case library alone "
            "covers 400+ industry applications — great for identifying where AI fits in your sector."
        ),
        "tags": ["Research", "Industry use cases", "Free"],
    },
    "usecase_genai_leaders": {
        "title": "Generative AI for Leaders — Vanderbilt University (Coursera)",
        "url": "https://www.coursera.org/learn/generative-ai-for-leaders",
        "type": "course",
        "desc": (
            "Built specifically for managers and executives. Covers GenAI use cases, "
            "prompt writing for leadership tasks, and applying AI to planning and communication. "
            "Audit free, ~2 hours."
        ),
        "tags": ["~2 hrs", "For leaders", "Audit free"],
    },

    # ── PILLAR 4: AI Project Lifecycle ───────────────────────────────────────
    "lifecycle_crisp_dm": {
        "title": "CRISP-DM: The Standard AI/Data Project Lifecycle — Overview (Coursera article)",
        "url": "https://www.coursera.org/articles/crisp-dm",
        "type": "read",
        "desc": (
            "CRISP-DM is the industry-standard framework for running data and AI projects: "
            "Business Understanding → Data → Modelling → Evaluation → Deployment. "
            "This free Coursera article explains each phase clearly for non-technical readers."
        ),
        "tags": ["Framework", "Lifecycle", "Free article"],
    },
    "lifecycle_mlops": {
        "title": "What is MLOps? Plain-English Guide for Managers",
        "url": "https://ml-ops.org/content/mlops-principles",
        "type": "read",
        "desc": (
            "MLOps is how AI models get built, tested, and kept running in production. "
            "This free guide explains the principles without requiring any technical background — "
            "essential reading before you manage your first AI delivery team."
        ),
        "tags": ["MLOps", "Delivery", "Free"],
    },
    "lifecycle_team_roles": {
        "title": "AI Project Team Roles Explained — IBM",
        "url": "https://www.ibm.com/think/topics/ai-team",
        "type": "read",
        "desc": (
            "Who does what on an AI project? IBM's plain-English breakdown of data scientists, "
            "ML engineers, data engineers, and AI product managers — so you know who to hire "
            "and what to ask each person."
        ),
        "tags": ["Team roles", "Hiring", "Free"],
    },
    "lifecycle_data_quality": {
        "title": "Why Data Quality Decides AI Project Success — MIT Sloan Review",
        "url": "https://sloanreview.mit.edu/article/the-hidden-fragility-of-ai/",
        "type": "read",
        "desc": (
            "The single biggest reason AI projects fail is poor data, not bad algorithms. "
            "MIT Sloan's article explains this for business leaders — essential context before "
            "you kick off any AI initiative."
        ),
        "tags": ["Data quality", "Risk", "Free"],
    },

    # ── PILLAR 5: AI Project Management ──────────────────────────────────────
    "pm_ai_everyone_w3": {
        "title": "AI for Everyone — Week 3: Building AI in Your Company (Andrew Ng)",
        "url": "https://www.coursera.org/learn/ai-for-everyone",
        "type": "course",
        "desc": (
            "Week 3 of AI for Everyone is the most PM-relevant module: AI project workflows, "
            "what to expect from your team, how to scope AI work, and how to evaluate feasibility. "
            "Audit the full course free, or jump to Week 3."
        ),
        "tags": ["~2 hrs (Week 3)", "For PMs", "Audit free"],
    },
    "pm_pmi": {
        "title": "PMI — AI in Project Management: Practitioner's Guide",
        "url": "https://www.pmi.org/learning/library/artificial-intelligence-project-management",
        "type": "read",
        "desc": (
            "Project Management Institute's practitioner-focused guide on incorporating AI "
            "into project delivery. Covers AI project planning, team structures, and risk. Free."
        ),
        "tags": ["For PMs", "Delivery", "PMI"],
    },
    "pm_dpm": {
        "title": "Managing AI Projects: A Guide for Project Managers — The Digital PM",
        "url": "https://thedigitalprojectmanager.com/projects/managing-ai-projects/",
        "type": "read",
        "desc": (
            "Written by practitioners for PMs: how AI projects differ from software projects, "
            "how to manage data dependencies, what 'done' means for an ML feature, "
            "and how to run retrospectives on model performance."
        ),
        "tags": ["Practical", "For PMs", "Free"],
    },
    "pm_risk": {
        "title": "NIST AI Risk Management Framework (Plain-English Overview)",
        "url": "https://www.nist.gov/itl/ai-risk-management-framework",
        "type": "read",
        "desc": (
            "The US government's reference framework for identifying, assessing, and managing "
            "AI risk. Read the overview summary — it's the vocabulary your risk and compliance "
            "teams will use, and you need to speak it fluently."
        ),
        "tags": ["Risk", "Governance", "Free"],
    },
    "pm_prompt": {
        "title": "Prompt Engineering Guide — Practical Prompting for Managers",
        "url": "https://www.promptingguide.ai/",
        "type": "read",
        "desc": (
            "As a manager you'll direct AI tools and review AI outputs daily. This free guide "
            "covers the prompting patterns that produce consistent, useful results — "
            "no coding involved."
        ),
        "tags": ["Prompting", "Practical", "Free"],
    },

    # ── PILLAR 6: AI Strategy, Ethics & Team Leadership ───────────────────────
    "strategy_responsible_ai": {
        "title": "Introduction to Responsible AI — Google Cloud (Coursera)",
        "url": "https://www.coursera.org/learn/introduction-to-responsible-ai",
        "type": "course",
        "desc": (
            "Google's micro-course on ethical AI: fairness, safety, accountability, and "
            "Google's 7 AI principles. Every delivery manager should understand this before "
            "shipping an AI feature. Free."
        ),
        "tags": ["~1 hr", "Ethics", "Governance", "Free"],
    },
    "strategy_mit_sloan": {
        "title": "MIT Sloan — AI Strategy for Business Leaders",
        "url": "https://sloanreview.mit.edu/big-ideas/artificial-intelligence/",
        "type": "read",
        "desc": (
            "MIT Sloan Management Review's AI hub: research-backed articles on AI strategy, "
            "organisational change, and leadership decisions. Some articles free each month."
        ),
        "tags": ["Strategy", "Leadership", "Research"],
    },
    "strategy_google_path": {
        "title": "Google Cloud — Introduction to Generative AI Learning Path",
        "url": "https://www.cloudskillsboost.google/paths/118",
        "type": "course",
        "desc": (
            "Google's free structured learning path covering GenAI fundamentals, LLMs, "
            "image generation, and responsible AI — all in short modules with no coding required. "
            "A solid structured alternative to individual courses."
        ),
        "tags": ["Structured path", "Free", "No-code"],
    },
    "strategy_chatgpt": {
        "title": "Try ChatGPT yourself (free tier)",
        "url": "https://chat.openai.com/",
        "type": "tool",
        "desc": (
            "Hands-on: summarise a project status report, generate a risk register draft, "
            "or ask it to explain a technical concept. Building daily intuition with AI tools "
            "is essential for any manager leading AI delivery."
        ),
        "tags": ["Hands-on", "Free tier"],
    },
    "strategy_claude": {
        "title": "Try Claude (free tier) — Compare AI Assistants",
        "url": "https://claude.ai/",
        "type": "tool",
        "desc": (
            "Compare how Claude handles the same prompt as ChatGPT. Understanding that different "
            "models have different strengths helps you make better vendor and tool decisions "
            "for your AI projects."
        ),
        "tags": ["Hands-on", "Free tier", "Compare models"],
    },
}

# --------------------------------------------------------------------------- #
# Phase templates — 6 pillars mapped to learning phases
# --------------------------------------------------------------------------- #
PHASE_TEMPLATES = [
    (
        "history_background",
        "AI History & Background",
        "Understand where AI came from, why it exploded recently, and why it matters for your organisation now.",
    ),
    (
        "concepts",
        "AI Concepts — Plain English",
        "Build a clear mental model of how AI and LLMs actually work, without any maths or code.",
    ),
    (
        "usecases_frameworks",
        "AI Use Cases & Frameworks",
        "Learn where AI creates business value, how to spot opportunities, and how to scope AI initiatives with your team.",
    ),
    (
        "lifecycle",
        "AI Project Lifecycle",
        "Understand the end-to-end AI delivery process — CRISP-DM, MLOps, team roles — so you can manage it confidently.",
    ),
    (
        "project_management",
        "Managing & Delivering AI Projects",
        "Apply PM skills to AI: planning, risk, stakeholders, data quality, and knowing when a model is 'done'.",
    ),
    (
        "strategy_ethics",
        "AI Strategy, Ethics & Leadership",
        "Lead AI at the organisational level — governance, responsible AI, building the right team, and making strategic decisions.",
    ),
]

TYPE_ICON  = {"course": "🎓", "video": "🎬", "read": "📖", "tool": "🛠️"}
TYPE_LABEL = {"course": "Course", "video": "Video", "read": "Read", "tool": "Try it"}


# --------------------------------------------------------------------------- #
# Roadmap builder
# --------------------------------------------------------------------------- #
def build_roadmap(answers: dict) -> dict:
    level     = answers.get("level", "none")
    interests = answers.get("interest", []) or []
    styles    = answers.get("style",    []) or []
    time      = answers.get("time",     "mid")
    goal      = answers.get("goal",     "lead")
    role      = answers.get("role",     "pm")

    likes_video  = "video"  in styles
    likes_read   = "read"   in styles
    likes_course = "course" in styles
    likes_hands  = "hands"  in styles

    buckets = {key: [] for key, _, _ in PHASE_TEMPLATES}

    def push(phase, key):
        if key in RESOURCES and key not in buckets[phase]:
            buckets[phase].append(key)

    # ── Phase 1: History & Background ────────────────────────────────────────
    # Everyone gets at least one history resource
    if "history" in interests or level in ("none", "buzz"):
        push("history_background", "history_elements")
    if "history" in interests or goal in ("lead", "strategy"):
        push("history_background", "history_ibm_exec")
    # Fallback: always show at least one
    if not buckets["history_background"]:
        push("history_background", "history_elements")

    # ── Phase 2: Concepts ────────────────────────────────────────────────────
    # Core anchor — always included
    push("concepts", "concepts_ai_everyone")
    if "concepts" in interests or level in ("none", "buzz"):
        push("concepts", "concepts_google_intro")
    if "concepts" in interests or level in ("user", "some"):
        push("concepts", "concepts_llm_google")
        push("concepts", "concepts_genai_everyone")
    if likes_course and level == "none":
        push("concepts", "concepts_ibm_foundations")

    # ── Phase 3: Use Cases & Frameworks ─────────────────────────────────────
    push("usecases_frameworks", "usecase_ml_canvas")   # everyone should see this
    if "usecases" in interests or goal == "strategy":
        push("usecases_frameworks", "usecase_hbr")
        push("usecases_frameworks", "usecase_mckinsey")
    if goal in ("lead", "career") or role in ("product",):
        push("usecases_frameworks", "usecase_genai_leaders")
    if not buckets["usecases_frameworks"]:
        push("usecases_frameworks", "usecase_hbr")

    # ── Phase 4: AI Project Lifecycle ────────────────────────────────────────
    # CRISP-DM is essential for every PM/DM leading AI delivery
    push("lifecycle", "lifecycle_crisp_dm")
    if "lifecycle" in interests or role in ("pm", "dm") or goal == "lead":
        push("lifecycle", "lifecycle_mlops")
        push("lifecycle", "lifecycle_team_roles")
    if likes_read or "lifecycle" in interests:
        push("lifecycle", "lifecycle_data_quality")
    if not buckets["lifecycle"]:
        push("lifecycle", "lifecycle_crisp_dm")

    # ── Phase 5: Project Management ──────────────────────────────────────────
    push("project_management", "pm_ai_everyone_w3")   # Week 3 of AI for Everyone
    if "managing" in interests or role in ("pm", "dm") or goal == "lead":
        push("project_management", "pm_dpm")
        push("project_management", "pm_pmi")
    if "managing" in interests or goal in ("lead", "talk"):
        push("project_management", "pm_risk")
    if likes_hands or "managing" in interests:
        push("project_management", "pm_prompt")
    if not buckets["project_management"]:
        push("project_management", "pm_dpm")

    # ── Phase 6: Strategy, Ethics & Leadership ───────────────────────────────
    if "strategy" in interests or goal in ("strategy", "lead", "career"):
        push("strategy_ethics", "strategy_responsible_ai")
        push("strategy_ethics", "strategy_mit_sloan")
    if likes_hands or "strategy" in interests:
        push("strategy_ethics", "strategy_chatgpt")
        push("strategy_ethics", "strategy_claude")
    if likes_course:
        push("strategy_ethics", "strategy_google_path")
    if not buckets["strategy_ethics"]:
        push("strategy_ethics", "strategy_responsible_ai")
        push("strategy_ethics", "strategy_chatgpt")

    # Build final phase list — skip empty buckets
    phases = []
    for key, title, goal_text in PHASE_TEMPLATES:
        res = [RESOURCES[k] for k in buckets[key]]
        if res:
            phases.append({"title": title, "goal": goal_text, "resources": res})

    total    = sum(len(p["resources"]) for p in phases)
    per_week = {"high": 4.0, "mid": 2.5, "low": 1.3}.get(time, 2.0)
    weeks    = max(4, math.ceil(total / per_week))

    return {"phases": phases, "total": total, "weeks": weeks}
