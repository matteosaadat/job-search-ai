# Job Hunt AI — Session Progress Log
**Session date:** 2026-05-26  
**Status:** All 10 phases implemented. Ready for real data.

---

## What Was Built — System Overview

A fully local AI-powered job hunt system. No SaaS. No subscriptions. Everything runs on your machine:

- **MCP server** (`src/core/mcp.py`) — 40 tools Claude uses to read/write the pipeline
- **FastAPI server** (`src/server.py`) — serves the UI and REST API at `localhost:8001`
- **Vanilla JS SPA** (`src/ui/index.html`) — 7-tab dashboard, no framework
- **Browser extension** (`extension/`) — captures job pages directly into the pipeline
- **File-based state** — all data is markdown files with YAML front matter, fully readable

Start the server: `python -m uvicorn src.server:app --port 8001 --reload`  
Open UI: `http://localhost:8001`

---

## Identity & Rules (`rules/config.yaml`)

| Field | Value |
|---|---|
| Name | Mahdi Saadat |
| Location | Hardwick, VT |
| Contract end | 2026-07-31 |
| Target start | 2026-08-01 |
| Rate min | $85/hr |
| Rate preferred | $120/hr |
| Work model | Remote-first |
| Special city | Boston (sister, hybrid/monthly OK) |
| Contract types | contract, fractional, part-time |
| Preferred duration | 3–6 months |
| Full-time perm | Never |

---

## Phase-by-Phase Breakdown

### Phase 1 — Project Setup
Config at `job-hunt.config.yaml`. Defines paths for truth, blueprints, rules.  
Core classes: `JHConfig` (config loader), `JHCore` (boots from config).

---

### Phase 2 — Truth System
**Purpose:** Mahdi's verified facts. Only what's in here can go into resumes/cover letters.

**Files:**
- `truth/chips/` — raw input files (docx, txt, paste). Feed anything here.
- `truth/master/truth.md` — synthesized master truth. Single source of fact.
- `truth/processed/` — chips moved here after digest
- `truth/master/truth_snapshot_YYYYMMDD.md` — snapshots before re-synthesis

**MCP tools:**
- `jh_ingest_truth_chip` — reads a chip and returns payload for Claude to synthesize
- `jh_synthesize_master_truth` — merges all chips into master truth
- `jh_get_master_truth` — returns full truth text
- `jh_snapshot_truth` — saves a timestamped snapshot before overwriting

**Current truth:** Mahdi's full career — Beta Technology, Black Lead Pencil, Nextmark + 3 key projects (Horse Platform, Smart Form, SAM).

---

### Phase 3 — Categorical Resumes
**Purpose:** Pre-built resume skeletons per job category (group). Tailored per-application at apply time.

**Resume Groups (from truth):**
- **Group A** — Full-Stack Platform (Horse Platform lead — React/Node/PostgreSQL)
- **Group B** — Frontend Systems (Smart Form lead — complex UI/UX)
- **Group C** — AI Systems (SAM/LLM tooling — Claude integration, MCP)
- **Group D** — Technical Leadership (team lead, architecture, mentoring)
- **Group E** — Enterprise / PLM (if applicable)

**Files:**
- `blueprints/resumes/templates/default.md` — base template with `{{PLACEHOLDER}}` tokens
- `blueprints/resumes/templates/group_a.md` (etc.) — group-specific override templates
- `blueprints/resumes/generated/group_a/resume.md` — generated Group A resume (exists)

**MCP tools:**
- `jh_get_categorical_template(group)` — returns template (group-specific → default fallback)
- `jh_generate_categorical_resume(group)` — returns JSON payload with template + truth + instructions. Claude fills placeholders, writes to `blueprints/resumes/generated/group_{x}/resume.md`

**Current state:** Group A resume exists. Groups B–E need generation.

---

### Phase 4 — Job Intake
**Purpose:** Get job descriptions into the pipeline, fast.

**Two intake modes:**

| Mode | When | What |
|---|---|---|
| `single` | One full JD | Writes to `jobs/raw/{job_id}.md` |
| `list` | LinkedIn search, email digest | Writes to `jobs/batches/{batch_id}.md` |

**Pipeline stages:**
```
jobs/raw/         — just captured, no analysis
jobs/batches/     — raw list batches
jobs/digested/    — structured fields extracted
jobs/whitelisted/ — active targets
jobs/archived/    — passed on
```

**MCP tools:**
- `jh_ingest_job(raw_text, source_url, job_type)` — captures single JD. Deduplicates by URL.
- `jh_ingest_job_list(raw_text, source)` — captures a multi-job page as a batch
- `jh_triage_job_list(batch_id)` — deterministic rules-based filter (no AI). Excludes: full-time perm, rate below $85, onsite non-allowed city
- `jh_digest_job(job_id)` — returns JSON payload. Claude extracts: title, company, skills[], rate, location, remote_policy, duration, red_flags[], group_fit[]. Also calls `jh_upsert_company`.
- `jh_get_job(job_id)` — reads from any stage

**Digested job front matter fields:**
```yaml
id, type, status, title, company, company_slug, location,
remote_policy, contract_type, duration_months, rate_stated,
required_skills, nice_to_have_skills, red_flags,
application_url, group_fit, score, recommendation, intake_date
```

---

### Phase 5 — Scoring Engine
**Purpose:** Deterministic 0–100 score. No AI. Pure rules + truth.

**Scoring weights** (`rules/config.yaml`):
| Dimension | Weight |
|---|---|
| Skill match | 30% |
| Rate match | 25% |
| Location match | 20% |
| Contract length | 15% |
| Timing | 10% |

**Recommendations:**
- `apply` — score ≥ 80
- `monitor` — score ≥ 65
- `stretch` — score ≥ 45
- `pass` — below 45

**MCP tools:**
- `jh_score_job(job_id)` — runs scoring, writes `score` + `recommendation` back to job front matter
- `jh_whitelist_job(job_id)` — moves digested → whitelisted
- `jh_archive_job(job_id, reason)` — moves any active job → archived
- `jh_list_whitelisted_jobs()` — returns all active targets with scores

---

### Phase 6 — Application Pipeline
**Purpose:** Generate tailored documents for each whitelisted job.

**Output directory:** `docs/{job_id}/`
- `docs/{job_id}/resume.md` — tailored resume
- `docs/{job_id}/cover_letter.md` — cover letter in Mahdi's voice
- `docs/{job_id}/interview_prep.md` — interview guide

**MCP tools:**
- `jh_generate_application_package(job_id)` — **main tool**. Reads whitelisted job, selects best group from `group_fit[]`, returns JSON payload with separate `resume_instructions` + `cover_letter_instructions`. Claude generates both and writes them.
- `jh_generate_tailored_resume(group, job_id)` — generate/re-generate just the resume for a specific group
- `jh_generate_interview_prep(job_id)` — returns payload. Claude generates: talking points mapped from JD → master truth stories, technical + behavioral questions, gap assessment, 5 questions to ask them
- `jh_log_application(job_id, method, contacts, notes)` — records submission. Creates `applications/active/{job_id}.md` with `follow_up_date = today + 5 days`. Updates job status → applied.

**Application methods:** `linkedin | email | direct | recruiter | referral`

---

### Phase 7 — Browser Extension
**Purpose:** Capture job pages directly into the pipeline without copy-paste.

**Location:** `extension/`  
**Install:** Chrome → chrome://extensions → Developer mode → Load unpacked → select `extension/`

**How it works:**
1. On any job page, click the extension icon
2. Pick **Single JD** (one full description) or **Job List** (LinkedIn search, email)
3. Click "Capture Page" — grabs `document.body.innerText` + current URL
4. POSTs to `http://localhost:8001/api/jobs/intake`
5. Shows the `job_id` or `batch_id` on success

**Files:** `manifest.json`, `popup.html`, `popup.js` (~130 lines total)

---

### Phase 8 — Follow-up Tracking
**Purpose:** Never let an application go cold. Track submissions, schedule follow-ups, record outcomes.

**MCP tools:**
- `jh_schedule_followup(job_id, days=5)` — sets/reschedules `follow_up_date` in the application record
- `jh_list_active_applications()` — returns all active apps sorted into: `overdue`, `due_today`, `upcoming`. Each entry has `days_since_applied` and `days_until_followup`.
- `jh_record_outcome(job_id, result, notes, rate_offered)` — records the outcome and moves the record to `applications/outcomes/`. Also archives the job from whitelisted.

**Outcome values:** `no_response | interview | offer | rejected | withdrew`

**Application record** (`applications/active/{job_id}.md`):
```yaml
job_id, title, company, status, applied_date, method,
contacts, follow_up_date, notes
```

---

### Phase 9 — Company Intelligence
**Purpose:** Track companies across jobs, flag warm leads, resurface them at the right time.

**Files:** `companies/{slug}.md`

**Company record front matter:**
```yaml
slug, name, status, industry, size, website,
contacts, jobs (list of job_ids), notes,
warm_lead_since, warm_lead_resurface, warm_lead_note,
blacklist_reason, created, last_updated
```

**Status values:** `cold | warm | active | blacklisted`

**MCP tools:**
- `jh_upsert_company(company_slug, data_json)` — create or update. Deduplicates contacts and jobs lists. **Auto-called by `jh_digest_job`** — every digested job creates a company record.
- `jh_get_company(company_slug)` — read full record
- `jh_list_companies(status="")` — list all, optionally filtered by status
- `jh_flag_warm_lead(company_slug, note)` — sets status → warm, sets resurface = today + 60 days

---

### Phase 10 — Strategy
**Purpose:** Market intelligence and portfolio gap analysis. Runs after enough jobs are in the pipeline.

**Output files:**
- `blueprints/strategy/market-patterns.md` — what the market wants
- `blueprints/strategy/gap-analysis.md` — what's missing from master truth
- `blueprints/strategy/portfolio-roadmap.md` — prioritized action plan

**MCP tools:**
- `jh_analyze_market_patterns()` — reads all whitelisted/digested jobs. Computes: top required skills (ranked), rate min/max/median, remote/hybrid/onsite split, duration distribution, group fit frequency, score distribution. Returns payload — Claude writes the doc.
- `jh_generate_gap_analysis()` — compares market skill demand vs master truth. Every skill either `covered` (truth has it) or `gap` (truth doesn't). Gaps ranked by frequency and weighted by recurrence. Returns payload — Claude writes the doc.
- `jh_update_portfolio_roadmap()` — reads gap analysis + patterns + truth. Returns payload with instructions for Claude to write a concrete roadmap: Priority 1/2/3 gaps, specific project ideas with effort estimates, 30-day sprint plan timed to contract end, success metrics.
- `jh_get_portfolio_roadmap()` — reads and returns the current roadmap file directly.

**Run in sequence:** market patterns → gap analysis → portfolio roadmap  
Or one chat command: `analyze market patterns` and Claude chains all three.

---

## UI Tabs — What Each Does

### Dashboard
- **Stats row:** Raw JDs / Digested / Whitelisted / Applications / Follow-ups Due / Companies
- **Follow-ups alert:** Red card appears when any application is overdue or due today — lists each with a "→ Follow up" button
- **Pipeline card:** Bar showing Raw → Digested → Whitelisted → Archived counts
- **Quick Actions:** Capture Job, Add Truth Chip, Follow-up Due, View Targets

### Jobs
**Left sidebar:** Pipeline grouped by stage (Whitelisted → Digested → Raw → Archived). Also shows List Batches section.  
**Job item shows:** Score badge (green=apply, yellow=monitor, orange=stretch, red=pass) + triage badge + recommendation  
**Job detail (right):** Full job content rendered as markdown. Action buttons change by status:
- Raw → ⚙ Digest
- Digested → ✓ Whitelist / ⚡ Score
- Whitelisted → 📄 Package / 📝 Prep / 🗂 Docs
- Archived → ↩ Unarchive

**Batch view:** Click a batch in sidebar → two-column passed/excluded split

### Applications
**Left sidebar:** Grouped into "Action Needed" (overdue/due-today, red header) + "Applied". Each shows follow-up urgency badge.  
**Detail view:**
- Application details card: company, applied date, method, follow-up date
- Generated documents card: links to resume.md, cover_letter.md, interview_prep.md — click to render inline
- Record Outcome row: 🗓 Interview / 🎉 Offer / ✗ Rejected / 😶 No Response / ↩ Withdrew / 🔔 Reschedule

### Companies
**Left sidebar:** Grouped by status (Active → Warm Leads → Cold → Blacklisted). Shows industry + job count. Yellow dot on warm leads due for resurfacing.  
**Detail view:** All metadata, associated job links (click → jumps to that job in Jobs tab), contacts, warm lead dates, Enrich/Warm Lead action buttons.

### Strategy
**Left sidebar:** Three strategy docs with green dot (exists) / grey circle (not generated). "Run Full Analysis" button triggers all three steps.  
**Detail view:** Renders the markdown document. "Regenerate" button if it exists, "Generate Now" if it doesn't.

### Resumes
**Left sidebar:** Lists generated group resumes with last-modified date.  
**Detail view:** Renders the resume markdown. "↻ Regenerate" button.

### Settings
Shows: Project config (name, path, AI model), file paths, Identity (name, location, rate min/max, target start from `rules/config.yaml`).

---

## Complete File Structure

```
job-search-ai/
├── src/
│   ├── core/
│   │   ├── mcp.py          ← 40 MCP tools (1700+ lines)
│   │   ├── config.py       ← JHConfig class
│   │   └── core.py         ← JHCore class
│   ├── server.py           ← FastAPI server + all REST endpoints
│   └── ui/
│       ├── index.html      ← entire SPA (700+ lines)
│       └── static/jh.css   ← dark theme CSS
├── extension/
│   ├── manifest.json       ← Chrome MV3
│   ├── popup.html          ← extension UI
│   └── popup.js            ← capture logic
├── truth/
│   ├── master/truth.md     ← synthesized master truth (exists)
│   ├── chips/              ← drop new truth inputs here
│   └── processed/          ← chips after digest
├── jobs/
│   ├── raw/                ← just captured
│   ├── batches/            ← list intake batches
│   ├── digested/           ← structured + scored
│   ├── whitelisted/        ← active targets
│   └── archived/           ← passed on
├── docs/{job_id}/          ← generated application docs per job
│   ├── resume.md
│   ├── cover_letter.md
│   └── interview_prep.md
├── applications/
│   ├── active/             ← in-flight applications
│   └── outcomes/           ← completed (interview/offer/rejected/etc)
├── companies/              ← one .md per company
├── blueprints/
│   ├── resumes/
│   │   ├── templates/      ← default.md + group_x.md overrides
│   │   └── generated/      ← group_a/resume.md etc
│   └── strategy/           ← market-patterns.md, gap-analysis.md, portfolio-roadmap.md
└── rules/config.yaml       ← identity, rates, location rules, scoring weights
```

---

## All MCP Tools (40 total)

### Truth
| Tool | What it does |
|---|---|
| `jh_ingest_truth_chip` | Read a chip file, return payload for Claude to synthesize |
| `jh_synthesize_master_truth` | Merge chips into truth/master/truth.md |
| `jh_get_master_truth` | Return full truth text |
| `jh_snapshot_truth` | Save dated snapshot before rewrite |

### Resumes
| Tool | What it does |
|---|---|
| `jh_get_categorical_template(group)` | Return template (group_x.md → default.md fallback) |
| `jh_generate_categorical_resume(group)` | Return payload → Claude fills + writes resume |
| `jh_generate_tailored_resume(group, job_id)` | Return payload → Claude tailors resume to specific job |
| `jh_export_resume_pdf(job_id)` | Convert MD resume to PDF |

### Jobs
| Tool | What it does |
|---|---|
| `jh_ingest_job(text, url, type)` | Capture single JD or list item. Deduplicates by URL. |
| `jh_ingest_job_list(text, source)` | Capture multi-job page as batch |
| `jh_triage_job_list(batch_id)` | Rules-based filter: exclude perm/low-rate/bad-location |
| `jh_digest_job(job_id)` | Return payload → Claude extracts structured fields |
| `jh_score_job(job_id)` | Deterministic score 0–100, writes back to front matter |
| `jh_whitelist_job(job_id)` | Move digested → whitelisted |
| `jh_archive_job(job_id, reason)` | Move any active → archived |
| `jh_get_job(job_id)` | Read from any stage |
| `jh_list_whitelisted_jobs()` | All active targets with scores |

### Application Pipeline
| Tool | What it does |
|---|---|
| `jh_generate_application_package(job_id)` | Return payload → Claude writes resume + cover letter to docs/{job_id}/ |
| `jh_generate_interview_prep(job_id)` | Return payload → Claude writes interview guide |
| `jh_log_application(job_id, method, …)` | Record submission, set follow-up date |

### Follow-up Tracking
| Tool | What it does |
|---|---|
| `jh_schedule_followup(job_id, days)` | Set/reschedule follow_up_date |
| `jh_list_active_applications()` | All apps split: overdue / due_today / upcoming |
| `jh_record_outcome(job_id, result, …)` | Record outcome, move to applications/outcomes/ |

### Companies
| Tool | What it does |
|---|---|
| `jh_upsert_company(slug, data_json)` | Create or update company record |
| `jh_get_company(slug)` | Read company record |
| `jh_list_companies(status)` | List all, filter by status |
| `jh_flag_warm_lead(slug, note)` | Mark warm, set resurface = today + 60d |

### Strategy
| Tool | What it does |
|---|---|
| `jh_analyze_market_patterns()` | Aggregate skill/rate/location stats from all jobs |
| `jh_generate_gap_analysis()` | Skills market wants vs skills in truth |
| `jh_update_portfolio_roadmap()` | Concrete action plan from gap analysis |
| `jh_get_portfolio_roadmap()` | Read current roadmap file |

### Rules
| Tool | What it does |
|---|---|
| `jh_get_rules()` | Return full rules/config.yaml |
| `jh_update_rule(path, value)` | Update a rule field |
| `jh_validate_rules()` | Check rules for consistency |

### Chat / Queue (system tools)
| Tool | What it does |
|---|---|
| `jh_chat_listen` | Claim next pending message from UI |
| `jh_chat_respond` | Write reply to outbox (shown in UI) |
| `jh_chat_ask` | Ask user a question, set status → waiting |
| `jh_chat_done` | Set status → idle |
| `jh_chat_progress` | Write progress update to outbox |
| `jh_log_session` | Log session start |
| `jh_get_opener` | Read OPENER.md for session briefing |

---

## Tomorrow's Plan

### Goal: First real JD → complete application package

**Step 1 — Start server**
```
python -m uvicorn src.server:app --port 8001 --reload
```

**Step 2 — UI tweaks** (before adding real data)
Things to address:
- Layout proportions (user said "not what I want" — identify what needs fixing)
- Any tab that feels wrong in practice
- CSS/spacing issues

**Step 3 — Capture first real JD**
Option A: browser extension on LinkedIn/job board → Single JD  
Option B: paste raw JD text into chat → `ingest this job: [paste]`  
Option C: POST to API directly

**Step 4 — Digest + score**
```
digest job {job_id}
```
Claude extracts all fields, creates company record, then calls score automatically.

**Step 5 — Review score + whitelist**
Check the breakdown. If ≥65, whitelist it:
```
whitelist job {job_id}
```

**Step 6 — Generate application package**
```
generate application package for {job_id}
```
Claude selects best group from group_fit[], generates tailored resume + cover letter, writes to `docs/{job_id}/`.

**Step 7 — Review docs**
Jobs tab → click job → 🗂 Docs → review resume and cover letter inline.  
Or Applications tab → click job → see both docs.

**Step 8 — Add truth chips as gaps appear**
If the cover letter needs a fact that's not in truth.md → add it:
- Drop a text file in `truth/chips/` and ask Claude to ingest it
- Or just tell Claude in chat: "add to truth: I also worked on X"

**Step 9 — Interview prep**
```
generate interview prep for {job_id}
```

**Step 10 — Log when you apply**
```
log application for {job_id} via linkedin
```

---

## Key Patterns to Know

**Scoring a job from scratch (full flow):**
```
ingest → digest → score → whitelist → generate package → log application
```

**Adding a batch of jobs (list flow):**
```
ingest list → triage batch → digest each passed job → score → whitelist best ones
```

**Follow-up session:**
```
what needs follow-up today?   (Claude calls jh_list_active_applications)
record outcome for {job_id}: interview
```

**Strategy session (after 10+ jobs):**
```
analyze market patterns   (Claude runs all three strategy tools in sequence)
```

**Company check:**
```
what companies am I tracking?   (Claude calls jh_list_companies)
flag warm lead {company-slug}
```

---

## Known Issues / Deferred

- **UI layout tweaks** — user deferred ("ok for now, tweak later"). Specific issues TBD tomorrow.
- **Group B–E resumes** — Group A exists. Others need `generate resume group B` etc.
- **`jh_export_resume_pdf`** — stub, not implemented. Low priority.
- **`jh_flag_anomalies`** — stub. Not in current scope.
- **`acme-corp.md`** — test company created during smoke test. Exists in `companies/`. Delete or ignore.
- **Test jobs in `jobs/raw/`** — 4 raw test jobs from earlier. Can digest or archive as needed.
- **`jobs/whitelisted/job_20260526_10c6be6c.md`** — one whitelisted test job (Meridian Labs, scored 96.1, APPLY). Can use as a test or archive.

---

*Generated: 2026-05-26*
