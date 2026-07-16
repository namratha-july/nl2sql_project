# Natural Language to SQL Query Conversion

A web application that converts plain-English questions into SQL queries
using a large language model (Groq, OpenAI GPT, or Google Gemini), then
executes them against a sample SQLite database and shows the results.

## How it works

1. **Sample database** (`create_database.py`) — builds a small SQLite
   database (`company.db`) with 4 related tables: `departments`,
   `employees`, `products`, `sales`.
2. **Schema extraction** (`nl_to_sql.py`) — reads the actual table/column
   structure from the database so the LLM knows exactly what it can query.
3. **Prompting the LLM** — the user's question + the schema are sent to
   the LLM with instructions to return only a valid SQL query.
4. **Execution** — the generated SQL is run against the database with
   `sqlite3`, and results are displayed in a table.
5. **Web UI** (`app.py`) — built with Streamlit: enter a question, pick a
   provider, see the generated SQL and the results side by side.

## Project structure

```
nl2sql_project/
├── app.py               # Streamlit web app (main entry point)
├── nl_to_sql.py          # Core NL → SQL conversion logic
├── create_database.py    # Creates & seeds the sample SQLite database
├── requirements.txt       # Python dependencies
└── README.md
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Get an API key (Groq is recommended — free, fast, no credit card needed):
   - Groq: https://console.groq.com/keys
   - OpenAI: https://platform.openai.com/api-keys
   - Gemini: https://aistudio.google.com/app/apikey

   You can either paste the key into the sidebar when the app runs, or
   set it as an environment variable before launching:
   ```bash
   export GROQ_API_KEY="your-key-here"
   # or
   export OPENAI_API_KEY="your-key-here"
   # or
   export GEMINI_API_KEY="your-key-here"
   ```

3. Run the app:
   ```bash
   streamlit run app.py
   ```

4. Open the local URL Streamlit prints (usually `http://localhost:8501`).

## Example questions to try

- "List all employees in the Engineering department"
- "What is the average salary by department?"
- "Show the top 3 best-selling products by total quantity sold"
- "Which employees have sold more than 5 units of any single product?"
- "Show total sales revenue for each product"

## Database schema

- **departments**(department_id, department_name, location)
- **employees**(employee_id, first_name, last_name, department_id, salary, hire_date, email)
- **products**(product_id, product_name, category, price)
- **sales**(sale_id, employee_id, product_id, quantity, sale_date)

## Notes for extending this project

- Swap `company.db` for your own SQLite database — the schema is read
  dynamically, so no code changes are needed.
- To support other databases (PostgreSQL, MySQL), replace the `sqlite3`
  calls in `nl_to_sql.py` with the appropriate driver (e.g. `psycopg2`)
  and adjust `get_schema_description`.
- For a report/demo, screenshot the generated SQL + results panels for
  a few example questions — this makes a good "sample output" section.
