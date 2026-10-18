# AI Tech Consultant

A capstone project with three connected AI-assisted workflows:

- **Task 1 — Knowledge Brain:** Sitemap ingestion, article chunking, lexical retrieval, source citations, and human escalation.
- **Task 2 — Inbox Agent:** 50 synthetic emails, Knowledge Brain API integration, draft review UI, and review feedback logging. Email delivery is simulated.
- **Task 3 — Meeting-to-Scope:** Meeting transcript analysis, requirement extraction, feasibility checks, provisional estimates, proposal generation, and heuristic scope comparison.

## Honest Limitations

This project is a working baseline; not every assignment criterion is fully implemented.

- Retrieval uses lexical search rather than embedding-based vector search.
- Images are stored as metadata but are not analyzed by a vision model.
- Scheduled daily ingestion and robust deleted-page reconciliation are not implemented.
- Meeting requirements and estimates use heuristic logic and require human review.
- Email delivery is simulated; no real emails are sent.
- Evaluation results must be measured and reported honestly. No unmeasured quality, cost, or latency results are claimed.

Claude integration is optional and requires an `ANTHROPIC_API_KEY`. Fallback behavior allows the workflows to run without this key.

## Requirements

- Python 3.11+
- Node.js 20+
- npm
- Optional Anthropic API key

## Windows PowerShell Setup

Run these commands from the extracted project root.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install -r .\task1-knowledge-brain\requirements.txt
python -m pip install -r .\task3-meeting-to-scope\requirements.txt

Copy-Item .env.example .env

cd .\task2-inbox-agent
npm install
Copy-Item .env.example .env
cd ..
```

If `.env` already exists, do not overwrite it; add any required settings manually.

## Start the Services

Open three separate PowerShell terminals from the project root.

### Terminal 1 — Knowledge Brain

```powershell
cd .\task1-knowledge-brain
..\..\.venv\Scripts\python.exe -m uvicorn task1_knowledge_brain.app.main:app --host 127.0.0.1 --port 8001
```

### Terminal 2 — Meeting-to-Scope

```powershell
cd .\task3-meeting-to-scope
..\..\.venv\Scripts\python.exe -m uvicorn task3_meeting_to_scope.main:app --host 127.0.0.1 --port 8003
```

### Terminal 3 — Inbox Agent and Dashboard

```powershell
npm --prefix .\task2-inbox-agent run dev
```

Open the dashboard in your browser:

http://localhost:8002

Keep all three terminals running while using the application.

## Run Tests

Run these commands from the project root:

```powershell
.\.venv\Scripts\python.exe -m pytest .\task1-knowledge-brain\tests -v

npm --prefix .\task2-inbox-agent test
npm --prefix .\task2-inbox-agent run build

.\.venv\Scripts\python.exe -m pytest .\task3-meeting-to-scope\tests -v
```

## Evaluation

The current automated tests cover basic functionality. They do not establish that all assignment evaluation requirements have been met.

See `EVALS.md` for the evaluation plan, required test cases, model/configuration comparisons, and metrics to measure. Record actual results, preserve failures, and clearly label tests that have not yet been run.

## Safety and Human Review

- Treat email content, meeting transcripts, and retrieved documents as untrusted input.
- Review generated drafts and scope changes before accepting them.
- Verify citations and feasibility claims against source material.
- Estimates are provisional and must be approved by a human.
- Never put API keys or credentials in source control.

## Project Structure

- `task1-knowledge-brain/` — Knowledge ingestion and retrieval API.
- `task2-inbox-agent/` — Inbox workflow, review interface, and dashboard.
- `task3-meeting-to-scope/` — Meeting analysis and scope generation.
- `shared-docs/` — Shared project documents.
- `DESIGN.md` — Architecture and design decisions.
- `EVALS.md` — Evaluation plan and metrics.
- `AI_LOG.md` — AI-assisted development log.
- `PROGRESS.md` — Implementation progress.

## Current Status

The three services have basic working functionality, and the existing automated tests have passed in the development environment. This does not mean all rubric requirements are complete. See `DESIGN.md` and `EVALS.md` for known gaps and evaluation requirements.
