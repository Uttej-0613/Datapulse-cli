# DataPulse 2.0

DataPulse is a local-first analytics workspace for CSV profiling, data validation, multi-table SQL analysis, and safe AI-assisted natural-language-to-SQL.

## Features
- CSV profiling: dimensions, inferred types, missing values, duplicates, and numeric summaries.
- Row-level validation with rejected-row reporting.
- Ingest multiple CSVs as separate SQLite tables and join them.
- Natural-language-to-SQL grounded in the actual database schema.
- SQLGlot parsing, single-statement enforcement, read-only SQLite execution, instruction budget, and result caps.
- CLI, FastAPI API, and Streamlit dashboard.

## Install
Python 3.10+ recommended.

    python -m venv .venv
    pip install -e ".[dev]"

Copy .env.example to .env. Set OPENAI_API_KEY to enable AI SQL generation. Profiling, validation, ingestion, and manual SQL work without an API key.

## Run
    datapulse profile samples/sample_data.csv
    datapulse validate samples/sample_data.csv
    datapulse ingest samples/sample_data.csv --table employees
    datapulse tables
    datapulse query "SELECT * FROM employees LIMIT 10"
    datapulse ask "What is the average salary by department?"
    streamlit run dashboard.py
    uvicorn datapulse.api:app --app-dir src --reload

## Safety
Generated SQL is never trusted. It must parse as one SELECT/CTE/UNION statement, then runs through a read-only SQLite connection with an execution budget and row limit. Do not expose the local API publicly without authentication, authorization, rate limiting, and tenant isolation.

## Limitations
NL-to-SQL accuracy depends on schema quality and the configured model. Business definitions absent from the data cannot be inferred reliably. SQLite is for local analytics, not high-concurrency production workloads. Review generated SQL and outputs before using them.

Run tests with pytest.
