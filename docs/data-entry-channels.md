# Data Entry Channels
> How data gets into the Job Hunt system
> Owner: Mahdi Saadat | May 2026

---

## Overview

Every piece of data the system uses — job postings, market signals, company intel, truth about you — enters through one of these channels. Each channel has a current state (what works today) and a target state (what it becomes at hour2).

```
CHANNEL             HOUR1 (NOW)                 HOUR2 (TARGET)
──────────────────────────────────────────────────────────────
Web Fetch           Claude fetches on request   jh_fetch_url tool in UI
Semi-login          Browser extension           Same (extension IS the bridge)
Platform feeds      Extension per site          Extension + RSS for open feeds
Email               Gmail MCP (manual trigger)  Polling loop / push webhook
Chat                Paste in Claude Code / UI   Same
File drop           Drop in data-storage/       Same + UI drag-and-drop
RSS feeds           Not yet                     Subscribe once, auto-ingest
Webhook / API POST  /api/jobs/intake exists now Zapier / Make / direct POST
```

---

## CH-01 — Web Fetch

**What it is:** Provide a URL, the system fetches the page and ingests it.

**Hour1:** Claude Code fetches it via WebFetch tool. Paste the link in chat.
```
Fetch this job posting and ingest it: https://company.com/jobs/senior-engineer
```

**Hour2:** `jh_fetch_url` MCP tool + UI input field for URL. Recursive discovery (follow links from a jobs page to individual postings) is a Phase 2 feature.

**Works on:** Any public job page. For authenticated pages, use the browser extension instead.

**Limitations:** JavaScript-heavy SPAs may not render properly via raw fetch. Use the extension for those.

---

## CH-02 — Browser Extension (Primary Capture Channel)

**What it is:** One-click capture from any job page you're browsing in Chrome.

**Current state:** Basic capture exists (`src/extension/`) — captures page URL + raw text, POSTs to `localhost:8001/api/jobs/intake`.

**Semi-login:** The extension runs inside your logged-in Chrome session. It captures the rendered DOM of whatever page you're on — including authenticated views on LinkedIn, Toptal, Contra, etc. No cookie sharing or credentials needed. Your login is already there; the extension just reads what's on screen.

**Target: Multi-facade extension**

One extension, multiple behaviors per site. Each facade is a `content_script` injected at matching URLs that knows how to extract structured data from that site's specific DOM.

| Facade | URL Pattern | What it extracts |
|--------|-------------|-----------------|
| LinkedIn Job List | `*linkedin.com/jobs/search*` | All visible job cards: title, company, location, link |
| LinkedIn Job Detail | `*linkedin.com/jobs/view/*` | Full JD, company, apply URL, easy-apply flag |
| LinkedIn Company | `*linkedin.com/company/*` | Company size, industry, recent posts, hiring signal |
| Toptal | `*toptal.com/*/jobs*` | Role, rate, contract type, skills |
| Contra | `*contra.com/*` | Opportunity details, client info |
| Wellfound | `*wellfound.com/jobs*` | Job details, funding stage, team size |
| Generic (fallback) | `*` | Raw page text + URL (current behavior) |

**Implementation notes:**
- Each facade lives in `src/extension/facades/{site}.js`
- Manifest `content_scripts` array maps URL patterns to facade scripts
- Facade extracts structured JSON, sends to intake endpoint
- Badge shows: "Captured — [title] at [company]" instead of raw ID

---

## CH-03 — Platform Feeds (RSS + Structured Sources)

**What it is:** Sources that publish structured job data directly — no scraping needed.

**RSS feeds (Indeed, Wellfound, others):**
- Indeed job alert emails contain RSS links. Subscribe to a search query → RSS feed URL.
- The system fetches the feed, extracts job listings, ingests automatically.
- No login required. Set it up once and it runs.

**LinkedIn:**
- No public jobs API for external apps. LinkedIn locks this down hard.
- Use the extension instead (CH-02).

**Toptal / Contra / Upwork:**
- No public feed API for job listings.
- Use the extension instead (CH-02).

**Hour2 implementation:** `jh_poll_rss` tool reads a list of RSS URLs from config, fetches new items since last poll, ingests each as a raw job.

---

## CH-04 — Email Entry

**What it is:** Job alerts, recruiter emails, and any job-related content arrive at an email address and get ingested automatically.

**Account:** mahdi.saadat.work@gmail.com (legitimate job-hunt use only — no spam subscriptions)

**Good uses for this address:**
- Indeed / LinkedIn job alert emails (digest of new postings)
- Recruiter outreach emails you want to log
- Platform notification emails with job matches

**Hour1:** Gmail MCP is available in Claude Code right now.
```
Check my email for any new job-related messages and ingest what's relevant.
```
The Gmail MCP can read, search, and label emails on demand.

**Hour2:** Scheduled polling loop checks for new emails tagged `job-hunt`, extracts content, auto-ingests. Non-job emails are never touched.

**Rule:** This address is for real, legitimate job-hunt signals only. No throwaway newsletter subscriptions. Everything ingested must be worth having in the pipeline.

---

## CH-05 — Chat Entry

**What it is:** You paste content or describe something directly in Claude Code or the UI chat. The AI ingests it on the spot.

**Works for:** Any unstructured content — job postings you copied, articles you read, recruiter messages, your own notes.

**Usage:**
```
Here's a job posting I found:
[paste raw text]
Ingest this.
```
```
Add to my truth: I finished the AWS Solutions Architect cert last week.
```
```
Here's a recruiter email I got:
[paste]
Score this against my profile and create a company record if there isn't one.
```

**Hour1 + Hour2:** Same. Chat is the most flexible entry point. It's always the right answer when nothing else fits.

---

## CH-06 — File Drop

**What it is:** Drop files into a watched folder. The system picks them up on the next ingestion run.

**Current folders:**
| Folder | What goes here |
|--------|---------------|
| `data-storage/truth/chips/` | Any truth input — old resumes, notes, LinkedIn export, anything about you |
| `data-storage/jobs/raw/` | Raw job postings (text files, copied JDs) |

**No schema required.** Drop a `.md` or `.txt` file. Name it anything. The AI figures out what it is.

**Hour1:** Drop the file, then tell Claude Code to ingest it:
```
There's a new chip in truth/chips/ — please ingest it.
```

**Hour2:** File watcher (`src/watcher.py`) detects new files and auto-triggers ingestion. UI shows a "pending" badge.

---

## CH-07 — RSS / Job Alert Feeds

*(Separate from CH-03 platform feeds — this is the generic RSS mechanism)*

**What it is:** Any job board that publishes an RSS feed or email digest with a structured feed link.

**Sources that work:**
- Indeed job alerts (email digest contains RSS link)
- Wellfound job alerts
- Some company career pages (e.g., Greenhouse-hosted pages often have feeds)

**Setup:** Save the RSS URL in `rules/config.yaml` under a `rss-feeds:` key. The system polls periodically.

**Hour2:** `jh_poll_feeds` tool iterates the configured feed URLs, fetches new items since last check, ingests each one via the standard job intake pipeline.

---

## CH-08 — Webhook / API POST

**What it is:** Anything that can make an HTTP POST request can push data into the system directly.

**Endpoint:** `POST http://localhost:8001/api/jobs/intake`

**Payload:**
```json
{
  "text": "raw job description or content",
  "source_url": "https://...",
  "job_type": "single"
}
```

**Works today.** The browser extension already uses this endpoint. Any automation tool (Zapier, Make.com, n8n, custom scripts) can POST to it.

**Hour2 use cases:**
- Zapier: "New email in Gmail matching job alert → POST to intake"
- Make.com: "New LinkedIn job alert → POST to intake"
- Custom script: "Scrape company careers page weekly → POST each new listing"

---

## What's Missing / Not Worth It

| Channel | Status | Reason |
|---------|--------|--------|
| LinkedIn API | Skip | Locked down for external job data. Extension is better. |
| Direct calendar sync | Later | Interview scheduling is a doc, not a calendar event, for now |
| Mobile capture | Later | Phone → email or clipboard → chat is good enough for now |
| Automated screen capture | Skip | Too fragile. Extension is cleaner. |

---

## Priority Order for Hour2 Build

1. **Extension multi-facade** (CH-02) — highest daily friction. LinkedIn is where most jobs are.
2. **RSS feeds** (CH-07) — zero-friction passive intake once set up.
3. **Email polling** (CH-04) — Gmail MCP already works; just needs a scheduled trigger.
4. **Web fetch tool** (CH-01) — already works via Claude Code; formalizing as a UI tool is quick.
5. **Webhook integrations** (CH-08) — endpoint exists; document and enable Zapier/Make connections.
