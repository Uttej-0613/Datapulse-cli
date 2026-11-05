import os
import re
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, inspect

DB_PATH = Path(os.getenv("DATAPULSE_DB", "./data/datapulse.db"))

def engine_for(path=None):
    target = Path(path or DB_PATH).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{target}", future=True)

def safe_identifier(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_]+", "_", value.strip()).strip("_").lower()
    if not cleaned or cleaned[0].isdigit():
        cleaned = f"table_{cleaned}"
    return cleaned[:60]

def ingest_csv(filepath, table_name=None, db_path=None):
    path = Path(filepath)
    if not path.is_file():
        raise FileNotFoundError(f"CSV file not found: {path}")
    if path.suffix.lower() != ".csv":
        raise ValueError("Only CSV files are supported.")
    frame = pd.read_csv(path)
    if frame.empty or len(frame.columns) == 0:
        raise ValueError("CSV contains no data columns or rows.")
    frame.columns = [safe_identifier(str(col)) for col in frame.columns]
    if len(set(frame.columns)) != len(frame.columns):
        raise ValueError("Column names collide after normalization.")
    table = safe_identifier(table_name or path.stem)
    with engine_for(db_path).begin() as conn:
        frame.to_sql(table, conn, if_exists="replace", index=False)
    return {"table": table, "rows": int(len(frame)), "columns": list(frame.columns)}

def list_tables(db_path=None):
    inspector = inspect(engine_for(db_path))
    return [{"name": table, "columns": [{"name": c["name"], "type": str(c["type"])} for c in inspector.get_columns(table)]} for table in inspector.get_table_names()]

def schema_text(db_path=None):
    parts = []
    for table in list_tables(db_path):
        cols = ", ".join(f"{c['name']} ({c['type']})" for c in table["columns"])
        parts.append(f"Table {table['name']}: {cols}")
    return "\n".join(parts) if parts else "No tables have been ingested."
