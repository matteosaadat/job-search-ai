# Job Hunt System — Complete Roadmap
> Personal career management system built on SAM architecture
> Owner: Mahdi Saadat | Last updated: May 2026

---

## System Overview

```
Truth Chips (raw input)
        ↓
  Master Truth + Personal Rules Config
        ↓
  Categorical Resumes (Group A–E)
        ↓
  Job Intake → JD Digestion → Company Intelligence
        ↓
  Match Scoring (truth × rules × timing)
        ↓
  Whitelist / Filter
        ↓
  Application Package (resume + cover letter + prep doc)
        ↓
  Submit → Follow-up Scheduler → Outcome Tracking
        ↓
  Feedback → Strategy → Portfolio Roadmap
```

---

## Folder Structure

```
/job-hunt/
  /truths/
    /chips/             # raw input — drop anything here
    /processed/         # chips merged into master (archived)
    /master/
      truth.md          # THE source of record
      truth.v{n}.md     # versioned snapshots
      anomalies.md      # unresolved conflicts flagged by AI

  /rules/
    config.yaml         # personal rules engine (rates, location, etc.)

  /resumes/
    /templates/         # base Group A–E templates (MD)
    /generated/         # per-application generated resumes
      /{job-id}/
        resume.md
        resume.pdf

  /jobs/
    /raw/               # JD as captured (text dump)
    /digested/          # structured job records (MD)
    /whitelisted/       # approved, active targets
    /archived/          # passed on or expired

  /companies/
    /{company-slug}.md  # company intelligence records

  /applications/
    /active/            # submitted, awaiting response
    /outcomes/          # result recorded

  /docs/
    /{job-id}/
      cover-letter.md
      interview-prep.md

  /strategy/
    portfolio-roadmap.md    # current enrichment plan
    gap-analysis.md         # market-derived skill gaps
    market-patterns.md      # patterns across whitelisted jobs

  /tools/
    /api/               # FastAPI backend
    /mcp/               # MCP server (Claude Code interface)
    /extension/         # browser extension
    /scripts/           # watchers, build tools

  /sam/
    README.md           # notes on borrowing from SAM
```

---

## Personal Rules Config (rules/config.yaml)

```yaml
# This file is the source of truth for all personal constraints.
# The AI reads this before scoring any job. Never bury rules in prose.

identity:
  name: Mahdi Saadat
  base_location: Hardwick, VT
  citizenship: US Citizen

availability:
  current_contract_end: 2026-07-31   # update as needed
  target_start: 2026-08-01
  urgency_window_days: 60            # prefer contracts starting within this window

contract_preferences:
  types: [contract, fractional, part-time]
  min_duration_months: 2
  max_duration_months: 12
  preferred_duration_months: [3, 4, 5, 6]
  full_time_permanent: false

rate:
  min_hourly: 85
  preferred_hourly: 120
  group_overrides:
    group_c: 120    # AI Systems — higher floor
    group_d: 100

location:
  remote_first: true
  willing_to_relocate: false
  special_cities:
    boston:
      allowed: true
      reason: sister lives there
      conditions:
        - short_term_only: true       # max 3 months in-office
        - can_stay_with_sister: true
        - hybrid_ok: true             # in-office to start, then remote
        - monthly_visit_ok: true      # fully remote but 1x/month in-person
  blacklisted_cities: []
  blacklisted_states: []

group_preferences:
  primary: [A, B, C]
  secondary: [D, E]
  fallback: [Bridge]

company_filters:
  min_team_size: 3
  blacklisted_companies: []
  preferred_industries:
    - SaaS
    - AI/ML tooling
    - PLM/enterprise software
    - fintech
    - healthtech
  avoid_industries: []

scoring_weights:
  rate_match: 0.25
  skill_match: 0.30
  location_match: 0.20
  contract_length_match: 0.15
  timing_match: 0.10
```

---

## MCP Tool List

These are the tools Claude Code calls via the MCP server.

### Truth Module
| Tool | Description |
|---|---|
| `ingest_truth_chip` | Read a new chip file, queue for merge |
| `synthesize_master_truth` | Merge all queued chips into master truth |
| `flag_anomalies` | Surface contradictions in master truth |
| `get_master_truth` | Return current master truth content |
| `snapshot_truth` | Version the current master truth |

### Rules Module
| Tool | Description |
|---|---|
| `get_rules` | Return parsed rules config |
| `validate_rules` | Check config for missing or conflicting rules |
| `update_rule` | Update a specific rule field |

### Resume Module
| Tool | Description |
|---|---|
| `get_categorical_template` | Return base resume for a group (A–E) |
| `generate_categorical_resume` | Rebuild a group resume from master truth |
| `generate_tailored_resume` | Customize a group resume for a specific job |
| `export_resume_pdf` | Convert MD resume to PDF |

### Job Module
| Tool | Description |
|---|---|
| `ingest_job` | Store raw JD text, assign job ID |
| `digest_job` | Extract structured fields from raw JD |
| `score_job` | Score digested job against master truth + rules |
| `whitelist_job` | Move job to whitelisted, mark as active target |
| `archive_job` | Remove from active pipeline |
| `list_whitelisted_jobs` | Return all active targets |
| `get_job` | Return full job record by ID |

### Company Module
| Tool | Description |
|---|---|
| `get_company` | Return company record |
| `upsert_company` | Create or update company intelligence |
| `list_companies` | Return all tracked companies |
| `flag_warm_lead` | Mark a company as warm for future outreach |

### Application Module
| Tool | Description |
|---|---|
| `generate_application_package` | Resume + cover letter for a job |
| `generate_interview_prep` | Prep doc from JD + master truth |
| `log_application` | Record submission date, method, contacts |
| `schedule_followup` | Set follow-up date (default: 5 days) |
| `record_outcome` | Log result (no response / interview / offer / rejected) |
| `list_active_applications` | Return all in-flight applications |

### Strategy Module
| Tool | Description |
|---|---|
| `analyze_market_patterns` | Find skill/type patterns across whitelisted jobs |
| `generate_gap_analysis` | Map market patterns against master truth |
| `update_portfolio_roadmap` | Rewrite roadmap from gap analysis |
| `get_portfolio_roadmap` | Return current enrichment plan |

---

## Phase Roadmap

### Phase 0 — Foundation
**Effort:** 1–2 days
**Goal:** Project scaffold, config, MCP server running, Claude Code can talk to it.

- [ ] Initialize project structure (folders above)
- [ ] FastAPI app scaffold (`/tools/api/`)
- [ ] MCP server scaffold (`/tools/mcp/`) — point Claude Code at SAM's MCP implementation as reference
- [ ] Boot validation — required files exist, rules config valid, master truth present
- [ ] Config loader — reads `rules/config.yaml`
- [ ] File utilities — read/write MD files, list folder contents, assign IDs
- [ ] Basic logging

**Deliverable:** Claude Code can `mcp list_tools` and get back the full tool list. All tools return stubs.

---

### Phase 1 — Truth Management
**Effort:** 2–3 days
**Goal:** Drop a chip, master truth updates automatically.

- [ ] `ingest_truth_chip` — reads file from `/truths/chips/`, moves to `/processed/` after merge
- [ ] `synthesize_master_truth` — Claude Code reads all chips + existing master, produces updated master
- [ ] `flag_anomalies` — detects contradictions (date conflicts, skill contradictions, role description mismatches), writes to `anomalies.md`
- [ ] `snapshot_truth` — versions current master before overwrite
- [ ] File watcher — auto-triggers ingestion when new file lands in `/chips/`
- [ ] Seed: import current `Mahdi_Saadat_TRUTH.md` as the initial master

**Chip format:** Any plain text or MD file. No schema required. The AI figures it out.

**Deliverable:** Drop a text file saying "I just finished a Docker project at Beta" — master truth updates, anomaly check runs.

---

### Phase 2 — Personal Rules Engine
**Effort:** 1 day
**Goal:** Rules config is live and enforced in all scoring.

- [ ] Write initial `rules/config.yaml` (template above, personalize)
- [ ] `get_rules` — parse and return structured rules
- [ ] `validate_rules` — catch missing required fields, flag logical conflicts
- [ ] Rules are read by every scoring and evaluation tool — not optional, not bypassed
- [ ] Boston rule tested: a Boston in-office contract scores correctly given conditions

**Deliverable:** Rules config populated. Claude Code reads and applies it in every job evaluation.

---

### Phase 3 — Categorical Resumes
**Effort:** 2–3 days
**Goal:** Five group resumes always in sync with master truth.

- [ ] Build base MD templates for Group A, B, C, D, E (pull from TRUTH.md resume groups)
- [ ] `generate_categorical_resume` — Claude Code rewrites a group resume from current master truth
- [ ] `generate_tailored_resume` — takes group + job ID → customizes language for that specific JD
- [ ] `export_resume_pdf` — MD to PDF via existing pipeline (use `pandoc` or `weasyprint`)
- [ ] Resume versioning — each generated resume saved with job ID and timestamp
- [ ] Validation: generated resume does not add skills not in master truth (hallucination guard)

**Deliverable:** `mcp generate_categorical_resume group=A` produces a clean, current Group A resume in MD and PDF.

---

### Phase 4 — Job Intake & Digestion
**Effort:** 2–3 days
**Goal:** Raw JD in → structured job record out.

- [ ] `/jobs/intake` POST endpoint — accepts raw text (JD paste or browser extension payload)
- [ ] `ingest_job` — stores raw text, assigns UUID-based job ID, timestamps
- [ ] `digest_job` — Claude Code extracts:
  - Title, company, location, remote policy
  - Contract vs full-time, estimated duration
  - Required skills, nice-to-have skills
  - Rate (if stated)
  - Key responsibilities
  - Red flags
  - Application URL / method
- [ ] Structured output saved as MD to `/jobs/digested/{job-id}.md`
- [ ] `upsert_company` — auto-creates or updates company record from job data
- [ ] Duplicate detection — same company + similar title within 30 days = flag, don't duplicate

**Job record schema (MD front matter):**
```yaml
id: job_20260601_abc123
title: Senior Full-Stack Engineer
company: Acme Corp
company_slug: acme-corp
location: Boston, MA
remote_policy: hybrid
contract_type: contract
duration_months: 4
rate_stated: null
posted_date: 2026-05-30
intake_date: 2026-06-01
status: digested
group_fit: [A, B]
score: null
```

**Deliverable:** Paste a LinkedIn JD into the intake endpoint → structured record created, company record created.

---

### Phase 5 — Match Scoring
**Effort:** 1–2 days
**Goal:** Every digested job gets a fit score and recommendation.

- [ ] `score_job` — runs after digestion automatically
  - Skill match: required skills vs master truth verified skills
  - Rate match: stated/implied rate vs rules floor
  - Location match: applies personal rules (Boston logic, remote-first, etc.)
  - Contract length match: duration vs preferences
  - Timing match: start date vs availability window
  - Weighted composite score (0–100)
  - Recommendation: `apply` / `monitor` / `pass` / `stretch`
- [ ] Score written back to job record front matter
- [ ] `whitelist_job` — sets status to `whitelisted`, moves to `/jobs/whitelisted/`
- [ ] `archive_job` — sets status to `archived`
- [ ] Auto-whitelist threshold: score ≥ 75 → flagged for review (not auto-applied)

**Deliverable:** Every digested job has a score and recommendation. Claude Code can explain the score.

---

### Phase 6 — Application Pipeline
**Effort:** 2–3 days
**Goal:** Whitelisted job → full application package in one command.

- [ ] `generate_application_package` — takes job ID:
  1. Reads job record + master truth + rules
  2. Selects best group fit
  3. Calls `generate_tailored_resume` for that group
  4. Generates cover letter — in Mahdi's voice, with his context (Boston angle if relevant, etc.)
  5. Saves both to `/docs/{job-id}/`
- [ ] Cover letter guardrails:
  - Does not claim skills not in master truth
  - Does not use language Mahdi has flagged as off-brand
  - Applies location nuance from rules config automatically
- [ ] `generate_interview_prep` — maps JD requirements to master truth, likely questions, strongest talking points
- [ ] `log_application` — records submission, method, contacts, date
- [ ] `schedule_followup` — writes follow-up reminder to `/applications/active/{job-id}.md`

**Deliverable:** One Claude Code command → resume + cover letter + prep doc for a specific job. All in Mahdi's voice, none hallucinated.

---

### Phase 7 — Browser Extension
**Effort:** 1–2 days
**Goal:** One-click JD capture from any page.

- [ ] Manifest V3 Chrome extension (`/tools/extension/`)
- [ ] "Capture Job" button in toolbar
- [ ] On click: grab page URL + full page text
- [ ] POST to `localhost:8000/jobs/intake`
- [ ] Badge confirms: "Job captured — ID: abc123"
- [ ] Works on: LinkedIn, Wellfound, Contra, Upwork, Toptal, direct company pages, anywhere
- [ ] Optional: right-click "Capture selected text as job" for partial-page capture

**~50 lines of JavaScript. No framework needed.**

**Deliverable:** Browse to any job posting, click button, job appears in `/jobs/raw/` within 2 seconds.

---

### Phase 8 — Tracking & Follow-up
**Effort:** 1–2 days
**Goal:** Nothing falls through the cracks.

- [ ] Application status lifecycle: `draft` → `submitted` → `followed_up` → `interviewing` → `closed`
- [ ] `list_active_applications` — returns all in-flight with days-since-submission
- [ ] Follow-up alert: applications > 5 days old with no update → surfaced by Claude Code on demand
- [ ] `record_outcome` — logs result, moves to `/applications/outcomes/`
- [ ] Outcome schema: result, notes, rate offered, reason for pass/rejection if known

**Deliverable:** Ask Claude Code "what needs follow-up today?" — gets accurate list.

---

### Phase 9 — Company Intelligence
**Effort:** 2 days
**Goal:** Companies are persistent entities, not throwaway context.

- [ ] Company record schema:
  - Name, slug, size, industry, website
  - Contract history (have they hired contractors before?)
  - Rate norms (inferred from job postings)
  - Culture signals (extracted from JDs and research)
  - Status: `cold` / `warm` / `active` / `blacklisted`
  - Notes (freeform)
- [ ] `flag_warm_lead` — company liked but bad timing → mark warm, resurface in 60 days
- [ ] Company record auto-enriched from every job intake
- [ ] `list_companies` with filters: warm leads, active, by industry
- [ ] Manual enrichment: drop a note chip referencing a company slug → merged into company record

**Deliverable:** After 20 job intakes, Claude Code can surface "3 warm leads to revisit this week."

---

### Phase 10 — Feedback Loop & Strategy
**Effort:** 2–3 days
**Goal:** System gets smarter over time. Portfolio roadmap is always current.

- [ ] `analyze_market_patterns` — scans all whitelisted jobs:
  - What skills appear most often?
  - What contract lengths are common?
  - What rates are offered?
  - Which groups (A–E) get most matches?
- [ ] `generate_gap_analysis` — market patterns vs master truth → gaps ranked by frequency and impact
- [ ] `update_portfolio_roadmap` — rewrites `/strategy/portfolio-roadmap.md`:
  - Specific gaps to close
  - Effort estimates
  - Suggested projects to build (e.g., "3 Group C jobs require RAG — build small RAG demo")
  - Prioritized by market signal, not intuition
- [ ] Outcome feedback: rejections with notes feed back into gap analysis
- [ ] Run on demand or after every 5 new whitelisted jobs

**Deliverable:** After 10 whitelisted jobs, Claude Code generates a market-grounded portfolio roadmap.

---

## Build Order Summary

| Phase | Name | Effort | MVP? |
|---|---|---|---|
| 0 | Foundation | 1–2 days | ✓ |
| 1 | Truth Management | 2–3 days | ✓ |
| 2 | Personal Rules Engine | 1 day | ✓ |
| 3 | Categorical Resumes | 2–3 days | ✓ |
| 4 | Job Intake & Digestion | 2–3 days | ✓ |
| 5 | Match Scoring | 1–2 days | ✓ |
| 6 | Application Pipeline | 2–3 days | ✓ |
| 7 | Browser Extension | 1–2 days | ✓ |
| 8 | Tracking & Follow-up | 1–2 days | later |
| 9 | Company Intelligence | 2 days | later |
| 10 | Feedback Loop & Strategy | 2–3 days | later |

**MVP (Phases 0–7): ~2–3 weeks part-time**
Enough to find, evaluate, and apply to contracts before your runway ends.

**Full system (all phases): ~4–6 weeks**
Self-improving, market-aware, nothing falls through cracks.

---

## Claude Code Kickoff Prompt

When starting the build, give Claude Code this context:

```
I'm building a job hunting system modeled on SAM architecture.
SAM is in [path to SAM]. Use its patterns for:
- MCP server structure and tool docstrings
- File-based state management
- Pipeline stage design
- Config/boot validation

The job hunt system lives at [path].
Start with Phase 0: scaffold the project structure,
FastAPI app, and MCP server stub.
Read the roadmap at [path/roadmap.md] before starting.
```

---

## Key Architectural Rules

1. **Master truth is read-only to all modules except Truth Management.** Nothing writes to it directly.
2. **Rules config is enforced everywhere.** No scoring, generation, or evaluation bypasses it.
3. **AI never invents.** Resumes and cover letters derive only from master truth. Hallucination guard validates output.
4. **Jobs are immutable after digestion.** Raw JD preserved as-is. Digested record is a separate file.
5. **Outcomes feed strategy, not truth.** A rejection doesn't change who you are — it changes what you build next.
6. **Boston is a rule, not a footnote.** It lives in config.yaml and is applied automatically. Never explain it in a cover letter unless the AI is explicitly asked to.
