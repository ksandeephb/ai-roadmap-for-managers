"""
ai_suggestions.py
-----------------
Optional AI layer (Claude Sonnet 4.6) that adds personalized, free, no-code
article suggestions on top of the curated roadmap.

Trusted domains are curated from publications verified to regularly publish
articles on: AI transformation, AI use cases, AI project management,
leading AI teams, and AI product delivery strategy.

All suggested URLs are validated with a live HTTP check before display.
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
# Curated trusted domains
# Sourced from publications verified to regularly publish articles on:
#   - Company AI transformation case studies
#   - AI use cases for business leaders
#   - AI project management & delivery strategy
#   - Leading AI teams & building AI-ready organisations
#   - AI product strategy & roadmapping
# --------------------------------------------------------------------------- #
TRUSTED_DOMAINS = {
    # ── Strategy & management research ──────────────────────────────────────
    "hbr.org",                        # Harvard Business Review — heavy AI leadership coverage
    "sloanreview.mit.edu",            # MIT Sloan Mgmt Review — AI strategy & transformation
    "mckinsey.com",                   # McKinsey Insights — state of AI, transformation reports
    "www.mckinsey.com",
    "bcg.com",                        # BCG — AI strategy and business transformation
    "www.bcg.com",
    "www2.deloitte.com",              # Deloitte Insights — AI adoption and delivery
    "deloitte.com",
    "pwc.com",                        # PwC — AI governance, strategy
    "www.pwc.com",
    "accenture.com",                  # Accenture — AI transformation case studies
    "www.accenture.com",

    # ── Project & delivery management ────────────────────────────────────────
    "thedigitalprojectmanager.com",   # DPM — dedicated AI in project management articles
    "pmi.org",                        # PMI — AI project delivery and PM strategy
    "www.pmi.org",
    "blog.iil.com",                   # IIL Blog — PM to project leadership with AI
    "apm.org.uk",                     # Association for Project Management — AI adoption research

    # ── Tech & AI journalism (business focus) ────────────────────────────────
    "technologyreview.com",           # MIT Technology Review — AI business impact
    "www.technologyreview.com",
    "venturebeat.com",                # VentureBeat — AI use cases, enterprise AI
    "zdnet.com",                      # ZDNet — AI strategy, enterprise adoption
    "www.zdnet.com",
    "wired.com",                      # Wired — AI transformation stories
    "www.wired.com",
    "www.ibm.com",                    # IBM Think — AI in project management, use cases
    "ibm.com",

    # ── Product & delivery strategy ──────────────────────────────────────────
    "productplan.com",                # ProductPlan — AI product strategy and roadmapping
    "www.productplan.com",
    "atlassian.com",                  # Atlassian — team delivery and AI adoption guides
    "www.atlassian.com",

    # ── Learning & AI literacy (article/guide pages only) ────────────────────
    "learnprompting.org",
    "elementsofai.com",
    "www.elementsofai.com",
    "learn.microsoft.com",
    "cloud.google.com",
}

# Paths that signal an index/homepage rather than a specific article
REJECT_PATH_PATTERNS = [
    r"^/$", r"^/en/?$", r"^/us/?$",
    r"^/topics/?$", r"^/insights/?$", r"^/capabilities/?$",
    r"^/services/?$", r"^/solutions/?$", r"^/resources/?$",
    r"^/blog/?$", r"^/articles/?$", r"^/news/?$",
    r"/tag/", r"/category/", r"/author/", r"/search",
    r"/landing_page/",
]

MIN_PATH_LENGTH = 15


def _parse_url(url: str):
    try:
        scheme, rest = url.split("//", 1)
        domain, _, path = rest.partition("/")
        return scheme.rstrip(":").lower(), domain.lower(), "/" + path.rstrip("/")
    except Exception:
        return "", "", "/"


def _url_live(url: str, timeout: int = 6) -> bool:
    """HEAD request — True only if server responds HTTP < 400."""
    try:
        req = urllib.request.Request(
            url, method="HEAD",
            headers={"User-Agent": "Mozilla/5.0 (compatible; LinkChecker/1.0)"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status < 400
    except Exception:
        return False


def validate_suggestions(suggestions: list) -> list:
    """
    Keep a suggestion only if:
    1. Domain is in TRUSTED_DOMAINS
    2. URL is HTTPS
    3. Path is long enough and doesn't match index/homepage patterns
    4. Live HTTP check passes
    """
    valid = []
    for s in suggestions:
        url = s.get("url", "").strip().rstrip("/")
        scheme, domain, path = _parse_url(url)

        if scheme != "https":
            continue
        if domain not in TRUSTED_DOMAINS:
            continue
        if len(path) < MIN_PATH_LENGTH:
            continue
        if any(re.search(p, path, re.IGNORECASE) for p in REJECT_PATH_PATTERNS):
            continue
        if not _url_live(url):
            continue

        valid.append(s)
    return valid


# --------------------------------------------------------------------------- #
# System prompt
# --------------------------------------------------------------------------- #
_DOMAIN_LIST = ", ".join(sorted({
    d.lstrip("www.").lstrip("www2.")
    for d in TRUSTED_DOMAINS
}))

SYSTEM_PROMPT = (
    "You are a knowledgeable advisor helping non-technical project and delivery "
    "managers find FREE, publicly accessible articles that COMPLEMENT their existing "
    "learning roadmap.\n\n"

    "The learner's roadmap already covers six pillars:\n"
    "  1. AI History & Background — where AI came from and why it matters now\n"
    "  2. AI Concepts in plain English — how AI/ML/LLMs actually work\n"
    "  3. AI Use Cases & Frameworks — where AI creates business value\n"
    "  4. AI Project Lifecycle — CRISP-DM, MLOps basics, team roles, data quality\n"
    "  5. Managing & Delivering AI Projects — planning, risk, stakeholders, delivery\n"
    "  6. AI Strategy, Ethics & Leadership — governance, responsible AI, team building\n\n"

    "You must ONLY recommend articles that clearly belong to one of these six pillars. "
    "Every suggestion must COMPLEMENT the resources already in the roadmap — do NOT "
    "repeat or overlap with what they already have. Focus on DEPTH and REAL-WORLD "
    "application: company case studies, practitioner guides, research reports, and "
    "leadership frameworks — not introductory explainers they have already covered.\n\n"

    "STRICT URL RULES:\n"
    "1. ARTICLES ONLY — no videos, courses, homepages, or tool pages.\n"
    f"2. Only use URLs from these trusted domains: {_DOMAIN_LIST}.\n"
    "3. The URL must point to a SPECIFIC published article or report — not a homepage, "
    "topic index, tag page, search page, or author page.\n"
    "4. The article must be FREE and publicly readable without login or paywall.\n"
    "5. Only include a URL if you are 100% certain it is a real, currently live, "
    "specific article page. If in any doubt, leave it out entirely.\n"
    "6. Better to return 2 verified articles than 4 broken links.\n\n"

    "PERSONALIZATION:\n"
    "- Match every suggestion to the learner's specific role (PM/DM/product lead), "
    "goal, current knowledge level, and the pillar(s) they are most interested in.\n"
    "- The 'why' sentence must explain exactly why THIS article fits THIS learner — "
    "not a generic description of the article.\n"
    "- Write a warm 1–2 sentence intro referencing their role and goal.\n\n"

    "Use clear, jargon-free language. Be specific and encouraging."
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
        f"Resources ALREADY in their roadmap — do NOT suggest anything that overlaps "
        f"with or repeats these:\n{existing}\n\n"
        "Based on this learner's profile and the six learning pillars, suggest 2–4 "
        "free articles that GO DEEPER than what they already have. Prioritise:\n"
        "- Real company AI transformation case studies relevant to their industry or role\n"
        "- Practitioner guides on AI project delivery, risk, or team leadership\n"
        "- Research reports on AI strategy or governance from credible sources\n"
        "- Articles on AI project lifecycle, data quality, or MLOps for non-technical managers\n\n"
        "Each article must be a specific published page with a direct URL from the "
        "allowed domains. No homepages, index pages, or topic hubs. "
        "Only include URLs you are 100% certain are real and live right now."
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
                "type": "read",
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
