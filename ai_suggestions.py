"""
ai_suggestions.py
-----------------
Optional AI layer (Claude Haiku 4.5) that adds a few *personalized*, fresh,
free, no-code resource suggestions on top of the curated roadmap.
"""

import os
import re
import urllib.request
from typing import List, Optional

import streamlit as st
from pydantic import BaseModel

MODEL = "claude-sonnet-4-6"


# --------------------------------------------------------------------------- #
# Structured output schema
# --------------------------------------------------------------------------- #
class Suggestion(BaseModel):
    title: str
    url: str
    type: str   # one of: course | video | read | tool
    why: str    # one sentence, tailored to this learner


class AIResult(BaseModel):
    intro: str
    suggestions: List[Suggestion]


# --------------------------------------------------------------------------- #
# API key resolution
# --------------------------------------------------------------------------- #
def get_api_key() -> Optional[str]:
    try:
        if "ANTHROPIC_API_KEY" in st.secrets:
            return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass
    return os.environ.get("ANTHROPIC_API_KEY")


def ai_available() -> bool:
    return bool(get_api_key())


# --------------------------------------------------------------------------- #
# URL validation — drop any link that doesn't return HTTP 200
# --------------------------------------------------------------------------- #
TRUSTED_DOMAINS = {
    "youtube.com", "www.youtube.com",
    "youtu.be",
    "coursera.org", "www.coursera.org",
    "edx.org", "www.edx.org",
    "linkedin.com", "www.linkedin.com",
    "elementsofai.com", "www.elementsofai.com",
    "learnprompting.org",
    "microsoft.com", "learn.microsoft.com",
    "google.com", "grow.google",
    "hbr.org",
    "mckinsey.com", "www.mckinsey.com",
    "mit.edu", "mitsloan.mit.edu",
    "harvard.edu",
    "deeplearning.ai", "www.deeplearning.ai",
}

YOUTUBE_WATCH_RE = re.compile(r"https://(?:www\.)?youtube\.com/watch\?v=[\w-]{11}")


def _domain(url: str) -> str:
    try:
        return url.split("//", 1)[1].split("/")[0].lower()
    except Exception:
        return ""


def _url_live(url: str, timeout: int = 4) -> bool:
    """HEAD request to check the URL is reachable and returns 2xx/3xx."""
    try:
        req = urllib.request.Request(url, method="HEAD",
                                     headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status < 400
    except Exception:
        return False


def validate_suggestions(suggestions: list) -> list:
    """
    Keep a suggestion only if:
    1. Its domain is in TRUSTED_DOMAINS, AND
    2. For YouTube: the URL matches the exact watch?v= pattern (11-char ID), AND
    3. The URL responds with HTTP < 400.
    """
    valid = []
    for s in suggestions:
        url = s.get("url", "").strip().rstrip("/")
        domain = _domain(url)

        # Must be a trusted domain
        if domain not in TRUSTED_DOMAINS:
            continue

        # YouTube links must be a proper watch URL, not a channel/playlist/search
        if "youtube" in domain or "youtu.be" in domain:
            if not YOUTUBE_WATCH_RE.match(url):
                continue

        # Live check
        if not _url_live(url):
            continue

        valid.append(s)
    return valid


# --------------------------------------------------------------------------- #
# System prompt
# --------------------------------------------------------------------------- #
SYSTEM_PROMPT = (
    "You are a warm, encouraging learning advisor for experienced but "
    "NON-TECHNICAL project and delivery managers who want to understand AI "
    "without writing any code.\n\n"

    "PERSONALIZATION: Tailor every suggestion to the learner's specific role, "
    "goal, and current knowledge level as described in their profile.\n\n"

    "STRICT URL RULES — these are non-negotiable:\n"
    "1. Only FREE resources. No paywalls.\n"
    "2. NO-CODE only — nothing requiring programming.\n"
    "3. YouTube videos ONLY: use the exact format "
    "https://www.youtube.com/watch?v=XXXXXXXXXXX (11-character video ID). "
    "Never link to a channel, playlist, or search page. "
    "Only include a YouTube video if you are 100% certain the video ID is correct.\n"
    "4. Non-YouTube links: only use well-known, stable domains such as "
    "coursera.org, edx.org, elementsofai.com, learnprompting.org, "
    "learn.microsoft.com, grow.google, hbr.org, mckinsey.com, deeplearning.ai. "
    "Link directly to the specific course or article page, not the homepage.\n"
    "5. If you are not 100% certain a URL is correct and live, DO NOT include "
    "that resource. It is better to return 2 verified resources than 4 broken ones.\n\n"

    "CONTENT FOCUS:\n"
    "- Managing, leading, or delivering AI projects (non-technical)\n"
    "- AI strategy, governance, product thinking for non-technical leaders\n"
    "- Practical AI literacy for managers and business stakeholders\n"
    "- Using AI tools (ChatGPT, Copilot, etc.) without code\n\n"

    "AVOID repeating any resource already in the learner's roadmap.\n\n"

    "OUTPUT FORMAT per resource: title, url, type (video/course/read/tool), "
    "and one sentence explaining why it fits THIS learner specifically.\n\n"

    "Write in clear, jargon-free language."
)


# --------------------------------------------------------------------------- #
# The AI call — cached per answer-pattern
# --------------------------------------------------------------------------- #
@st.cache_data(show_spinner=False, ttl=60 * 60 * 24 * 7)
def fetch_ai_suggestions(signature: tuple, profile_text: str, existing_titles: tuple):
    """Return {intro, suggestions:[...]}, {"error": msg}, or None."""
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
        f"Their roadmap ALREADY includes these resources (do not repeat any):\n"
        f"{existing}\n\n"
        "Suggest 2–4 additional free, no-code resources tailored to this person. "
        "Only include a resource if you are 100% certain the URL is correct and live. "
        "For each: title, url, type (video/course/read/tool), one-sentence why. "
        "Also write a 1–2 sentence personalized intro addressing their role and goal."
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

        valid_types = {"course", "video", "read", "tool"}
        raw = []
        for s in result.suggestions:
            t = s.type.lower().strip()
            raw.append({
                "title": s.title,
                "url": s.url,
                "type": t if t in valid_types else "read",
                "why": s.why,
            })

        # Drop hallucinated / broken links
        cleaned = validate_suggestions(raw)

        if not cleaned:
            return {"error": "No verified links could be confirmed right now. Showing your curated roadmap."}

        return {"intro": result.intro, "suggestions": cleaned}

    except anthropic.AuthenticationError:
        return {"error": "Invalid API key. Check ANTHROPIC_API_KEY."}
    except anthropic.RateLimitError:
        return {"error": "Rate limited by the API. Please try again in a moment."}
    except Exception as e:
        return {"error": f"Couldn't reach the AI service ({type(e).__name__}). Showing your curated roadmap."}
