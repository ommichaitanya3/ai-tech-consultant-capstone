from pydantic import BaseModel, Field
from typing import Literal

class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=4000)
    top_k: int = Field(default=5, ge=1, le=10)

class Source(BaseModel):
    title: str
    url: str
    excerpt: str
    relevance: float

class QueryResponse(BaseModel):
    answer: str
    status: Literal["answered", "insufficient_evidence", "service_error"]
    sources: list[Source]
    needs_human: bool
    escalation_id: int | None = None

class EscalationRequest(BaseModel):
    question: str = Field(min_length=3, max_length=4000)
    reason: str = Field(min_length=3, max_length=1000)

class ResolveRequest(BaseModel):
    expert_answer: str = Field(min_length=3, max_length=5000)

class IngestionRequest(BaseModel):
    sitemap_url: str = "https://support.brilliantdirectories.com/support/sitemap.xml"
    max_pages: int = Field(default=20, ge=1, le=500)
