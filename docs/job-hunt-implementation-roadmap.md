# Job Hunt System — Implementation Roadmap
> Owner: Mahdi Saadat | May 2026

---

## Goals Recap

| Priority | Goal | Horizon |
|---|---|---|
| 1 | Find next contract quickly — in 2 months | Immediate |
| 2 | Sustainable search system — 4-10 contracts/year, low overhead | Medium |
| 3 | Portfolio and business optimization — richer skills, higher rates | Ongoing |

**The critical insight driving this roadmap:**
Goal 1 cannot wait for Goal 2 to be built.
Start searching on day one using Claude chat + prompts.
Build the system in parallel. The system supports the next search cycle, not just this one.

---

## Phase Map

```
TODAY ──────────────────────────────────────────────────────────► ONGOING

Phase 0       Phase 1          Phase 2           Phase 3        Phase 4
DAY 1         WEEKS 1-3        WEEKS 3-6         MONTH 2-3+     MONTH 3+
Manual        Core Engine      Full System       Cadence        Optimization
Search Now    SAM Backbone     All 16 WF         Sustainable    Portfolio Loop

[GOAL 1 ──────────────────────────►]
              [GOAL 2 ─────────────────────────────────────────►]
                                                 [GOAL 3 ───────────────────►]
```

---

## Phase 0 — Search Now (Day 1, No Code)

**Goal served:** Goal 1 — find next contract immediately
**Time needed:** Half a day to set up, then 30 min/day ongoing
**Principle:** Don't wait for the system. Use Claude chat as the system right now.

### What you do

**Set up your working folder (30 min)**
Create the folder structure from the architecture doc manually.
Seed `tier2-core/truth.md` from your existing TRUTH.md — it's already written.
Write `rules/config.yaml` — rates, location rules, Boston logic, availability date.
This becomes the source of truth that Claude reads in every session.

**Activate Toptal immediately (today)**
Toptal vetting takes 2–3 weeks.
If you don't start today you lose the window for your August target.
Use the Toptal profile prompt from the workflows doc to write your bio.
Submit the application this week.

**Update LinkedIn (this week)**
Headline: what you do + what you build + open to contract
About section: generated from master truth using WF-09 prompt
Open to Work → recruiters only → Contract type → available August 2026
This takes 1 hour. It runs in the background forever after.

**Network activation (this week)**
5 messages to Nextmark colleagues using WF-07 prompt.
1 message to Beta Technology contact — you're wrapping up, staying available.
These 6 messages are your highest-ROI action in the entire system.

**Start daily dump habit (day 1)**
Every morning: paste whatever you read (job emails, LinkedIn, articles) into this Claude Project.
Use the Universal Dump prompt. Let AI extract jobs, companies, signals.
Review the staged report. Commit what's good.
This habit is the system. Everything else automates it.

### How Claude helps right now (no code)
All 16 workflow prompts from the workflows doc work in this chat today.
This Claude Project holds your master truth in context.
You dump, review, refine, commit. AI tells you what to save where.

### Deliverable
Active search running on day 1.
Toptal application in.
LinkedIn updated.
Network activated.
Daily dump habit started.

---

## Phase 1 — Core Engine (Weeks 1–3)

**Goal served:** Goal 1 (faster applications) + Goal 2 foundation
**Time needed:** 1–2 weeks part-time with Claude Code
**Principle:** Build the minimum system that makes active search meaningfully faster.

### What Claude Code builds

**Truth Management**
Drop a chip file → system reads it → merges into master truth → flags anomalies.
File watcher on `/tier1-inputs/chips/` triggers automatically.
No more manual editing of master truth. You just drop chips.

**Job Intake + Digestion**
POST endpoint that accepts raw JD text.
Digestion pipeline: extract structured fields, score against master truth + rules config.
Auto-creates company record on first encounter with a company.
Outputs a clean job record in `/tier2-core/jobs/`.

**Review Loop (staged reports)**
Every ingestion produces a staged report — nothing committed yet.
You review in the terminal or a simple web output.
Say commit → files written to disk.
Say exclude, refine, find similar → loop continues.

**Application Package Generator**
Give it a job ID → reads master truth + job record + company record + rules.
Outputs: tailored resume (correct group), cover letter, interview prep doc.
Hallucination guard: validates no skill claimed that isn't in master truth.

**MCP Server**
Claude Code connects to the system via MCP.
Key tools: ingest_truth_chip, digest_job, score_job, generate_application_package.
This means you can run everything from the Claude Code terminal without switching tools.

### What you tell Claude Code to start
```
Read the architecture doc at /job-hunt/docs/architecture.md
and the roadmap at /job-hunt/docs/roadmap.md.

Reference SAM at [path to SAM] for:
- MCP server structure
- File watcher pattern
- Staged report format
- Config/boot validation

Build Phase 1: truth management, job intake + digestion,
review loop, application package generator, MCP server.

Storage is local markdown files. No database.
FastAPI for the backend. Python for pipeline logic.
Start with the MCP server scaffold and truth management.
```

### Deliverable
Drop a chip → master truth updates.
Paste a JD → structured record + score in 10 seconds.
Type one command → full application package generated.
Everything reviewable before commit.

---

## Phase 2 — Full System (Weeks 3–6)

**Goal served:** Goal 2 — all 16 workflows have system support
**Time needed:** 2–3 weeks part-time with Claude Code
**Principle:** No workflow should require more than 5 minutes of your time.

### What Claude Code builds

**Browser Extension**
One-click capture from any job posting on any site.
POSTs page URL + text to local intake endpoint.
Works on LinkedIn, Wellfound, Contra, Toptal, Upwork, direct company pages, anywhere.
Badge confirms capture. No switching to the terminal.

**Company Intelligence**
Company registry becomes a real database of records.
Auto-enriched from every job intake.
Manual enrichment: dump a news article mentioning a company → company record updated.
Index view: list all companies by status (warm, active, cold, blacklisted).

**Platform Profile Generator**
Generate LinkedIn, Toptal, Contra, portfolio content from master truth in one command.
Flags which profiles are stale when master truth changes.

**Follow-up Scheduler**
Logs every application with submission date.
Surfaces applications that need follow-up (day 5, day 10, day 20).
Drafts the follow-up message. You send.

**Exposure Content Pipeline**
Give it a topic or project → drafts LinkedIn post in your voice.
Maintains a draft queue. You review, edit, post.
Tracks what was published and when.

**Market Intelligence Aggregator**
Accumulates patterns across all job dumps over time.
Weekly summary: which skills appeared most, rate trends, role demand.
Feeds gap analysis automatically.

**Network Registry**
Contact records with relationship warmth, last touchpoint, relevance.
Quarterly activation prompt: surfaces who to reach out to.
Drafts personalized messages per contact.

**Pipeline Dashboard**
Simple view of all active applications with status and timing.
Surfaces conflicts (offer expires before top choice decides).
Suggests next actions.

### What you tell Claude Code
```
Phase 1 is complete. Now build Phase 2.

Priority order:
1. Browser extension (highest daily friction to remove)
2. Follow-up scheduler (nothing should fall through)
3. Company intelligence (persistent across search cycles)
4. Platform profile generator
5. Market intelligence aggregator
6. Network registry
7. Exposure content pipeline
8. Pipeline dashboard

Each should integrate with the existing MCP server — 
add tools, don't rebuild. The review loop pattern from 
Phase 1 applies to all new ingestion.
```

### Deliverable
All 16 workflows have system support.
Job found → application package → sent → tracked → followed up → outcome recorded.
Company profiles persist across search cycles.
Platform profiles stay current.
Content drafts on demand.

---

## Phase 3 — Sustainable Cadence (Month 2–3+)

**Goal served:** Goal 2 — job search as a business process, not a sprint
**Time needed:** Low — mostly configuration and habit, not building
**Principle:** The system runs on a schedule. You check in, not grind.

### What this looks like

**Weekly rhythm (30 min/week)**
Monday: dump everything from the week (emails, articles, job alerts).
Review staged report. Commit good stuff.
Check follow-up queue. Send any due messages.
Check pipeline dashboard. Any timing conflicts?

**Monthly rhythm (1 hour/month)**
Pull market intelligence summary.
Review gap analysis — any new skills appearing repeatedly?
Update portfolio roadmap if needed.
Review exposure calendar — any posts scheduled?
Refresh platform profiles if anything changed.

**Quarterly rhythm (2–3 hours/quarter)**
Network activation sweep — who haven't you talked to in 3 months?
Availability update on all platforms (your next contract window).
Rate review — has market rate moved? Adjust rules config floor.
Retrospective — what worked in the last search cycle? What didn't?

**Contracting as a business cadence**
6 weeks before contract end: activate network, update availability.
4 weeks before: first applications out.
2 weeks before: interviews happening.
Contract end: signed, ready to start.
Repeat.

This is the target state. Not a panic sprint every 3 months.
A low-hum process that runs in the background of your real work.

### What Claude Code adds here
Scheduled reports (weekly market summary, monthly gap analysis).
Availability reminders (6 weeks before contract end → trigger network activation).
Nothing complex — mostly wiring existing tools to a schedule.

### Deliverable
Job search feels like a business process, not a job.
Next contract search starts 6 weeks before you need one.
System surfaces what matters when it matters.
You spend 30 min/week on search, not 3 hours/day.

---

## Phase 4 — Portfolio & Business Optimization (Month 3+, Ongoing)

**Goal served:** Goal 3 — richer skills, higher rates, better positioning
**Principle:** Every contract and every personal project feeds back into the system and makes you more valuable.

### The loop

```
Market Intelligence → Gap Analysis → Portfolio Roadmap
         ↑                                    ↓
    Outcomes Feed ←── Contract Work ←── Learn / Build
         ↑                                    ↓
    Rate Increase ←── Richer Profile ←── Ship It
```

**How the system supports this**

Portfolio roadmap is market-driven, not intuition-driven.
System tells you: "5 Group C jobs this month required RAG experience.
You don't have it. Here's the smallest project that closes that gap."
You build it. Drop a truth chip. Master truth updates. Group C resume rebuilds.
Next contract search: stronger candidate for higher-rate roles.

Personal projects feed the portfolio the same way contracts do.
Every SAM feature shipped → truth chip → master truth → resume updated.
Every Beta Technology learning (Java, PLM) → truth chip → captured.
Nothing falls out of the record.

Rate optimization becomes data-driven.
System tracks market rates across all job dumps.
When market rate for your profile rises, you raise your floor.
You know when to hold and when to counter because the data is there.

Fractional/executive positioning develops over time.
As portfolio grows (Horse Platform live, SAM in use, Beta contract done),
the Group D/E positioning strengthens.
System tracks which companies respond to Group D framing vs Group A.
Outcome data shows you which positioning lands.
You lean into what works.

### What Claude Code adds here
Outcome analysis: patterns across all historical applications and results.
Rate trend alerts: "market rate for AI Systems roles up 15% since January."
Portfolio gap notifications: "3 new skills appearing in your target roles — none in your truth."
Nothing you'd build immediately — this emerges from accumulated data.

### Deliverable
Each 3-month contract cycle ends with:
- Master truth richer than when it started
- Market data updated
- Rates calibrated to current market
- Portfolio roadmap updated with real signal
- Positioning stronger for next cycle

Over 2 years: rate goes up, search time goes down, contract quality improves.
The system compounds.

---

## Implementation Summary

| Phase | When | Time Investment | Primary Goal | What's Running After |
|---|---|---|---|---|
| 0 — Search Now | Day 1 | Half day setup + 30 min/day | Goal 1 | Active search, Claude chat as system |
| 1 — Core Engine | Weeks 1–3 | 1–2 weeks part-time | Goal 1 + 2 | Truth mgmt, job intake, app packages |
| 2 — Full System | Weeks 3–6 | 2–3 weeks part-time | Goal 2 | All 16 workflows supported |
| 3 — Cadence | Month 2–3 | Ongoing, low effort | Goal 2 | Search runs on schedule, not sprint |
| 4 — Optimization | Month 3+ | Ongoing, compound | Goal 3 | Portfolio grows with every cycle |

---

## What to Keep in Mind for Claude Code

**The SAM reference is your architecture guide.**
Claude Code should read SAM before touching this project.
The patterns — MCP server, file-based state, staged reports, pipeline stages — all apply.
This is SAM pointed at your career instead of a codebase.

**Never build what you can use today.**
If a Claude chat prompt handles it well enough, don't automate it yet.
Build automation for what you actually use and feel the friction of daily.
The browser extension before the dashboard. The follow-up scheduler before the analytics.

**The review loop is non-negotiable.**
Every ingestion, every document build is staged before commit.
You are always in the loop. The system never acts without your approval.
This is the same principle as SAM's hard rule: results don't flow back in without review.

**Files are the database.**
No Postgres. No Redis. Markdown files with YAML front matter.
Simple, portable, readable by humans and AI.
If the system crashes, nothing is lost — files are the state.

**The goal is 30 minutes per week, not a full-time job.**
Every build decision should be evaluated against this.
Does this save more time than it takes to build and maintain?
If not, use the prompt instead.
