
import "dotenv/config";
import express from "express";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { emails } from "./data.js";
import {
    createDraft,
    recordReview,
    autonomyStatus,
    reviewLog
} from "./service.js";

const app = express();
app.use(express.json({ limit: "1mb" }));

const here = path.dirname(fileURLToPath(import.meta.url));
const publicDir = path.join(here, "..", "public");

app.use(express.static(publicDir));

app.get("/inbox", (_req, res) => {
    res.sendFile(path.join(publicDir, "inbox.html"));
});

app.get("/api/health", (_req, res) => {
    res.json({ status: "ok", delivery: "simulated" });
});

app.get("/api/emails", (_req, res) => res.json(emails));

app.post("/api/draft", async (req, res) => {
    try {
        const email = emails.find(e => e.id === req.body?.emailId);
        if (!email) {
            return res.status(404).json({ error: "Email not found" });
        }
        res.json(await createDraft(email));
    } catch (error) {
        res.status(500).json({
            error: error instanceof Error ? error.message : "Draft generation failed"
        });
    }
});

app.post("/api/review", (req, res) => {
    const { emailId, category, action, finalText, originalText, note } =
        req.body ?? {};

    if (
        !emailId ||
        !category ||
        !["approved", "edited", "rejected", "escalated"].includes(action)
    ) {
        return res.status(400).json({
            error: "emailId, category and valid action required"
        });
    }

    if (action === "approved" && !finalText) {
        return res.status(400).json({ error: "finalText required" });
    }

    recordReview({ emailId, category, action, finalText, originalText, note });

    res.json({
        status: "recorded",
        delivery:
            action === "approved"
                ? "simulated only; no real email sent"
                : "not sent"
    });
});

app.get("/api/reviews", (_req, res) => res.json(reviewLog));
app.get("/api/autonomy", (_req, res) => res.json(autonomyStatus()));

async function proxyPost(
    targetUrl: string,
    body: unknown,
    res: express.Response
) {
    try {
        const response = await fetch(targetUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
        });

        const responseText = await response.text();
        res.status(response.status);

        try {
            res.json(JSON.parse(responseText));
        } catch {
            res.send(responseText);
        }
    } catch (error) {
        res.status(502).json({
            error:
                "Could not connect to the service. Check that its server is running.",
            details: error instanceof Error ? error.message : String(error)
        });
    }
}

const knowledgeUrl = (
    process.env.KNOWLEDGE_API_URL || "http://127.0.0.1:8001"
).replace(/\/$/, "");

const meetingUrl = (
    process.env.MEETING_API_URL || "http://127.0.0.1:8003"
).replace(/\/$/, "");

app.post("/api/knowledge/query", (req, res) => {
    return proxyPost(`${knowledgeUrl}/query`, req.body, res);
});

app.post("/api/meeting/analyze", (req, res) => {
    return proxyPost(`${meetingUrl}/analyze`, req.body, res);
});

const port = Number(process.env.INBOX_PORT || 8002);

app.listen(port, () => {
    console.log(`AI Tech Consultant dashboard: http://localhost:${port}`);
});
