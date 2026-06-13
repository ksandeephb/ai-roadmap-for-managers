"""
pdf_export.py — AI Roadmap PDF

Colour system inspired by industry-standard learning platforms
(Coursera, LinkedIn Learning, Google Learn):
  - ONE primary colour: deep teal #006D77
  - ONE accent: warm amber #E89C45 (used ONLY for highlights/tip)
  - Dark charcoal #1C2B36 for header + titles
  - Light grey #F5F7FA for card alt rows + profile bg
  - White #FFFFFF for main cards
  - Border #DCE3EA throughout

No rainbow phases. All phase headers use the same teal — 
differentiation comes from number badges only.
Type badges: small pill in muted grey, coloured text only.
"""

import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate,
    Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, NextPageTemplate,
)

# ── Author ────────────────────────────────────────────────────────────────────
AUTHOR_NAME     = "Sandeep Kumar"
AUTHOR_EMAIL    = "ksandeep.srm@gmail.com"
AUTHOR_LINKEDIN = "https://www.linkedin.com/in/sandeep-kumar-23b02445/"

# ── Palette — industry-standard learning platform colours ─────────────────────
#
#  Coursera uses deep navy + teal.
#  LinkedIn Learning uses dark charcoal header + blue-teal primary.
#  Google Learn uses charcoal + clean teal/cyan.
#  We use:
#    CHARCOAL  — header band, page header text
#    TEAL      — primary accent: phase headers, badges, links, left bars
#    AMBER     — one warm accent for tip box only
#    DARK      — body titles (softer than charcoal)
#    MUTED     — body copy, meta text, captions
#    BG_ALT    — alternating card rows, profile box
#    BORDER    — card borders, dividers
#
CHARCOAL  = colors.HexColor("#1C2B36")   # header band
TEAL      = colors.HexColor("#006D77")   # primary — Coursera-like deep teal
TEAL_LT   = colors.HexColor("#E8F4F5")   # very light teal tint for phase bg
AMBER     = colors.HexColor("#E89C45")   # warm accent — tip only
DARK      = colors.HexColor("#1E2B33")   # titles
MUTED     = colors.HexColor("#5C6B74")   # body / meta
BG_ALT    = colors.HexColor("#F5F7FA")   # alternate card bg
BORDER    = colors.HexColor("#DCE3EA")   # borders / dividers
LINK      = colors.HexColor("#006D77")   # links match primary

PAGE_W, PAGE_H = A4
M         = 18 * mm
CONTENT_W = PAGE_W - 2 * M
HEADER_H  = 40 * mm
FOOTER_H  = 14 * mm
TOP_P1    = HEADER_H + 8 * mm
TOP_CONT  = 8 * mm

# ── Resource type label colours — muted, not badges ──────────────────────────
TYPE_COLOR = {
    "video":  colors.HexColor("#C0392B"),   # red  — video
    "course": colors.HexColor("#6C3FC5"),   # purple — course
    "read":   colors.HexColor("#1A6BBF"),   # blue — article
    "tool":   colors.HexColor("#1E7E49"),   # green — tool
}
TYPE_LABEL = {
    "video": "▶ VIDEO", "course": "COURSE",
    "read": "READ", "tool": "TOOL",
}

_U = {"\u2013":"-","\u2014":"-","\u2018":"'","\u2019":"'",
      "\u201c":'"',"\u201d":'"',"\u2022":"-","\u2192":"->",
      "\u2026":"...","\u00a0":" "}
def _t(s):
    if not s: return ""
    for k, v in _U.items(): s = s.replace(k, v)
    return s.encode("latin-1","ignore").decode("latin-1")

# ── Styles ────────────────────────────────────────────────────────────────────
def _S():
    return {
        "eyebrow": ParagraphStyle("eyebrow", fontName="Helvetica-Bold",    fontSize=7,   textColor=TEAL,   leading=9,  spaceAfter=2, letterSpacing=1.5),
        "pk":      ParagraphStyle("pk",      fontName="Helvetica-Bold",    fontSize=9,   textColor=DARK,   leading=13),
        "pv":      ParagraphStyle("pv",      fontName="Helvetica",         fontSize=9,   textColor=MUTED,  leading=13),
        "sn":      ParagraphStyle("sn",      fontName="Helvetica-Bold",    fontSize=22,  textColor=TEAL,   leading=26, alignment=TA_CENTER),
        "sl":      ParagraphStyle("sl",      fontName="Helvetica",         fontSize=7,   textColor=MUTED,  leading=9,  alignment=TA_CENTER),
        "pnum":    ParagraphStyle("pnum",    fontName="Helvetica-Bold",    fontSize=10,  textColor=colors.white, leading=13, alignment=TA_CENTER),
        "ptitle":  ParagraphStyle("ptitle",  fontName="Helvetica-Bold",    fontSize=11,  textColor=colors.white, leading=14),
        "pgoal":   ParagraphStyle("pgoal",   fontName="Helvetica-Oblique", fontSize=8.5, textColor=colors.HexColor("#B8D8DB"), leading=12),
        "rtitle":  ParagraphStyle("rtitle",  fontName="Helvetica-Bold",    fontSize=10,  textColor=DARK,   leading=13),
        "rdesc":   ParagraphStyle("rdesc",   fontName="Helvetica",         fontSize=8.5, textColor=MUTED,  leading=12),
        "rurl":    ParagraphStyle("rurl",    fontName="Helvetica",         fontSize=7.5, textColor=LINK,   leading=10),
        "rmeta":   ParagraphStyle("rmeta",   fontName="Helvetica",         fontSize=7.5, textColor=MUTED,  leading=10),
        "aihead":  ParagraphStyle("aihead",  fontName="Helvetica-Bold",    fontSize=11,  textColor=TEAL,   leading=14),
        "aiintro": ParagraphStyle("aiintro", fontName="Helvetica-Oblique", fontSize=8.5, textColor=MUTED,  leading=12),
        "tip":     ParagraphStyle("tip",     fontName="Helvetica-Oblique", fontSize=8,   textColor=MUTED,  leading=12),
    }

# ── Page decorator ────────────────────────────────────────────────────────────
class _Deco:
    def __init__(self, title, subtitle):
        self.title    = _t(title)
        self.subtitle = _t(subtitle)

    def __call__(self, canvas, doc):
        canvas.saveState()
        W, H = PAGE_W, PAGE_H

        if doc.page == 1:
            # Charcoal header band
            canvas.setFillColor(CHARCOAL)
            canvas.rect(0, H - HEADER_H, W, HEADER_H, fill=1, stroke=0)
            # Single teal accent line at band bottom
            canvas.setFillColor(TEAL)
            canvas.rect(0, H - HEADER_H, W, 4, fill=1, stroke=0)
            # Small teal pill
            canvas.setFillColor(TEAL)
            canvas.roundRect(M, H - 10*mm, 50*mm, 5*mm, 2, fill=1, stroke=0)
            canvas.setFont("Helvetica-Bold", 6.5)
            canvas.setFillColor(colors.white)
            canvas.drawString(M + 3*mm, H - 6.8*mm, "FREE  |  NO CODE  |  8 WEEKS")
            # Title
            canvas.setFont("Helvetica-Bold", 20)
            canvas.setFillColor(colors.white)
            canvas.drawString(M, H - 19*mm, self.title)
            # Subtitle
            canvas.setFont("Helvetica", 9)
            canvas.setFillColor(colors.HexColor("#8AAAB0"))
            canvas.drawString(M, H - 27*mm, self.subtitle)
        else:
            # Slim teal bar on continuation pages
            canvas.setFillColor(TEAL)
            canvas.rect(0, H - 4, W, 4, fill=1, stroke=0)
            canvas.setFont("Helvetica", 7.5)
            canvas.setFillColor(MUTED)
            canvas.drawString(M, H - 3.2*mm, self.title)

        # ── Footer ────────────────────────────────────────────────────────────
        fy = 11 * mm
        canvas.setStrokeColor(BORDER)
        canvas.setLineWidth(0.4)
        canvas.line(M, fy + 5.5*mm, W - M, fy + 5.5*mm)

        canvas.setFont("Helvetica-Bold", 8.5)
        canvas.setFillColor(DARK)
        canvas.drawString(M, fy + 1.5*mm, _t(AUTHOR_NAME))

        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(M + 37*mm, fy + 1.5*mm, _t(AUTHOR_EMAIL))

        pg = f"Page {doc.page}"
        pg_w = canvas.stringWidth(pg, "Helvetica", 7.5)
        canvas.drawRightString(W - M, fy + 1.5*mm, pg)

        li_label = "LinkedIn"
        canvas.setFont("Helvetica-Bold", 8)
        li_w = canvas.stringWidth(li_label, "Helvetica-Bold", 8)
        li_x = W - M - pg_w - 8*mm - li_w
        canvas.setFillColor(TEAL)
        canvas.drawString(li_x, fy + 1.5*mm, li_label)
        canvas.setStrokeColor(TEAL)
        canvas.setLineWidth(0.4)
        canvas.line(li_x, fy + 0.8*mm, li_x + li_w, fy + 0.8*mm)
        canvas.linkURL(AUTHOR_LINKEDIN,
            (li_x, fy - 0.5*mm, li_x + li_w, fy + 4*mm), relative=0)

        canvas.restoreState()

# ── Resource card ─────────────────────────────────────────────────────────────
def _card(s, title, desc, url, rtype, meta, bg=colors.white):
    short = _t(url[:68] + ("..." if len(url) > 68 else ""))

    # Type label inline in title row — coloured text, no background pill
    type_clr = TYPE_COLOR.get(rtype, MUTED)
    type_str = TYPE_LABEL.get(rtype, rtype.upper())
    type_para = ParagraphStyle("tl", fontName="Helvetica-Bold", fontSize=7,
        textColor=type_clr, leading=9)

    inner_w = CONTENT_W - 4

    rows = [
        # Row 0: type label + title on same row
        [Table([[Paragraph(type_str, type_para)],
                [Paragraph(_t(title), s["rtitle"])]],
               colWidths=[inner_w],
               style=TableStyle([
                   ("BACKGROUND",(0,0),(-1,-1), bg),
                   ("TOPPADDING",(0,0),(-1,0), 7),
                   ("BOTTOMPADDING",(0,0),(-1,0), 1),
                   ("TOPPADDING",(0,1),(-1,1), 1),
                   ("BOTTOMPADDING",(0,1),(-1,1), 2),
                   ("LEFTPADDING",(0,0),(-1,-1), 10),
                   ("RIGHTPADDING",(0,0),(-1,-1), 10),
               ]))],
    ]
    if desc:
        rows.append([Paragraph(_t(desc), s["rdesc"])])
    rows.append([Paragraph(
        f'<link href="{url}" color="#006D77"><u>{short}</u></link>',
        s["rurl"])])
    if meta:
        rows.append([Paragraph(_t(meta), s["rmeta"])])

    # Pad non-header rows
    body = rows[1:]
    if body:
        body_t = Table(body, colWidths=[inner_w], style=TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), bg),
            ("TOPPADDING",    (0,0),(-1,-1), 2),
            ("BOTTOMPADDING", (0,-1),(-1,-1), 7),
            ("LEFTPADDING",   (0,0),(-1,-1), 10),
            ("RIGHTPADDING",  (0,0),(-1,-1), 10),
        ]))
        combined = Table([[rows[0][0]], [body_t]], colWidths=[inner_w],
            style=TableStyle([
                ("BACKGROUND",(0,0),(-1,-1), bg),
                ("TOPPADDING",(0,0),(-1,-1), 0),
                ("BOTTOMPADDING",(0,0),(-1,-1), 0),
                ("LEFTPADDING",(0,0),(-1,-1), 0),
                ("RIGHTPADDING",(0,0),(-1,-1), 0),
            ]))
    else:
        combined = rows[0][0]

    # Teal left bar + border
    outer = Table([[None, combined]], colWidths=[4, inner_w],
        style=TableStyle([
            ("BACKGROUND", (0,0),(0,-1), TEAL),
            ("BACKGROUND", (1,0),(1,-1), bg),
            ("BOX",        (0,0),(-1,-1), 0.5, BORDER),
            ("TOPPADDING",    (0,0),(-1,-1), 0),
            ("BOTTOMPADDING", (0,0),(-1,-1), 0),
            ("LEFTPADDING",   (0,0),(-1,-1), 0),
            ("RIGHTPADDING",  (0,0),(-1,-1), 0),
        ]))
    return [outer, Spacer(1, 2.5*mm)]

# ── Phase header — solid teal, white text ─────────────────────────────────────
def _phase_hdr(s, num, title, goal):
    import re
    title = re.sub(r"^Phase \d+\s*[—–\-]+\s*", "", title)

    badge = Table([[Paragraph(str(num), s["pnum"])]],
        colWidths=[9*mm], rowHeights=[9*mm],
        style=TableStyle([
            ("BACKGROUND", (0,0),(-1,-1), colors.HexColor("#005B63")),
            ("ALIGN",      (0,0),(-1,-1), "CENTER"),
            ("VALIGN",     (0,0),(-1,-1), "MIDDLE"),
        ]))
    text = Table([
        [Paragraph(_t(title), s["ptitle"])],
        [Paragraph(_t(goal),  s["pgoal"])],
    ], colWidths=[CONTENT_W - 14*mm], style=TableStyle([
        ("TOPPADDING",    (0,0),(-1,-1), 1),
        ("BOTTOMPADDING", (0,0),(-1,-1), 1),
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
    ]))
    hdr = Table([[badge, text]],
        colWidths=[12*mm, CONTENT_W - 12*mm],
        style=TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), TEAL),
            ("TOPPADDING",    (0,0),(-1,-1), 8),
            ("BOTTOMPADDING", (0,0),(-1,-1), 8),
            ("LEFTPADDING",   (0,0),(0,-1),  2),
            ("LEFTPADDING",   (1,0),(1,-1),  8),
            ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ]))
    return [hdr, Spacer(1, 2.5*mm)]

# ── Stats bar ─────────────────────────────────────────────────────────────────
def _stats(s, phases, resources, pace, weeks):
    cw = CONTENT_W / 4
    return Table([
        [Paragraph(str(phases),    s["sn"]),
         Paragraph(str(resources), s["sn"]),
         Paragraph(_t(pace),       s["sn"]),
         Paragraph(f"{weeks} wks", s["sn"])],
        [Paragraph("PHASES",    s["sl"]),
         Paragraph("RESOURCES", s["sl"]),
         Paragraph("YOUR PACE", s["sl"]),
         Paragraph("TO FINISH", s["sl"])],
    ], colWidths=[cw]*4, style=TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), BG_ALT),
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10),
        ("ALIGN",         (0,0),(-1,-1), "CENTER"),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("LINEAFTER",     (0,0),(2,-1),  0.4, BORDER),
        ("BOX",           (0,0),(-1,-1), 0.5, BORDER),
    ]))

# ── Profile card ──────────────────────────────────────────────────────────────
def _profile(s, lines):
    rows = []
    for line in lines:
        k, _, v = line.partition(":")
        rows.append([
            Paragraph(_t(k.strip()) + ":", s["pk"]),
            Paragraph(_t(v.strip()),       s["pv"]),
        ])
    return Table(rows, colWidths=[32*mm, CONTENT_W - 32*mm],
        style=TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), BG_ALT),
            ("TOPPADDING",    (0,0),(-1,-1), 4),
            ("BOTTOMPADDING", (0,0),(-1,-1), 4),
            ("LEFTPADDING",   (0,0),(-1,-1), 10),
            ("RIGHTPADDING",  (0,0),(-1,-1), 8),
            ("LINEBEFORE",    (0,0),(0,-1),  3, TEAL),
            ("BOX",           (0,0),(-1,-1), 0.5, BORDER),
        ]))

# ── Main builder ──────────────────────────────────────────────────────────────
def build_pdf(name, profile_lines, plan, ai_result=None) -> bytes:
    buf = io.BytesIO()
    s   = _S()

    title    = _t(f"{name}'s AI Learning Roadmap" if name else "AI Learning Roadmap")
    subtitle = _t("A focused 8-week path to leading AI projects - 100% free resources")
    deco     = _Deco(title, subtitle)

    def _frame(top):
        return Frame(M, FOOTER_H + 2*mm, CONTENT_W,
            PAGE_H - top - FOOTER_H - 4*mm,
            leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)

    doc = BaseDocTemplate(buf, pagesize=A4,
        leftMargin=M, rightMargin=M,
        topMargin=TOP_P1, bottomMargin=FOOTER_H + 4*mm)
    doc.addPageTemplates([
        PageTemplate(id="First", frames=[_frame(TOP_P1)],   onPage=deco, pagesize=A4),
        PageTemplate(id="Later", frames=[_frame(TOP_CONT)], onPage=deco, pagesize=A4),
    ])

    raw  = " ".join(profile_lines).lower()
    pace = "6+ hrs/wk" if ("6+" in raw or "high" in raw) else \
           "3-5 hrs/wk" if ("3" in raw or "mid" in raw) else "1-2 hrs/wk"

    story = []

    story.append(Paragraph("YOUR PROFILE", s["eyebrow"]))
    story.append(Spacer(1, 2*mm))
    story.append(_profile(s, profile_lines))
    story.append(Spacer(1, 5*mm))
    story.append(_stats(s, len(plan["phases"]), plan["total"], pace, plan["weeks"]))
    story.append(Spacer(1, 6*mm))
    story.append(HRFlowable(width="100%", thickness=0.4, color=BORDER, spaceAfter=5*mm))
    story.append(NextPageTemplate("Later"))
    story.append(Paragraph("LEARNING ROADMAP", s["eyebrow"]))
    story.append(Spacer(1, 3*mm))

    alt = False
    for i, phase in enumerate(plan["phases"]):
        story.extend(_phase_hdr(s, i+1, phase["title"], phase["goal"]))
        for r in phase["resources"]:
            rtype = r.get("type", "read")
            tags  = [t for t in r.get("tags", []) if t != "Free"][:3]
            meta  = "  ·  ".join(tags) if tags else ""
            story.extend(_card(s, r["title"], r.get("desc",""), r["url"],
                rtype=rtype, meta=meta,
                bg=BG_ALT if alt else colors.white))
            alt = not alt
        story.append(Spacer(1, 2*mm))

    # AI picks
    if ai_result and "error" not in ai_result and ai_result.get("suggestions"):
        story.append(HRFlowable(width="100%", thickness=0.4, color=BORDER, spaceAfter=3*mm))
        story.append(Paragraph("PERSONALISED FOR YOU", s["eyebrow"]))
        story.append(Paragraph("AI-curated picks based on your answers", s["aihead"]))
        story.append(Spacer(1, 2*mm))
        if ai_result.get("intro"):
            story.append(Paragraph(_t(ai_result["intro"]), s["aiintro"]))
        story.append(Spacer(1, 2*mm))
        for sug in ai_result["suggestions"]:
            story.extend(_card(s, sug["title"], sug.get("why",""), sug["url"],
                rtype="read", meta="AI-picked  ·  Free",
                bg=colors.HexColor("#F0F8F8")))
        story.append(Spacer(1, 1*mm))

    # Tip — plain paragraph, no table, flows freely
    story.append(HRFlowable(width="100%", thickness=0.4, color=BORDER, spaceAfter=3*mm))
    tip_style = ParagraphStyle("tip2", fontName="Helvetica-Oblique", fontSize=8,
        textColor=MUTED, leading=12, leftIndent=10, rightIndent=10,
        backColor=BG_ALT, borderPad=10,
        borderWidth=0.5, borderColor=BORDER)
    story.append(Paragraph(_t(
        "Tip: Schedule a recurring weekly learning slot. After each resource, "
        "explain the key idea to a colleague in one sentence. Tie it to a real "
        "project at work. Your goal is judgment - not code."
    ), tip_style))

    doc.build(story)
    return buf.getvalue()
