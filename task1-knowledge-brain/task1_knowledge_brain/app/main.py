from fastapi import FastAPI, HTTPException
from .db import init_db, connect
from .schemas import QueryRequest, QueryResponse, EscalationRequest, ResolveRequest, IngestionRequest
from .retrieval import search
from .llm import answer_with_claude
from .ingestion import crawl_sitemap

app=FastAPI(title="Task 1 — Knowledge Brain",version="0.1.0")

@app.on_event("startup")
def startup(): init_db()

@app.get("/health")
def health():
    init_db()
    with connect() as c: count=c.execute("SELECT COUNT(*) n FROM articles WHERE active=1").fetchone()["n"]
    return {"status":"ok","active_articles":count,"retrieval":"lexical baseline"}

@app.post("/query",response_model=QueryResponse)
def query(req:QueryRequest):
    init_db()
    sources=search(req.question,req.top_k)
    if not sources:
        with connect() as c:
            cur=c.execute("INSERT INTO escalations(question,reason) VALUES(?,?)",(req.question,"No relevant evidence retrieved"))
            eid=cur.lastrowid
        return QueryResponse(answer="I couldn't find enough evidence in the current knowledge base to answer safely. This question has been flagged for human review.",status="insufficient_evidence",sources=[],needs_human=True,escalation_id=eid)
    generated=answer_with_claude(req.question,sources)
    answer=generated or ("I found potentially relevant documentation. Review these cited excerpts before acting: "+" ".join(s["excerpt"][:220] for s in sources[:2]))
    return QueryResponse(answer=answer,status="answered",sources=sources,needs_human=False)

@app.post("/ingestion/run")
async def ingestion(req:IngestionRequest):
    init_db()
    try: return await crawl_sitemap(req.sitemap_url,req.max_pages)
    except Exception as exc: raise HTTPException(status_code=502,detail=f"Ingestion failed: {str(exc)[:200]}")

@app.get("/ingestion/status")
def ingestion_status():
    init_db()
    with connect() as c:
        counts=c.execute("SELECT status,COUNT(*) count FROM ingestion GROUP BY status").fetchall()
        recent=c.execute("SELECT url,status,attempts,error,updated_at FROM ingestion ORDER BY updated_at DESC LIMIT 20").fetchall()
    return {"counts":{r["status"]:r["count"] for r in counts},"recent":[dict(r) for r in recent]}

@app.post("/escalations")
def create_escalation(req:EscalationRequest):
    init_db()
    with connect() as c:
        cur=c.execute("INSERT INTO escalations(question,reason) VALUES(?,?)",(req.question,req.reason))
        return {"id":cur.lastrowid,"status":"open"}

@app.post("/escalations/{escalation_id}/resolve")
def resolve_escalation(escalation_id:int,req:ResolveRequest):
    init_db()
    with connect() as c:
        row=c.execute("SELECT id FROM escalations WHERE id=?",(escalation_id,)).fetchone()
        if not row: raise HTTPException(status_code=404,detail="Escalation not found")
        c.execute("UPDATE escalations SET status='resolved',expert_answer=?,resolved_at=CURRENT_TIMESTAMP WHERE id=?",(req.expert_answer,escalation_id))
    return {"id":escalation_id,"status":"resolved","note":"Expert answer recorded for audit; automatic retrieval indexing is not enabled."}
