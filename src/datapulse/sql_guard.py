import os
import sqlite3
from pathlib import Path
import sqlglot
from sqlglot import exp
from datapulse.database import DB_PATH

MAX_ROWS = int(os.getenv("MAX_QUERY_ROWS", "500"))
MAX_STEPS = 5_000_000

class UnsafeQuery(ValueError):
    pass

def validate_select(sql: str) -> str:
    if not sql or len(sql) > 12000:
        raise UnsafeQuery("SQL is empty or exceeds the 12,000-character limit.")
    try:
        statements = sqlglot.parse(sql, read="sqlite")
    except Exception as exc:
        raise UnsafeQuery(f"SQL could not be parsed: {exc}") from exc
    if len(statements) != 1 or statements[0] is None:
        raise UnsafeQuery("Exactly one SQL statement is allowed.")
    tree = statements[0]
    if not isinstance(tree, (exp.Select, exp.Union, exp.Intersect, exp.Except)):
        raise UnsafeQuery("Only SELECT queries, including CTEs and set operations, are allowed.")
    if tree.find(exp.Into):
        raise UnsafeQuery("SELECT INTO is not allowed.")
    if not tree.args.get("limit"):
        tree = tree.limit(MAX_ROWS)
    return tree.sql(dialect="sqlite")

def execute_readonly(sql: str, db_path=None) -> dict:
    safe_sql = validate_select(sql)
    path = Path(db_path or DB_PATH).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError("No DataPulse database exists. Ingest a CSV first.")
    connection = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True, timeout=5)
    connection.row_factory = sqlite3.Row
    try:
        connection.set_progress_handler(lambda: 1, MAX_STEPS)
        cursor = connection.execute(safe_sql)
        rows = [dict(row) for row in cursor.fetchmany(MAX_ROWS)]
        return {"sql": safe_sql, "columns": [c[0] for c in cursor.description or []], "rows": rows, "row_count": len(rows), "truncated": len(rows) == MAX_ROWS}
    except sqlite3.OperationalError as exc:
        if "interrupted" in str(exc).lower():
            raise TimeoutError("Query exceeded the SQLite execution budget.") from exc
        raise
    finally:
        connection.close()
