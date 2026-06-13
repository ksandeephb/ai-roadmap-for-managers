"""
pdf_export.py
-------------
Renders a visually polished, industry-standard learning roadmap PDF.
Uses ReportLab Platypus for rich layout: coloured header band, phase cards
with left accent bars, resource rows, a styled author footer with a live link.

Colour palette — inspired by professional learning roadmap design:
  Deep navy    #1A2340  — page background accent, header
  Indigo       #4F5FD4  — phase number badges, accent bars
  Teal         #2BB5A0  — section headings, AI picks band
  Amber        #F0A500  — resource type chips / highlights
  Light slate  #F4F6FB  — alternating card backgrounds
  White        #FFFFFF  — main page background
  Body text    #1E2433
  Muted        #6B7694
"""

import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate,
    Paragraph, Spacer, Table, TableStyle, HRFlowable,
    KeepTogether,
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus.flowables import Flowable

# ── Author details ──────────────────────────────────────────────────────────
AUTHOR_NAME     = "Sandeep Kumar"
AUTHOR_EMAIL    = "ksandeep.srm@gmail.com"
AUTHOR_LINKEDIN = "https://www.linkedin.com/in/sandeep-kumar-23b02445/"

# ── Palette ─────────────────────────────────────────────────────────────────
C_NAVY    = colors.HexColor("#1A2340")
C_INDIGO  = colors.HexColor("#4F5FD4")
C_TEAL    = colors.HexColor("#2BB5A0")
C_AMBER   = colors.HexColor("#F0A500")
C_SLATE   = colors.HexColor("#F4F6FB")
C_WHITE   = colors.white
C_BODY    = colors.HexColor("#1E2433")
C_MUTED   = colors.HexColor("#6B7694")
C_LINK    = colors.HexColor("#4F5FD4")
C_DIVIDER = colors.HexColor("#DDE2F0")
C_PHASE_BG= colors.HexColor("#ECEFFE")   # very light indigo for phase header bg

PAGE_W, PAGE_H = A4
MARGIN = 18 * mm

# ── Unicode → latin-1 safe replacement ──────────────────────────────────────
_REPLACEMENTS = {
    "\u2013": "-", "\u2014": "-",
    "\u2018": "'", "\u2019": "'",
    "\u201c": '"', "\u201d": '"',
    "\u2022": "-", "\u2192": "->",
    "\u2026": "...", "\u00a0": " ",
}

def _clean(s: str) -> str:
    if not s:
        return ""
    for k, v in _REPLACEMENTS.items():
        s = s.replace(k, v)
    return s.encode("latin-1", "ignore").decode("latin-1")


# ── Custom flowable: coloured rectangle (used for accent bars) ───────────────
class ColorBar(Flowable):
    def __init__(self, width, height, color):
        super().__init__()
        self.width  = width
        self.height = height
        self.color  = color

    def draw(self):
        self.canv.setFillColor(self.color)
        self.canv.rect(0, 0, self.width, self.height, fill=1, stroke=0)


# ── Paragraph styles ─────────────────────────────────────────────────────────
def _styles():
    return {
        "doc_title": ParagraphStyle(
            "doc_title", fontName="Helvetica-Bold", fontSize=22,
            textColor=C_WHITE, leading=28, spaceAfter=2,
        ),
        "doc_sub": ParagraphStyle(
            "doc_sub", fontName="Helvetica", fontSize=10,
            textColor=colors.HexColor("#B8C4E8"), leading=14,
        ),
        "section_label": ParagraphStyle(
            "section_label", fontName="Helvetica-Bold", fontSize=8,
            textColor=C_TEAL, leading=10, spaceBefore=10, spaceAfter=2,
            letterSpacing=1.2,
        ),
        "profile_item": ParagraphStyle(
            "profile_item", fontName="Helvetica", fontSize=9.5,
            textColor=C_BODY, leading=14,
        ),
        "stats_val": ParagraphStyle(
            "stats_val", fontName="Helvetica-Bold", fontSize=16,
            textColor=C_INDIGO, leading=20, alignment=TA_CENTER,
        ),
        "stats_lbl": ParagraphStyle(
            "stats_lbl", fontName="Helvetica", fontSize=7.5,
            textColor=C_MUTED, leading=10, alignment=TA_CENTER,
        ),
        "phase_num": ParagraphStyle(
            "phase_num", fontName="Helvetica-Bold", fontSize=9,
            textColor=C_WHITE, leading=12, alignment=TA_CENTER,
        ),
        "phase_title": ParagraphStyle(
            "phase_title", fontName="Helvetica-Bold", fontSize=13,
            textColor=C_NAVY, leading=16,
        ),
        "phase_goal": ParagraphStyle(
            "phase_goal", fontName="Helvetica-Oblique", fontSize=9,
            textColor=C_MUTED, leading=13,
        ),
        "res_title": ParagraphStyle(
            "res_title", fontName="Helvetica-Bold", fontSize=10,
            textColor=C_BODY, leading=14,
        ),
        "res_desc": ParagraphStyle(
            "res_desc", fontName="Helvetica", fontSize=8.5,
            textColor=C_MUTED, leading=12,
        ),
        "res_link": ParagraphStyle(
            "res_link", fontName="Helvetica", fontSize=8,
            textColor=C_LINK, leading=11,
        ),
        "res_tag": ParagraphStyle(
            "res_tag", fontName="Helvetica-Bold", fontSize=7,
            textColor=C_AMBER, leading=10,
        ),
        "ai_heading": ParagraphStyle(
            "ai_heading", fontName="Helvetica-Bold", fontSize=13,
            textColor=C_TEAL, leading=16, spaceBefore=6,
        ),
        "ai_intro": ParagraphStyle(
            "ai_intro", fontName="Helvetica-Oblique", fontSize=9,
            textColor=C_MUTED, leading=13,
        ),
        "tip": ParagraphStyle(
            "tip", fontName="Helvetica-Oblique", fontSize=8.5,
            textColor=C_MUTED, leading=13,
        ),
        "footer_name": ParagraphStyle(
            "footer_name", fontName="Helvetica-Bold", fontSize=8,
            textColor=C_BODY, leading=10,
        ),
        "footer_detail": ParagraphStyle(
            "footer_detail", fontName="Helvetica", fontSize=7.5,
            textColor=C_MUTED, leading=10,
        ),
        "footer_link": ParagraphStyle(
            "footer_link", fontName="Helvetica", fontSize=7.5,
            textColor=C_LINK, leading=10,
        ),
        "page_num": ParagraphStyle(
            "page_num", fontName="Helvetica", fontSize=7.5,
            textColor=C_MUTED, leading=10, alignment=TA_RIGHT,
        ),
    }


# ── Header band (drawn on every page) ────────────────────────────────────────
def _header_band(canvas, doc, title_text, subtitle_text):
    """Dark navy header band on page 1 only; slim rule on subsequent pages."""
    canvas.saveState()
    if doc.page == 1:
        band_h = 52 * mm
        canvas.setFillColor(C_NAVY)
        canvas.rect(0, PAGE_H - band_h, PAGE_W, band_h, fill=1, stroke=0)
        # Indigo accent strip at bottom of band
        canvas.setFillColor(C_INDIGO)
        canvas.rect(0, PAGE_H - band_h - 3, PAGE_W, 3, fill=1, stroke=0)
        # Title
        canvas.setFont("Helvetica-Bold", 20)
        canvas.setFillColor(C_WHITE)
        canvas.drawString(MARGIN, PAGE_H - 22 * mm, _clean(title_text))
        # Subtitle
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(colors.HexColor("#B8C4E8"))
        canvas.drawString(MARGIN, PAGE_H - 30 * mm, _clean(subtitle_text))
    else:
        # Slim top rule on continuation pages
        canvas.setFillColor(C_INDIGO)
        canvas.rect(0, PAGE_H - 6, PAGE_W, 6, fill=1, stroke=0)

    # ── Footer ───────────────────────────────────────────────────────────────
    footer_y = 10 * mm
    canvas.setFillColor(C_DIVIDER)
    canvas.rect(MARGIN, footer_y + 8, PAGE_W - 2 * MARGIN, 0.5, fill=1, stroke=0)

    # Author name + email
    canvas.setFont("Helvetica-Bold", 7.5)
    canvas.setFillColor(C_BODY)
    canvas.drawString(MARGIN, footer_y + 2, _clean(f"Created by {AUTHOR_NAME}"))

    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(C_MUTED)
    canvas.drawString(MARGIN, footer_y - 5, _clean(AUTHOR_EMAIL))

    # LinkedIn as a live link — bright indigo, underlined feel
    linkedin_x = MARGIN + 80 * mm
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(C_LINK)
    canvas.drawString(linkedin_x, footer_y + 2, "LinkedIn Profile")
    canvas.linkURL(AUTHOR_LINKEDIN,
                   (linkedin_x, footer_y, linkedin_x + 45 * mm, footer_y + 8),
                   relative=0)

    # Page number right-aligned
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(C_MUTED)
    page_str = f"Page {doc.page}"
    canvas.drawRightString(PAGE_W - MARGIN, footer_y + 2, page_str)

    canvas.restoreState()


# ── Resource card ─────────────────────────────────────────────────────────────
def _resource_card(s, title, desc, url, tags, bg=C_WHITE):
    """Returns a KeepTogether block for one resource."""
    tag_str = "  |  ".join(t.upper() for t in tags if t)
    rows = [
        [Paragraph(_clean(title), s["res_title"])],
    ]
    if desc:
        rows.append([Paragraph(_clean(desc), s["res_desc"])])

    link_para = Paragraph(
        f'<link href="{url}" color="#4F5FD4">{_clean(url)}</link>',
        s["res_link"],
    )
    rows.append([link_para])
    rows.append([Paragraph(tag_str, s["res_tag"])])

    inner = Table(
        rows,
        colWidths=[PAGE_W - 2 * MARGIN - 8 * mm],
        style=TableStyle([
            ("BACKGROUND",  (0, 0), (-1, -1), bg),
            ("TOPPADDING",  (0, 0), (-1, 0),  6),
            ("BOTTOMPADDING",(0,-1),(-1,-1),   6),
            ("LEFTPADDING", (0, 0), (-1, -1),  8),
            ("RIGHTPADDING",(0, 0), (-1, -1),  8),
            ("LINEAFTER",   (0, 0), (0, -1),   3, C_INDIGO),
        ]),
    )
    return KeepTogether([inner, Spacer(1, 3 * mm)])


# ── Phase header card ─────────────────────────────────────────────────────────
def _phase_header(s, number, title, goal):
    badge_cell = Table(
        [[Paragraph(str(number), s["phase_num"])]],
        colWidths=[7 * mm],
        rowHeights=[7 * mm],
        style=TableStyle([
            ("BACKGROUND",  (0, 0), (-1, -1), C_INDIGO),
            ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
            ("ROUNDEDCORNERS", (0, 0), (-1, -1), [3]),
        ]),
    )
    text_cell = Table(
        [
            [Paragraph(_clean(title), s["phase_title"])],
            [Paragraph(_clean(f"Goal: {goal}"), s["phase_goal"])],
        ],
        colWidths=[PAGE_W - 2 * MARGIN - 14 * mm],
        style=TableStyle([
            ("TOPPADDING",    (0, 0), (-1, -1), 1),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ]),
    )
    header = Table(
        [[badge_cell, text_cell]],
        colWidths=[10 * mm, PAGE_W - 2 * MARGIN - 10 * mm],
        style=TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), C_PHASE_BG),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (0, -1),  4),
            ("LEFTPADDING",   (1, 0), (1, -1),  6),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("LINEBELOW",     (0, 0), (-1, -1), 2, C_INDIGO),
        ]),
    )
    return KeepTogether([header, Spacer(1, 2 * mm)])


# ── Stats row ─────────────────────────────────────────────────────────────────
def _stats_row(s, phases, resources, pace, weeks):
    cells = [
        [Paragraph(str(phases),    s["stats_val"]),
         Paragraph(str(resources), s["stats_val"]),
         Paragraph(str(pace),      s["stats_val"]),
         Paragraph(f"~{weeks}",    s["stats_val"])],
        [Paragraph("PHASES",       s["stats_lbl"]),
         Paragraph("FREE RESOURCES",s["stats_lbl"]),
         Paragraph("YOUR PACE",    s["stats_lbl"]),
         Paragraph("EST. WEEKS",   s["stats_lbl"])],
    ]
    col_w = (PAGE_W - 2 * MARGIN) / 4
    return Table(
        cells,
        colWidths=[col_w] * 4,
        style=TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), C_SLATE),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("LINEAFTER",     (0, 0), (2, -1),  0.5, C_DIVIDER),
        ]),
    )


# ── Profile block ─────────────────────────────────────────────────────────────
def _profile_block(s, profile_lines):
    rows = [[Paragraph(_clean(f"  {line}"), s["profile_item"])]
            for line in profile_lines]
    return Table(
        rows,
        colWidths=[PAGE_W - 2 * MARGIN],
        style=TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), C_SLATE),
            ("TOPPADDING",    (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("LINEBEFORE",    (0, 0), (0, -1),  3, C_TEAL),
        ]),
    )


# ── Main builder ─────────────────────────────────────────────────────────────
def build_pdf(name, profile_lines, plan, ai_result=None) -> bytes:
    buf = io.BytesIO()
    s = _styles()

    title_text = (
        f"{name}, here's your personalized AI roadmap"
        if name else "Your personalized AI roadmap"
    )
    subtitle_text = "A no-code path to understanding AI - built from free resources"

    # Page template with header/footer
    def _on_page(canvas, doc):
        _header_band(canvas, doc, title_text, subtitle_text)

    frame = Frame(
        MARGIN, 14 * mm,
        PAGE_W - 2 * MARGIN,
        PAGE_H - 14 * mm - 58 * mm,   # leave room for navy header on p1
        leftPadding=0, rightPadding=0,
        topPadding=0, bottomPadding=0,
    )
    frame_cont = Frame(
        MARGIN, 14 * mm,
        PAGE_W - 2 * MARGIN,
        PAGE_H - 14 * mm - 12 * mm,   # continuation pages: only footer gap
        leftPadding=0, rightPadding=0,
        topPadding=0, bottomPadding=0,
    )
    doc = BaseDocTemplate(
        buf, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=58 * mm, bottomMargin=14 * mm,
    )
    doc.addPageTemplates([
        PageTemplate(id="First", frames=[frame], onPage=_on_page, pagesize=A4),
        PageTemplate(id="Later", frames=[frame_cont], onPage=_on_page, pagesize=A4),
    ])

    story = []

    # ── Profile section ─────────────────────────────────────────────────────
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph("YOUR PROFILE", s["section_label"]))
    story.append(Spacer(1, 1 * mm))
    story.append(_profile_block(s, profile_lines))
    story.append(Spacer(1, 4 * mm))

    # ── Stats ───────────────────────────────────────────────────────────────
    from roadmap_data import build_roadmap   # local import to avoid circular
    pace_map = {"high": "6+ hrs/wk", "mid": "3-5 hrs/wk", "low": "1-2 hrs/wk"}
    # derive pace from profile_lines
    pace_str = next(
        (pace_map[k] for k in pace_map if k in str(profile_lines).lower()),
        "Your pace"
    )
    story.append(
        _stats_row(s, len(plan["phases"]), plan["total"], pace_str, plan["weeks"])
    )
    story.append(Spacer(1, 5 * mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_DIVIDER))
    story.append(Spacer(1, 4 * mm))

    # Switch to continuation frame after page 1
    from reportlab.platypus import NextPageTemplate
    # (handled automatically by BaseDocTemplate cycling)

    # ── Phases ──────────────────────────────────────────────────────────────
    story.append(Paragraph("LEARNING PHASES", s["section_label"]))
    story.append(Spacer(1, 2 * mm))

    alt = False
    for i, phase in enumerate(plan["phases"], start=1):
        story.append(_phase_header(s, i, phase["title"], phase["goal"]))
        for r in phase["resources"]:
            bg = C_SLATE if alt else C_WHITE
            alt = not alt
            story.append(_resource_card(
                s, r["title"], r.get("desc", ""), r["url"],
                tags=[r.get("type", "read").upper(), "FREE"] + r.get("tags", []),
                bg=bg,
            ))
        story.append(Spacer(1, 4 * mm))

    # ── AI picks ────────────────────────────────────────────────────────────
    if ai_result and "error" not in ai_result and ai_result.get("suggestions"):
        story.append(HRFlowable(width="100%", thickness=0.5, color=C_DIVIDER))
        story.append(Spacer(1, 3 * mm))
        story.append(Paragraph("PERSONALIZED PICKS FOR YOU", s["section_label"]))
        story.append(Paragraph("AI-SUGGESTED", s["ai_heading"]))
        if ai_result.get("intro"):
            story.append(Paragraph(_clean(ai_result["intro"]), s["ai_intro"]))
        story.append(Spacer(1, 2 * mm))
        for sug in ai_result["suggestions"]:
            story.append(_resource_card(
                s, sug["title"], sug.get("why", ""), sug["url"],
                tags=["READ", "FREE", "AI-SUGGESTED"],
                bg=colors.HexColor("#F0FDFB"),   # very light teal tint
            ))
        story.append(Spacer(1, 3 * mm))

    # ── Closing tip ──────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_DIVIDER))
    story.append(Spacer(1, 3 * mm))
    tip = Table(
        [[Paragraph(
            _clean(
                "Tip: block a recurring learning slot each week, explain each topic "
                "to a colleague out loud, and tie what you learn to a real initiative at work. "
                "Your goal is judgment and confidence - not code."
            ),
            s["tip"],
        )]],
        colWidths=[PAGE_W - 2 * MARGIN],
        style=TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), C_SLATE),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
            ("LINEBEFORE",    (0, 0), (0, -1),  3, C_AMBER),
        ]),
    )
    story.append(tip)

    doc.build(story)
    return buf.getvalue()
