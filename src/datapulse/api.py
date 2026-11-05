import hmac
import logging
import os
import tempfile
from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from datapulse.database import ingest_csv, list_tables
from datapulse.sql_guard import execute_readonly, UnsafeQuery
from datapulse.nl2sql import ask

logger = logging.getLogger("datapulse")
app = FastAPI(title="DataPulse API", version="2.1.0")

class QueryRequest(BaseModel):
    sql: str = Field(min_length=1, max_length=12000)
class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)

@app.middleware("http")
async def api_key_guard(request: Request, call_next):
    environment = os.getenv("ENVIRONMENT", "development").lower()
    api_key = os.getenv("DATAPULSE_API_KEY")
    if environment == "production" and not api_key:
        return JSONResponse(status_code=503, content={"detail": "Service authentication is not configured."})
    if api_key and request.url.path != "/health":
        supplied = request.headers.get("X-API-Key", "")
        if not hmac.compare_digest(supplied, api_key):
            return JSONResponse(status_code=401, content={"detail": "A valid API key is required."})
    return await call_next(request)

@app.get("/health")
def health():
    return {"status": "ok", "service": "DataPulse", "version": "2.1.0"}

@app.get("/ready")
def ready():
    try:
        list_tables()
        return {"status": "ready", "database": "ok"}
    except Exception as exc:
        logger.exception("Readiness check failed")
        raise HTTPException(503, "Database is not ready.") from exc

@app.get("/tables")
def tables():
    return {"tables": list_tables()}

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(400, "Upload a CSV file.")
    try:
        limit = min(max(int(os.getenv("MAX_UPLOAD_BYTES", str(20 * 1024 * 1024))), 1024), 100 * 1024 * 1024)
    except ValueError:
        limit = 20 * 1024 * 1024
    payload = await file.read(limit + 1)
    if len(payload) > limit:
        raise HTTPException(413, "Maximum CSV upload size exceeded.")
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        tmp.write(payload)
        path = tmp.name
    try:
        return ingest_csv(path, Path(file.filename).stem)
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:
        logger.exception("CSV ingestion failed")
        raise HTTPException(500, "CSV ingestion failed. Check the file and server logs.") from exc
    finally:
        Path(path).unlink(missing_ok=True)

@app.post("/query")
def query(request: QueryRequest):
    try:
        return execute_readonly(request.sql)
    except (UnsafeQuery, ValueError) as exc:
        raise HTTPException(400, str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(409, "No database exists. Ingest a CSV first.") from exc
    except TimeoutError as exc:
        raise HTTPException(408, str(exc)) from exc
    except Exception as exc:
        logger.exception("SQL query failed")
        raise HTTPException(422, "SQL execution failed. Check the query and server logs.") from exc

@app.post("/ask")
def natural_language_query(request: AskRequest):
    try:
        return ask(request.question)
    except RuntimeError as exc:
        raise HTTPException(503, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:
        logger.exception("Natural-language SQL request failed")
        raise HTTPException(502, "AI SQL provider is temporarily unavailable.") from exc
