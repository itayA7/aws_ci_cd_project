import logging
import os

import psycopg
from fastapi import FastAPI, HTTPException, Query
from psycopg.rows import dict_row
from pydantic import BaseModel, Field

app = FastAPI(title="Entries API")
logger = logging.getLogger("app")


class EntryIn(BaseModel):
    message: str = Field(min_length=1, max_length=280)


# ---------------------------------------------------------------------------
# Database (PostgreSQL). Connection settings come from environment variables.
# In AWS, ECS injects DB_USER and DB_PASSWORD from Secrets Manager.
# ---------------------------------------------------------------------------
CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS entries (
    id         BIGSERIAL PRIMARY KEY,
    message    VARCHAR(280) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
)
"""

_table_ready = False


def get_conn():
    """Open a connection, and create the table the first time it is needed."""
    global _table_ready
    conn = psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "appdb"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        connect_timeout=5,
        row_factory=dict_row,
    )
    if not _table_ready:
        conn.execute(CREATE_TABLE)
        conn.commit()
        _table_ready = True
    return conn


def db_add_entry(message: str) -> dict:
    with get_conn() as conn:
        return conn.execute(
            "INSERT INTO entries (message) VALUES (%s) "
            "RETURNING id, message, created_at",
            (message,),
        ).fetchone()


def db_latest_entries(limit: int = 10) -> list[dict]:
    with get_conn() as conn:
        return conn.execute(
            "SELECT id, message, created_at FROM entries ORDER BY id DESC LIMIT %s",
            (limit,),
        ).fetchall()


def db_ping() -> None:
    with get_conn() as conn:
        conn.execute("SELECT 1")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "Welcome to my app"}


@app.get("/health")
def health():
    # Liveness: the process is up. Never touches the database.
    return {"status": "ok"}


@app.get("/ready")
def ready():
    # Readiness: the database must be reachable.
    try:
        db_ping()
    except Exception:
        logger.exception("readiness check failed")
        raise HTTPException(status_code=503, detail="database not ready")
    return {"status": "ready"}


@app.get("/version")
def version():
    # APP_VERSION is set at build time (Git SHA in CI).
    return {"version": os.getenv("APP_VERSION", "dev")}


@app.post("/entries", status_code=201)
def create_entry(entry: EntryIn):
    try:
        return db_add_entry(entry.message)
    except psycopg.Error:
        logger.exception("failed to save entry")
        raise HTTPException(status_code=503, detail="database unavailable")


@app.get("/entries")
def list_entries(limit: int = Query(10, ge=1, le=100)):
    # Latest entries, newest first.
    try:
        return db_latest_entries(limit)
    except psycopg.Error:
        logger.exception("failed to read entries")
        raise HTTPException(status_code=503, detail="database unavailable")
