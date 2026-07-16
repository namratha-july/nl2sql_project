"""
nl_to_sql.py
Core logic: takes a natural language question + a DB schema description,
sends it to an LLM (OpenAI or Google Gemini), and returns a clean SQL query.
"""

import os
import re
import sqlite3


def get_schema_description(db_path: str) -> str:
    """
    Reads the SQLite database schema (tables + columns) and returns it
    as a readable text block to give the LLM context about the database.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    schema_lines = []
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        col_desc = ", ".join(f"{col[1]} ({col[2]})" for col in columns)
        schema_lines.append(f"Table: {table}\n  Columns: {col_desc}")

    conn.close()
    return "\n".join(schema_lines)


def build_prompt(question: str, schema: str) -> str:
    return f"""You are an expert SQL developer. Convert the user's natural
language question into a single valid SQLite SQL query.

Database schema:
{schema}

Rules:
- Return ONLY the SQL query, no explanations, no markdown code fences.
- Use only tables/columns that exist in the schema above.
- Prefer explicit JOINs with clear ON conditions.
- End the query with a semicolon.

Question: "{question}"

SQL query:"""


def clean_sql_output(raw_text: str) -> str:
    """Strips markdown fences / stray text so we're left with pure SQL."""
    text = raw_text.strip()
    text = re.sub(r"^```(sql)?", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"```$", "", text).strip()
    return text


# ---------------------------------------------------------------------
# OpenAI backend
# ---------------------------------------------------------------------
def generate_sql_openai(question: str, schema: str, api_key: str, model: str = "gpt-4o-mini") -> str:
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    prompt = build_prompt(question, schema)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You convert natural language to SQL."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )
    raw = response.choices[0].message.content
    return clean_sql_output(raw)


# ---------------------------------------------------------------------
# Google Gemini backend
# ---------------------------------------------------------------------
def generate_sql_gemini(question: str, schema: str, api_key: str, model: str = "gemini-1.5-flash") -> str:
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    prompt = build_prompt(question, schema)

    gen_model = genai.GenerativeModel(model)
    response = gen_model.generate_content(prompt)
    return clean_sql_output(response.text)


# ---------------------------------------------------------------------
# Groq backend (free developer tier, OpenAI-compatible API)
# ---------------------------------------------------------------------
def generate_sql_groq(question: str, schema: str, api_key: str, model: str = "llama-3.3-70b-versatile") -> str:
    from openai import OpenAI

    # Groq exposes an OpenAI-compatible endpoint, so we reuse the OpenAI
    # client but point it at Groq's base URL.
    client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
    prompt = build_prompt(question, schema)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You convert natural language to SQL."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )
    raw = response.choices[0].message.content
    return clean_sql_output(raw)


def generate_sql(question: str, schema: str, provider: str, api_key: str) -> str:
    """Dispatch to the selected LLM provider."""
    if provider == "OpenAI":
        return generate_sql_openai(question, schema, api_key)
    elif provider == "Gemini":
        return generate_sql_gemini(question, schema, api_key)
    elif provider == "Groq":
        return generate_sql_groq(question, schema, api_key)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def run_sql_query(db_path: str, sql: str):
    """Executes the SQL against the SQLite DB and returns (columns, rows)."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(sql)
    columns = [desc[0] for desc in cursor.description] if cursor.description else []
    rows = cursor.fetchall()
    conn.close()
    return columns, rows
