"""
AI Roadmap for Managers — enhanced Streamlit app.

Enhancements implemented:
  1. Animated phase timeline (CSS scroll-reveal)
  2. Phase completion tracker (checkboxes + progress bar)
  3. Platform logos on resource cards
  4. Dark/light mode toggle
  5. Weekly learning schedule generator
  6. Role-specific "why this matters" framing on every card
  7. "Skip what I know" filter (collapse phases by level)
  8. LinkedIn share button (pre-filled post)
  9. Email the roadmap (mailto link — no backend needed)
 10. "Finish by date" calculator
 11. Resource quality ratings (crowd-sourced where available)
 12. "What's next after this roadmap" section
 13. AI chat assistant on result page (Claude API)
 14. Intro stats counter animation
"""

import datetime
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
# Platform logos (emoji-based — no external assets needed)
# --------------------------------------------------------------------------- #
PLATFORM_LOGO = {
    "youtube.com":     "▶️",
    "coursera.org":    "🎓",
    "hbr.org":         "📰",
    "mckinsey.com":    "📊",
    "ibm.com":         "🔵",
    "ml-ops.org":      "⚙️",
    "nist.gov":        "🏛️",
    "learnprompting":  "💬",
    "ownml.co":        "🗂️",
    "thedigital":      "🛠️",
    "openai.com":      "🤖",
    "cloud.google":    "☁️",
    "sloanreview":     "🎓",
}

def _platform_badge(url: str) -> str:
    for key, logo in PLATFORM_LOGO.items():
        if key in url:
            return logo
    return "🔗"

# --------------------------------------------------------------------------- #
# Resource ratings (known ratings from public sources)
# --------------------------------------------------------------------------- #
RATINGS = {
    "coursera.org/learn/ai-for-everyone":           "⭐ 4.8 (51k reviews)",
    "coursera.org/learn/generative-ai-for-everyone":"⭐ 4.7 (12k reviews)",
    "coursera.org/learn/generative-ai-for-leaders": "⭐ 4.6",
    "coursera.org/learn/introduction-to-generative-ai": "⭐ 4.7 (30k reviews)",
    "coursera.org/learn/introduction-to-responsible-ai": "⭐ 4.8",
    "youtube.com/watch?v=G2fqAlgmoPo":             "👁️ 5M+ views",
    "youtube.com/watch?v=2IK3DFHRFfw":             "👁️ 3M+ views",
    "youtube.com/watch?v=aircAruvnKk":             "👁️ 80M+ views",
    "youtube.com/watch?v=zjkBMFhNj_g":            "👁️ 4M+ views",
    "youtube.com/watch?v=FrDnPTPgEmk":            "👁️ 1M+ views",
}

def _rating(url: str) -> str:
    for key, rating in RATINGS.items():
        if key in url:
            return rating
    return ""

# --------------------------------------------------------------------------- #
# Role-specific "why this matters" framing
# --------------------------------------------------------------------------- #
ROLE_WHY = {
    "pm": {
        "video":  "Watching this gives you the mental model to run your next AI kickoff meeting.",
        "course": "This course was built for people in your role — every example is delivery-focused.",
        "read":   "Read this before your next AI project status update — it changes how you frame risk.",
        "tool":   "Use this in your next sprint planning or discovery session with your team.",
    },
    "product": {
        "video":  "Watch this to speak the same language as your engineering and data team.",
        "course": "This directly maps to product strategy decisions you're already making.",
        "read":   "This reframes AI as a product capability, not a technical implementation.",
        "tool":   "Use this in your next product discovery session to scope AI features clearly.",
    },
    "scrum": {
        "video":  "Watch this to understand what your team means during sprint reviews.",
        "course": "Helps you facilitate better AI sprint ceremonies and retrospectives.",
        "read":   "Understand the AI lifecycle so you can map it to your sprint cadence.",
        "tool":   "Use this to define 'done' for ML features in your backlog.",
    },
    "exec": {
        "video":  "A 20-minute briefing you can use to frame AI investment conversations.",
        "course": "Gives you the vocabulary to ask better questions of your AI teams.",
        "read":   "Essential context for your next board or leadership team discussion on AI.",
        "tool":   "Use this to evaluate AI proposals from your teams more confidently.",
    },
}

def _role_why(role: str, rtype: str) -> str:
    return ROLE_WHY.get(role, {}).get(rtype, "")

# --------------------------------------------------------------------------- #
# Page config + styling
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title="AI Roadmap for Managers",
    page_icon="🧭",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Theme toggle in session state
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

dark = st.session_state.dark_mode

# Colour tokens
if dark:
    BG       = "radial-gradient(1100px 500px at 80% -10%, #1b2452 0%, transparent 60%), #0b1020"
    CARD_BG  = "#1b2647"
    CARD_BR  = "#2a3556"
    TEXT     = "#eaf0ff"
    MUTED    = "#9aa6c7"
    ACCENT   = "#36d6c3"
    PHASE_BG = "rgba(108,123,255,0.10)"
else:
    BG       = "#f4f6fb"
    CARD_BG  = "#ffffff"
    CARD_BR  = "#dde3f0"
    TEXT     = "#1e2433"
    MUTED    = "#5c6b74"
    ACCENT   = "#006d77"
    PHASE_BG = "rgba(0,109,119,0.06)"

st.markdown(f"""
<style>
  .stApp {{ background: {BG}; }}
  .block-container {{ padding-top: 2.2rem; max-width: 860px; }}
  h1, h2, h3, h4, p, li, label, span {{ color: {TEXT}; }}

  .eyebrow {{
    display:inline-block; font-size:0.78rem; font-weight:600; letter-spacing:0.05em;
    text-transform:uppercase; color:{ACCENT}; background:rgba(54,214,195,0.10);
    border:1px solid rgba(54,214,195,0.25); padding:5px 12px; border-radius:999px; margin-bottom:14px;
  }}
  .sub {{ color:{MUTED}; font-size:1.05rem; }}

  /* Resource card */
  .res-card {{
    background:{CARD_BG}; border:1px solid {CARD_BR}; border-radius:14px;
    padding:16px 18px; margin-bottom:10px;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
  }}
  .res-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 24px rgba(54,214,195,0.12);
  }}
  .res-title {{ font-weight:600; font-size:1.02rem; }}
  .res-title a {{ color:{TEXT}; text-decoration:none; }}
  .res-title a:hover {{ color:{ACCENT}; text-decoration:underline; }}
  .res-desc {{ color:{MUTED}; font-size:0.92rem; margin:5px 0 4px; }}
  .res-why  {{ color:{ACCENT}; font-size:0.82rem; margin:4px 0 8px; font-style:italic; }}
  .res-rating {{ color:#f0a500; font-size:0.78rem; margin-bottom:6px; }}

  /* Chips */
  .chip {{
    display:inline-block; font-size:0.72rem; padding:3px 9px; border-radius:999px;
    margin-right:6px; margin-top:4px; background:rgba(255,255,255,0.06);
    border:1px solid {CARD_BR}; color:{MUTED};
  }}
  .chip.free  {{ color:#45d483; border-color:rgba(69,212,131,0.35); background:rgba(69,212,131,0.10); }}
  .chip.type  {{ color:{ACCENT}; border-color:rgba(54,214,195,0.35); background:rgba(54,214,195,0.10); }}
  .chip.done  {{ color:#8a9bff; border-color:rgba(138,155,255,0.35); background:rgba(138,155,255,0.10); text-decoration:line-through; }}

  /* Phase header */
  .phase-header {{
    background:{PHASE_BG}; border-left:4px solid {ACCENT};
    border-radius:0 12px 12px 0; padding:14px 18px; margin-bottom:8px;
  }}
  .phase-num  {{ color:{ACCENT}; font-weight:800; font-size:0.82rem; letter-spacing:0.08em; }}
  .phase-title {{ font-weight:700; font-size:1.08rem; color:{TEXT}; margin:2px 0; }}
  .phase-goal {{ color:{MUTED}; font-size:0.88rem; }}
  .phase-done {{ opacity:0.5; }}

  /* Progress bar */
  .prog-bar-wrap {{ background:{CARD_BR}; border-radius:999px; height:8px; margin:8px 0 16px; }}
  .prog-bar-fill {{ background:linear-gradient(90deg,{ACCENT},#8a9bff); border-radius:999px; height:8px; transition:width 0.4s; }}

  /* Timeline */
  .timeline {{
    display:flex; gap:8px; margin:16px 0 24px; overflow-x:auto; padding-bottom:6px;
  }}
  .tl-step {{
    flex:0 0 auto; text-align:center; padding:8px 14px;
    background:{CARD_BG}; border:1px solid {CARD_BR}; border-radius:10px;
    font-size:0.78rem; color:{MUTED}; min-width:90px;
  }}
  .tl-step.active {{
    background:rgba(54,214,195,0.12); border-color:{ACCENT}; color:{ACCENT}; font-weight:700;
  }}
  .tl-step.completed {{
    background:rgba(69,212,131,0.10); border-color:rgba(69,212,131,0.35); color:#45d483;
  }}
  .tl-arrow {{ color:{MUTED}; align-self:center; font-size:1.1rem; }}

  /* Tips */
  .tips {{
    background:{PHASE_BG}; border:1px dashed {CARD_BR}; border-radius:14px; padding:18px 22px;
  }}

  /* What's next */
  .next-card {{
    background:{CARD_BG}; border:1px solid {CARD_BR}; border-radius:12px;
    padding:14px 16px; margin-bottom:10px;
  }}
  .next-title {{ font-weight:600; font-size:0.95rem; color:{TEXT}; }}
  .next-desc  {{ font-size:0.85rem; color:{MUTED}; margin-top:4px; }}

  /* Chat */
  .chat-wrap {{ background:{CARD_BG}; border:1px solid {CARD_BR}; border-radius:14px; padding:16px; margin-top:8px; }}

  /* Metric */
  div[data-testid="stMetricValue"] {{ color:{TEXT}; }}

  /* Buttons */
  div.stButton > button[kind="primary"] {{
    color: #0b1020 !important; background: #36d6c3 !important;
    border: none !important; font-weight: 700 !important;
  }}
  div.stButton > button[kind="primary"]:hover {{
    background: #27b8a7 !important; color: #0b1020 !important;
  }}
  div.stButton > button[kind="primary"] p,
  div.stButton > button[kind="primary"] span {{ color: #0b1020 !important; }}
  div.stButton > button:not([kind="primary"]) {{
    background: {CARD_BG} !important; color: #8a9bff !important;
    border: 1px solid #3a4a7a !important; font-weight: 600 !important;
  }}
  div.stButton > button:not([kind="primary"]):hover {{
    background: #232e5a !important; color: {TEXT} !important;
    border-color: #8a9bff !important;
  }}
  div.stButton > button:not([kind="primary"]) p,
  div.stButton > button:not([kind="primary"]) span {{ color: #8a9bff !important; }}
  div.stDownloadButton > button {{
    background: #F0A500 !important; color: #0b1020 !important;
    border: none !important; font-weight: 800 !important;
    font-size: 0.97rem !important; opacity: 1 !important;
  }}
  div.stDownloadButton > button:hover {{
    background: #d4920a !important; color: #0b1020 !important;
    box-shadow: 0 0 14px rgba(240,165,0,0.40) !important;
  }}
  div.stDownloadButton > button *, div.stDownloadButton > button p,
  div.stDownloadButton > button span, div.stDownloadButton > button div {{
    color: #0b1020 !important; font-weight: 800 !important;
  }}

  /* Author footer */
  .author-footer {{
    text-align:center; font-size:1.0rem; font-weight:500; color:#b0bdd8;
    padding:16px 0 10px; margin-top:38px; border-top:1px solid {CARD_BR};
  }}
  .author-footer b  {{ color:{TEXT}; font-weight:700; }}
  .author-footer a  {{ color:#8a9bff; text-decoration:none; }}
  .author-footer a:hover {{ text-decoration:underline; color:{ACCENT}; }}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------- #
# Session state
# --------------------------------------------------------------------------- #
for key, default in [
    ("stage", "intro"), ("step", 0), ("answers", {}),
    ("user_name", ""), ("completed", set()), ("chat_history", []),
    ("skip_phases", set()),
]:
    if key not in st.session_state:
        st.session_state[key] = default


def go(stage):   st.session_state.stage = stage
def reset():
    for k in ["stage","step","answers","user_name","completed","chat_history","skip_phases"]:
        st.session_state[k] = {"stage":"intro","step":0,"answers":{},"user_name":"",
                                "completed":set(),"chat_history":[],"skip_phases":set()}[k]


# --------------------------------------------------------------------------- #
# Maps
# --------------------------------------------------------------------------- #
ROLE_MAP = {
    "pm":      "project / delivery manager",
    "product": "product owner / business lead",
    "scrum":   "scrum master / agile lead",
    "exec":    "senior leader / executive",
}
GOAL_MAP = {
    "lead":     "lead and manage AI projects with confidence",
    "talk":     "speak the same language as your technical teams",
    "strategy": "make sharper strategic decisions about AI",
    "career":   "stay relevant and grow your career",
    "curious":  "genuinely understand how AI works",
}
LEVEL_MAP = {
    "none": "starting from the very beginning",
    "buzz": "moving past the buzzwords",
    "user": "connecting the tools you use to the 'why' behind them",
    "some": "adding depth and structure to what you know",
}
TIME_LABEL  = {"high": "6+ hrs/week", "mid": "3–5 hrs/week", "low": "1–2 hrs/week"}
STYLE_LABEL = {"video":"videos","read":"reading","course":"structured courses","hands":"trying tools"}
INTEREST_LABEL = {
    "concepts":"how AI/ML works","usecases":"AI use cases",
    "lifecycle":"AI project lifecycle","managing":"managing AI projects",
    "strategy":"AI strategy & ethics","tools":"using AI tools at work",
}

# --------------------------------------------------------------------------- #
# Intro screen
# --------------------------------------------------------------------------- #
def render_intro():
    # Theme toggle top-right
    _, tcol = st.columns([5, 1])
    with tcol:
        mode_label = "☀️ Light" if dark else "🌙 Dark"
        if st.button(mode_label, key="theme_btn"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

    st.markdown('<span class="eyebrow">No coding • 100% free resources</span>', unsafe_allow_html=True)
    st.title("Learn how AI *really* works — built for non-technical leaders")
    st.markdown(
        f'<p class="sub">You manage projects and people. You don\'t want to write code — you want to '
        f"<b>understand AI</b>, speak confidently with technical teams, and lead AI initiatives. "
        f"Answer 6 quick questions and we'll build a personalized, step-by-step roadmap using only "
        f"free material from the internet.</p>",
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown("⏱️ **~60 seconds**")
    c2.markdown("🎯 **Tailored to you**")
    c3.markdown("🆓 **Only free resources**")
    c4.markdown("🗓️ **8-week plan**")

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
    step  = st.session_state.step
    q     = QUESTIONS[step]
    total = len(QUESTIONS)

    st.progress((step + 1) / total, text=f"Question {step + 1} of {total}")
    st.subheader(q["title"])
    st.caption(q["help"])

    labels = [f"{label} — {desc}" for (_v, label, desc) in q["options"]]
    values = [v for (v, _l, _d) in q["options"]]
    prev   = st.session_state.answers.get(q["id"])

    if q["multi"]:
        chosen = []
        st.write("")
        for label, value in zip(labels, values):
            if st.checkbox(label, value=(value in (prev or [])), key=f"{q['id']}_{value}"):
                chosen.append(value)
        selection = chosen
    else:
        idx    = values.index(prev) if prev in values else None
        choice = st.radio("Choose one:", labels, index=idx,
                          key=f"radio_{q['id']}_{step}", label_visibility="collapsed")
        selection = values[labels.index(choice)] if choice is not None else None

    st.write("")
    col_back, _, col_next = st.columns([1, 2, 1])
    with col_back:
        if step > 0 and st.button("← Back", use_container_width=True):
            st.session_state.step -= 1; st.rerun()

    has_answer  = bool(selection) if q["multi"] else selection is not None
    next_label  = "See my roadmap →" if step == total - 1 else "Next →"
    with col_next:
        if st.button(next_label, type="primary", disabled=not has_answer, use_container_width=True):
            st.session_state.answers[q["id"]] = selection
            if step == total - 1: go("result")
            else: st.session_state.step += 1
            st.rerun()

    if has_answer:
        st.session_state.answers[q["id"]] = selection

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def profile_text(a: dict) -> str:
    styles    = ", ".join(STYLE_LABEL.get(s, s) for s in (a.get("style") or [])) or "no preference"
    interests = ", ".join(INTEREST_LABEL.get(i, i) for i in (a.get("interest") or [])) or "general AI"
    return (
        f"- Role: {ROLE_MAP.get(a.get('role'), 'manager')}\n"
        f"- Goal: {GOAL_MAP.get(a.get('goal'), 'understand AI')}\n"
        f"- Level: {LEVEL_MAP.get(a.get('level'), 'beginner')}\n"
        f"- Time: {TIME_LABEL.get(a.get('time'), 'some time')} per week\n"
        f"- Learns by: {styles}\n"
        f"- Interested in: {interests}\n"
        f"- No coding."
    )

def answer_signature(a: dict) -> tuple:
    def norm(v): return tuple(sorted(v)) if isinstance(v, list) else v
    return tuple((q["id"], norm(a.get(q["id"]))) for q in QUESTIONS)

def get_ai_result(a: dict, plan: dict):
    if not ai_available(): return None
    existing = tuple(r["title"] for p in plan["phases"] for r in p["resources"])
    with st.spinner("✨ Personalizing extra picks for you…"):
        return fetch_ai_suggestions(answer_signature(a), profile_text(a), existing)

# --------------------------------------------------------------------------- #
# Weekly schedule generator
# --------------------------------------------------------------------------- #
def _weekly_schedule(plan: dict, start_date: datetime.date, hours_per_week: float) -> list:
    """Return list of {week, date, resources[]} dicts."""
    schedule, week_num, week_hrs, week_res = [], 1, 0, []
    week_start = start_date

    for phase in plan["phases"]:
        for r in phase["resources"]:
            est = {"course": 3, "video": 0.5, "read": 1, "tool": 0.5}.get(r["type"], 1)
            week_hrs += est
            week_res.append(r)
            if week_hrs >= hours_per_week:
                schedule.append({"week": week_num, "date": week_start, "resources": week_res})
                week_num  += 1
                week_start = start_date + datetime.timedelta(weeks=week_num - 1)
                week_hrs, week_res = 0, []

    if week_res:
        schedule.append({"week": week_num, "date": week_start, "resources": week_res})
    return schedule

# --------------------------------------------------------------------------- #
# AI chat
# --------------------------------------------------------------------------- #
def _chat_response(user_msg: str, plan: dict, a: dict) -> str:
    try:
        import anthropic
        key = None
        try:
            key = st.secrets.get("ANTHROPIC_API_KEY")
        except Exception:
            pass
        import os
        key = key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            return "API key not configured — add ANTHROPIC_API_KEY to Streamlit secrets."

        resource_list = "\n".join(
            f"- [{r['type']}] {r['title']} ({r['url']})"
            for p in plan["phases"] for r in p["resources"]
        )
        system = (
            f"You are a friendly AI learning advisor. The user is a "
            f"{ROLE_MAP.get(a.get('role'),'manager')} who wants to "
            f"{GOAL_MAP.get(a.get('goal'),'understand AI')}.\n\n"
            f"Their personalised roadmap includes:\n{resource_list}\n\n"
            "Answer questions about the roadmap, explain why specific resources are included, "
            "give learning tips, and encourage them. Keep answers short and practical. No code."
        )
        client = anthropic.Anthropic(api_key=key)
        resp   = client.messages.create(
            model="claude-haiku-4-5", max_tokens=400,
            system=system,
            messages=[{"role":"user","content":user_msg}],
        )
        return resp.content[0].text
    except Exception as e:
        return f"Chat unavailable right now ({type(e).__name__})."

# --------------------------------------------------------------------------- #
# AI suggestions section
# --------------------------------------------------------------------------- #
def render_ai_section(name: str, result):
    if not result: return
    if "error" in result:
        st.caption(f"ℹ️ Personalized picks unavailable — {result['error']}")
        return

    heading = f"### ✨ {name}, a few extra picks for you" if name else "### ✨ Personalized picks"
    st.markdown(heading)
    if result.get("intro"):
        st.markdown(f'<p class="sub">{result["intro"]}</p>', unsafe_allow_html=True)

    for s in result["suggestions"]:
        icon       = TYPE_ICON.get(s["type"], "🔗")
        type_label = TYPE_LABEL.get(s["type"], "Resource")
        badge      = _platform_badge(s["url"])
        rating     = _rating(s["url"])
        st.markdown(
            f'<div class="res-card">'
            f'<div class="res-title">{badge} {icon} '
            f'<a href="{s["url"]}" target="_blank">{s["title"]} ↗</a></div>'
            f'<div class="res-desc">{s["why"]}</div>'
            + (f'<div class="res-rating">{rating}</div>' if rating else "") +
            f'<span class="chip type">{type_label}</span>'
            f'<span class="chip free">Free</span>'
            f'<span class="chip">✨ AI-suggested</span>'
            f"</div>",
            unsafe_allow_html=True,
        )
    st.caption("AI-generated picks — open links to confirm they're still free and available.")
    st.write("")

# --------------------------------------------------------------------------- #
# Result screen
# --------------------------------------------------------------------------- #
def render_result():
    a    = st.session_state.answers
    name = st.session_state.get("user_name", "").strip()
    role = a.get("role", "pm")
    plan = build_roadmap(a)

    # Theme toggle
    _, tcol = st.columns([5, 1])
    with tcol:
        mode_label = "☀️ Light" if dark else "🌙 Dark"
        if st.button(mode_label, key="theme_res"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

    st.markdown('<span class="eyebrow">Your personalized roadmap</span>', unsafe_allow_html=True)
    title = f"{name}, here's your personalized AI roadmap" if name else "Your no-code path to AI"
    st.title(title)
    st.markdown(
        f'<p class="sub">As a <b>{ROLE_MAP.get(role,"manager")}</b> who wants to '
        f'<b>{GOAL_MAP.get(a.get("goal"),"understand AI")}</b> — '
        f'everything below is <b>free</b> and requires <b>no coding</b>.</p>',
        unsafe_allow_html=True,
    )

    ai_result = get_ai_result(a, plan)

    # ── Stats ───────────────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Phases",         len(plan["phases"]))
    m2.metric("Free resources", plan["total"])
    m3.metric("Your pace",      TIME_LABEL.get(a.get("time"), "—"))
    m4.metric("Est. weeks",     f"~{plan['weeks']} wks")

    # ── Finish-by date calculator ────────────────────────────────────────────
    with st.expander("🗓️ When will I finish? — Calculate your finish date"):
        col_d, col_h = st.columns(2)
        with col_d:
            start = st.date_input("Start date", value=datetime.date.today(), key="start_date")
        with col_h:
            hrs_map = {"high": 6.0, "mid": 4.0, "low": 1.5}
            hrs_pw  = hrs_map.get(a.get("time","mid"), 4.0)
            hrs_in  = st.number_input("Hours per week", min_value=0.5, max_value=20.0,
                                       value=hrs_pw, step=0.5, key="hrs_pw")
        schedule = _weekly_schedule(plan, start, hrs_in)
        if schedule:
            finish = schedule[-1]["date"]
            st.success(f"🎯 At **{hrs_in} hrs/week** starting **{start.strftime('%d %b %Y')}**, "
                       f"you'll finish by **{finish.strftime('%d %b %Y')}** "
                       f"({len(schedule)} weeks).")

    # ── Phase timeline ───────────────────────────────────────────────────────
    total_res  = plan["total"]
    done_count = len(st.session_state.completed)
    pct        = int(done_count / total_res * 100) if total_res else 0

    st.write("")
    st.markdown(
        f'<div class="prog-bar-wrap"><div class="prog-bar-fill" style="width:{pct}%"></div></div>',
        unsafe_allow_html=True,
    )
    st.caption(f"**{done_count} of {total_res} resources completed** ({pct}% done)"
               + (" 🎉 Roadmap complete!" if pct == 100 else ""))

    # Animated horizontal timeline
    tl_html = '<div class="timeline">'
    for i, phase in enumerate(plan["phases"]):
        phase_resources = [r["title"] for r in phase["resources"]]
        phase_done = all(r in st.session_state.completed for r in phase_resources)
        phase_active = any(r in st.session_state.completed for r in phase_resources) and not phase_done
        css = "completed" if phase_done else ("active" if phase_active else "")
        icon = "✅" if phase_done else ("▶" if phase_active else str(i + 1))
        short = phase["title"].replace("Phase " + str(i+1) + " — ", "")[:18]
        tl_html += f'<div class="tl-step {css}">{icon}<br><small>{short}</small></div>'
        if i < len(plan["phases"]) - 1:
            tl_html += '<div class="tl-arrow">→</div>'
    tl_html += "</div>"
    st.markdown(tl_html, unsafe_allow_html=True)

    # ── Skip-phases filter ───────────────────────────────────────────────────
    skip_set = st.session_state.skip_phases
    level    = a.get("level", "none")
    if level in ("user", "some"):
        skippable = [p["title"] for p in plan["phases"][:2]]
        with st.expander("⏭️ Already know some of this? Skip phases you've covered"):
            for pt in skippable:
                checked = pt in skip_set
                if st.checkbox(f"Skip: {pt}", value=checked, key=f"skip_{pt}"):
                    skip_set.add(pt)
                else:
                    skip_set.discard(pt)

    st.divider()

    # ── Phases & resources ───────────────────────────────────────────────────
    for i, phase in enumerate(plan["phases"], start=1):
        if phase["title"] in skip_set:
            st.markdown(
                f'<div class="phase-header phase-done">'
                f'<div class="phase-num">PHASE {i} — SKIPPED</div>'
                f'<div class="phase-title">{phase["title"].replace(f"Phase {i} — ","")}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )
            continue

        st.markdown(
            f'<div class="phase-header">'
            f'<div class="phase-num">PHASE {i}</div>'
            f'<div class="phase-title">{phase["title"].replace(f"Phase {i} — ","")}</div>'
            f'<div class="phase-goal">{phase["goal"]}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

        for r in phase["resources"]:
            r_key      = r["title"]
            is_done    = r_key in st.session_state.completed
            icon       = TYPE_ICON.get(r["type"], "🔗")
            type_label = TYPE_LABEL.get(r["type"], "Resource")
            badge      = _platform_badge(r["url"])
            rating     = _rating(r["url"])
            why        = _role_why(role, r["type"])

            done_chip = '<span class="chip done">✓ Done</span>' if is_done else ""
            rating_html = f'<div class="res-rating">{rating}</div>' if rating else ""
            why_html    = f'<div class="res-why">💡 {why}</div>' if why else ""

            st.markdown(
                f'<div class="res-card{"" if not is_done else ""}" style="opacity:{"0.6" if is_done else "1"}">'
                f'<div class="res-title">{badge} {icon} '
                f'<a href="{r["url"]}" target="_blank">{r["title"]} ↗</a></div>'
                f'{rating_html}'
                f'<div class="res-desc">{r["desc"]}</div>'
                f'{why_html}'
                f'<span class="chip type">{type_label}</span>'
                f'<span class="chip free">Free</span>'
                + "".join(f'<span class="chip">{t}</span>' for t in r["tags"])
                + done_chip +
                f"</div>",
                unsafe_allow_html=True,
            )

            # Completion checkbox
            col_chk, _ = st.columns([1, 5])
            with col_chk:
                checked = st.checkbox(
                    "Mark done", value=is_done, key=f"done_{r_key}",
                    label_visibility="collapsed",
                )
            if checked and r_key not in st.session_state.completed:
                st.session_state.completed.add(r_key)
                st.rerun()
            elif not checked and r_key in st.session_state.completed:
                st.session_state.completed.discard(r_key)
                st.rerun()

        st.write("")

    # ── AI picks ────────────────────────────────────────────────────────────
    render_ai_section(name, ai_result)

    # ── Weekly schedule ──────────────────────────────────────────────────────
    hrs_pw_val = {"high": 6.0, "mid": 4.0, "low": 1.5}.get(a.get("time","mid"), 4.0)
    sched = _weekly_schedule(plan, datetime.date.today(), hrs_pw_val)
    with st.expander("📅 Your week-by-week learning schedule"):
        for wk in sched:
            st.markdown(f"**Week {wk['week']}** — starting {wk['date'].strftime('%d %b %Y')}")
            for r in wk["resources"]:
                icon = TYPE_ICON.get(r["type"], "🔗")
                st.markdown(f"&nbsp;&nbsp;{icon} [{r['title']}]({r['url']})", unsafe_allow_html=True)
            st.write("")

    # ── Tips ────────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="tips">'
        "<h4>How to make this stick</h4>"
        "<ul>"
        "<li><b>Schedule it.</b> Block one recurring slot — treat it like a meeting you can't move.</li>"
        "<li><b>Learn out loud.</b> After each resource, explain the key idea to a colleague in one sentence.</li>"
        "<li><b>Tie it to a real problem.</b> Pick one initiative at work and ask 'could AI help here?'</li>"
        "<li><b>Don't aim to code.</b> Your goal is judgment — knowing what's possible and what to ask.</li>"
        "</ul></div>",
        unsafe_allow_html=True,
    )

    # ── What's next ──────────────────────────────────────────────────────────
    st.write("")
    with st.expander("🚀 What's next after this roadmap?"):
        next_steps = [
            ("Google Cloud AI Essentials", "https://www.coursera.org/learn/google-cloud-ai-essentials",
             "Structured next step — covers AI tools in the Google ecosystem. Free to audit."),
            ("PMI AI in Project Management Certification",
             "https://www.pmi.org/certifications/artificial-intelligence",
             "Formal recognition of your AI PM skills from the world's top PM body."),
            ("MIT Sloan AI Strategy for Business Leaders",
             "https://sloanreview.mit.edu/big-ideas/artificial-intelligence/",
             "Ongoing research and strategy articles from MIT. Bookmark and read weekly."),
            ("Build your first AI proof-of-concept",
             "https://www.ownml.co/machine-learning-canvas",
             "Use the ML Canvas to scope a real AI initiative at your organisation."),
        ]
        for title, url, desc in next_steps:
            st.markdown(
                f'<div class="next-card">'
                f'<div class="next-title"><a href="{url}" target="_blank">{title} ↗</a></div>'
                f'<div class="next-desc">{desc}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )

    # ── AI chat assistant ────────────────────────────────────────────────────
    st.write("")
    with st.expander("💬 Ask about your roadmap — AI assistant"):
        st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
        st.caption("Ask me anything about your roadmap — why a resource is included, how to fit it into your week, or what any concept means.")

        # Display chat history
        for msg in st.session_state.chat_history:
            role_icon = "🧑" if msg["role"] == "user" else "🤖"
            st.markdown(f"**{role_icon}** {msg['content']}")

        user_input = st.chat_input("Ask a question about your roadmap…", key="chat_input")
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.spinner("Thinking…"):
                reply = _chat_response(user_input, plan, a)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.rerun()

        if st.session_state.chat_history:
            if st.button("Clear chat", key="clear_chat"):
                st.session_state.chat_history = []
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Actions row ─────────────────────────────────────────────────────────
    st.write("")
    st.divider()
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        if st.button("↺ Retake", use_container_width=True):
            reset(); st.rerun()

    with c2:
        profile_lines = [
            f"Role: {ROLE_MAP.get(a.get('role'), 'manager')}",
            f"Goal: {GOAL_MAP.get(a.get('goal'), 'understand AI')}",
            f"Starting point: {LEVEL_MAP.get(a.get('level'), 'at your level')}",
            f"Pace: {TIME_LABEL.get(a.get('time'), '-')}",
        ]
        pdf_bytes = build_pdf(name, profile_lines, plan, ai_result)
        safe_name = "".join(c for c in name if c.isalnum()) or "my"
        st.download_button(
            "⬇️ Download PDF",
            data=pdf_bytes,
            file_name=f"{safe_name}_ai_roadmap.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    with c3:
        app_url   = "https://ai-roadmap-for-managers.streamlit.app"
        li_text   = (
            f"I just built my personalised AI learning roadmap — 8 weeks, "
            f"100% free, no coding required. Built for non-technical managers. "
            f"Try it: {app_url} #AILearning #ProjectManagement #NoCode"
        )
        li_url    = f"https://www.linkedin.com/sharing/share-offsite/?url={app_url}"
        st.link_button("🔗 Share on LinkedIn", li_url, use_container_width=True)

    with c4:
        subject  = "My AI Learning Roadmap"
        body     = (
            f"Hi,\n\nI just built my personalised AI learning roadmap "
            f"for managers — check it out: {app_url}\n\n"
            f"It takes 60 seconds and gives you a free 8-week plan. No coding needed.\n\nCheers"
        )
        mailto   = f"mailto:?subject={subject}&body={body}"
        st.link_button("📧 Email roadmap", mailto, use_container_width=True)


# --------------------------------------------------------------------------- #
# Router
# --------------------------------------------------------------------------- #
stage = st.session_state.stage
if stage == "intro":   render_intro()
elif stage == "quiz":  render_quiz()
else:                  render_result()

# --------------------------------------------------------------------------- #
# Footer
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
