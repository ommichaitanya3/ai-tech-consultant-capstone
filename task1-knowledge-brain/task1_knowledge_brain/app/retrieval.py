import re
from .db import connect

STOP = {"the","a","an","is","are","how","do","i","to","and","or","for","of","in","on","my","can","please","what","with","it","this","that","where","change"}

def terms(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 1 and w not in STOP}

def search(question: str, top_k: int = 5):
    q = terms(question)
    if not q:
        return []

    with connect() as c:
        rows = c.execute(
            "SELECT ch.id,ch.url,ch.title,ch.heading,ch.content FROM chunks ch JOIN articles a ON a.url=ch.url WHERE a.active=1"
        ).fetchall()

    scored = []
    for row in rows:
        title_terms = terms(row["title"])
        heading_terms = terms(row["heading"] or "")
        body_terms = terms(row["content"])

        title_overlap = len(q & title_terms)
        heading_overlap = len(q & heading_terms)
        body_overlap = len(q & body_terms)

        score = (
            0.5 * title_overlap / max(1, len(q))
            + 0.3 * heading_overlap / max(1, len(q))
            + 0.2 * body_overlap / max(1, len(q))
        )

        if score >= 0.20:
            scored.append((score, row))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [
        {
            "title": r["title"],
            "url": r["url"],
            "excerpt": r["content"][:700],
            "relevance": round(s, 3),
        }
        for s, r in scored[:top_k]
    ]
