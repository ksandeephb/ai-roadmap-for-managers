"""
pdf_export.py
-------------
Industry-standard learning roadmap PDF using ReportLab.
SimpleDocTemplate + canvas callbacks for the header/footer.
"""

import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether,
)
from reportlab.platypus.flowables import Flowable

# ── Author ───────────────────────────────────────────────────────────────────
AUTHOR_NAME     = "Sandeep Kumar"
AUTHOR_EMAIL    = "ksandeep.srm@gmail.com"
AUTHOR_LINKEDIN = "https://www.linkedin.com/in/sandeep-kumar-23b02445/"

# ── Palette ──────────────────────────────────────────────────────────────────
C_NAVY    = colors.HexColor("#1A2340")
C_INDIGO  = colors.HexColor("#4F5FD4")
C_TEAL    = colors.HexColor("#2BB5A0")
C_AMBER   = colors.HexColor("#F0A500")
C_SLATE   = colors.HexColor("#F4F6FB")
C_PHASE   = colors.HexColor("#ECEFFE")
C_WHITE   = colors.white
C_BODY    = colors.HexColor("#1E2433")
C_MUTED   = colors.HexColor("#6B7694")
C_LINK    = colors.HexColor("#4F5FD4")
C_DIV     = colors.HexColor("#DDE2F0")
C_AI_BG   = colors.HexColor("#F0FDFB")

PAGE_W, PAGE_H = A4
MARGIN      = 18 * mm
HEADER_H    = 48 * mm   # navy band height on page 1
FOOTER_H    = 16 * mm   # space reserved at bottom

# Unicode → latin-1 safe
_REP = {
    "\u2013":"-","\u2014":"-","\u2018":"'","\u2019":"'",
    "\u201c":'"',"\u201d":'"',"\u2022":"-","\u2192":"->",
    "\u2026":"...","\u00a0":" ",
}
def _c(s):
    if not s: return ""
    for k,v in _REP.items(): s=s.replace(k,v)
    return s.encode("latin-1","ignore").decode("latin-1")


# ── Styles ───────────────────────────────────────────────────────────────────
def _S():
    return {
        "eyebrow": ParagraphStyle("eyebrow",
            fontName="Helvetica-Bold", fontSize=7.5, textColor=C_TEAL,
            leading=10, spaceBefore=8, spaceAfter=2, letterSpacing=1.5),
        "section_title": ParagraphStyle("section_title",
            fontName="Helvetica-Bold", fontSize=14, textColor=C_NAVY,
            leading=18, spaceBefore=4, spaceAfter=4),
        "profile_item": ParagraphStyle("profile_item",
            fontName="Helvetica", fontSize=9.5, textColor=C_BODY, leading=14),
        "stat_val": ParagraphStyle("stat_val",
            fontName="Helvetica-Bold", fontSize=18, textColor=C_INDIGO,
            leading=22, alignment=TA_CENTER),
        "stat_lbl": ParagraphStyle("stat_lbl",
            fontName="Helvetica", fontSize=7, textColor=C_MUTED,
            leading=9, alignment=TA_CENTER),
        "phase_num": ParagraphStyle("phase_num",
            fontName="Helvetica-Bold", fontSize=10, textColor=C_WHITE,
            leading=13, alignment=TA_CENTER),
        "phase_title": ParagraphStyle("phase_title",
            fontName="Helvetica-Bold", fontSize=12, textColor=C_NAVY, leading=15),
        "phase_goal": ParagraphStyle("phase_goal",
            fontName="Helvetica-Oblique", fontSize=8.5, textColor=C_MUTED, leading=12),
        "res_title": ParagraphStyle("res_title",
            fontName="Helvetica-Bold", fontSize=10, textColor=C_BODY, leading=13),
        "res_desc": ParagraphStyle("res_desc",
            fontName="Helvetica", fontSize=8.5, textColor=C_MUTED, leading=12),
        "res_link": ParagraphStyle("res_link",
            fontName="Helvetica", fontSize=8, textColor=C_LINK, leading=11),
        "res_tag": ParagraphStyle("res_tag",
            fontName="Helvetica-Bold", fontSize=7, textColor=C_AMBER, leading=10),
        "ai_label": ParagraphStyle("ai_label",
            fontName="Helvetica-Bold", fontSize=7.5, textColor=C_TEAL,
            leading=10, letterSpacing=1.5),
        "ai_title": ParagraphStyle("ai_title",
            fontName="Helvetica-Bold", fontSize=13, textColor=C_TEAL, leading=16),
        "ai_intro": ParagraphStyle("ai_intro",
            fontName="Helvetica-Oblique", fontSize=9, textColor=C_MUTED, leading=13),
        "tip": ParagraphStyle("tip",
            fontName="Helvetica-Oblique", fontSize=8.5, textColor=C_MUTED, leading=13),
    }


# ── Header/footer drawn on every page ────────────────────────────────────────
class _PageDeco:
    def __init__(self, title, subtitle):
        self.title    = _c(title)
        self.subtitle = _c(subtitle)

    def __call__(self, canvas, doc):
        canvas.saveState()
        w, h = PAGE_W, PAGE_H

        if doc.page == 1:
            # Navy band
            canvas.setFillColor(C_NAVY)
            canvas.rect(0, h - HEADER_H, w, HEADER_H, fill=1, stroke=0)
            # Indigo bottom strip of band
            canvas.setFillColor(C_INDIGO)
            canvas.rect(0, h - HEADER_H - 3, w, 3, fill=1, stroke=0)
            # Title
            canvas.setFont("Helvetica-Bold", 19)
            canvas.setFillColor(colors.white)
            canvas.drawString(MARGIN, h - 20*mm, self.title)
            # Subtitle
            canvas.setFont("Helvetica", 9)
            canvas.setFillColor(colors.HexColor("#B8C4E8"))
            canvas.drawString(MARGIN, h - 28*mm, self.subtitle)
            # Teal eyebrow tag
            canvas.setFillColor(C_TEAL)
            canvas.roundRect(MARGIN, h - 13*mm, 54*mm, 6*mm, 3, fill=1, stroke=0)
            canvas.setFont("Helvetica-Bold", 7)
            canvas.setFillColor(colors.white)
            canvas.drawString(MARGIN + 3*mm, h - 9.5*mm, "PERSONALIZED AI LEARNING ROADMAP")
        else:
            # Slim indigo top bar on continuation pages
            canvas.setFillColor(C_INDIGO)
            canvas.rect(0, h - 5, w, 5, fill=1, stroke=0)

        # ── Footer ───────────────────────────────────────────────────────────
        fy = FOOTER_H - 4*mm
        # Divider line
        canvas.setStrokeColor(C_DIV)
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN, fy + 9*mm, w - MARGIN, fy + 9*mm)

        # Left: name (bold, dark)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.setFillColor(C_BODY)
        canvas.drawString(MARGIN, fy + 5*mm, _c(AUTHOR_NAME))

        # Middle-left: email
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(C_MUTED)
        canvas.drawString(MARGIN, fy + 1.5*mm, _c(AUTHOR_EMAIL))

        # Middle-right: LinkedIn as clickable indigo link
        li_x = MARGIN + 70*mm
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(C_LINK)
        canvas.drawString(li_x, fy + 5*mm, "LinkedIn")
        # Underline
        li_w = canvas.stringWidth("LinkedIn", "Helvetica", 7.5)
        canvas.setStrokeColor(C_LINK)
        canvas.setLineWidth(0.4)
        canvas.line(li_x, fy + 4.2*mm, li_x + li_w, fy + 4.2*mm)
        # Clickable area
        canvas.linkURL(
            AUTHOR_LINKEDIN,
            (li_x, fy + 1*mm, li_x + li_w + 2, fy + 7*mm),
            relative=0,
        )
        # LinkedIn URL in muted below
        canvas.setFont("Helvetica", 6.5)
        canvas.setFillColor(C_MUTED)
        canvas.drawString(li_x, fy + 1.5*mm, _c(AUTHOR_LINKEDIN[:45]))

        # Right: page number
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(C_MUTED)
        canvas.drawRightString(w - MARGIN, fy + 5*mm, f"Page {doc.page}")

        canvas.restoreState()


# ── Resource card ─────────────────────────────────────────────────────────────
def _res_card(s, title, desc, url, tags, bg=C_WHITE):
    cw = PAGE_W - 2*MARGIN - 6*mm
    rows = [[Paragraph(_c(title), s["res_title"])]]
    if desc:
        rows.append([Paragraph(_c(desc), s["res_desc"])])
    rows.append([Paragraph(
        f'<link href="{url}" color="#4F5FD4"><u>{_c(url)}</u></link>',
        s["res_link"])])
    rows.append([Paragraph("  |  ".join(t.upper() for t in tags if t), s["res_tag"])])

    t = Table(rows, colWidths=[cw], style=TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), bg),
        ("TOPPADDING",   (0,0),(-1, 0), 6),
        ("BOTTOMPADDING",(0,-1),(-1,-1),5),
        ("LEFTPADDING",  (0,0),(-1,-1), 8),
        ("RIGHTPADDING", (0,0),(-1,-1), 8),
        ("LINEAFTER",    (0,0),(0,-1),  3, C_INDIGO),
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[bg]),
    ]))
    return KeepTogether([t, Spacer(1, 2.5*mm)])


# ── Phase header ──────────────────────────────────────────────────────────────
def _phase_hdr(s, num, title, goal):
    badge = Table([[Paragraph(str(num), s["phase_num"])]],
        colWidths=[7*mm], rowHeights=[7*mm],
        style=TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),C_INDIGO),
            ("ALIGN",(0,0),(-1,-1),"CENTER"),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ]))
    text = Table([
        [Paragraph(_c(title), s["phase_title"])],
        [Paragraph(_c(f"Goal: {goal}"), s["phase_goal"])],
    ], colWidths=[PAGE_W - 2*MARGIN - 14*mm],
    style=TableStyle([
        ("TOPPADDING",(0,0),(-1,-1),1),("BOTTOMPADDING",(0,0),(-1,-1),1),
        ("LEFTPADDING",(0,0),(-1,-1),0),
    ]))
    hdr = Table([[badge, text]],
        colWidths=[10*mm, PAGE_W - 2*MARGIN - 10*mm],
        style=TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),C_PHASE),
            ("TOPPADDING",(0,0),(-1,-1),6),
            ("BOTTOMPADDING",(0,0),(-1,-1),6),
            ("LEFTPADDING",(0,0),(0,-1),4),
            ("LEFTPADDING",(1,0),(1,-1),6),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("LINEBELOW",(0,0),(-1,-1),2,C_INDIGO),
        ]))
    return KeepTogether([hdr, Spacer(1, 2*mm)])


# ── Stats bar ─────────────────────────────────────────────────────────────────
def _stats(s, phases, resources, pace, weeks):
    cw = (PAGE_W - 2*MARGIN) / 4
    data = [
        [Paragraph(str(phases),s["stat_val"]),
         Paragraph(str(resources),s["stat_val"]),
         Paragraph(_c(pace),s["stat_val"]),
         Paragraph(f"~{weeks} wks",s["stat_val"])],
        [Paragraph("PHASES",s["stat_lbl"]),
         Paragraph("FREE RESOURCES",s["stat_lbl"]),
         Paragraph("YOUR PACE",s["stat_lbl"]),
         Paragraph("EST. DURATION",s["stat_lbl"])],
    ]
    return Table(data, colWidths=[cw]*4, style=TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),C_SLATE),
        ("TOPPADDING",(0,0),(-1,-1),7),
        ("BOTTOMPADDING",(0,0),(-1,-1),7),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("LINEAFTER",(0,0),(2,-1),0.5,C_DIV),
    ]))


# ── Profile block ─────────────────────────────────────────────────────────────
def _profile(s, lines):
    rows = [[Paragraph(_c(f"  {l}"), s["profile_item"])] for l in lines]
    return Table(rows, colWidths=[PAGE_W - 2*MARGIN], style=TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),C_SLATE),
        ("TOPPADDING",(0,0),(-1,-1),3),
        ("BOTTOMPADDING",(0,0),(-1,-1),3),
        ("LEFTPADDING",(0,0),(-1,-1),8),
        ("LINEBEFORE",(0,0),(0,-1),3,C_TEAL),
    ]))


# ── Main ──────────────────────────────────────────────────────────────────────
def build_pdf(name, profile_lines, plan, ai_result=None) -> bytes:
    buf  = io.BytesIO()
    s    = _S()

    title    = _c(f"{name}, here's your personalized AI roadmap" if name
                  else "Your personalized AI roadmap")
    subtitle = _c("A no-code path to understanding AI  -  built from free resources only")

    deco = _PageDeco(title, subtitle)

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=HEADER_H + 8*mm,   # clear the navy band
        bottomMargin=FOOTER_H + 4*mm,
    )

    # Detect pace from profile_lines string
    pace_raw = " ".join(profile_lines).lower()
    if "6+" in pace_raw or "high" in pace_raw:
        pace = "6+ hrs/wk"
    elif "3" in pace_raw or "mid" in pace_raw:
        pace = "3-5 hrs/wk"
    else:
        pace = "1-2 hrs/wk"

    story = []

    # Profile
    story.append(Paragraph("YOUR PROFILE", s["eyebrow"]))
    story.append(Spacer(1, 1*mm))
    story.append(_profile(s, profile_lines))
    story.append(Spacer(1, 5*mm))

    # Stats
    story.append(_stats(s, len(plan["phases"]), plan["total"], pace, plan["weeks"]))
    story.append(Spacer(1, 5*mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_DIV, spaceAfter=5*mm))

    # Phases
    story.append(Paragraph("LEARNING PHASES", s["eyebrow"]))
    story.append(Spacer(1, 2*mm))
    alt = False
    for i, phase in enumerate(plan["phases"], 1):
        story.append(_phase_hdr(s, i, phase["title"], phase["goal"]))
        for r in phase["resources"]:
            story.append(_res_card(
                s, r["title"], r.get("desc",""), r["url"],
                tags=[r.get("type","read").upper(), "FREE"] + r.get("tags",[]),
                bg=C_SLATE if alt else C_WHITE,
            ))
            alt = not alt
        story.append(Spacer(1, 4*mm))

    # AI picks
    if ai_result and "error" not in ai_result and ai_result.get("suggestions"):
        story.append(HRFlowable(width="100%", thickness=0.5, color=C_DIV, spaceAfter=3*mm))
        story.append(Paragraph("PERSONALIZED PICKS", s["eyebrow"]))
        story.append(Paragraph("AI-Suggested Reads For You", s["ai_title"]))
        story.append(Spacer(1, 1*mm))
        if ai_result.get("intro"):
            story.append(Paragraph(_c(ai_result["intro"]), s["ai_intro"]))
        story.append(Spacer(1, 2*mm))
        for sug in ai_result["suggestions"]:
            story.append(_res_card(
                s, sug["title"], sug.get("why",""), sug["url"],
                tags=["READ","FREE","AI-SUGGESTED"], bg=C_AI_BG,
            ))
        story.append(Spacer(1, 3*mm))

    # Tip
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_DIV, spaceAfter=3*mm))
    tip_t = Table([[Paragraph(_c(
        "Tip: block a recurring learning slot, explain each topic to a colleague "
        "out loud, and tie what you learn to a real initiative at work. "
        "Your goal is judgment and confidence - not code."
    ), s["tip"])]], colWidths=[PAGE_W - 2*MARGIN], style=TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),C_SLATE),
        ("TOPPADDING",(0,0),(-1,-1),8),
        ("BOTTOMPADDING",(0,0),(-1,-1),8),
        ("LEFTPADDING",(0,0),(-1,-1),10),
        ("RIGHTPADDING",(0,0),(-1,-1),10),
        ("LINEBEFORE",(0,0),(0,-1),3,C_AMBER),
    ]))
    story.append(tip_t)

    doc.build(story, onFirstPage=deco, onLaterPages=deco)
    return buf.getvalue()
