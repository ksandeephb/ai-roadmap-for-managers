"""
pdf_export.py
-------------
Render a personalized roadmap to a downloadable PDF using fpdf2 (pure-Python,
no system dependencies — works locally and on Streamlit Cloud).

The PDF includes the learner's name, profile, every phase + resource, any AI
personalized picks, and a footer crediting the author with contact details.
"""

from fpdf import FPDF
from fpdf.enums import XPos, YPos

# Author / contact details shown in the PDF footer.
AUTHOR_NAME = "Sandeep Kumar"
AUTHOR_EMAIL = "ksandeep.srm@gmail.com"
AUTHOR_LINKEDIN = "https://www.linkedin.com/in/sandeep-kumar-23b02445/"

# Brand-ish colors (R, G, B)
ACCENT = (108, 123, 255)
TEAL = (54, 160, 150)
MUTED = (110, 120, 150)
DARK = (30, 35, 55)
LINK = (60, 90, 220)

_REPLACEMENTS = {
    "–": "-", "—": "-", "‘": "'", "’": "'",
    "“": '"', "”": '"', "•": "-", "→": "->",
    "…": "...", " ": " ",
}


def _clean(s: str) -> str:
    """Make text safe for the core PDF fonts (latin-1): swap common unicode
    punctuation and drop anything else (e.g. emojis)."""
    if not s:
        return ""
    for k, v in _REPLACEMENTS.items():
        s = s.replace(k, v)
    return s.encode("latin-1", "ignore").decode("latin-1")


class RoadmapPDF(FPDF):
    def footer(self):
        self.set_y(-16)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*MUTED)
        line = f"Created by {AUTHOR_NAME}  -  {AUTHOR_EMAIL}  -  {AUTHOR_LINKEDIN}"
        self._cell(line, h=5, align="C")
        self._cell(f"Page {self.page_no()}", h=5, align="C")

    def _cell(self, text, h=5.5, align="L"):
        """Full-width line that always starts at the left margin."""
        self.set_x(self.l_margin)
        self.multi_cell(self.epw, h, _clean(text), align=align,
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def _link(self, url, h=5):
        self.set_x(self.l_margin)
        self.multi_cell(self.epw, h, _clean(url), link=url,
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def build_pdf(name, profile_lines, plan, ai_result=None) -> bytes:
    """Return PDF bytes for the roadmap.

    name           : learner's first name (may be empty)
    profile_lines  : list of "Label: value" strings describing the learner
    plan           : dict from build_roadmap() -> {phases, total, weeks}
    ai_result      : optional dict {intro, suggestions:[{title,url,type,why}]}
    """
    pdf = RoadmapPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=22)
    pdf.set_margins(18, 18, 18)
    pdf.add_page()

    # --- Title ---
    pdf.set_font("Helvetica", "B", 19)
    pdf.set_text_color(*DARK)
    title = f"{name}, here's your personalized AI roadmap" if name else "Your personalized AI roadmap"
    pdf._cell(title, h=8)
    pdf.ln(1)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*MUTED)
    pdf._cell("A no-code path to understanding AI - built from free resources on the internet.", h=6)
    pdf.ln(3)

    # --- Profile ---
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*ACCENT)
    pdf._cell("Your profile", h=7)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*DARK)
    for line in profile_lines:
        pdf._cell(f"- {line}", h=5.5)
    pdf.ln(1)
    pdf.set_text_color(*MUTED)
    pdf._cell(
        f"{len(plan['phases'])} phases  -  {plan['total']} free resources  -  about {plan['weeks']} weeks at your pace",
        h=6,
    )
    pdf.ln(4)

    # --- Phases ---
    for i, phase in enumerate(plan["phases"], start=1):
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(*DARK)
        pdf._cell(f"Phase {i}: {phase['title']}", h=7)
        pdf.set_font("Helvetica", "I", 10)
        pdf.set_text_color(*MUTED)
        pdf._cell(f"Goal: {phase['goal']}", h=5.5)
        pdf.ln(1)
        for r in phase["resources"]:
            _resource_block(pdf, r["title"], r.get("desc", ""), r["url"],
                            tags=["Free", r.get("type", "resource")])
        pdf.ln(2)

    # --- AI personalized picks ---
    if ai_result and "error" not in ai_result and ai_result.get("suggestions"):
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(*TEAL)
        pdf._cell("Personalized picks for you", h=7)
        if ai_result.get("intro"):
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_text_color(*MUTED)
            pdf._cell(ai_result["intro"], h=5.5)
        pdf.ln(1)
        for s in ai_result["suggestions"]:
            _resource_block(pdf, s["title"], s.get("why", ""), s["url"],
                            tags=["Free", s.get("type", "resource"), "AI-suggested - verify link"])
        pdf.ln(2)

    # --- Closing tip ---
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(*MUTED)
    pdf._cell(
        "Tip: schedule a recurring learning slot, explain each topic out loud to a colleague, "
        "and tie what you learn to a real initiative at work.",
        h=5,
    )

    return bytes(pdf.output())


def _resource_block(pdf, title, desc, url, tags):
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*DARK)
    pdf._cell(title, h=5.5)
    if desc:
        pdf.set_font("Helvetica", "", 9.5)
        pdf.set_text_color(70, 75, 95)
        pdf._cell(desc, h=5)
    pdf.set_font("Helvetica", "U", 9)
    pdf.set_text_color(*LINK)
    pdf._link(url, h=5)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*MUTED)
    pdf._cell("  ".join(f"[{t}]" for t in tags), h=4.5)
    pdf.ln(1.5)
