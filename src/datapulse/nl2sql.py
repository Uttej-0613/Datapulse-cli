import os
import re
from dotenv import load_dotenv
from openai import OpenAI
from datapulse.database import schema_text
from datapulse.sql_guard import execute_readonly

load_dotenv()

def generate_sql(question: str) -> str:
    if not question or len(question) > 2000:
        raise ValueError("Question must contain 1–2,000 characters.")
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("Set OPENAI_API_KEY in .env to enable natural-language SQL.")
    client = OpenAI(api_key=key)
    response = client.chat.completions.create(model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"), temperature=0, messages=[
        {"role": "system", "content": "Translate the question into exactly one SQLite SELECT query using only the supplied schema. Joins and CTEs are allowed. Never invent tables or columns. Never emit writes, DDL, PRAGMA, ATTACH, multiple statements, or markdown. Return SQL only. Add LIMIT 500."},
        {"role": "user", "content": f"Schema:\n{schema_text()}\n\nQuestion: {question}"}
    ])
    sql = (response.choices[0].message.content or "").strip()
    return re.sub(r"^\s*```(?:sql)?\s*|\s*```\s*$", "", sql, flags=re.I).strip()

def ask(question: str) -> dict:
    sql = generate_sql(question)
    return {"question": question, **execute_readonly(sql)}
