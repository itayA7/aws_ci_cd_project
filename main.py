import os
from datetime import datetime, timezone

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Entries API")

# In-memory storage for now. In Phase 7 replace this list with RDS PostgreSQL
# (only create_entry, list_entries and ready need to change).
entries: list[dict] = []


class EntryIn(BaseModel):
    message: str = Field(min_length=1, max_length=280)


@app.get("/")
def root():
    return {"message": "Welcome to my app"}


@app.get("/health")
def health():
    # Liveness: the process is up. Never touches the database.
    return {"status": "ok"}


@app.get("/ready")
def ready():
    # Readiness: later, check the database connection here and return 503 on failure.
    return {"status": "ready"}


@app.get("/version")
def version():
    # APP_VERSION is set at build time (Git SHA in CI).
    return {"version": os.getenv("APP_VERSION", "dev")}


@app.post("/entries", status_code=201)
def create_entry(entry: EntryIn):
    item = {
        "id": len(entries) + 1,
        "message": entry.message,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    entries.append(item)
    return item


@app.get("/entries")
def list_entries():
    # Latest 10, newest first.
    return entries[::-1][:10]