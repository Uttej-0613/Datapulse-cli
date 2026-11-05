from pathlib import Path
import tempfile
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from datapulse.database import ingest_csv, list_tables
from datapulse.sql_guard import execute_readonly, UnsafeQuery
from datapulse.nl2sql import ask

app = FastAPI(title="DataPulse API", version="2.0.0")

class QueryRequest(BaseModel):
    sql: str = Field(min_length=1, max_length=12000)
class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)

@app.get("/health")
def health():
    return {"status": "ok", "service": "DataPulse", "version": "2.0.0"}

@app.get("/tables")
def tables():
    return {"tables": list_tables()}

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(400, "Upload a CSV file.")
    payload = await file.read()
    if len(payload) > 20 * 1024 * 1024:
        raise HTTPException(413, "Maximum upload size is 20 MB.")
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        tmp.write(payload)
        path = tmp.name
    try:
        return ingest_csv(path, Path(file.filename).stem)
    except Exception as exc:
        raise HTTPException(400, str(exc))
    finally:
        Path(path).unlink(missing_ok=True)

@app.post("/query")
def query(request: QueryRequest):
    try:
        return execute_readonly(request.sql)
    except (UnsafeQuery, ValueError) as exc:
        raise HTTPException(400, str(exc))
    except Exception as exc:
        raise HTTPException(422, str(exc))

@app.post("/ask")
def natural_language_query(request: AskRequest):
    try:
        return ask(request.question)
    except RuntimeError as exc:
        raise HTTPException(503, str(exc))
    except Exception as exc:
        raise HTTPException(422, str(exc))
