# Decision Journal 🧠

**Preserve what you thought then. Layer what you know now. Learn without shame.**

Decision Journal is a personal, private tool for capturing the evolution of your thinking. It helps you log decisions exactly as you understood them in the moment, then return later to add honest reflections — creating a timeline of intellectual growth without rewriting history.

This is a **single-file Streamlit application** — easy to run locally or deploy instantly on Streamlit Community Cloud.

---

## Why Decision Journal Exists

Most software rewards revision, erasure, and optimization.  
Life, unfortunately, does not.

We learn not by editing the past, but by *seeing it clearly*.

Decision Journal is built on a simple but radical idea:

> **Your past reasoning deserves preservation, not correction.**

This tool does not help you “fix” old decisions.  
It helps you **understand how you think**, over time, without shame.

---

## Features

- **Immutable decision logs**  
  Original context, assumptions, and reasoning are preserved forever.

- **Layered reflections**  
  Add multiple timestamped reflections as time reveals new information.

- **Confidence & outcome scoring**  
  Rate how confident you were (1–10) and how things actually turned out.

- **Tagging system**  
  Categorize decisions (Career, Finance, Relationships, Health, Learning, etc.).

- **Powerful search & filters**  
  Full-text search across titles, context, reflections, and tags.

- **Dashboard**  
  See patterns: reflection rate, confidence calibration, outcome trends.

- **Timeline view**  
  A chronological journey of your thinking across months or years.

- **Export anytime**  
  Download your complete journal as JSON or CSV. Your data stays yours.

- **Guided reflection prompts**  
  Optional questions to help when the page feels empty.

- **International-ready**  
  Multi-language support (10 languages), timezone handling, RTL for Arabic,
  and culturally-aware default tags.

---

## Quick Start

### Run Locally

```bash
# Create project folder
mkdir decision-journal && cd decision-journal

# Create app.py and paste the full application code

# Install dependencies
pip install streamlit pytz pandas

# Run the app
streamlit run app.py

Open http://localhost:8501 in your browser.

---

## Deploy on Streamlit Community Cloud (Free)

1. Create a GitHub repository  
2. Add two files:
   - **app.py** — the complete application code  
   - **requirements.txt**:
     ```txt
     streamlit
     pytz
     pandas
     ```
3. Visit https://share.streamlit.io  
4. Click **New app**, connect your repository, and deploy

Data is stored locally in `decisions.db` and persisted on Streamlit Cloud.

---

## How to Use

### Log a Decision  
Capture the title, full context, reasoning, confidence score, and tags.

### Add a Reflection  
Return later to layer hindsight: what changed, what surprised you, and how the outcome unfolded.

### Browse & Search  
Explore decisions by time, tag, or keyword. Edit tags freely.

### Review the Dashboard & Timeline  
Watch patterns emerge — recurring biases, improving judgment, changing priorities.

### Export Your Journal  
Back up or analyze your data whenever you choose.

---

## International Features

### Language Selector (with flags)
- English  
- Arabic (RTL supported)  
- Spanish  
- French  
- German  
- Portuguese  
- Hindi  
- Chinese  
- Japanese  
- Russian  

### Localization & Accessibility
- Full right-to-left layout support for Arabic  
- Timezone selection using `pytz` with automatic conversion  
- Multiple date formats (EU, US, ISO, Asian)  
- Culturally-aware default tags per language  
- All UI text dynamically translated  

---

## Privacy & Ownership

- 100% local data — stored only in `decisions.db`  
- No external services  
- No tracking  
- No analytics  
- No accounts  

You own everything. Export anytime. Walk away anytime.

---

## Built With

- Python  
- Streamlit  
- SQLite (built-in, zero setup)  
- pytz for timezone handling  
- pandas for export utilities  

---

## Philosophy

Most tools encourage editing or deleting past mistakes.

Decision Journal does the opposite.

It preserves *intermediate thinking* — the assumptions, the uncertainty, the partial knowledge — because that is where learning actually lives.

Over time, something subtle happens:

- Confidence becomes calibrated  
- Biases become visible  
- Wisdom emerges without self-punishment  

Start with one meaningful past decision today.  
Return in a month and reflect.

That moment — when your past self becomes legible rather than embarrassing — is where the real value begins.

---

**Built with care in Durban, South Africa**  
by **Sifiso Cyprian**

For anyone, anywhere, who wants to think better over time. 🌍🧠

*January 2026*
