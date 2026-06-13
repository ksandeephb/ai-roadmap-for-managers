"""
ai_suggestions.py
-----------------
Optional AI layer (Claude Haiku 4.5) that adds a few *personalized*, fresh,
free, no-code resource suggestions on top of the curated roadmap.

Design notes
------------
* The curated roadmap (roadmap_data.py) is always the reliable backbone.
  This layer only *augments* it — if no API key is set, or the call fails,
  the app falls back to the curated roadmap with no error.
* Results are cached per answer-pattern via @st.cache_data, so the 2nd person
  who answers identically reuses the stored result and triggers no API call.
  The 6 questions have fixed options, so the space of patterns is finite.
* Model knowledge only — no web search — so links can occasionally be stale.
  We mark every AI suggestion as "verify the link" in the UI and instruct the
  model to give canonical homepage URLs for well-known resources only.
"""

import os
from typing import List, Optional

import streamlit as st
from pydantic import BaseModel

MODEL = "claude-haiku-4-5"


# --------------------------------------------------------------------------- #
# Structured output schema
# --------------------------------------------------------------------------- #
class Suggestion(BaseModel):
    title: str
    url: str
    type: str  # one of: course | video | read | tool
    why: str   # one sentence, tailored to this learner


class AIResult(BaseModel):
    intro: str               # 1–2 warm, personalized sentences
    suggestions: List[Suggestion]


# --------------------------------------------------------------------------- #
# API key resolution (Streamlit secrets first, then environment)
# --------------------------------------------------------------------------- #
def get_api_key() -> Optional[str]:
    try:
        if "ANTHROPIC_API_KEY" in st.secrets:
            return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        # st.secrets raises if no secrets file exists — that's fine
        pass
    return os.environ.get("ANTHROPIC_API_KEY")


def ai_available() -> bool:
    return bool(get_api_key())


# --------------------------------------------------------------------------- #
# The AI call — cached per answer-pattern
# --------------------------------------------------------------------------- #
SYSTEM_PROMPT = (
    "You are a warm, encouraging learning advisor for experienced but "
    "NON-TECHNICAL project and delivery managers who want to understand AI "
    "without writing any code.\n\n"

    "PERSONALIZATION: The learner has already shared their background, goals, "
    "and current knowledge level in this conversation. Tailor every suggestion "
    "to match their specific role, industry, and learning gaps. Do not give "
    "generic advice — reference what they told you.\n\n"

    "RESOURCE RULES — follow all of these strictly:\n"
    "1. Only recommend FREE resources (free courses, free YouTube videos, "
    "free articles, tools with a free tier). No paywalls, no sign-up required.\n"
    "2. Every resource must be NO-CODE — nothing that requires programming.\n"
    "3. Only recommend resources you are highly confident exist and are "
    "currently live. If you are not sure a URL is real and working, do NOT "
    "include it.\n"
    "4. Each link must point directly to the specific video, article, or "
    "resource — NOT to a homepage, channel page, search page, or category "
    "listing. Example of a BAD link: https://www.youtube.com/c/GoogleCloud. "
    "Example of a GOOD link: https://www.youtube.com/watch?v=l2dpSZCOSMI.\n"
    "5. For YouTube: provide the direct watch URL (https://www.youtube.com/watch?v=...). "
    "For articles: provide the direct article URL, not the site's homepage.\n"
    "6. If you cannot provide a direct, working link to a specific piece of "
    "content, omit that resource entirely. Never include a resource without "
    "its direct link.\n\n"

    "CONTENT FOCUS — only recommend resources about:\n"
    "- Managing, leading, or delivering AI projects (no technical coding)\n"
    "- AI strategy, governance, and product thinking for non-technical leaders\n"
    "- Practical AI literacy for managers and business stakeholders\n"
    "- Prompting and using AI tools (ChatGPT, Copilot, etc.) without code\n\n"

    "AVOID REPETITION: Your suggestions must complement the learner's existing "
    "roadmap. Do not repeat resources they already have or have been shown.\n\n"

    "FORMAT: For each resource, provide:\n"
    "- Title\n"
    "- Type (YouTube video / Article / Course)\n"
    "- Direct link\n"
    "- One sentence on why it fits THIS learner specifically\n\n"

    "Write in clear, jargon-free language. Be encouraging and specific."
)


@st.cache_data(show_spinner=False, ttl=60 * 60 * 24 * 7)
def fetch_ai_suggestions(signature: tuple, profile_text: str, existing_titles: tuple):
    """Return a dict with {intro, suggestions:[...]}, {"error": msg}, or None.

    `signature` is the tuple of the user's answers — it is what @st.cache_data
    keys on, so identical answer-patterns reuse the cached result (no API call).
    """
    key = get_api_key()
    if not key:
        return None

    try:
        import anthropic
    except ImportError:
        return {"error": "The 'anthropic' package isn't installed. Run: pip install anthropic"}

    existing = "\n".join(f"- {t}" for t in existing_titles)
    user_msg = (
        f"Here is the learner's profile:\n{profile_text}\n\n"
        f"Their roadmap ALREADY includes these resources (do not repeat any of them):\n"
        f"{existing}\n\n"
        "Suggest 2 to 4 additional free, no-code resources tailored to this specific "
        "person, plus a 1–2 sentence personalized intro that speaks to their role and goal. "
        "For each resource give: title, url (canonical homepage), type (exactly one of "
        "course/video/read/tool), and a one-sentence 'why' tailored to them."
    )

    try:
        client = anthropic.Anthropic(api_key=key)
        resp = client.messages.parse(
            model=MODEL,
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
            output_format=AIResult,
        )
        result = resp.parsed_output
        # Keep only valid types; coerce anything unexpected to "read"
        valid = {"course", "video", "read", "tool"}
        cleaned = []
        for s in result.suggestions:
            t = s.type.lower().strip()
            cleaned.append({
                "title": s.title,
                "url": s.url,
                "type": t if t in valid else "read",
                "why": s.why,
            })
        return {"intro": result.intro, "suggestions": cleaned}
    except anthropic.AuthenticationError:
        return {"error": "Invalid API key. Check ANTHROPIC_API_KEY."}
    except anthropic.RateLimitError:
        return {"error": "Rate limited by the API. Please try again in a moment."}
    except Exception as e:  # network, parsing, etc. — never crash the app
        return {"error": f"Couldn't reach the AI service ({type(e).__name__}). Showing your curated roadmap."}
