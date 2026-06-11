# 🧭 AI Roadmap for Managers

A small web app for **experienced but non-technical** project managers, delivery
managers and program leads who want to **understand AI without coding**.

It asks 6 quick questions and generates a **personalized, step-by-step learning
roadmap** that links only to **free** resources on the internet (courses you can
audit for free, YouTube explainers, practical guides, and tools with free tiers).

Built with [Streamlit](https://streamlit.io/) (Python).

---

## What it does

1. **Asks 6 questions** — your role, why you want to learn AI, your current level,
   weekly time, how you like to learn, and which topics interest you.
2. **Builds a 4-phase roadmap** — Foundations → How it works → Hands-on → Apply it
   to your work — choosing resources that match your answers.
3. **Lets you download it** as a Markdown file to keep.

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

## Files

| File              | What it is                                                        |
|-------------------|-------------------------------------------------------------------|
| `app.py`          | The Streamlit app — screens, questionnaire flow, and rendering.   |
| `roadmap_data.py` | The questions, the curated free-resource library, and the logic that assembles a roadmap from your answers. |
| `requirements.txt`| Python dependencies.                                              |

### Want to add or change resources?
Open `roadmap_data.py`. Add an entry to the `RESOURCES` dictionary, then reference
its key inside `build_roadmap()` so it gets placed into the right phase. No changes
to `app.py` are needed.

---

> **Note on links:** all linked resources are free at the time of writing.
> Course providers occasionally change their free/paid tiers — if a link changes,
> update it in `roadmap_data.py`.
