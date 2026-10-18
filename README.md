# AI Tech Consultant

A runnable capstone baseline with three connected workflows:
- Task 1: Knowledge Brain â€” sitemap ingestion, article chunks, lexical retrieval, citations, and human escalations.
- Task 2: Inbox Agent â€” 50 synthetic emails, knowledge API integration, draft review UI, and feedback log. Email delivery is simulated.
- Task 3: Meeting to Scope â€” transcript extraction, feasibility checks, scope, provisional estimates, proposal, and heuristic change report.

## Honest Limitations
This is a working baseline, not proof that every capstone criterion is complete. Retrieval is lexical, not embedding/vector-based. Images are stored as metadata but are not processed by a vision model. Daily scheduled ingestion and robust deleted-page reconciliation are not implemented. Task 3 estimates are illustrative and require human review. Email delivery is simulated. Evaluation results must be measured, not invented.

Claude calls are optional and require `ANTHROPIC_API_KEY`. Without a key, safe fallback behavior keeps the demo usable.

## Requirements
- Python 3.11+
- Node.js 20+
- Optional Anthropic API key

## Windows PowerShell Setup
Run from the extracted project root:

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
