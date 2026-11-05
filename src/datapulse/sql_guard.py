import os
import sqlite3
from pathlib import Path
import sqlglot
from sqlglot import exp
from datapulse.database import DB_PATH


def _bounded_env_int(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        value = default
    return min(max(value, minimum), maximum)

MAX_ROWS = _bounded_env_int("MAX_QUERY_ROWS", 500, 1, 5000)
MAX_STEPS = _bounded_env_int("MAX_QUERY_STEPS", 5_000_000, 100_000, 50_000_000)

class UnsafeQuery(ValueError):
    pass


def validate_select(sql: str) -> str:
    if not sql or len(sql) > 12000:
        raise UnsafeQuery("SQL is empty or exceeds the 12,000-character limit.")
    try:
        statements = sqlglot.parse(sql, read="sqlite")
    except Exception as exc:
        raise UnsafeQuery("SQL could not be parsed.") from exc
    if len(statements) != 1 or statements[0] is None:
        raise UnsafeQuery("Exactly one SQL statement is allowed.")
    tree = statements[0]
    if not isinstance(tree, (exp.Select, exp.Union, exp.Intersect, exp.Except)):
        raise UnsafeQuery("Only SELECT queries, including CTEs and set operations, are allowed.")
    forbidden_names = ("Into", "Delete", "Insert", "Update", "Command", "Pragma", "Attach")
    for name in forbidden_names:
        node_type = getattr(exp, name, None)
        if node_type is not None and tree.find(node_type) is not None:
            raise UnsafeQuery("The query contains a prohibited SQL operation.")
    for function in tree.find_all(exp.Func):
        function_name = (function.name or function.sql_name()).lower()
        if function_name in {"load_extension", "readfile", "writefile", "fts3_tokenizer"}:
            raise UnsafeQuery("The query contains a prohibited SQLite function.")
    if not tree.args.get("limit"):
        tree = tree.limit(MAX_ROWS + 1)
    return tree.sql(dialect="sqlite")


def execute_readonly(sql: str, db_path=None) -> dict:
    safe_sql = validate_select(sql)
    path = Path(db_path or DB_PATH).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError("No DataPulse database exists. Ingest a CSV first.")
    connection = sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True, timeout=5)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA query_only=ON")
        connection.set_progress_handler(lambda: 1, MAX_STEPS)
        cursor = connection.execute(safe_sql)
        rows = [dict(row) for row in cursor.fetchmany(MAX_ROWS + 1)]
        truncated = len(rows) > MAX_ROWS
        rows = rows[:MAX_ROWS]
        return {"sql": safe_sql, "columns": [c[0] for c in cursor.description or []], "rows": rows, "row_count": len(rows), "truncated": truncated}
    except sqlite3.OperationalError as exc:
        if "interrupted" in str(exc).lower():
            raise TimeoutError("Query exceeded the SQLite execution budget.") from exc
        raise
    finally:
        connection.close()
