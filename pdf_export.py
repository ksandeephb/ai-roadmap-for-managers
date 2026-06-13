"""
pdf_export.py
-------------
Clean, professional learning roadmap PDF using ReportLab.
"""

import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether,
)

# ── Author ───────────────────────────────────────────────────────────────────
AUTHOR_NAME     = "Sandeep Kumar"
AUTHOR_EMAIL    = "ksandeep.srm@gmail.com"
AUTHOR_LINKEDIN = "https://www.linkedin.com/in/sandeep-kumar-23b02445/"

# ── Palette ──────────────────────────────────────────────────────────────────
C_NAVY   = colors.HexColor("#1A2340")
C_INDIGO = colors.HexColor("#4F5FD4")
C_TEAL   = colors.HexColor("#2BB5A0")
C_AMBER  = colors.HexColor("#F0A500")
C_SLATE  = colors.HexColor("#F4F6FB")
C_WHITE  = colors.white
C_BODY   = colors.HexColor("#1E2433")
C_MUTED  = colors.HexColor("#6B7694")
C_LINK   = colors.HexColor("#3D52C4")
C_DIV    = colors.HexColor("#DDE2F0")
C_PHASE  = colors.HexColor("#EEF0FD")
C_AI_BG  = colors.HexColor("#F0FDFB")

PAGE_W, PAGE_H = A4
M          = 20 * mm   # margin
HEADER_H   = 44 * mm
FOOTER_H   = 18 * mm
CONTENT_W  = PAGE_W - 2 * M

# ── Unicode → latin-1 ────────────────────────────────────────────────────────
_R = {"\u2013":"-","\u2014":"-","\u2018":"'","\u2019":"'",
      "\u201c":'"',"\u201d":'"',"\u2022":"-","\u2192":"->",
      "\u2026":"...","\u00a0":" ","\u2013":"-"}

def _t(s):
    if not s: return ""
    for k, v in _R.items(): s = s.replace(k, v)
    return s.encode("latin-1", "ignore").decode("latin-1")

# ── Styles ────────────────────────────────────────────────────────────────────
def _styles():
    return {
        "label":       ParagraphStyle("label",       fontName="Helvetica-Bold",    fontSize=7,    textColor=C_TEAL,   leading=9,  spaceAfter=3,  letterSpacing=1.2),
        "profile_key": ParagraphStyle("profile_key", fontName="Helvetica-Bold",    fontSize=9,    textColor=C_BODY,   leading=13),
        "profile_val": ParagraphStyle("profile_val", fontName="Helvetica",         fontSize=9,    textColor=C_MUTED,  leading=13),
        "stat_n":      ParagraphStyle("stat_n",      fontName="Helvetica-Bold",    fontSize=20,   textColor=C_INDIGO, leading=24, alignment=TA_CENTER),
        "stat_l":      ParagraphStyle("stat_l",      fontName="Helvetica",         fontSize=7,    textColor=C_MUTED,  leading=9,  alignment=TA_CENTER),
        "ph_num":      ParagraphStyle("ph_num",      fontName="Helvetica-Bold",    fontSize=9,    textColor=C_WHITE,  leading=12, alignment=TA_CENTER),
        "ph_title":    ParagraphStyle("ph_title",    fontName="Helvetica-Bold",    fontSize=11,   textColor=C_NAVY,   leading=14),
        "ph_goal":     ParagraphStyle("ph_goal",     fontName="Helvetica-Oblique", fontSize=8.5,  textColor=C_MUTED,  leading=12),
        "r_title":     ParagraphStyle("r_title",     fontName="Helvetica-Bold",    fontSize=9.5,  textColor=C_BODY,   leading=13),
        "r_desc":      ParagraphStyle("r_desc",      fontName="Helvetica",         fontSize=8.5,  textColor=C_MUTED,  leading=12),
        "r_url":       ParagraphStyle("r_url",       fontName="Helvetica",         fontSize=7.5,  textColor=C_LINK,   leading=10),
        "r_tag":       ParagraphStyle("r_tag",       fontName="Helvetica-Bold",    fontSize=6.5,  textColor=C_AMBER,  leading=9),
        "ai_title":    ParagraphStyle("ai_title",    fontName="Helvetica-Bold",    fontSize=11,   textColor=C_TEAL,   leading=14),
        "ai_intro":    ParagraphStyle("ai_intro",    fontName="Helvetica-Oblique", fontSize=8.5,  textColor=C_MUTED,  leading=12),
        "tip":         ParagraphStyle("tip",         fontName="Helvetica-Oblique", fontSize=8.5,  textColor=C_MUTED,  leading=13),
    }

# ── Page decorator ────────────────────────────────────────────────────────────
class _Deco:
    def __init__(self, title, subtitle):
        self.title    = _t(title)
        self.subtitle = _t(subtitle)

    def __call__(self, canvas, doc):
        canvas.saveState()
        W, H = PAGE_W, PAGE_H

        # ── Header ────────────────────────────────────────────────────────────
        if doc.page == 1:
            # Navy band
            canvas.setFillColor(C_NAVY)
            canvas.rect(0, H - HEADER_H, W, HEADER_H, fill=1, stroke=0)
            # Teal pill tag
            canvas.setFillColor(C_TEAL)
            canvas.roundRect(M, H - 11*mm, 60*mm, 5.5*mm, 2.5, fill=1, stroke=0)
            canvas.setFont("Helvetica-Bold", 6.5)
            canvas.setFillColor(C_WHITE)
            canvas.drawString(M + 3*mm, H - 7.2*mm, "FREE  |  NO CODE  |  8 WEEKS")
            # Title
            canvas.setFont("Helvetica-Bold", 18)
            canvas.setFillColor(C_WHITE)
            canvas.drawString(M, H - 19*mm, self.title)
            # Subtitle
            canvas.setFont("Helvetica", 9)
            canvas.setFillColor(colors.HexColor("#9AAFD4"))
            canvas.drawString(M, H - 26*mm, self.subtitle)
            # Indigo accent line at bottom of header
            canvas.setFillColor(C_INDIGO)
            canvas.rect(0, H - HEADER_H - 2, W, 2, fill=1, stroke=0)
        else:
            # Slim top bar on subsequent pages
            canvas.setFillColor(C_INDIGO)
            canvas.rect(0, H - 6, W, 6, fill=1, stroke=0)
            canvas.setFont("Helvetica", 7.5)
            canvas.setFillColor(C_MUTED)
            canvas.drawString(M, H - 4.5*mm, self.title)

        # ── Footer ────────────────────────────────────────────────────────────
        fy = 12 * mm
        # Divider
        canvas.setStrokeColor(C_DIV)
        canvas.setLineWidth(0.5)
        canvas.line(M, fy + 6*mm, W - M, fy + 6*mm)

        # Author name — bold, dark
        canvas.setFont("Helvetica-Bold", 8.5)
        canvas.setFillColor(C_BODY)
        canvas.drawString(M, fy + 2.5*mm, _t(AUTHOR_NAME))

        # Email — muted, same line slightly right
        email_x = M + 38*mm
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(C_MUTED)
        canvas.drawString(email_x, fy + 2.5*mm, _t(AUTHOR_EMAIL))

        # LinkedIn — indigo, underlined, clickable
        li_x = W - M - 28*mm
        canvas.setFont("Helvetica-Bold", 8)
        canvas.setFillColor(C_INDIGO)
        canvas.drawString(li_x, fy + 2.5*mm, "LinkedIn Profile")
        lw = canvas.stringWidth("LinkedIn Profile", "Helvetica-Bold", 8)
        canvas.setStrokeColor(C_INDIGO)
        canvas.setLineWidth(0.5)
        canvas.line(li_x, fy + 1.8*mm, li_x + lw, fy + 1.8*mm)
        canvas.linkURL(AUTHOR_LINKEDIN,
                       (li_x, fy + 0.5*mm, li_x + lw + 1, fy + 4*mm), relative=0)

        # Page number — right aligned
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(C_MUTED)
        canvas.drawRightString(W - M, fy + 2.5*mm, f"Page {doc.page}")

        canvas.restoreState()

# ── Resource card ─────────────────────────────────────────────────────────────
def _res_card(s, title, desc, url, tags, bg=C_WHITE):
    """Single resource row: left indigo accent bar, title, desc, url, tags."""
    inner_w = CONTENT_W - 5*mm   # 5mm for the left accent bar column

    content_rows = [[Paragraph(_t(title), s["r_title"])]]
    if desc:
        content_rows.append([Paragraph(_t(desc), s["r_desc"])])
    # URL as clickable link
    url_p = Paragraph(
        f'<link href="{url}" color="#3D52C4"><u>{_t(url[:72])}{"..." if len(url) > 72 else ""}</u></link>',
        s["r_url"]
    )
    content_rows.append([url_p])
    # Tags
    tag_str = "   ·   ".join(_t(tg) for tg in tags if tg)
    content_rows.append([Paragraph(tag_str, s["r_tag"])])

    content_table = Table(
        content_rows,
        colWidths=[inner_w],
        style=TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), bg),
            ("TOPPADDING",    (0, 0), (-1,  0), 6),
            ("BOTTOMPADDING", (0,-1), (-1, -1), 6),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
            ("TOPPADDING",    (0, 1), (-1, -1), 2),
        ]),
    )

    # Wrap with left accent bar
    outer = Table(
        [[None, content_table]],
        colWidths=[4, inner_w],
        style=TableStyle([
            ("BACKGROUND",    (0, 0), (0, -1), C_INDIGO),
            ("BACKGROUND",    (1, 0), (1, -1), bg),
            ("TOPPADDING",    (0, 0), (-1,-1), 0),
            ("BOTTOMPADDING", (0, 0), (-1,-1), 0),
            ("LEFTPADDING",   (0, 0), (-1,-1), 0),
            ("RIGHTPADDING",  (0, 0), (-1,-1), 0),
        ]),
    )
    return KeepTogether([outer, Spacer(1, 2.5*mm)])

# ── Phase header ──────────────────────────────────────────────────────────────
def _phase_header(s, num, title, goal):
    badge = Table(
        [[Paragraph(str(num), s["ph_num"])]],
        colWidths=[8*mm], rowHeights=[8*mm],
        style=TableStyle([
            ("BACKGROUND", (0,0),(-1,-1), C_INDIGO),
            ("ALIGN",      (0,0),(-1,-1), "CENTER"),
            ("VALIGN",     (0,0),(-1,-1), "MIDDLE"),
        ])
    )
    text = Table(
        [[Paragraph(_t(title), s["ph_title"])],
         [Paragraph(_t(goal),  s["ph_goal"])]],
        colWidths=[CONTENT_W - 13*mm],
        style=TableStyle([
            ("TOPPADDING",    (0,0),(-1,-1), 1),
            ("BOTTOMPADDING", (0,0),(-1,-1), 1),
            ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ])
    )
    header = Table(
        [[badge, text]],
        colWidths=[12*mm, CONTENT_W - 12*mm],
        style=TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), C_PHASE),
            ("TOPPADDING",    (0,0),(-1,-1), 7),
            ("BOTTOMPADDING", (0,0),(-1,-1), 7),
            ("LEFTPADDING",   (0,0),(0, -1), 2),
            ("LEFTPADDING",   (1,0),(1, -1), 8),
            ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
            ("LINEBELOW",     (0,0),(-1,-1), 1.5, C_INDIGO),
        ])
    )
    return KeepTogether([header, Spacer(1, 2*mm)])

# ── Stats bar ─────────────────────────────────────────────────────────────────
def _stats_bar(s, phases, resources, pace, weeks):
    cw = CONTENT_W / 4
    data = [
        [Paragraph(str(phases),    s["stat_n"]),
         Paragraph(str(resources), s["stat_n"]),
         Paragraph(_t(pace),       s["stat_n"]),
         Paragraph(f"≤{weeks}",    s["stat_n"])],
        [Paragraph("PHASES",         s["stat_l"]),
         Paragraph("RESOURCES",      s["stat_l"]),
         Paragraph("PACE",           s["stat_l"]),
         Paragraph("WEEKS",          s["stat_l"])],
    ]
    return Table(data, colWidths=[cw]*4, style=TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), C_SLATE),
        ("TOPPADDING",    (0,0),(-1,-1), 8),
        ("BOTTOMPADDING", (0,0),(-1,-1), 8),
        ("ALIGN",         (0,0),(-1,-1), "CENTER"),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("LINEAFTER",     (0,0),(2, -1), 0.5, C_DIV),
        ("ROUNDEDCORNERS",(0,0),(-1,-1), [3]),
    ]))

# ── Profile card ──────────────────────────────────────────────────────────────
def _profile_card(s, lines):
    rows = []
    for line in lines:
        if ":" in line:
            key, _, val = line.partition(":")
            rows.append([
                Paragraph(_t(key.strip()) + ":", s["profile_key"]),
                Paragraph(_t(val.strip()),        s["profile_val"]),
            ])
        else:
            rows.append([Paragraph(_t(line), s["profile_val"]), Paragraph("", s["profile_val"])])

    return Table(rows, colWidths=[38*mm, CONTENT_W - 40*mm], style=TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), C_SLATE),
        ("TOPPADDING",    (0,0),(-1,-1), 3),
        ("BOTTOMPADDING", (0,0),(-1,-1), 3),
        ("LEFTPADDING",   (0,0),(-1,-1), 10),
        ("RIGHTPADDING",  (0,0),(-1,-1), 8),
        ("LINEBEFORE",    (0,0),(0, -1), 3, C_TEAL),
    ]))

# ── Tip box ───────────────────────────────────────────────────────────────────
def _tip_box(s):
    text = _t(
        "Schedule a recurring learning slot each week. After each resource, "
        "explain the key idea to a colleague in one sentence. Tie what you "
        "learn to a real project at work. Your goal is judgment and confidence "
        "- not code."
    )
    return Table(
        [[Paragraph(text, s["tip"])]],
        colWidths=[CONTENT_W],
        style=TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), C_SLATE),
            ("TOPPADDING",    (0,0),(-1,-1), 10),
            ("BOTTOMPADDING", (0,0),(-1,-1), 10),
            ("LEFTPADDING",   (0,0),(-1,-1), 12),
            ("RIGHTPADDING",  (0,0),(-1,-1), 12),
            ("LINEBEFORE",    (0,0),(0, -1), 3, C_AMBER),
        ])
    )

# ── Main builder ──────────────────────────────────────────────────────────────
def build_pdf(name, profile_lines, plan, ai_result=None) -> bytes:
    buf = io.BytesIO()
    s   = _styles()

    title    = _t(f"{name}'s AI Learning Roadmap" if name else "Your AI Learning Roadmap")
    subtitle = _t("A focused 8-week path to leading AI projects - free resources only")

    deco = _Deco(title, subtitle)

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=M, rightMargin=M,
        topMargin=HEADER_H + 6*mm,
        bottomMargin=FOOTER_H + 4*mm,
    )

    # Detect pace
    raw = " ".join(profile_lines).lower()
    pace = "6+ hrs/wk" if ("6+" in raw or "high" in raw) else \
           "3-5 hrs/wk" if ("3" in raw or "mid" in raw) else "1-2 hrs/wk"

    story = []

    # ── Profile ───────────────────────────────────────────────────────────────
    story.append(Paragraph("YOUR PROFILE", s["label"]))
    story.append(Spacer(1, 1*mm))
    story.append(_profile_card(s, profile_lines))
    story.append(Spacer(1, 5*mm))

    # ── Stats ─────────────────────────────────────────────────────────────────
    story.append(_stats_bar(s, len(plan["phases"]), plan["total"], pace, plan["weeks"]))
    story.append(Spacer(1, 6*mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_DIV, spaceAfter=5*mm))

    # ── Phases ────────────────────────────────────────────────────────────────
    story.append(Paragraph("YOUR LEARNING ROADMAP", s["label"]))
    story.append(Spacer(1, 3*mm))

    alt = False
    for i, phase in enumerate(plan["phases"], 1):
        story.append(_phase_header(s, i, phase["title"], phase["goal"]))
        for r in phase["resources"]:
            tags = [r.get("type", "read").upper(), "FREE"] + [
                tg for tg in r.get("tags", []) if tg not in ("Free",)
            ]
            story.append(_res_card(
                s, r["title"], r.get("desc", ""), r["url"],
                tags=tags, bg=C_SLATE if alt else C_WHITE,
            ))
            alt = not alt
        story.append(Spacer(1, 5*mm))

    # ── AI picks ──────────────────────────────────────────────────────────────
    if ai_result and "error" not in ai_result and ai_result.get("suggestions"):
        story.append(HRFlowable(width="100%", thickness=0.5, color=C_DIV, spaceAfter=4*mm))
        story.append(Paragraph("AI-CURATED PICKS FOR YOU", s["label"]))
        story.append(Paragraph("Personalised reads based on your answers", s["ai_title"]))
        story.append(Spacer(1, 1*mm))
        if ai_result.get("intro"):
            story.append(Paragraph(_t(ai_result["intro"]), s["ai_intro"]))
        story.append(Spacer(1, 3*mm))
        for sug in ai_result["suggestions"]:
            story.append(_res_card(
                s, sug["title"], sug.get("why", ""), sug["url"],
                tags=["READ", "FREE", "AI-PICKED"], bg=C_AI_BG,
            ))
        story.append(Spacer(1, 4*mm))

    # ── Tip ───────────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_DIV, spaceAfter=4*mm))
    story.append(_tip_box(s))

    doc.build(story, onFirstPage=deco, onLaterPages=deco)
    return buf.getvalue()
