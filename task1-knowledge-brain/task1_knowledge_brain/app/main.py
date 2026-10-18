from fastapi import FastAPI, HTTPException

from db import init_db, connect
from schemas import (
    QueryRequest,
    QueryResponse,
    EscalationRequest,
    ResolveRequest,
    IngestionRequest,
)
from retrieval import search
from llm import answer_with_claude
from ingestion import crawl_sitemap

app = FastAPI(
    title="Task 1 — Knowledge Brain",
    version="0.1.0",
)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "healthy"}


# Keep the remaining existing API endpoints below this line.
