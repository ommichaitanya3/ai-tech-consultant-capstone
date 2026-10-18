# Evaluations

**Status:** This is a test plan/template. Do not claim quality, cost, or latency results until they are measured.

Run at least 20 cases per task and compare at least two model/configuration choices on the same frozen cases, as required by the assignment. Record exact model IDs, prompt versions, latency, cost, pass/fail, and failure reason.

Task 1 cases: supported answers, multi-article questions, image-only evidence, missing evidence, citation support, updated/deleted pages, interrupted crawl, malformed request, timeout.
Task 2 cases: all categories, missing evidence, refund/quote/complaint, urgent email, prompt injection, duplicate review, edits, rejection, API outage.
Task 3 cases: explicit/inferred requirements, vague requests, contradictions, missing budget, feature feasibility, API outage, added/removed/modified scope, out-of-scope requests, approval.

CSV columns:
`task,case_id,model_or_config,prompt_version,expected,actual,quality_score,latency_ms,cost_usd,passed,failure_reason`

Report pass rate with denominator, citation support, abstention quality, classification accuracy, edit rate, unsafe commitments, requirement coverage, change-detection accuracy, estimate error against a human-reviewed reference, median/p95 latency, cost and failure rate. Preserve failed cases. Mark unrun tests pending.
