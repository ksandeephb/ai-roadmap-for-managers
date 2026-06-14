"""
ai_roadmap_builder.py
---------------------
LLM-powered roadmap builder. Instead of if/else rules, Claude analyses
the learner's answers and decides:
  - which phases to include
  - which resources belong in each phase
  - the order within each phase
  - a personalised reason for every resource

Falls back to the rule-based build_roadmap() if the API is unavailable
or the call fails — so the app always works.

The brain prompt gives Claude:
  1. Full learner profile (role, goal, level, time, style, interests)
  2. Complete resource catalogue with metadata
  3. Strict constraints (no invented URLs, only from the catalogue,
     respect time budget, phase structure must be maintained)
  4. Output schema (JSON)

Claude returns a structured plan which is then merged with the
full resource objects from RESOURCES dict for rendering.
"""

import json
import os
from typing import Optional

import streamlit as st

from roadmap_data import RESOURCES, PHASE_TEMPLATES, build_roadmap

MODEL = "claude-haiku-4-5"   # fast + cheap — this runs on every quiz submit

# --------------------------------------------------------------------------- #
# API key
# --------------------------------------------------------------------------- #
def get_api_key() -> Optional[str]:
    try:
        if "ANTHROPIC_API_KEY" in st.secrets:
            return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass
    return os.environ.get("ANTHROPIC_API_KEY")

def ai_brain_available() -> bool:
    return bool(get_api_key())

# --------------------------------------------------------------------------- #
# Resource catalogue for the prompt
# --------------------------------------------------------------------------- #
def _catalogue_text() -> str:
    """Compact text representation of every resource for the LLM prompt."""
    lines = []
    for key, r in RESOURCES.items():
        tags = ", ".join(r.get("tags", []))
        lines.append(
            f'  KEY="{key}" TYPE={r["type"].upper()} TITLE="{r["title"]}" '
            f'TAGS=[{tags}]'
        )
    return "\n".join(lines)

# --------------------------------------------------------------------------- #
# Profile text
# --------------------------------------------------------------------------- #
ROLE_MAP = {
    "pm":      "Project / Delivery Manager",
    "product": "Product Owner / Business Lead",
    "scrum":   "Scrum Master / Agile Lead",
    "exec":    "Senior Leader / Executive",
}
GOAL_MAP = {
    "lead":     "Lead and manage AI projects with confidence",
    "talk":     "Speak the same language as technical teams",
    "strategy": "Make sharper strategic decisions about AI",
    "career":   "Stay relevant and grow career",
    "curious":  "Genuinely understand how AI works",
}
LEVEL_MAP = {
    "none": "Complete beginner — mostly knows AI from the news",
    "buzz": "Knows the buzzwords — heard of ML, LLMs, ChatGPT but it is fuzzy",
    "user": "Uses AI tools like ChatGPT but does not know the why",
    "some": "Gets the basics — wants more depth and structure",
}
TIME_LABELS = {"high": "6+ hours/week", "mid": "3-5 hours/week", "low": "1-2 hours/week"}
TIME_CAPS   = {"high": 15, "mid": 11, "low": 7}
ROLE_CAPS   = {"exec": 8,  "product": 10, "scrum": 11, "pm": 14}

STYLE_MAP = {
    "video":  "watching videos",
    "read":   "reading articles and guides",
    "course": "structured courses with clear progression",
    "hands":  "trying tools hands-on",
}
INTEREST_MAP = {
    "concepts":  "how AI and ML actually work (plain English)",
    "usecases":  "AI use cases and business value",
    "lifecycle": "AI project lifecycle and team roles",
    "managing":  "managing and delivering AI projects",
    "strategy":  "AI strategy, ethics and leadership",
    "tools":     "using AI tools at work (prompting, ChatGPT)",
}

def _profile_text(answers: dict) -> str:
    role      = ROLE_MAP.get(answers.get("role"), "Manager")
    goal      = GOAL_MAP.get(answers.get("goal"), "understand AI")
    level     = LEVEL_MAP.get(answers.get("level"), "beginner")
    time      = TIME_LABELS.get(answers.get("time"), "some time per week")
    styles    = [STYLE_MAP.get(s, s) for s in (answers.get("style") or [])]
    interests = [INTEREST_MAP.get(i, i) for i in (answers.get("interest") or [])]
    return (
        f"Role: {role}\n"
        f"Goal: {goal}\n"
        f"Current AI knowledge: {level}\n"
        f"Time available: {time}\n"
        f"Preferred learning style: {', '.join(styles) if styles else 'no strong preference'}\n"
        f"Most interested in: {', '.join(interests) if interests else 'general AI understanding'}"
    )

# --------------------------------------------------------------------------- #
# System prompt
# --------------------------------------------------------------------------- #
SYSTEM_PROMPT = """You are an expert AI learning advisor who builds personalised learning roadmaps
for non-technical business managers. You have deep knowledge of adult learning, professional
development, and the AI landscape for business leaders.

You will receive:
1. A learner profile (role, goal, knowledge level, time, learning style, interests)
2. A catalogue of available resources (each with a unique KEY)

Your job is to select the RIGHT resources for THIS specific person and arrange them
into a meaningful learning journey.

STRICT RULES:
- Only use KEYs from the provided catalogue. Never invent keys or URLs.
- Respect the time budget: low=max 7 resources, mid=max 11, high=max 15.
- Respect the role cap: exec=max 8, product=max 10, scrum=max 11, pm=max 14.
- The actual cap is min(time_cap, role_cap).
- Match learning style: video learners get video resources, readers get reads/articles.
- Match knowledge level: beginners get foundational content, advanced users skip basics.
- Match role: executives get strategy/ethics focus, PMs get delivery/lifecycle focus.
- Phases with no relevant resources should be omitted entirely.
- The 5 mandatory YouTube videos (google_genai_intro_video, ibm_genai_business_video,
  kniberg_genai_video, 3b1b_neural_nets_video, karpathy_llm_video) should ONLY appear
  if the learner prefers video learning. Do not force them on readers or course-takers.

PERSONALISATION INTELLIGENCE:
- An executive with 1-2hrs/week should get max 7 high-impact strategic resources.
  Do NOT give them delivery mechanics or PM playbooks — they have teams for that.
- A Scrum Master should get delivery framework content and team-facilitation angle.
- A complete beginner needs foundational concepts before advanced strategy.
- Someone who prefers reading should get zero videos and more articles/courses.
- Someone who selected "using AI tools" interest MUST get the ChatGPT hands-on tool.
- Strategy interest → McKinsey, HBR, GenAI for Leaders.
- Lifecycle/managing interest → CRISP-DM, MLOps, Managing AI Projects guide.

OUTPUT FORMAT — respond with ONLY valid JSON, no other text:
{
  "personalised_intro": "2-3 sentence personalised intro explaining WHY this specific roadmap was built for them",
  "phases": [
    {
      "phase_key": "mental_model",
      "resources": [
        {
          "resource_key": "ai_for_everyone",
          "reason": "One sentence explaining why THIS resource is right for THIS person"
        }
      ]
    }
  ]
}

Valid phase_keys: mental_model, genai_tools, delivery, pm_practice, strategy_ethics
Only include phases that have at least one resource."""

# --------------------------------------------------------------------------- #
# Main AI brain call — cached per answer pattern
# --------------------------------------------------------------------------- #
@st.cache_data(show_spinner=False, ttl=60 * 60 * 24)
def build_ai_roadmap(answer_signature: tuple, answers_json: str) -> Optional[dict]:
    """
    Call Claude to build a personalised roadmap.
    Returns enriched plan dict (same shape as build_roadmap()) or None on failure.
    answer_signature is used as cache key.
    """
    key = get_api_key()
    if not key:
        return None

    try:
        import anthropic
    except ImportError:
        return None

    answers = json.loads(answers_json)
    role    = answers.get("role", "pm")
    time    = answers.get("time", "mid")

    hard_cap = min(
        TIME_CAPS.get(time, 11),
        ROLE_CAPS.get(role, 12),
    )

    user_msg = f"""Learner Profile:
{_profile_text(answers)}

Resource Catalogue:
{_catalogue_text()}

Hard cap: maximum {hard_cap} resources total (time={time}, role={role}).

Build the optimal personalised roadmap for this learner.
Return ONLY valid JSON matching the specified output format."""

    try:
        client = anthropic.Anthropic(api_key=key)
        resp   = client.messages.create(
            model=MODEL,
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
        raw = resp.content[0].text.strip()

        # Strip any markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        data = json.loads(raw)

        # Validate and enrich with full resource objects
        return _enrich(data, answers)

    except Exception as e:
        return None   # silent fallback to rule-based

# --------------------------------------------------------------------------- #
# Enrich Claude's output with full resource objects
# --------------------------------------------------------------------------- #
def _enrich(data: dict, answers: dict) -> dict:
    """
    Merge Claude's resource key selections with the full RESOURCES dict.
    Returns a plan dict in the same shape as build_roadmap() but with
    an extra 'ai_reason' field per resource and a 'personalised_intro'.
    """
    phase_map = {key: (title, goal) for key, title, goal in PHASE_TEMPLATES}
    phases    = []

    seen_keys = set()
    for phase_data in data.get("phases", []):
        phase_key = phase_data.get("phase_key")
        if phase_key not in phase_map:
            continue

        title, goal = phase_map[phase_key]
        resources   = []

        for item in phase_data.get("resources", []):
            rkey = item.get("resource_key")
            if not rkey or rkey not in RESOURCES or rkey in seen_keys:
                continue
            seen_keys.add(rkey)
            r = dict(RESOURCES[rkey])          # copy so we don't mutate global
            r["ai_reason"] = item.get("reason", "")
            resources.append(r)

        if resources:
            phases.append({"title": title, "goal": goal, "resources": resources})

    if not phases:
        return None   # Claude returned nothing usable — trigger fallback

    total    = sum(len(p["resources"]) for p in phases)
    time     = answers.get("time", "mid")
    per_week = {"high": 5.0, "mid": 3.0, "low": 1.5}.get(time, 3.0)
    weeks    = min(8, max(3, -(-total // per_week.__ceil__() if total else 3)))  # ceiling div
    weeks    = min(8, max(3, int(total / per_week) + (1 if total % per_week else 0)))

    return {
        "phases":            phases,
        "total":             total,
        "weeks":             weeks,
        "personalised_intro": data.get("personalised_intro", ""),
        "ai_built":          True,   # flag so app.py knows to show AI badge
    }

# --------------------------------------------------------------------------- #
# Public helper: get roadmap (AI if available, rules if not)
# --------------------------------------------------------------------------- #
def get_roadmap(answers: dict) -> dict:
    """
    Try AI brain first. Fall back to rule-based if unavailable or failed.
    Always returns a valid plan dict.
    """
    import hashlib

    if not ai_brain_available():
        return build_roadmap(answers)

    # Build a stable cache key from answers
    answers_json = json.dumps(answers, sort_keys=True)
    sig = tuple(hashlib.md5(answers_json.encode()).hexdigest())

    result = build_ai_roadmap(sig, answers_json)
    if result:
        return result

    # Fallback
    return build_roadmap(answers)
