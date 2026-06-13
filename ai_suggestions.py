"""
ai_suggestions.py
-----------------
Optional AI layer (Claude Sonnet 4.6) that adds personalized, free, no-code
article suggestions on top of the curated roadmap.

Only articles from trusted, established publications are allowed.
No YouTube or video links — article URLs are far more stable and verifiable.
All links are validated with a live HTTP check before being shown to the user.
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
    type: str   # one of: read | course | tool
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
# URL validation
# --------------------------------------------------------------------------- #
TRUSTED_DOMAINS = {
    # Strategy & business publications
    "hbr.org",
    "sloanreview.mit.edu",
    "mckinsey.com", "www.mckinsey.com",
    "bcg.com", "www.bcg.com",
    "www2.deloitte.com", "deloitte.com",
    "pwc.com", "www.pwc.com",
    "accenture.com", "www.accenture.com",
    # Tech & AI journalism
    "technologyreview.com", "www.technologyreview.com",
    "venturebeat.com",
    "zdnet.com", "www.zdnet.com",
    "wired.com", "www.wired.com",
    # Project & product management
    "pmi.org", "www.pmi.org",
    "atlassian.com", "www.atlassian.com",
    "productplan.com", "www.productplan.com",
    # Learning platforms (guide/article pages)
    "learnprompting.org",
    "elementsofai.com", "www.elementsofai.com",
    "learn.microsoft.com",
    "cloud.google.com",
    "coursera.org", "www.coursera.org",
}

# Path lengths this short almost always mean a homepage or top-level section
MIN_PATH_LENGTH = 12


def _domain(url: str) -> str:
    try:
        return url.split("//", 1)[1].split("/")[0].lower()
    except Exception:
        return ""


def _path(url: str) -> str:
    try:
        after_domain = url.split("//", 1)[1].split("/", 1)
        return "/" + after_domain[1].rstrip("/") if len(after_domain) > 1 else "/"
    except Exception:
        return "/"


def _url_live(url: str, timeout: int = 5) -> bool:
    """HEAD request — returns True only if the server responds with HTTP < 400."""
    try:
        req = urllib.request.Request(
            url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status < 400
    except Exception:
        return False


def validate_suggestions(suggestions: list) -> list:
    """
    Keep a suggestion only if:
    1. Domain is in TRUSTED_DOMAINS
    2. Path is long enough to be a real article (not a homepage/section root)
    3. Live HTTP check passes
    """
    valid = []
    for s in suggestions:
        url = s.get("url", "").strip().rstrip("/")
        if not url.startswith("https://"):
            continue
        if _domain(url) not in TRUSTED_DOMAINS:
            continue
        if len(_path(url)) < MIN_PATH_LENGTH:
            continue
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
    "goal, and current knowledge level. Reference what they told you.\n\n"

    "STRICT RULES — all must be followed:\n"
    "1. Only FREE resources. No paywalls or sign-up walls.\n"
    "2. NO-CODE only — nothing requiring programming.\n"
    "3. ARTICLES ONLY — no YouTube or video links. Only written articles, "
    "guides, and reports from well-known publications.\n"
    "4. Only use URLs from these trusted domains: hbr.org, sloanreview.mit.edu, "
    "mckinsey.com, bcg.com, deloitte.com, pwc.com, accenture.com, "
    "technologyreview.com, venturebeat.com, zdnet.com, wired.com, "
    "pmi.org, atlassian.com, productplan.com, learnprompting.org, "
    "elementsofai.com, learn.microsoft.com, cloud.google.com, coursera.org.\n"
    "5. Every URL must link to a SPECIFIC article or guide page — never a "
    "homepage, topic index, or search results page.\n"
    "6. Only include a URL if you are certain it exists and is publicly "
    "accessible. If unsure, omit the resource entirely.\n"
    "7. It is better to return 2 real articles than 4 broken links.\n\n"

    "CONTENT FOCUS — articles about:\n"
    "- How companies have transformed their business using AI (case studies)\n"
    "- AI use cases for non-technical business leaders\n"
    "- Managing and leading AI projects and teams\n"
    "- AI product delivery and roadmap strategy\n"
    "- AI governance, ethics, and risk for managers\n"
    "- Practical AI literacy for project/delivery managers\n\n"

    "Do NOT repeat any resource already in the learner's roadmap.\n\n"

    "For each resource provide: title, url, type (read/course/tool), "
    "and one sentence on why it fits THIS learner specifically.\n"
    "Also write a 1–2 sentence personalized intro referencing their role and goal.\n\n"

    "Write in clear, jargon-free language. Be encouraging and specific."
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
        "Suggest 2–4 additional free articles tailored to this person. "
        "Only include an article if you are certain the URL is a real, specific, "
        "publicly accessible page — not a homepage or category page. "
        "For each: title, url, type (read/course/tool), one-sentence why it fits them. "
        "Also write a 1–2 sentence personalized intro."
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

        valid_types = {"course", "read", "tool"}
        raw = []
        for s in result.suggestions:
            t = s.type.lower().strip()
            raw.append({
                "title": s.title,
                "url": s.url,
                "type": t if t in valid_types else "read",
                "why": s.why,
            })

        cleaned = validate_suggestions(raw)

        if not cleaned:
            return {"error": "No verified article links could be confirmed right now. Showing your curated roadmap."}

        return {"intro": result.intro, "suggestions": cleaned}

    except anthropic.AuthenticationError:
        return {"error": "Invalid API key. Check ANTHROPIC_API_KEY."}
    except anthropic.RateLimitError:
        return {"error": "Rate limited. Please try again in a moment."}
    except Exception as e:
        return {"error": f"Couldn't reach the AI service ({type(e).__name__}). Showing your curated roadmap."}
