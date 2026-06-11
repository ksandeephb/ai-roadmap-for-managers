# 🧭 AI Roadmap for Managers

A small web app for **experienced but non-technical** project managers, delivery
managers and program leads who want to **understand AI without coding**.

It asks 6 quick questions and generates a **personalized, step-by-step learning
roadmap** that links only to **free** resources on the internet (courses you can
audit for free, YouTube explainers, practical guides, and tools with free tiers).

Built with [Streamlit](https://streamlit.io/) (Python).

---

## What it does

1. **Asks your name + 6 questions** — your role, why you want to learn AI, your
   current level, weekly time, how you like to learn, and which topics interest you.
   The results are personalized to your name ("Ravi, here's your roadmap…").
2. **Builds a 4-phase roadmap** — Foundations → How it works → Hands-on → Apply it
   to your work — choosing resources that match your answers.
3. **Lets you download it as a PDF** (named after you) to keep or share.

No login, no tracking, no cost.

---

## How to run it

You need **Python 3.9+** installed.

### 1. (Recommended) Create a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install the requirements
```bash
pip install -r requirements.txt
```

### 3. Start the app
```bash
python -m streamlit run app.py
```
> If `python` isn't recognized, try `py -m streamlit run app.py`, or use the
> full path to your Python executable. Using `python -m streamlit` (rather than
> `streamlit` on its own) avoids PATH issues on Windows.

Streamlit will open the app in your browser (usually at http://localhost:8501).
To stop it, press `Ctrl + C` in the terminal.

---

## Optional: personalized AI picks (Claude)

The app works fully **without** any AI — the curated roadmap is the reliable
backbone. If you provide an **Anthropic API key**, it adds a small *"✨ Personalized
picks for you"* section with a few extra free, no-code resources tailored to the
person's answers, plus a personalized intro.

- **Model:** Claude Haiku 4.5 (cheap and fast) — roughly **less than 1¢ per visit**.
- **Caching:** results are cached per answer-pattern, so repeated answer sets cost
  nothing. With the 6 fixed-option questions, real-world cost is typically a few
  dollars a month even with steady traffic.
- **Graceful fallback:** no key, or any API error → the app silently shows the
  curated roadmap only.

### Add your key (never commit it)

**Local — option A (environment variable):**
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-..."   # PowerShell (this terminal session)
python -m streamlit run app.py
```
```bash
export ANTHROPIC_API_KEY="sk-ant-..."   # macOS / Linux
python -m streamlit run app.py
```

**Local — option B (Streamlit secrets file):** create `.streamlit/secrets.toml`:
```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```
> `.streamlit/secrets.toml` is already in `.gitignore`, so it won't be committed.

**On Streamlit Community Cloud:** open your app → **Settings → Secrets** and paste:
```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```
Never paste your key into the code or commit it to GitHub.

---

## Files

| File              | What it is                                                        |
|-------------------|-------------------------------------------------------------------|
| `app.py`          | The Streamlit app — screens, questionnaire flow, and rendering.   |
| `roadmap_data.py` | The questions, the curated free-resource library, and the logic that assembles a roadmap from your answers. |
| `ai_suggestions.py` | Optional Claude (Haiku 4.5) layer for personalized fresh picks; cached per answer-pattern. |
| `pdf_export.py`   | Builds the downloadable PDF (via `fpdf2`), including the author credit footer. |
| `requirements.txt`| Python dependencies.                                              |

### Want to add or change resources?
Open `roadmap_data.py`. Add an entry to the `RESOURCES` dictionary, then reference
its key inside `build_roadmap()` so it gets placed into the right phase. No changes
to `app.py` are needed.

---

> **Note on links:** all linked resources are free at the time of writing.
> Course providers occasionally change their free/paid tiers — if a link changes,
> update it in `roadmap_data.py`.
