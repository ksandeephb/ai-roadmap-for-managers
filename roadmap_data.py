"""
roadmap_data.py
----------------
Lean, high-signal learning roadmap for delivery/project managers.

Designed from the learner's perspective:
  - Every resource earns its place — no filler, no overlap
  - One best resource per concept (not three that cover the same thing)
  - Capped at ~20 resources so it fits in 8 weeks at 3-5 hrs/week
  - Ordered so each phase builds on the last — you can't skip ahead safely
  - Tools and hands-on come AFTER concepts, not before

The 5 phases mirror how a manager actually gains AI confidence:
  1. Get the mental model right (what is AI, where did it come from)
  2. Understand GenAI and LLMs specifically (what your team is building)
  3. Learn the delivery framework (how AI projects actually run)
  4. Master the manager's job on AI projects (your specific role)
  5. Lead strategically and responsibly (ethics, governance, team)

All resources are free (audit / free tier) and require NO coding.
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
            ("lead",     "🎯 Lead AI projects",              "Run AI initiatives with confidence"),
            ("talk",     "🗣️ Talk to technical teams",       "Understand what engineers mean"),
            ("strategy", "♟️ Make strategic decisions",      "Spot opportunities, risks & scope"),
            ("career",   "📈 Stay relevant & grow",          "Future-proof my skills"),
            ("curious",  "💡 Understand how AI works",       "From curiosity, no coding wanted"),
        ],
    },
    {
        "id": "level",
        "title": "How familiar are you with AI today?",
        "help": "Be honest — there are no wrong answers.",
        "multi": False,
        "options": [
            ("none", "🌱 Complete beginner",    "I mostly know AI from the news"),
            ("buzz", "📰 I know the buzzwords", "Heard of ML, LLMs, ChatGPT — still fuzzy"),
            ("user", "🤖 I use AI tools",       "I use ChatGPT/Copilot but not the 'why'"),
            ("some", "🧠 I get the basics",     "I can hold a conversation; want more depth"),
        ],
    },
    {
        "id": "time",
        "title": "How much time can you give each week?",
        "help": "We'll size the roadmap to fit your real life.",
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
            ("video",  "🎬 Watching videos",     "Visual, narrated explanations"),
            ("read",   "📖 Reading",             "Articles, guides & short books"),
            ("course", "🎓 Structured courses",  "Step-by-step with a clear path"),
            ("hands",  "🛠️ Trying tools",        "Learn by doing — no coding needed"),
        ],
    },
    {
        "id": "interest",
        "title": "Which topics interest you most?",
        "help": "Choose all that apply — we'll prioritize these.",
        "multi": True,
        "options": [
            ("concepts",  "⚙️ How AI actually works",          "Plain-English mental models"),
            ("usecases",  "💼 AI use cases & business value",  "Where AI creates real impact"),
            ("lifecycle", "🔄 AI project lifecycle",           "How AI projects are built & delivered"),
            ("managing",  "🧩 Managing AI projects",           "Planning, risk, stakeholders"),
            ("strategy",  "♟️ AI strategy & ethics",           "Leadership, governance, responsible AI"),
            ("tools",     "🛠️ Using AI tools at work",         "Prompting, ChatGPT, Copilot"),
        ],
    },
]

# --------------------------------------------------------------------------- #
# Resource library — lean, ranked, no overlap
#
# Curation principle: if two resources cover the same ground, keep the better
# one and drop the other. Every resource here is the single best free option
# for that specific learning need.
# --------------------------------------------------------------------------- #
RESOURCES = {

    # ── WEEK 1-2: What is AI & where did it come from ────────────────────────
    # ONE course covers history + concepts better than splitting across two.
    # Andrew Ng's AI for Everyone is the consensus #1 non-technical AI course
    # (51,000+ reviews, 4.8 stars). Covers: what AI is, history, what it can/
    # can't do, and how to run AI projects. This alone is worth 2 weeks.
    "ai_for_everyone": {
        "title": "AI for Everyone — Andrew Ng (DeepLearning.AI)",
        "url": "https://www.coursera.org/learn/ai-for-everyone",
        "type": "course",
        "desc": (
            "The single best non-technical AI course for managers. 4 weeks of content, "
            "covers AI history, what AI can/can't do, how to spot use cases, and how to "
            "run AI projects — all without a line of code. Audit free on Coursera."
        ),
        "tags": ["~6 hrs", "4.8★ 51k reviews", "Audit free"],
    },

    # ── WEEK 2: GenAI specifically — what your team is building ──────────────
    # Most managers need to understand GenAI/LLMs more than classical ML.
    # Generative AI for Everyone by Andrew Ng is the direct follow-up and
    # the most praised non-technical GenAI course available.
    "genai_for_everyone": {
        "title": "Generative AI for Everyone — Andrew Ng (DeepLearning.AI)",
        "url": "https://www.coursera.org/learn/generative-ai-for-everyone",
        "type": "course",
        "desc": (
            "Andrew Ng's follow-up focused entirely on LLMs and generative AI. "
            "Covers how ChatGPT-style tools work, what they're genuinely good at, "
            "their real limitations, and how to apply them at work. Audit free."
        ),
        "tags": ["~4 hrs", "Beginner-friendly", "Audit free"],
    },

    # ── WEEK 2-3: Apply AI tools at work immediately ─────────────────────────
    # Don't just learn theory — use AI tools in your actual job from week 1.
    # ChatGPT is the most widely used; hands-on intuition beats any course.
    "chatgpt_hands_on": {
        "title": "Try ChatGPT at work — free tier (OpenAI)",
        "url": "https://chat.openai.com/",
        "type": "tool",
        "desc": (
            "Start using AI immediately alongside your learning. Use it to: summarise "
            "a project status report, draft a stakeholder update, rewrite meeting notes, "
            "or ask it to explain any AI concept you just studied. Daily use builds "
            "intuition faster than any course."
        ),
        "tags": ["Hands-on", "Free tier", "Do this week 1"],
    },

    # ── WEEK 3: Prompting — the manager's core AI skill ──────────────────────
    # As a manager you direct AI tools and review outputs every day.
    # Learn Prompting is the most comprehensive free guide — practical, no code.
    "prompting_guide": {
        "title": "Learn Prompting — Free Prompt Engineering Guide",
        "url": "https://learnprompting.org/docs/introduction",
        "type": "read",
        "desc": (
            "The most practical free guide to writing prompts that actually work. "
            "Focus on: basic prompting, chain-of-thought, and the techniques for "
            "summarisation and rewriting — the prompting tasks managers use most. "
            "Skip the advanced sections until later."
        ),
        "tags": ["~2 hrs", "Practical", "No code"],
    },

    # ── WEEK 3: AI project lifecycle — CRISP-DM ──────────────────────────────
    # CRISP-DM is the industry-standard framework for AI/data projects.
    # Every PM leading an AI team needs to know this — it's how your data
    # scientists structure their work whether they tell you or not.
    "crisp_dm": {
        "title": "CRISP-DM: The AI Project Lifecycle Explained (IBM)",
        "url": "https://www.ibm.com/docs/en/spss-modeler/saas?topic=dm-crisp-help-overview",
        "type": "read",
        "desc": (
            "CRISP-DM is the standard framework AI/data teams use: Business Understanding "
            "→ Data Understanding → Data Preparation → Modelling → Evaluation → Deployment. "
            "Read this so you can map your project management process onto how your "
            "technical team actually works."
        ),
        "tags": ["~45 min", "Framework", "Essential for PMs"],
    },

    # ── WEEK 4: What MLOps means for delivery managers ───────────────────────
    # MLOps is how AI gets from experiment to production. You don't need to
    # know the tools — but you need to know what your team means when they
    # talk about pipelines, model drift, and retraining schedules.
    "mlops_managers": {
        "title": "MLOps Explained for Non-Technical Managers (ml-ops.org)",
        "url": "https://ml-ops.org/content/mlops-principles",
        "type": "read",
        "desc": (
            "Plain-English explanation of MLOps principles: how AI models are built, "
            "tested, deployed, and kept healthy in production. Covers model drift, "
            "retraining, monitoring — the concepts you'll hear in every AI delivery "
            "meeting. Read the principles page, skip the tool-specific sections."
        ),
        "tags": ["~1 hr", "Delivery", "Essential"],
    },

    # ── WEEK 4: AI team roles — know who does what ───────────────────────────
    # Before you can manage an AI team you need to know who's on it and
    # what each person does. This is the fastest way to get there.
    "ai_team_roles": {
        "title": "AI Team Roles & Responsibilities — Google Cloud",
        "url": "https://cloud.google.com/learn/what-is-a-data-scientist",
        "type": "read",
        "desc": (
            "Who does what on an AI project? Understand the difference between a "
            "data scientist, ML engineer, data engineer, and AI product manager — "
            "so you know who to hire, who to ask what, and how to structure your team."
        ),
        "tags": ["~30 min", "Team structure", "Free"],
    },

    # ── WEEK 5: Managing AI projects — the PM playbook ───────────────────────
    # This is the most directly relevant resource for delivery managers.
    # The Digital PM's guide covers exactly how AI projects differ from
    # software projects and what that means for your PM process.
    "managing_ai_projects": {
        "title": "Managing AI Projects: A PM's Guide — The Digital Project Manager",
        "url": "https://thedigitalprojectmanager.com/projects/managing-ai-projects/",
        "type": "read",
        "desc": (
            "Written by practitioners for PMs: how AI projects differ from software "
            "projects, how to manage data dependencies, how to define 'done' for an "
            "ML feature, managing uncertainty, and running retrospectives on model "
            "performance. The most practical PM-specific AI guide available free."
        ),
        "tags": ["~1 hr", "For PMs/DMs", "Practical", "Free"],
    },

    # ── WEEK 5: AI use case scoping tool ─────────────────────────────────────
    # The ML Canvas is the most used tool for scoping AI initiatives.
    # Use this with your team when defining what to build and why.
    "ml_canvas": {
        "title": "Machine Learning Canvas — Free Template (ownml.co)",
        "url": "https://www.ownml.co/machine-learning-canvas",
        "type": "tool",
        "desc": (
            "A one-page canvas for scoping any AI initiative — like a Business Model "
            "Canvas but for ML projects. Covers: the prediction task, data sources, "
            "decisions it supports, and value created. Use this in your next AI "
            "discovery session to align your team fast."
        ),
        "tags": ["Template", "Use-case scoping", "Free"],
    },

    # ── WEEK 6: AI risk & governance — what every leader must know ────────────
    # NIST AI RMF is the reference standard for AI risk. You don't need to
    # implement it — but you need to speak this language with your risk,
    # legal, and compliance teams.
    "nist_risk": {
        "title": "NIST AI Risk Management Framework — Overview (NIST)",
        "url": "https://www.nist.gov/itl/ai-risk-management-framework",
        "type": "read",
        "desc": (
            "The US government's reference framework for AI risk: how to identify, "
            "assess, and manage risks across the AI lifecycle. Read the overview "
            "and the four core functions (Govern, Map, Measure, Manage) — this is "
            "the vocabulary your risk and compliance teams will use."
        ),
        "tags": ["~1 hr", "Risk", "Governance", "Free"],
    },

    # ── WEEK 6: Responsible AI — shipping AI ethically ───────────────────────
    # Google's responsible AI course is the clearest 1-hour introduction to
    # AI ethics for non-technical people. Every manager shipping AI needs this.
    "responsible_ai": {
        "title": "Introduction to Responsible AI — Google Cloud (Coursera)",
        "url": "https://www.coursera.org/learn/introduction-to-responsible-ai",
        "type": "course",
        "desc": (
            "Google's 1-hour micro-course: what responsible AI means, why it matters, "
            "fairness, safety, accountability, and Google's 7 AI principles. Essential "
            "before you ship any AI feature to users. Free."
        ),
        "tags": ["~1 hr", "Ethics", "Free"],
    },

    # ── WEEK 7: Strategy — where AI creates business value ───────────────────
    # McKinsey's State of AI report is the most cited executive-level view
    # of where AI is creating value across industries. Read this to speak
    # credibly with senior stakeholders about AI strategy.
    "mckinsey_state_of_ai": {
        "title": "McKinsey — The State of AI (Annual Report)",
        "url": "https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai",
        "type": "read",
        "desc": (
            "McKinsey's annual survey of AI adoption across industries. Covers where "
            "AI is generating real ROI, where adoption is stalling, and what separates "
            "high-performing AI teams from the rest. The single best executive briefing "
            "on AI strategy — read the key findings section."
        ),
        "tags": ["~1 hr", "Strategy", "Executive-level", "Free"],
    },

    # ── WEEK 7: HBR — leadership and people side of AI ───────────────────────
    # HBR consistently publishes the best non-technical leadership perspective
    # on AI. Bookmark and read 2-3 articles that match your current challenge.
    "hbr_ai": {
        "title": "Harvard Business Review — AI & Leadership Articles",
        "url": "https://hbr.org/topic/subject/ai-and-machine-learning",
        "type": "read",
        "desc": (
            "HBR's AI topic hub: the best business and leadership thinking on AI — "
            "team building, change management, strategy, and real case studies. "
            "Pick 2-3 articles that match your current challenge. A few free reads "
            "per month; bookmark it and return regularly."
        ),
        "tags": ["Ongoing", "Strategy", "Leadership", "Free tier"],
    },

    # ── WEEK 8: GenAI for leaders — putting it all together ──────────────────
    # Vanderbilt's 2-hour course is specifically designed for managers who
    # have learned the basics and want to apply GenAI to leadership tasks.
    # Perfect capstone for week 8 — short, practical, role-specific.
    "genai_for_leaders": {
        "title": "Generative AI for Leaders — Vanderbilt University (Coursera)",
        "url": "https://www.coursera.org/learn/generative-ai-for-leaders",
        "type": "course",
        "desc": (
            "Designed for managers and executives who already know the GenAI basics. "
            "Covers applying AI to real leadership tasks: planning, stakeholder "
            "communication, proposal review, and decision-making. 2 hours. "
            "The ideal week-8 capstone — ties everything together. Audit free."
        ),
        "tags": ["~2 hrs", "For leaders", "Capstone", "Audit free"],
    },
}

# --------------------------------------------------------------------------- #
# Phase templates — 5 phases, tight and sequential
# --------------------------------------------------------------------------- #
PHASE_TEMPLATES = [
    (
        "mental_model",
        "Phase 1 — Build Your AI Mental Model",
        "Understand what AI is, where it came from, and what it can/can't do — the foundation everything else builds on.",
    ),
    (
        "genai_tools",
        "Phase 2 — Master GenAI & Start Using It",
        "Understand how LLMs and ChatGPT actually work, and start using AI tools in your real work immediately.",
    ),
    (
        "delivery",
        "Phase 3 — Learn the AI Delivery Framework",
        "Understand how AI projects are structured (CRISP-DM), how they reach production (MLOps), and who does what.",
    ),
    (
        "pm_practice",
        "Phase 4 — The AI Project Manager's Playbook",
        "Apply your PM skills to AI: scoping, managing uncertainty, defining done, and keeping delivery on track.",
    ),
    (
        "strategy_ethics",
        "Phase 5 — Lead Strategically & Responsibly",
        "Govern AI risk, make strategic decisions, and speak credibly with senior stakeholders and technical teams alike.",
    ),
]

TYPE_ICON  = {"course": "🎓", "video": "🎬", "read": "📖", "tool": "🛠️"}
TYPE_LABEL = {"course": "Course", "video": "Video", "read": "Read", "tool": "Try it"}


# --------------------------------------------------------------------------- #
# Roadmap builder — max 8 weeks, personalised by answers
# --------------------------------------------------------------------------- #
def build_roadmap(answers: dict) -> dict:
    level    = answers.get("level", "none")
    interests= answers.get("interest", []) or []
    styles   = answers.get("style",    []) or []
    time     = answers.get("time",     "mid")
    goal     = answers.get("goal",     "lead")
    role     = answers.get("role",     "pm")

    likes_hands  = "hands"  in styles
    likes_read   = "read"   in styles
    likes_course = "course" in styles

    buckets = {key: [] for key, _, _ in PHASE_TEMPLATES}

    def push(phase, key):
        if key in RESOURCES and key not in buckets[phase]:
            buckets[phase].append(key)

    # ── Phase 1: Mental model ─────────────────────────────────────────────────
    # AI for Everyone is mandatory — it's the best single resource for this audience.
    push("mental_model", "ai_for_everyone")

    # ── Phase 2: GenAI + tools ────────────────────────────────────────────────
    # GenAI for Everyone is the logical next step after AI for Everyone.
    push("genai_tools", "genai_for_everyone")
    # Everyone should start using AI tools immediately.
    push("genai_tools", "chatgpt_hands_on")
    # Prompting is the manager's core daily AI skill — add if they care about tools.
    if "tools" in interests or likes_hands or goal in ("lead", "talk"):
        push("genai_tools", "prompting_guide")

    # ── Phase 3: Delivery framework ───────────────────────────────────────────
    # CRISP-DM is essential for any PM leading AI delivery — always included.
    push("delivery", "crisp_dm")
    # MLOps for managers — essential for DMs and PMs, skip for pure strategists.
    if role in ("pm", "dm") or goal in ("lead", "talk") or "lifecycle" in interests:
        push("delivery", "mlops_managers")
    # Team roles — essential if they're building or inheriting a team.
    if role in ("pm", "dm", "product") or "managing" in interests or "lifecycle" in interests:
        push("delivery", "ai_team_roles")

    # ── Phase 4: PM practice ──────────────────────────────────────────────────
    # The DPM guide is the most directly applicable PM-specific resource.
    push("pm_practice", "managing_ai_projects")
    # ML Canvas — add for everyone; great to use in practice immediately.
    push("pm_practice", "ml_canvas")

    # ── Phase 5: Strategy & ethics ────────────────────────────────────────────
    # Responsible AI — everyone shipping AI needs this.
    push("strategy_ethics", "responsible_ai")
    # NIST risk — add for PMs/DMs who will face governance conversations.
    if role in ("pm", "dm") or "strategy" in interests or goal in ("lead", "strategy"):
        push("strategy_ethics", "nist_risk")
    # McKinsey state of AI — for strategic/career goals.
    if "strategy" in interests or goal in ("strategy", "career", "lead"):
        push("strategy_ethics", "mckinsey_state_of_ai")
    # HBR — for readers who want ongoing strategy content.
    if likes_read or "strategy" in interests:
        push("strategy_ethics", "hbr_ai")
    # GenAI for leaders — capstone for anyone focused on leading AI work.
    if goal in ("lead", "strategy", "career") or role in ("product", "dm"):
        push("strategy_ethics", "genai_for_leaders")

    # ── Build phase list ──────────────────────────────────────────────────────
    phases = []
    for key, title, goal_text in PHASE_TEMPLATES:
        res = [RESOURCES[k] for k in buckets[key]]
        if res:
            phases.append({"title": title, "goal": goal_text, "resources": res})

    total = sum(len(p["resources"]) for p in phases)

    # ── Time & week calculation capped at 8 weeks ─────────────────────────────
    per_week = {"high": 5.0, "mid": 3.0, "low": 1.5}.get(time, 3.0)
    weeks    = min(8, max(3, math.ceil(total / per_week)))

    return {"phases": phases, "total": total, "weeks": weeks}
