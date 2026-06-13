"""
AI Roadmap for Managers — a Streamlit app.

A short questionnaire that builds a personalized, no-code AI learning roadmap
for experienced but non-technical project / delivery managers, using only
free resources from the internet.

Run it with:
    streamlit run app.py
"""

import streamlit as st

from roadmap_data import (
    QUESTIONS,
    TYPE_ICON,
    TYPE_LABEL,
    build_roadmap,
)
from ai_suggestions import ai_available, fetch_ai_suggestions
from pdf_export import build_pdf, AUTHOR_NAME, AUTHOR_EMAIL, AUTHOR_LINKEDIN

# --------------------------------------------------------------------------- #
# Page config + styling
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title="AI Roadmap for Managers",
    page_icon="🧭",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
      .stApp { background: radial-gradient(1100px 500px at 80% -10%, #1b2452 0%, transparent 60%), #0b1020; }
      .block-container { padding-top: 2.2rem; max-width: 820px; }
      h1, h2, h3, h4, p, li, label, span { color: #eaf0ff; }
      .eyebrow {
        display:inline-block; font-size:0.78rem; font-weight:600; letter-spacing:0.05em;
        text-transform:uppercase; color:#36d6c3; background:rgba(54,214,195,0.10);
        border:1px solid rgba(54,214,195,0.25); padding:5px 12px; border-radius:999px; margin-bottom:14px;
      }
      .sub { color:#9aa6c7; font-size:1.05rem; }
      .res-card {
        background:#1b2647; border:1px solid #2a3556; border-radius:14px;
        padding:16px 18px; margin-bottom:12px;
      }
      .res-title { font-weight:600; font-size:1.02rem; }
      .res-title a { color:#eaf0ff; text-decoration:none; }
      .res-title a:hover { color:#8a9bff; text-decoration:underline; }
      .res-desc { color:#9aa6c7; font-size:0.92rem; margin:6px 0 10px; }
      .chip {
        display:inline-block; font-size:0.72rem; padding:3px 9px; border-radius:999px;
        margin-right:6px; margin-top:4px; background:rgba(255,255,255,0.06);
        border:1px solid #2a3556; color:#9aa6c7;
      }
      .chip.free { color:#45d483; border-color:rgba(69,212,131,0.35); background:rgba(69,212,131,0.10); }
      .chip.type { color:#36d6c3; border-color:rgba(54,214,195,0.35); background:rgba(54,214,195,0.10); }
      .phase-goal { color:#9aa6c7; }
      .tips { background:rgba(108,123,255,0.07); border:1px dashed #2a3556; border-radius:14px; padding:18px 22px; }
      div[data-testid="stMetricValue"] { color:#eaf0ff; }

      /* FIX 2 — Primary buttons: dark text on bright background so label is always visible */
      div.stButton > button[kind="primary"],
      div.stDownloadButton > button[kind="primary"] {
        background: #36d6c3 !important;
        color: #0b1020 !important;
        border: none !important;
        font-weight: 700 !important;
      }
      div.stButton > button[kind="primary"]:hover,
      div.stDownloadButton > button[kind="primary"]:hover {
        background: #27b8a7 !important;
        color: #0b1020 !important;
      }

      /* Secondary / default buttons */
      div.stButton > button:not([kind="primary"]) {
        background: #1b2647 !important;
        color: #eaf0ff !important;
        border: 1px solid #2a3556 !important;
        font-weight: 600 !important;
      }
      div.stButton > button:not([kind="primary"]):hover {
        background: #232e5a !important;
        color: #ffffff !important;
        border-color: #8a9bff !important;
      }

      /* FIX 3 — Download button: always show label clearly */
      div.stDownloadButton > button {
        background: #8a9bff !important;
        color: #0b1020 !important;
        border: none !important;
        font-weight: 700 !important;
      }
      div.stDownloadButton > button:hover {
        background: #6c7cff !important;
        color: #0b1020 !important;
      }
      /* Force the inner span/text inside any download button to be dark */
      div.stDownloadButton > button * {
        color: #0b1020 !important;
      }

      /* FIX 1 — Author footer: bigger, brighter text */
      .author-footer {
        text-align: center;
        font-size: 1.05rem;       /* was 0.85rem */
        font-weight: 500;
        color: #c8d3f0;           /* brighter than #9aa6c7 */
        padding-bottom: 14px;
        margin-top: 38px;
        border-top: 1px solid #2a3556;
        padding-top: 18px;
      }
      .author-footer b { color: #eaf0ff; font-weight: 700; }
      .author-footer a { color: #8a9bff; text-decoration: none; }
      .author-footer a:hover { text-decoration: underline; color: #36d6c3; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------- #
# Session state
# --------------------------------------------------------------------------- #
if "stage" not in st.session_state:
    st.session_state.stage = "intro"   # intro -> quiz -> result
if "step" not in st.session_state:
    st.session_state.step = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "user_name" not in st.session_state:
    st.session_state.user_name = ""


def go(stage):
    st.session_state.stage = stage


def reset():
    st.session_state.stage = "intro"
    st.session_state.step = 0
    st.session_state.answers = {}
    st.session_state.user_name = ""


# --------------------------------------------------------------------------- #
# Intro screen
# --------------------------------------------------------------------------- #
def render_intro():
    st.markdown('<span class="eyebrow">No coding • 100% free resources</span>', unsafe_allow_html=True)
    st.title("Learn how AI *really* works — built for non-technical leaders")
    st.markdown(
        '<p class="sub">You manage projects and people. You don\'t want to write code — you want to '
        "<b>understand AI</b>, speak confidently with technical teams, and lead AI initiatives. "
        "Answer 6 quick questions and we'll build a personalized, step-by-step roadmap using only "
        "free material from the internet.</p>",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    c1.markdown("⏱️ **~60 seconds**")
    c2.markdown("🎯 **Tailored to you**")
    c3.markdown("🆓 **Only free resources**")

    st.write("")
    name = st.text_input(
        "First, what should we call you?",
        value=st.session_state.user_name,
        placeholder="e.g. Ravi (optional)",
        max_chars=40,
    )
    st.session_state.user_name = name.strip()

    if st.button("Build my roadmap  →", type="primary", use_container_width=True):
        st.session_state.step = 0
        go("quiz")
        st.rerun()


# --------------------------------------------------------------------------- #
# Quiz screen
# --------------------------------------------------------------------------- #
def render_quiz():
    step = st.session_state.step
    q = QUESTIONS[step]
    total = len(QUESTIONS)

    st.progress((step + 1) / total, text=f"Question {step + 1} of {total}")
    st.subheader(q["title"])
    st.caption(q["help"])

    # Build label -> value maps
    labels = [f"{label} — {desc}" for (_v, label, desc) in q["options"]]
    values = [v for (v, _l, _d) in q["options"]]
    prev = st.session_state.answers.get(q["id"])

    if q["multi"]:
        default = [labels[values.index(v)] for v in (prev or []) if v in values]
        chosen = []
        st.write("")
        for label, value in zip(labels, values):
            checked = st.checkbox(label, value=(value in (prev or [])), key=f"{q['id']}_{value}")
            if checked:
                chosen.append(value)
        selection = chosen
    else:
        idx = values.index(prev) if prev in values else None
        choice = st.radio(
            "Choose one:",
            labels,
            index=idx,
            key=f"radio_{q['id']}_{step}",
            label_visibility="collapsed",
        )
        selection = values[labels.index(choice)] if choice is not None else None

    st.write("")
    col_back, col_spacer, col_next = st.columns([1, 2, 1])

    with col_back:
        if step > 0 and st.button("← Back", use_container_width=True):
            st.session_state.step -= 1
            st.rerun()

    has_answer = bool(selection) if q["multi"] else selection is not None
    next_label = "See my roadmap →" if step == total - 1 else "Next →"

    with col_next:
        if st.button(next_label, type="primary", disabled=not has_answer, use_container_width=True):
            st.session_state.answers[q["id"]] = selection
            if step == total - 1:
                go("result")
            else:
                st.session_state.step += 1
            st.rerun()

    # Persist current selection so Back/Next remembers it even without clicking Next
    if has_answer:
        st.session_state.answers[q["id"]] = selection


# --------------------------------------------------------------------------- #
# Result screen
# --------------------------------------------------------------------------- #
ROLE_MAP = {
    "pm": "project manager", "dm": "delivery / program manager",
    "product": "product / business lead", "other": "experienced manager",
}
GOAL_MAP = {
    "lead": "lead and manage AI projects with confidence",
    "talk": "speak the same language as your technical teams",
    "strategy": "make sharper strategic decisions about AI",
    "career": "stay relevant and grow your career",
    "curious": "genuinely understand how AI works",
}
LEVEL_MAP = {
    "none": "starting from the very beginning",
    "buzz": "moving past the buzzwords",
    "user": "connecting the tools you use to the 'why' behind them",
    "some": "adding depth and structure to what you know",
}
TIME_LABEL = {"high": "6+ hrs/week", "mid": "3–5 hrs/week", "low": "1–2 hrs/week"}

STYLE_LABEL = {"video": "videos", "read": "reading", "course": "structured courses", "hands": "trying tools"}
INTEREST_LABEL = {
    "genai": "generative AI & ChatGPT", "prompt": "prompting & everyday AI tools",
    "concepts": "how AI/ML works", "strategy": "AI strategy & use-cases",
    "ethics": "risk, ethics & governance", "managing": "managing AI projects",
}


def profile_text(a: dict) -> str:
    """A short natural-language description of the learner for the AI prompt."""
    styles = ", ".join(STYLE_LABEL.get(s, s) for s in (a.get("style") or [])) or "no strong preference"
    interests = ", ".join(INTEREST_LABEL.get(i, i) for i in (a.get("interest") or [])) or "general AI understanding"
    return (
        f"- Role: {ROLE_MAP.get(a.get('role'), 'manager')}\n"
        f"- Main goal: {GOAL_MAP.get(a.get('goal'), 'understand AI')}\n"
        f"- Current level: {LEVEL_MAP.get(a.get('level'), 'beginner')}\n"
        f"- Time available: {TIME_LABEL.get(a.get('time'), 'some time')} per week\n"
        f"- Prefers learning by: {styles}\n"
        f"- Most interested in: {interests}\n"
        f"- Wants NO coding."
    )


def answer_signature(a: dict) -> tuple:
    """Hashable, order-stable signature of the answers (cache key)."""
    def norm(v):
        return tuple(sorted(v)) if isinstance(v, list) else v
    return tuple((q["id"], norm(a.get(q["id"]))) for q in QUESTIONS)


def get_ai_result(a: dict, plan: dict):
    """Fetch (cached) AI suggestions, or None if unavailable. Reused for page + PDF."""
    if not ai_available():
        return None
    existing_titles = tuple(r["title"] for p in plan["phases"] for r in p["resources"])
    with st.spinner("✨ Personalizing a few extra picks for you…"):
        return fetch_ai_suggestions(answer_signature(a), profile_text(a), existing_titles)


def render_ai_section(name: str, result):
    """Render personalized AI suggestions from a pre-fetched result."""
    if not result:
        return
    if "error" in result:
        st.caption(f"ℹ️ Personalized picks unavailable right now — {result['error']}")
        return

    heading = f"### ✨ {name}, here are some picks for you" if name else "### ✨ Personalized picks for you"
    st.markdown(heading)
    if result.get("intro"):
        st.markdown(f'<p class="sub">{result["intro"]}</p>', unsafe_allow_html=True)

    for s in result["suggestions"]:
        icon = TYPE_ICON.get(s["type"], "🔗")
        type_label = TYPE_LABEL.get(s["type"], "Resource")
        st.markdown(
            f'<div class="res-card">'
            f'<div class="res-title">{icon} <a href="{s["url"]}" target="_blank">{s["title"]} ↗</a></div>'
            f'<div class="res-desc">{s["why"]}</div>'
            f'<span class="chip type">{type_label}</span>'
            f'<span class="chip free">Free</span>'
            f'<span class="chip">✨ AI-suggested — verify the link</span>'
            f"</div>",
            unsafe_allow_html=True,
        )
    st.caption("These are generated by AI based on your answers. Links are best-effort — open them to confirm they're still free and available.")
    st.write("")


def render_result():
    a = st.session_state.answers
    name = st.session_state.get("user_name", "").strip()
    plan = build_roadmap(a)

    st.markdown('<span class="eyebrow">Your personalized roadmap</span>', unsafe_allow_html=True)
    title = f"{name}, here's your personalized AI roadmap" if name else "Your no-code path to understanding AI"
    st.title(title)
    st.markdown(
        f'<p class="sub">As a <b>{ROLE_MAP.get(a.get("role"), "manager")}</b> who wants to '
        f'<b>{GOAL_MAP.get(a.get("goal"), "understand AI")}</b>, here\'s a path that meets you where you are — '
        f'<b>{LEVEL_MAP.get(a.get("level"), "at your level")}</b>. Everything below is '
        f"<b>free</b> and requires <b>no coding</b>.</p>",
        unsafe_allow_html=True,
    )

    # Fetch AI suggestions once — reused for the page section and the PDF
    ai_result = get_ai_result(a, plan)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Phases", len(plan["phases"]))
    m2.metric("Free resources", plan["total"])
    m3.metric("Your pace", TIME_LABEL.get(a.get("time"), "—"))
    m4.metric("Est. to finish", f"~{plan['weeks']} wks")

    st.divider()

    for i, phase in enumerate(plan["phases"], start=1):
        st.markdown(f"### {i}. {phase['title']}")
        st.markdown(f'<p class="phase-goal"><b>Goal:</b> {phase["goal"]}</p>', unsafe_allow_html=True)
        for r in phase["resources"]:
            icon = TYPE_ICON.get(r["type"], "🔗")
            type_label = TYPE_LABEL.get(r["type"], "Resource")
            chips = (
                f'<span class="chip type">{type_label}</span>'
                f'<span class="chip free">Free</span>'
                + "".join(f'<span class="chip">{t}</span>' for t in r["tags"])
            )
            st.markdown(
                f'<div class="res-card">'
                f'<div class="res-title">{icon} <a href="{r["url"]}" target="_blank">{r["title"]} ↗</a></div>'
                f'<div class="res-desc">{r["desc"]}</div>'
                f"{chips}"
                f"</div>",
                unsafe_allow_html=True,
            )
        st.write("")

    # ---- Optional AI layer: personalized fresh picks ----
    render_ai_section(name, ai_result)

    st.markdown(
        '<div class="tips">'
        "<h4>How to make this stick</h4>"
        "<ul>"
        "<li><b>Schedule it.</b> Block one recurring slot in your calendar — treat it like a meeting you can't move.</li>"
        "<li><b>Learn out loud.</b> After each resource, write 3 sentences explaining it to a colleague. "
        "If you can explain it, you understand it.</li>"
        "<li><b>Tie it to a real problem.</b> Pick one initiative at work and keep asking "
        "\"could AI help here, and how would I know?\"</li>"
        "<li><b>Don't aim to code.</b> Your goal is judgment, not syntax — knowing what's possible, "
        "what's hard, and what questions to ask your team.</li>"
        "</ul></div>",
        unsafe_allow_html=True,
    )

    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("↺ Retake the quiz", use_container_width=True):
            reset()
            st.rerun()
    with col2:
        profile_lines = [
            f"Role: {ROLE_MAP.get(a.get('role'), 'manager')}",
            f"Goal: {GOAL_MAP.get(a.get('goal'), 'understand AI')}",
            f"Starting point: {LEVEL_MAP.get(a.get('level'), 'at your level')}",
            f"Pace: {TIME_LABEL.get(a.get('time'), '-')}",
        ]
        pdf_bytes = build_pdf(name, profile_lines, plan, ai_result)
        safe_name = "".join(c for c in name if c.isalnum()) or "my"
        st.download_button(
            "⬇️ Download my roadmap (PDF)",
            data=pdf_bytes,
            file_name=f"{safe_name}_ai_roadmap.pdf",
            mime="application/pdf",
            use_container_width=True,
        )


# --------------------------------------------------------------------------- #
# Router
# --------------------------------------------------------------------------- #
stage = st.session_state.stage
if stage == "intro":
    render_intro()
elif stage == "quiz":
    render_quiz()
else:
    render_result()

# --------------------------------------------------------------------------- #
# Footer — author credit & contact (shown on every screen)
# --------------------------------------------------------------------------- #
st.markdown(
    f'<hr style="border-color:#2a3556; margin-top:38px;">'
    f'<div class="author-footer">'
    f"Created by <b>{AUTHOR_NAME}</b>&nbsp; ·&nbsp; "
    f'<a href="mailto:{AUTHOR_EMAIL}">{AUTHOR_EMAIL}</a>&nbsp; ·&nbsp; '
    f'<a href="{AUTHOR_LINKEDIN}" target="_blank">LinkedIn ↗</a>'
    f"</div>",
    unsafe_allow_html=True,
)
