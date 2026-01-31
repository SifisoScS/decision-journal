import streamlit as st
import sqlite3
import pandas as pd
import json
from datetime import datetime

# Page config
st.set_page_config(page_title="Decision Journal", page_icon="🧠", layout="wide")
st.markdown("""
    <style>
    .stMultiSelect [data-baseweb="select"] div[role="listbox"] div {
        background-color: white !important;
        color: black !important;
    }
    .stMultiSelect [data-baseweb="select"] div[role="listbox"] div:hover {
        background-color: #f0f2f6 !important;
    }
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #e0e0e0 !important;
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🧠 Decision Journal")
st.markdown("_Preserve what you thought then. Layer what you know now. Learn without shame._")

# Database connection
@st.cache_resource
def get_connection():
    return sqlite3.connect("decisions.db", check_same_thread=False)

import contextlib
conn = get_connection()
cursor = conn.cursor()

# Decisions table - add confidence if missing
cursor.execute("""
CREATE TABLE IF NOT EXISTS decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    context TEXT NOT NULL,
    timestamp TEXT NOT NULL
)
""")
# Add confidence column if not exists
with contextlib.suppress(sqlite3.OperationalError):
    cursor.execute("ALTER TABLE decisions ADD COLUMN confidence INTEGER")
    print("Added confidence column")
# Tags tables (unchanged, safe)
cursor.execute("""
CREATE TABLE IF NOT EXISTS tags (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS decision_tags (
    decision_id INTEGER,
    tag_id INTEGER,
    PRIMARY KEY (decision_id, tag_id)
)
""")

# Reflections table - add new scoring columns if missing
cursor.execute("""
CREATE TABLE IF NOT EXISTS reflections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_id INTEGER NOT NULL,
    thought_now TEXT NOT NULL,
    difference TEXT NOT NULL,
    timestamp TEXT NOT NULL
)
""")
# Add outcome_rating
with contextlib.suppress(sqlite3.OperationalError):
    cursor.execute("ALTER TABLE reflections ADD COLUMN outcome_rating INTEGER")
# Add reasoning_rating
with contextlib.suppress(sqlite3.OperationalError):
    cursor.execute("ALTER TABLE reflections ADD COLUMN reasoning_rating INTEGER")
conn.commit()

# Predefined tags
PREDEFINED_TAGS = [
    "Career", "Finance", "Relationships", "Health", 
    "Product", "Personal", "Investment", "Learning", "Family", "Other"
]

for tag in PREDEFINED_TAGS:
    cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
conn.commit()

def get_all_tags():
    cursor.execute("SELECT name FROM tags ORDER BY name")
    return [row[0] for row in cursor.fetchall()]

ALL_TAGS = get_all_tags()

# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", [
    "Home/Dashboard", 
    "Log Decision", 
    "Add Reflection", 
    "Browse & Search", 
    "Timeline View",
    "Export Data"
])

# Global search & filter (for relevant pages)
if page in ["Home/Dashboard", "Browse & Search", "Timeline View"]:
    st.sidebar.header("🔍 Search & Filter")
    search_query = st.sidebar.text_input("Search titles, context, reflections, tags")
    selected_tags = st.sidebar.multiselect("Filter by tags", ALL_TAGS)

# -----------------------------
# Home / Dashboard
# -----------------------------
if page == "Home/Dashboard":
    st.header("📊 Dashboard")

    cursor.execute("SELECT COUNT(*) FROM decisions")
    total_decisions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT decision_id) FROM reflections")
    with_reflections = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(confidence) FROM decisions WHERE confidence IS NOT NULL")
    avg_confidence = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(outcome_rating) FROM reflections WHERE outcome_rating IS NOT NULL")
    avg_outcome = cursor.fetchone()[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Decisions", total_decisions)
    col2.metric("With Reflections", with_reflections)
    col3.metric("Reflection Rate", f"{(with_reflections/total_decisions*100):.1f}%" if total_decisions else "0%")
    col4.metric("Avg Confidence (then)", f"{avg_confidence:.1f}" if avg_confidence else "-")

    if avg_outcome:
        st.metric("Average Outcome Rating", f"{avg_outcome:.1f}/10")

    st.markdown("### Recent Activity")
    params = []
    query = """
    SELECT DISTINCT d.id, d.title, d.timestamp
    FROM decisions d
    LEFT JOIN decision_tags dt ON d.id = dt.decision_id
    LEFT JOIN tags t ON dt.tag_id = t.tag_id
    LEFT JOIN reflections r ON d.id = r.decision_id
    WHERE 1=1
    """
    if search_query:
        like = f"%{search_query}%"
        query += " AND (d.title LIKE ? OR d.context LIKE ? OR r.thought_now LIKE ? OR r.difference LIKE ? OR t.name LIKE ?)"
        params.extend([like]*5)
    if selected_tags:
        placeholders = ",".join(["?"] * len(selected_tags))
        query += f" AND t.name IN ({placeholders})"
        params.extend(selected_tags)

    query += " ORDER BY d.timestamp DESC LIMIT 8"
    cursor.execute(query, params)
    recent = cursor.fetchall()

    for dec in recent:
        st.markdown(f"• **{dec[1]}** (ID: {dec[0]} — {dec[2][:10]})")

elif page == "Log Decision":
    st.header("📝 Log a New Decision")
    with st.form("log_decision"):
        title = st.text_input("Title")
        context = st.text_area("Context & Reasoning at the Time")
        confidence = st.slider("Confidence level at the time (1 = low, 10 = high)", 1, 10, 5)
        tags = st.multiselect("Tags", ALL_TAGS)
        if submitted := st.form_submit_button("Log Decision"):
            if title and context:
                ts = datetime.now().isoformat()
                cursor.execute(
                    "INSERT INTO decisions (title, context, confidence, timestamp) VALUES (?, ?, ?, ?)",
                    (title, context, confidence, ts)
                )
                decision_id = cursor.lastrowid

                for tag_name in tags:
                    cursor.execute("SELECT tag_id FROM tags WHERE name=?", (tag_name,))
                    tag_id = cursor.fetchone()[0]
                    cursor.execute("INSERT OR IGNORE INTO decision_tags (decision_id, tag_id) VALUES (?, ?)",
                                   (decision_id, tag_id))
                conn.commit()
                st.success(f"Decision logged! ID: **{decision_id}**")
                st.balloons()
            else:
                st.warning("Title and context required.")

elif page == "Add Reflection":
    st.header("✨ Add a Reflection")
    decision_id = st.number_input("Decision ID", min_value=1, step=1)

    cursor.execute("SELECT title, context, confidence, timestamp FROM decisions WHERE id=?", (decision_id,))
    original = cursor.fetchone()

    if original:
        st.info(f"**{original[0]}** (logged {original[3][:10]}) — Confidence then: {original[2]}/10")
        st.write("_Original context:_")
        st.write(original[1])

        # Tags
        cursor.execute("""SELECT t.name FROM tags t JOIN decision_tags dt ON t.tag_id = dt.tag_id WHERE dt.decision_id = ?""", (decision_id,))
        if tags := [row[0] for row in cursor.fetchall()]:
            st.caption("🏷️ " + ", ".join(tags))

        # Guided prompts
        st.markdown("#### Optional Guided Prompts")
        prompts = [
            "What outcome actually happened?",
            "What information did I miss or overweight?",
            "What would I tell my past self now?",
            "What alternative would I choose today?",
            "How has my thinking evolved?"
        ]
        chosen_prompt = st.selectbox("Pick a prompt to get started (or write freely)", ["None"] + prompts)

    with st.form("add_reflection"):
        if original and chosen_prompt and chosen_prompt != "None":
            st.info(f"💡 Prompt: {chosen_prompt}")

        thought_now = st.text_area("What I think now", height=150)
        difference = st.text_area("What I'd do differently / Key learnings", height=150)
        col1, col2 = st.columns(2)
        outcome_rating = col1.slider("Outcome rating (1 = bad, 10 = great)", 1, 10, 5)
        reasoning_rating = col2.slider("Reasoning quality then (hindsight, 1-10)", 1, 10, 5)
        submitted = st.form_submit_button("Save Reflection")

        if submitted and original:
            if thought_now and difference:
                ts = datetime.now().isoformat()
                cursor.execute("""
                INSERT INTO reflections 
                (decision_id, thought_now, difference, outcome_rating, reasoning_rating, timestamp) 
                VALUES (?, ?, ?, ?, ?, ?)
                """, (decision_id, thought_now, difference, outcome_rating, reasoning_rating, ts))
                conn.commit()
                st.success("Reflection saved!")
                st.balloons()
            else:
                st.warning("Please fill both reflection fields.")

elif page == "Browse & Search":
    st.header("📋 Browse & Search Decisions")

    # Same query logic as dashboard
    params = []
    query = """
    SELECT DISTINCT d.id, d.title, d.timestamp, d.confidence
    FROM decisions d
    LEFT JOIN decision_tags dt ON d.id = dt.decision_id
    LEFT JOIN tags t ON dt.tag_id = t.tag_id
    LEFT JOIN reflections r ON d.id = r.decision_id
    WHERE 1=1
    """
    if search_query:
        like = f"%{search_query}%"
        query += " AND (d.title LIKE ? OR d.context LIKE ? OR r.thought_now LIKE ? OR r.difference LIKE ? OR t.name LIKE ?)"
        params.extend([like]*5)
    if selected_tags:
        placeholders = ",".join(["?"] * len(selected_tags))
        query += f" AND t.name IN ({placeholders})"
        params.extend(selected_tags)

    query += " ORDER BY d.timestamp DESC"
    cursor.execute(query, params)
    if decisions := cursor.fetchall():
        for dec in decisions:
            conf = dec[3] if dec[3] is not None else "—"
            with st.expander(f"{dec[1]} (ID: {dec[0]} • {dec[2][:10]} • Confidence: {conf}/10)"):
                cursor.execute("SELECT context FROM decisions WHERE id=?", (dec[0],))
                st.write("**Original Context:** " + cursor.fetchone()[0])

                # Tags + Edit
                cursor.execute("""SELECT t.name, t.tag_id FROM tags t JOIN decision_tags dt ON t.tag_id = dt.tag_id WHERE dt.decision_id = ?""", (dec[0],))
                current_tags = [row[0] for row in cursor.fetchall()]
                tag_ids = [row[1] for row in cursor.fetchall()]
                st.caption("🏷️ Tags: " + ", ".join(current_tags) if current_tags else "No tags")

                with st.form(f"edit_tags_{dec[0]}"):
                    new_tags = st.multiselect("Update tags", ALL_TAGS, default=current_tags)
                    if st.form_submit_button("Save Tags"):
                        # Clear old
                        cursor.execute("DELETE FROM decision_tags WHERE decision_id=?", (dec[0],))
                        # Add new
                        for tag_name in new_tags:
                            cursor.execute("SELECT tag_id FROM tags WHERE name=?", (tag_name,))
                            tag_id = cursor.fetchone()[0]
                            cursor.execute("INSERT OR IGNORE INTO decision_tags (decision_id, tag_id) VALUES (?, ?)", (dec[0], tag_id))
                        conn.commit()
                        st.success("Tags updated!")
                        st.rerun()

                # Reflections
                cursor.execute("SELECT thought_now, difference, outcome_rating, reasoning_rating, timestamp FROM reflections WHERE decision_id=? ORDER BY timestamp", (dec[0],))
                if reflections := cursor.fetchall():
                    st.write("**Reflections:**")
                    for ref in reflections:
                        st.caption(f"{ref[4][:10]} — Outcome: {ref[2]}/10 | Reasoning then: {ref[3]}/10")
                        st.write(f"_Now:_ {ref[0]}")
                        st.write(f"_Difference:_ {ref[1]}")
                else:
                    st.info("No reflections yet.")
    else:
        st.info("No matching decisions. Try adjusting filters.")

elif page == "Timeline View":
    st.header("⏳ Timeline of Your Thinking")

    params = []
    query = "SELECT id, title, timestamp FROM decisions WHERE 1=1"
    if search_query or selected_tags:
        query = """
        SELECT DISTINCT d.id, d.title, d.timestamp 
        FROM decisions d
        LEFT JOIN decision_tags dt ON d.id = dt.decision_id
        LEFT JOIN tags t ON dt.tag_id = t.tag_id
        WHERE 1=1
        """
    if search_query:
        like = f"%{search_query}%"
        query += " AND (d.title LIKE ? OR d.context LIKE ? OR t.name LIKE ?)"
        params.extend([like]*3)
    if selected_tags:
        placeholders = ",".join(["?"] * len(selected_tags))
        query += f" AND t.name IN ({placeholders})"
        params.extend(selected_tags)

    query += " ORDER BY timestamp ASC"
    cursor.execute(query, params)
    if decisions := cursor.fetchall():
        for dec in decisions:
            date_str = dec[2][:10]
            with st.container():
                st.markdown(f"**{date_str}** — [{dec[1]}](?page=Browse+%26+Search) (ID: {dec[0]})")
                st.markdown("---")
    else:
        st.info("No decisions yet.")

else:  # Export Data
    st.header("💾 Export Your Journal")

    st.markdown("### Download as JSON")
    cursor.execute("""
    SELECT d.*, GROUP_CONCAT(t.name) as tags
    FROM decisions d
    LEFT JOIN decision_tags dt ON d.id = dt.decision_id
    LEFT JOIN tags t ON dt.tag_id = t.tag_id
    GROUP BY d.id
    """)
    decisions_data = cursor.fetchall()
    decisions_cols = [desc[0] for desc in cursor.description]

    cursor.execute("SELECT * FROM reflections")
    reflections_data = cursor.fetchall()
    reflections_cols = [desc[0] for desc in cursor.description]

    export_data = {
        "decisions": [dict(zip(decisions_cols, row)) for row in decisions_data],
        "reflections": [dict(zip(reflections_cols, row)) for row in reflections_data]
    }

    st.download_button(
        label="Download Full Journal (JSON)",
        data=json.dumps(export_data, indent=2, ensure_ascii=False),
        file_name=f"decision_journal_{datetime.now().strftime('%Y%m%d')}.json",
        mime="application/json"
    )

    st.markdown("### Download as CSV (Decisions + Reflections)")

    # Decisions DF
    df_dec = pd.read_sql_query("""
    SELECT d.id, d.title, d.timestamp, d.confidence, GROUP_CONCAT(t.name) as tags
    FROM decisions d
    LEFT JOIN decision_tags dt ON d.id = dt.decision_id
    LEFT JOIN tags t ON dt.tag_id = t.tag_id
    GROUP BY d.id
    """, conn)
    df_ref = pd.read_sql_query("SELECT * FROM reflections", conn)

    col1, col2 = st.columns(2)
    with col1:
        csv_dec = df_dec.to_csv(index=False)
        st.download_button("Download Decisions CSV", csv_dec, "decisions.csv", "text/csv")
    with col2:
        csv_ref = df_ref.to_csv(index=False)
        st.download_button("Download Reflections CSV", csv_ref, "reflections.csv", "text/csv")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Decision Journal** • Built with ❤️ by iKhaya AI")
st.sidebar.caption("Wisdom is the art of learning from yesterday's choices to make better ones tomorrow.")