import os,re
from pathlib import Path
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field
import httpx
from dotenv import load_dotenv

ROOT=Path(__file__).resolve().parents[2]
load_dotenv(ROOT/".env")
KB_URL=os.getenv("KNOWLEDGE_API_URL","http://localhost:8001")
app=FastAPI(title="Task 3 — Meeting to Scope",version="0.1.0")

class AnalyzeRequest(BaseModel):
 project_id:str=Field(min_length=2,max_length=100)
 transcript:str=Field(min_length=20,max_length=100000)
 baseline:dict|None=None

async def ask_knowledge(question:str):
 try:
  async with httpx.AsyncClient(timeout=8) as client:
   response=await client.post(f"{KB_URL}/query",json={"question":question,"top_k":4})
   response.raise_for_status()
   return response.json()
 except Exception:
  return {"answer":"Knowledge service unavailable; feasibility needs human verification.","status":"service_error","sources":[],"needs_human":True}

def extract_requirements(transcript:str):
 sentences=[s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+",transcript) if len(s.strip())>15]
 keywords=("need","want","would like","must","should","add","remove","change","search","filter","payment","checkout","mobile","notification","deadline","launch")
 found=[]
 for i,sentence in enumerate(sentences):
  if any(k in sentence.lower() for k in keywords):
   found.append({"id":f"REQ-{i+1:03d}","description":sentence,"source_passage":sentence,
    "certainty":"explicit" if any(k in sentence.lower() for k in ("need","must","please","remove","change","add")) else "inferred",
    "status":"needs_review","priority":"must-have" if "must" in sentence.lower() else "should-have"})
 return found[:40] or [{"id":"REQ-001","description":"No clear requirement extracted; clarify project goals.","source_passage":transcript[:300],"certainty":"inferred","status":"needs_clarification","priority":"unknown"}]

async def build_result(req:AnalyzeRequest):
 requirements=extract_requirements(req.transcript)
 feasibility=[]
 for item in requirements[:10]:
  kb=await ask_knowledge(item["description"])
  feasibility.append({"requirement_id":item["id"],
   "classification":"existing_configuration_or_feature_to_verify" if kb["status"]=="answered" and kb.get("sources") else "needs_clarification",
   "evidence_status":kb["status"],"answer":kb["answer"],"sources":kb.get("sources",[]),"human_review_required":True})
 tasks=[{"requirement_id":x["id"],"task":f"Clarify, implement and test: {x['description'][:100]}","low_hours":2,"likely_hours":4,"high_hours":8,"assumptions":["Illustrative estimate; validate with an engineer"],"confidence":"low"} for x in requirements]
 totals={"low_hours":sum(x["low_hours"] for x in tasks),"likely_hours":sum(x["likely_hours"] for x in tasks),"high_hours":sum(x["high_hours"] for x in tasks)}
 scope={"project_id":req.project_id,"version":1,"objective":"Convert the client discussion into a reviewable scope.","requirements":requirements,
  "deliverables":[{"name":x["task"],"acceptance_criteria":"Client confirmation required."} for x in tasks],
  "exclusions":["Unapproved integrations, prices and delivery commitments"],"assumptions":["All estimates are provisional and require engineering review"],
  "open_questions":["Confirm acceptance criteria, budget, deadline, integrations and dependencies"],"approval_status":"pending_human_approval"}
 proposal={"title":f"Draft proposal — {req.project_id}","executive_summary":"Draft based on supplied meeting transcript; review before sharing.",
  "scope":scope,"estimate":{**totals,"note":"Not a commercial quote; figures are provisional."},
  "timeline":"To be confirmed after validating requirements and dependencies.","approval_status":"pending_human_approval"}
 changes=[]
 if req.baseline:
  old={x.get("id"):x for x in req.baseline.get("requirements",[]) if x.get("id")}
  new={x.get("id"):x for x in requirements if x.get("id")}
  for rid,item in new.items():
   if rid not in old: changes.append({"type":"added","requirement_id":rid,"description":item["description"]})
   elif old[rid].get("description")!=item.get("description"): changes.append({"type":"modified","requirement_id":rid,"description":item["description"]})
  for rid,item in old.items():
   if rid not in new: changes.append({"type":"removed","requirement_id":rid,"description":item.get("description","")})
  if not changes: changes=[{"type":"review_needed","note":"No ID-based differences found; verify manually because extracted IDs depend on sentence order."}]
 return {"project_id":req.project_id,"requirements":requirements,"feasibility":feasibility,"scope":scope,"tasks":tasks,"estimate_summary":totals,
  "proposal":proposal,"changes":changes,"approval_required":True,"limitations":["Estimates are illustrative.","Requirement matching is heuristic and requires human validation.","No proposal is sent automatically."]}

@app.get("/health")
def health(): return {"status":"ok","knowledge_api":KB_URL}
@app.post("/analyze")
async def analyze(req:AnalyzeRequest): return await build_result(req)
@app.post("/compare")
async def compare(req:AnalyzeRequest):
 if not req.baseline: raise HTTPException(status_code=400,detail="baseline is required for comparison")
 return await build_result(req)
