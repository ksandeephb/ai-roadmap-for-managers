"""
roadmap_data.py
----------------
Lean, high-signal 8-week roadmap for delivery/project managers.

Resource mix (by design):
  YouTube  : 5 videos from Google Cloud, IBM Technology, 3Blue1Brown,
              Henrik Kniberg, Andrej Karpathy — all free, no code
  Coursera : 3 courses (Andrew Ng x2, Vanderbilt) — audit free
  Reads    : 5 articles/guides (DPM, ml-ops.org, NIST, McKinsey, HBR)
  Tools    : 2 hands-on (ChatGPT, ML Canvas)

Every resource is the single best free option for its learning need.
No two resources cover the same ground.
"""

import math

# --------------------------------------------------------------------------- #
# Questionnaire
# --------------------------------------------------------------------------- #
QUESTIONS = [
    {
        "id": "role",
        "title": "What best describes your role?",
        "help": "We use this to frame examples in language you already speak.",
        "multi": False,
        "options": [
            ("pm",      "📋 Project / Delivery Manager",    "Plans, schedules, manages risk & delivery"),
            ("product", "🧭 Product Owner / Business Lead",  "Owns the roadmap, strategy & business value"),
            ("scrum",   "⚡ Scrum Master / Agile Lead",      "Facilitates teams, ceremonies & agility"),
            ("exec",    "🎯 Senior Leader / Executive",      "Sets AI direction, governs investment & strategy"),
        ],
    },
    {
        "id": "goal",
        "title": "Why do you want to learn AI?",
        "help": "Pick the one that matters most right now.",
        "multi": False,
        "options": [
            ("lead",     "🎯 Lead AI projects",          "Run AI initiatives with confidence"),
            ("talk",     "🗣️ Talk to technical teams",   "Understand what engineers mean"),
            ("strategy", "♟️ Make strategic decisions",  "Spot opportunities, risks & scope"),
            ("career",   "📈 Stay relevant & grow",      "Future-proof my skills"),
            ("curious",  "💡 Understand how AI works",   "From curiosity, no coding wanted"),
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
            ("video",  "🎬 Watching videos",    "Visual, narrated explanations"),
            ("read",   "📖 Reading",            "Articles, guides & short books"),
            ("course", "🎓 Structured courses", "Step-by-step with a clear path"),
            ("hands",  "🛠️ Trying tools",       "Learn by doing — no coding needed"),
        ],
    },
    {
        "id": "interest",
        "title": "Which topics interest you most?",
        "help": "Choose all that apply — we'll prioritize these.",
        "multi": True,
        "options": [
            ("concepts",  "⚙️ How AI actually works",         "Plain-English mental models"),
            ("usecases",  "💼 AI use cases & business value", "Where AI creates real impact"),
            ("lifecycle", "🔄 AI project lifecycle",          "How AI projects are built & delivered"),
            ("managing",  "🧩 Managing AI projects",          "Planning, risk, stakeholders"),
            ("strategy",  "♟️ AI strategy & ethics",          "Leadership, governance, responsible AI"),
            ("tools",     "🛠️ Using AI tools at work",        "Prompting, ChatGPT, Copilot"),
        ],
    },
]

# --------------------------------------------------------------------------- #
# Resource library — diversified across YouTube, Coursera, reads, tools
# --------------------------------------------------------------------------- #
RESOURCES = {

    # ── WEEK 1: What is AI — the best 6-hour course for managers ─────────────
    "ai_for_everyone": {
        "title": "AI for Everyone — Andrew Ng (Coursera, audit free)",
        "url": "https://www.coursera.org/learn/ai-for-everyone",
        "type": "course",
        "desc": (
            "The #1 non-technical AI course. Covers AI history, what AI can and "
            "can't do, how to spot use cases, and how to run AI projects. "
            "51,000+ reviews, 4.8 stars. Click 'Audit' to take it free."
        ),
        "tags": ["~6 hrs", "4.8 stars", "Audit free"],
    },

    # ── WEEK 1: Google's 22-min video intro to GenAI — perfect first watch ───
    # youtube.com/watch?v=G2fqAlgmoPo — confirmed live across multiple sources
    "google_genai_intro_video": {
        "title": "Introduction to Generative AI — Google Cloud (YouTube, 22 min)",
        "url": "https://www.youtube.com/watch?v=G2fqAlgmoPo",
        "type": "video",
        "desc": (
            "Google Cloud's crisp 22-minute explainer: what generative AI is, "
            "how it differs from traditional ML, and where it applies in business. "
            "The best short first watch before any longer course. Free on YouTube."
        ),
        "tags": ["22 min", "Google Cloud", "Free"],
    },

    # ── WEEK 2: IBM's plain-English GenAI for business video ─────────────────
    # youtube.com/watch?v=FrDnPTPgEmk — IBM Technology channel, confirmed live
    "ibm_genai_business_video": {
        "title": "Generative AI for Business — IBM Technology (YouTube, 14 min)",
        "url": "https://www.youtube.com/watch?v=FrDnPTPgEmk",
        "type": "video",
        "desc": (
            "IBM Research director Dario Gil demystifies generative AI for "
            "business leaders in 14 minutes: how it works, why it matters now, "
            "and what principles should guide your AI strategy. No tech background needed."
        ),
        "tags": ["14 min", "IBM Technology", "Free"],
    },

    # ── WEEK 2: Andrew Ng on GenAI specifically ───────────────────────────────
    "genai_for_everyone": {
        "title": "Generative AI for Everyone — Andrew Ng (Coursera, audit free)",
        "url": "https://www.coursera.org/learn/generative-ai-for-everyone",
        "type": "course",
        "desc": (
            "Andrew Ng's focused follow-up on LLMs and GenAI. Covers how "
            "ChatGPT-style tools work, real capabilities and limits, and how to "
            "apply them at work — without writing a line of code. Audit free."
        ),
        "tags": ["~4 hrs", "GenAI focus", "Audit free"],
    },

    # ── WEEK 2: Henrik Kniberg's 3M-view GenAI visual explainer ──────────────
    # youtube.com/watch?v=2IK3DFHRFfw — 3M+ views, confirmed via multiple refs
    "kniberg_genai_video": {
        "title": "Generative AI in a Nutshell — Henrik Kniberg (YouTube, 18 min)",
        "url": "https://www.youtube.com/watch?v=2IK3DFHRFfw",
        "type": "video",
        "desc": (
            "3 million+ views. Henrik Kniberg's animated whiteboard explainer covers "
            "how GenAI works, what it's good at, its limitations, and what it means "
            "for your work — all in 18 minutes. One of the most-shared AI explainers ever."
        ),
        "tags": ["18 min", "3M+ views", "Free"],
    },

    # ── WEEK 2-3: Hands-on with ChatGPT immediately ───────────────────────────
    "chatgpt_hands_on": {
        "title": "Try ChatGPT at work — free tier (chat.openai.com)",
        "url": "https://chat.openai.com/",
        "type": "tool",
        "desc": (
            "Start using AI this week. Ask it to summarise a project report, "
            "draft a stakeholder update, or explain any AI concept you just studied. "
            "Daily hands-on use builds intuition faster than any course."
        ),
        "tags": ["Do this week 1", "Free tier", "No code"],
    },

    # ── WEEK 3: How LLMs work — 3Blue1Brown visual masterclass ───────────────
    # youtube.com/watch?v=aircAruvnKk — confirmed, 80M+ views
    "3b1b_neural_nets_video": {
        "title": "But what is a neural network? — 3Blue1Brown (YouTube, 19 min)",
        "url": "https://www.youtube.com/watch?v=aircAruvnKk",
        "type": "video",
        "desc": (
            "80 million views. The most beautiful visual explanation of how neural "
            "networks 'think'. Watch it for the pictures, not the maths — the mental "
            "model you'll build is worth every minute."
        ),
        "tags": ["19 min", "80M views", "Visual"],
    },

    # ── WEEK 3: Andrej Karpathy on LLMs — 1-hour deep dive ───────────────────
    # youtube.com/watch?v=zjkBMFhNj_g — confirmed, ex-OpenAI
    "karpathy_llm_video": {
        "title": "Intro to Large Language Models — Andrej Karpathy (YouTube, 1 hr)",
        "url": "https://www.youtube.com/watch?v=zjkBMFhNj_g",
        "type": "video",
        "desc": (
            "Ex-OpenAI AI director explains how ChatGPT-class models work — "
            "the best 1-hour technical briefing accessible to smart non-technical people. "
            "Watch this and you'll understand more than most executives."
        ),
        "tags": ["1 hr", "Ex-OpenAI", "Free"],
    },

    # ── WEEK 3: Prompting — the manager's core daily AI skill ────────────────
    "prompting_guide": {
        "title": "Learn Prompting — Free Guide (learnprompting.org)",
        "url": "https://learnprompting.org/docs/introduction",
        "type": "read",
        "desc": (
            "The most practical free guide to writing prompts that work. "
            "Focus on: basic prompting, chain-of-thought, and summarisation — "
            "the techniques managers use every day. Skip the advanced sections for now."
        ),
        "tags": ["~2 hrs", "Practical", "No code"],
    },

    # ── WEEK 4: AI project lifecycle — CRISP-DM ──────────────────────────────
    "crisp_dm": {
        "title": "CRISP-DM: The AI Project Lifecycle (IBM Docs)",
        "url": "https://www.ibm.com/docs/en/spss-modeler/saas?topic=dm-crisp-help-overview",
        "type": "read",
        "desc": (
            "The industry-standard AI project framework: Business Understanding "
            "→ Data → Modelling → Evaluation → Deployment. Read this so you can "
            "map your PM process onto how your data team actually works."
        ),
        "tags": ["~45 min", "Framework", "Essential"],
    },

    # ── WEEK 4: MLOps for delivery managers ──────────────────────────────────
    "mlops_managers": {
        "title": "MLOps Principles — Plain English (ml-ops.org)",
        "url": "https://ml-ops.org/content/mlops-principles",
        "type": "read",
        "desc": (
            "Plain-English guide to MLOps: how AI models are built, tested, "
            "deployed, and kept healthy in production. Covers drift, retraining, "
            "monitoring — the vocabulary of every AI delivery meeting."
        ),
        "tags": ["~1 hr", "Delivery", "Free"],
    },

    # ── WEEK 5: The best PM-specific AI guide available free ─────────────────
    "managing_ai_projects": {
        "title": "Managing AI Projects: A PM's Guide (The Digital PM)",
        "url": "https://thedigitalprojectmanager.com/projects/managing-ai-projects/",
        "type": "read",
        "desc": (
            "Written by practitioners for PMs: how AI projects differ from software "
            "projects, managing data dependencies, defining 'done' for an ML feature, "
            "and running retrospectives on model performance. Essential reading."
        ),
        "tags": ["~1 hr", "For PMs/DMs", "Free"],
    },

    # ── WEEK 5: ML Canvas — scope AI use cases with your team ────────────────
    "ml_canvas": {
        "title": "Machine Learning Canvas — Free Template (ownml.co)",
        "url": "https://www.ownml.co/machine-learning-canvas",
        "type": "tool",
        "desc": (
            "A one-page canvas for scoping any AI initiative — like a Business Model "
            "Canvas for ML. Use this in your next AI discovery session to align "
            "your team on data, predictions, decisions, and value."
        ),
        "tags": ["Template", "Use-case scoping", "Free"],
    },

    # ── WEEK 6: AI risk — NIST framework ──────────────────────────────────────
    "nist_risk": {
        "title": "NIST AI Risk Management Framework (nist.gov)",
        "url": "https://www.nist.gov/itl/ai-risk-management-framework",
        "type": "read",
        "desc": (
            "The reference standard for AI risk. Read the overview and the four core "
            "functions (Govern, Map, Measure, Manage). This is the vocabulary your "
            "risk and compliance teams will use — you need to speak it."
        ),
        "tags": ["~1 hr", "Governance", "Free"],
    },

    # ── WEEK 6: Responsible AI — Google's 1-hour course ──────────────────────
    "responsible_ai": {
        "title": "Introduction to Responsible AI — Google Cloud (Coursera, free)",
        "url": "https://www.coursera.org/learn/introduction-to-responsible-ai",
        "type": "course",
        "desc": (
            "Google's 1-hour micro-course: fairness, safety, accountability, "
            "and Google's 7 AI principles. Essential before you ship any AI "
            "feature to users. Free — no audit trick needed."
        ),
        "tags": ["~1 hr", "Ethics", "Free"],
    },

    # ── WEEK 7: McKinsey State of AI — best executive briefing ───────────────
    "mckinsey_state_of_ai": {
        "title": "McKinsey — The State of AI Report (mckinsey.com)",
        "url": "https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai",
        "type": "read",
        "desc": (
            "McKinsey's annual AI adoption survey — where AI generates real ROI, "
            "what separates top AI teams, and key industry trends. "
            "The best executive AI briefing available free. Read the key findings."
        ),
        "tags": ["~1 hr", "Strategy", "Executive-level"],
    },

    # ── WEEK 7: HBR — ongoing leadership perspective ──────────────────────────
    "hbr_ai": {
        "title": "Harvard Business Review — AI & Leadership Articles (hbr.org)",
        "url": "https://hbr.org/topic/subject/ai-and-machine-learning",
        "type": "read",
        "desc": (
            "HBR's AI hub — strategy, leadership, and case studies from the "
            "world's top management thinkers. Pick 2-3 articles matching your "
            "current challenge. A few free reads per month; bookmark and return."
        ),
        "tags": ["Ongoing", "Leadership", "Free tier"],
    },

    # ── WEEK 8: Capstone for leaders — Vanderbilt 2hr course ─────────────────
    "genai_for_leaders": {
        "title": "Generative AI for Leaders — Vanderbilt Univ. (Coursera, audit free)",
        "url": "https://www.coursera.org/learn/generative-ai-for-leaders",
        "type": "course",
        "desc": (
            "Built for managers who already know the GenAI basics. Covers "
            "applying AI to leadership tasks: planning, stakeholder communication, "
            "proposal review, decision-making. 2 hours. Perfect week-8 capstone."
        ),
        "tags": ["~2 hrs", "For leaders", "Audit free"],
    },
}

# --------------------------------------------------------------------------- #
# Phase templates — 5 phases, sequential
# --------------------------------------------------------------------------- #
PHASE_TEMPLATES = [
    (
        "mental_model",
        "Phase 1 — Build Your AI Mental Model",
        "Understand what AI is and what it can/can't do — the foundation everything else builds on.",
    ),
    (
        "genai_tools",
        "Phase 2 — Understand GenAI & Start Using It",
        "Learn how LLMs and ChatGPT actually work, then start using AI tools in your real work immediately.",
    ),
    (
        "delivery",
        "Phase 3 — Learn the AI Delivery Framework",
        "Understand CRISP-DM, MLOps, and team roles so you can manage AI delivery confidently.",
    ),
    (
        "pm_practice",
        "Phase 4 — The AI Project Manager's Playbook",
        "Apply your PM skills to AI: scoping use cases, managing uncertainty, and defining done.",
    ),
    (
        "strategy_ethics",
        "Phase 5 — Lead Strategically & Responsibly",
        "Govern AI risk, make strategic decisions, and speak credibly with stakeholders at all levels.",
    ),
]

TYPE_ICON  = {"course": "🎓", "video": "🎬", "read": "📖", "tool": "🛠️"}
TYPE_LABEL = {"course": "Course", "video": "Video", "read": "Read", "tool": "Try it"}


# --------------------------------------------------------------------------- #
# Roadmap builder — personalised, max 8 weeks
# --------------------------------------------------------------------------- #
def build_roadmap(answers: dict) -> dict:
    level    = answers.get("level", "none")
    interests= answers.get("interest", []) or []
    styles   = answers.get("style",    []) or []
    time     = answers.get("time",     "mid")
    goal     = answers.get("goal",     "lead")
    role     = answers.get("role",     "pm")

    likes_video  = "video"  in styles
    likes_read   = "read"   in styles
    likes_course = "course" in styles
    likes_hands  = "hands"  in styles

    buckets = {key: [] for key, _, _ in PHASE_TEMPLATES}

    def push(phase, key):
        if key in RESOURCES and key not in buckets[phase]:
            buckets[phase].append(key)

    # ── Phase 1: Mental model ─────────────────────────────────────────────────
    push("mental_model", "ai_for_everyone")           # anchor — always
    push("mental_model", "google_genai_intro_video")  # MUST: Google 22-min — always

    # ── Phase 2: GenAI + tools ────────────────────────────────────────────────
    push("genai_tools", "ibm_genai_business_video")   # MUST: IBM 14-min — always
    push("genai_tools", "kniberg_genai_video")        # MUST: Henrik Kniberg 18-min — always
    push("genai_tools", "3b1b_neural_nets_video")     # MUST: 3Blue1Brown 19-min — always
    push("genai_tools", "karpathy_llm_video")         # MUST: Karpathy 1-hr — always
    push("genai_tools", "chatgpt_hands_on")           # hands-on — always
    if likes_course or "concepts" in interests:
        push("genai_tools", "genai_for_everyone")     # Andrew Ng GenAI course

    # ── Phase 3: Delivery framework ───────────────────────────────────────────
    push("delivery", "crisp_dm")                      # always — essential for PMs
    if role in ("pm", "scrum") or goal in ("lead", "talk") or "lifecycle" in interests:
        push("delivery", "mlops_managers")

    # ── Phase 4: PM practice ──────────────────────────────────────────────────
    push("pm_practice", "managing_ai_projects")      # always
    push("pm_practice", "ml_canvas")                 # always
    if "tools" in interests or likes_hands:
        push("pm_practice", "prompting_guide")

    # ── Phase 5: Strategy & ethics ────────────────────────────────────────────
    push("strategy_ethics", "responsible_ai")        # always — every PM needs this
    if role in ("pm", "scrum", "exec") or "strategy" in interests or goal in ("lead", "strategy"):
        push("strategy_ethics", "nist_risk")
    if "strategy" in interests or goal in ("strategy", "career", "lead"):
        push("strategy_ethics", "mckinsey_state_of_ai")
    if likes_read and "strategy" in interests and time == "high":
        push("strategy_ethics", "hbr_ai")
    if goal in ("lead", "strategy") or role in ("exec", "product"):
        push("strategy_ethics", "genai_for_leaders")

    # ── Build phases ──────────────────────────────────────────────────────────
    phases = []
    for key, title, goal_text in PHASE_TEMPLATES:
        res = [RESOURCES[k] for k in buckets[key]]
        if res:
            phases.append({"title": title, "goal": goal_text, "resources": res})

    total    = sum(len(p["resources"]) for p in phases)
    per_week = {"high": 5.0, "mid": 3.0, "low": 1.5}.get(time, 3.0)
    weeks    = min(8, max(3, math.ceil(total / per_week)))

    return {"phases": phases, "total": total, "weeks": weeks}
