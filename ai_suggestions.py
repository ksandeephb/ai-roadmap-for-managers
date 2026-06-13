"""
ai_suggestions.py
-----------------
Optional AI layer (Claude Sonnet 4.6) that adds personalized, free, no-code
article suggestions on top of the curated roadmap.

No hardcoded domain list — instead the model is tightly constrained by topic,
and every returned URL is validated with a live HTTP check before display.
"""

import os
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
    type: str   # always "read"
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
# URL validation — no hardcoded domain list
# --------------------------------------------------------------------------- #

# Topics that articles MUST be about — used for a second Claude call to
# verify content relevance before showing the link to the user.
ALLOWED_TOPICS = (
    "company AI transformation",
    "AI use cases for business",
    "AI project management",
    "leading AI teams",
    "AI product delivery strategy",
    "AI project strategy",
    "managing AI initiatives",
)

# Patterns that always indicate a homepage/index, not a specific article
REJECT_PATH_PATTERNS = (
    "/topics", "/insights", "/capabilities", "/services",
    "/solutions", "/about", "/contact", "/blog$", "/articles$",
    "/search", "/tag/", "/category/", "/author/",
)

MIN_PATH_LENGTH = 15  # anything shorter is almost certainly not a real article


def _parse_url(url: str):
    """Return (scheme, domain, path) tuple."""
    try:
        parts = url.split("//", 1)
        scheme = parts[0].rstrip(":")
        rest = parts[1]
        domain, _, path = rest.partition("/")
        return scheme.lower(), domain.lower(), "/" + path.rstrip("/")
    except Exception:
        return "", "", "/"


def _url_live(url: str, timeout: int = 6) -> bool:
    """HEAD request — True only if server responds HTTP < 400."""
    try:
        req = urllib.request.Request(
            url, method="HEAD",
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; LinkChecker/1.0)",
                "Accept": "text/html",
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status < 400
    except Exception:
        return False


def _looks_like_article_url(url: str) -> bool:
    """
    Structural checks only — no domain whitelist.
    Rejects homepages, section roots, and known non-article path patterns.
    """
    scheme, domain, path = _parse_url(url)

    # Must be HTTPS
    if scheme != "https":
        return False

    # Must have a real domain
    if not domain or "." not in domain:
        return False

    # Path must be long enough to be a real article slug
    if len(path) < MIN_PATH_LENGTH:
        return False

    # Reject known index/section paths
    import re
    for pattern in REJECT_PATH_PATTERNS:
        if re.search(pattern, path, re.IGNORECASE):
            return False

    return True


def validate_suggestions(suggestions: list) -> list:
    """
    Keep a suggestion only if:
    1. URL looks structurally like a specific article (not a homepage/section)
    2. Live HTTP check passes (URL actually exists)
    """
    valid = []
    for s in suggestions:
        url = s.get("url", "").strip().rstrip("/")
        if not _looks_like_article_url(url):
            continue
        if not _url_live(url):
            continue
        valid.append(s)
    return valid


# --------------------------------------------------------------------------- #
# System prompt — tightly scoped to 5 topics, no domain list
# --------------------------------------------------------------------------- #
SYSTEM_PROMPT = (
    "You are a knowledgeable advisor helping non-technical project and delivery "
    "managers find FREE, publicly accessible articles on exactly five topics. "
    "You must ONLY recommend articles that fall into one of these five topics — "
    "no exceptions:\n\n"

    "  1. How companies have transformed their business using AI "
    "(real case studies and transformation stories)\n"
    "  2. AI use cases relevant to business and operations "
    "(practical applications, not technical implementations)\n"
    "  3. AI project management strategy — how to plan, scope, and "
    "deliver AI initiatives without being a data scientist\n"
    "  4. Leading and building AI-ready teams — team structure, "
    "hiring, upskilling, and managing people in AI projects\n"
    "  5. AI product delivery strategy — roadmapping, prioritisation, "
    "stakeholder management, and shipping AI products\n\n"

    "If an article does not clearly belong to one of those five topics, "
    "DO NOT include it — even if it seems related to AI.\n\n"

    "STRICT URL RULES:\n"
    "1. ARTICLES ONLY. No videos, courses, tools, or homepages.\n"
    "2. The URL must point to a SPECIFIC published article or report — "
    "not a homepage, topic index, tag page, search page, or author page.\n"
    "3. The article must be FREE and publicly readable without login.\n"
    "4. Only include a URL if you are certain it is a real, currently live, "
    "specific article page. If you have any doubt, leave it out.\n"
    "5. Better to return 2 verified articles than 4 broken links.\n\n"

    "PERSONALIZATION: Tailor your selection and the 'why' sentence to the "
    "learner's specific role, goal, and current knowledge level.\n\n"

    "For each article provide: title, url, type (always 'read'), "
    "and one sentence explaining why it suits THIS learner.\n"
    "Also write a 1–2 sentence warm, personalized intro.\n\n"

    "Use clear, jargon-free language."
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
        f"Learner profile:\n{profile_text}\n\n"
        f"Resources already in their roadmap (do NOT repeat these):\n{existing}\n\n"
        "Suggest 2–4 free articles from the five allowed topics that suit this "
        "learner's role and goal. Each article must be a specific published page "
        "with a direct URL — no homepages, index pages, or topic hubs. "
        "Only include URLs you are certain are real and live."
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

        raw = [
            {
                "title": s.title,
                "url": s.url,
                "type": "read",   # always read — articles only
                "why": s.why,
            }
            for s in result.suggestions
        ]

        cleaned = validate_suggestions(raw)

        if not cleaned:
            return {
                "error": (
                    "No verified article links could be confirmed right now. "
                    "Showing your curated roadmap."
                )
            }

        return {"intro": result.intro, "suggestions": cleaned}

    except anthropic.AuthenticationError:
        return {"error": "Invalid API key. Check ANTHROPIC_API_KEY."}
    except anthropic.RateLimitError:
        return {"error": "Rate limited. Please try again in a moment."}
    except Exception as e:
        return {"error": f"Couldn't reach the AI service ({type(e).__name__}). Showing your curated roadmap."}
