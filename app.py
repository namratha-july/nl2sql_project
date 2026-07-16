"""
app.py
Streamlit web app for Natural Language to SQL Query Conversion.

Run with:
    streamlit run app.py
"""

import os
import streamlit as st
import pandas as pd

from nl_to_sql import get_schema_description, generate_sql, run_sql_query
from create_database import create_database, DB_PATH

st.set_page_config(page_title="NL to SQL Converter", page_icon="🗄️", layout="wide")

st.title("🗄️ Natural Language to SQL Query Converter")
st.caption("Ask a question in plain English. An LLM converts it to SQL and runs it on a sample database.")

# ---------------------------------------------------------------------
# Setup: ensure sample DB exists
# ---------------------------------------------------------------------
if not os.path.exists(DB_PATH):
    create_database()

schema_text = get_schema_description(DB_PATH)

# ---------------------------------------------------------------------
# Sidebar: settings
# ---------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    provider = st.selectbox("LLM Provider", ["Groq", "OpenAI", "Gemini"])
    env_var_map = {
        "OpenAI": "OPENAI_API_KEY",
        "Gemini": "GEMINI_API_KEY",
        "Groq": "GROQ_API_KEY",
    }
    api_key = st.text_input(
        f"{provider} API Key",
        type="password",
        value=os.environ.get(env_var_map[provider], ""),
        help="Your key is used only for this session and is never stored.",
    )
    if provider == "Groq":
        st.caption("Free tier — get a key at console.groq.com/keys (no credit card needed).")
    st.divider()
    st.subheader("📋 Database Schema")
    st.code(schema_text, language="text")
    st.divider()
    if st.button("🔄 Reset sample database"):
        create_database()
        st.success("Database reset with fresh sample data.")

# ---------------------------------------------------------------------
# Example questions
# ---------------------------------------------------------------------
st.subheader("💡 Try an example, or type your own question below")
examples = [
    "List all employees in the Engineering department",
    "What is the average salary by department?",
    "Show the top 3 best-selling products by total quantity sold",
    "Which employees have sold more than 5 units of any single product?",
    "Show total sales revenue for each product",
]
cols = st.columns(len(examples))
selected_example = None
for c, ex in zip(cols, examples):
    if c.button(ex, use_container_width=True):
        selected_example = ex

# ---------------------------------------------------------------------
# Main input
# ---------------------------------------------------------------------
question = st.text_area(
    "Your question",
    value=selected_example if selected_example else "",
    placeholder="e.g. Show me all employees hired after 2020 along with their department name",
    height=80,
)

run_clicked = st.button("▶️ Generate & Run SQL", type="primary")

if run_clicked:
    if not api_key:
        st.error(f"Please enter your {provider} API key in the sidebar.")
    elif not question.strip():
        st.error("Please enter a question.")
    else:
        with st.spinner("Converting your question to SQL..."):
            try:
                sql_query = generate_sql(question, schema_text, provider, api_key)
            except Exception as e:
                st.error(f"Error generating SQL: {e}")
                sql_query = None

        if sql_query:
            st.subheader("📝 Generated SQL")
            st.code(sql_query, language="sql")

            with st.spinner("Running query..."):
                try:
                    columns, rows = run_sql_query(DB_PATH, sql_query)
                    st.subheader("📊 Results")
                    if rows:
                        df = pd.DataFrame(rows, columns=columns)
                        st.dataframe(df, use_container_width=True)
                        st.caption(f"{len(rows)} row(s) returned.")
                    else:
                        st.info("Query ran successfully but returned no rows.")
                except Exception as e:
                    st.error(f"Error executing SQL against the database: {e}")

st.divider()
st.caption(
    "Project: Natural Language to SQL Query Conversion · Built with Streamlit + LLM API · "
    "Sample SQLite database with employees, departments, products, and sales tables."
)
