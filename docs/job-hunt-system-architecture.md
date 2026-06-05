# Job Hunt System — Architecture
> SAM-pattern applied to career management
> Owner: Mahdi Saadat | May 2026

---

## The Four-Tier Model

Same architectural principle as SAM. Every tier derives from the one below it.
Nothing at a higher tier is invented — it is synthesized from verified lower-tier content.

```
┌─────────────────────────────────────────────────────────────┐
│  TIER 4 — ACTIONS & OUTCOMES                                │
│  Applications · Messages · Results · Pipeline Status        │
│  These record what happened. They feed back into Tier 2.    │
└───────────────────────┬─────────────────────────────────────┘
                        │ outcomes feed back ↓
┌───────────────────────▼─────────────────────────────────────┐
│  TIER 3 — DERIVED DOCUMENTS                                 │
│  Resumes · Cover Letters · Plans · Strategies · Prep Docs   │
│  Built from Tier 2. Never from raw input or memory.         │
└───────────────────────┬─────────────────────────────────────┘
                        │ derives from ↓
┌───────────────────────▼─────────────────────────────────────┐
│  TIER 2 — CORE DOCUMENTS                                    │
│  Master Truth · Company Registry · JD Registry ·            │
│  Market Intelligence · Network Registry                     │
│  These are always current. Updated by Tier 1 digestion.     │
└───────────────────────┬─────────────────────────────────────┘
                        │ digested and atomized from ↓
┌───────────────────────▼─────────────────────────────────────┐
│  TIER 1 — RAW INPUTS                                        │
│  Truth Chips · Job Dumps · Market Content · Emails ·        │
│  Recruiter Messages · Outcome Notes · Anything              │
│  Raw, unstructured, unverified. Never directly referenced   │
│  in Tier 3. Must pass through Tier 2 first.                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Hard Architectural Rules

These are not guidelines. The system enforces them.

1. **Tier 3 derives only from Tier 2.** A resume is generated from Master Truth. A cover letter pulls from Master Truth + Company Profile + JD Record. Never from raw memory or a Tier 1 dump directly.

2. **Tier 1 is always preserved as-is.** Raw dumps are never modified. Digestion creates new Tier 2 atoms — it does not rewrite Tier 1.

3. **Tier 4 outcomes update Tier 2, not Tier 3.** A rejection updates the Company Profile and Market Intelligence. It does not directly modify a resume. Tier 3 rebuilds from updated Tier 2.

4. **Nothing commits without review.** Every digestion, every document build, every update is staged first. The human reviews, refines, then commits.

5. **Hallucination is a Tier 3 violation.** Any claim in a resume, cover letter, or strategy document that cannot be traced to a Tier 2 atom is invalid and must be removed.

6. **The Master Truth is the single source of identity.** No other document defines who Mahdi is. Everything else derives from it.

---

## Tier 1 — Raw Inputs

Everything that comes in. No schema required. Dump anything.

| Input Type | Examples |
|---|---|
| Truth Chips | "Finished the Horse Platform launch." "Just restructured 39-API Java file." "Realized I should emphasize governance framing more." |
| Job Dumps | Indeed email digests, LinkedIn job alerts, copied JD pages, recruiter emails with roles |
| Market Content | Industry articles, salary reports, LinkedIn posts about hiring trends, Stack Overflow surveys |
| Company Intel | News articles, Glassdoor reviews, LinkedIn team pages, blog posts |
| Network Activity | Recruiter emails, LinkedIn messages, referral notes, intro requests |
| Outcome Data | Interview notes, rejection emails, offer details, contract terms |
| Session Notes | Anything Mahdi wants to remember from a job hunt session |

**The dump prompt opens every session:**
```
Here's today's dump. Digest everything, extract atoms to relevant 
Tier 2 documents, stage the report. Don't commit yet.
[paste anything]
```

---

## Tier 2 — Core Documents

These are the living databases of the system. Always current.
Updated by digestion. Read by every Tier 3 build.

---

### T2-01 — Master Truth
**The source of record for everything about Mahdi.**

Sections:
- Identity & contact
- The core narrative (transformation story, fast learner proof, artist/UX angle)
- Work history (each role with full context, constraints, what it proves)
- Projects (each project: what it is, what's built, what it proves, known gaps)
- Skills (verified in production vs learning vs aware)
- Resume group definitions (A–E with targeting and salary data)
- Gaps inventory
- Notes for resume writing (what to claim, what not to claim, how to frame the layoff)
- Personal rules (rates, location, availability, contract preferences)

Updated by: Truth Chip digestion only
Read by: Every Tier 3 document

**Anomaly detection runs on every update:**
New chip conflicts with existing atom → flagged for review before commit.

---

### T2-02 — Market Intelligence
**What the market looks like right now.**

Sections:
- Skill demand trends (skills appearing across whitelisted jobs, frequency, trajectory)
- Rate data (by role type, by group A–E, by contract length — sourced, dated)
- Contract length norms (what's common in the current market)
- In-demand role titles (what companies are actually calling these jobs)
- Emerging signals (skills or approaches appearing more this month vs last)
- Geographic patterns (remote vs hybrid vs on-site trends)

Updated by: Job dump digestion, market content digestion, outcome data
Read by: Gap Analysis, Portfolio Roadmap, Resume Group targeting

---

### T2-03 — Company Registry
**One record per company. Persistent across job cycles.**

Index: `/companies/index.md` — sortable list with status and last-updated date

Per company record (`/companies/{slug}.md`):
- Name, website, size, industry, funding stage
- Tech stack (if known)
- Contract history (do they hire contractors? Repeatedly?)
- Rate norms (what they've offered or implied)
- Culture signals (from JD language, Glassdoor, news)
- Hiring contacts (names, titles, LinkedIn)
- Status: `cold` / `warm` / `active` / `applied` / `blacklisted`
- Notes (freeform — anything worth knowing)
- Associated JDs (links to JD Registry records)
- Outcomes (if applied: result, date, notes)

Updated by: Every job dump (auto-creates or enriches), company research, outcomes
Read by: Cover letters, outreach messages, company research briefs

---

### T2-04 — JD Registry
**One record per job description. The job pipeline.**

Index: `/jobs/index.md` — filterable list with score, status, group fit, date

Per JD record (`/jobs/{id}.md`):

```yaml
---
id: job_20260529_abc123
title: Senior Full-Stack Engineer
company: acme-corp
location: Boston, MA
remote_policy: hybrid
contract_type: contract
duration_months: 4
rate_stated: 140
rate_currency: USD
posted_date: 2026-05-28
captured_date: 2026-05-29
source: linkedin
status: whitelisted        # raw / digested / whitelisted / applied / closed
group_fit: [A, B]
score: 88
recommendation: apply
application_id: null       # filled when applied
---
```

Body: extracted JD content — requirements, responsibilities, culture signals, red flags, application URL

Updated by: Job dump digestion (creates), scoring (updates), application pipeline (updates status)
Read by: Resume generation, cover letters, interview prep, match scoring

---

### T2-05 — Network Registry
**Contacts who matter to the job search.**

Index: `/network/index.md`

Per contact record (`/network/{slug}.md`):
- Name, title, company, LinkedIn
- Relationship context (how we know each other, what we worked on)
- Relationship warmth: `close` / `warm` / `cold`
- Last touchpoint (date + what was said)
- Relevance to current search (do they have network in target areas?)
- Actions taken (intro requests, referrals, responses)
- Notes

Key segments pre-loaded:
- Nextmark colleagues (10 years = high value)
- Beta Technology contacts (current contract)
- Past freelance clients
- Recruiters who've reached out
- VTC alumni

Updated by: Network activity digestion, relationship maintenance actions
Read by: Network activation workflow, outreach drafting, warm intro identification

---

## Tier 3 — Derived Documents

Built from Tier 2. Never from raw input. Rebuilt when Tier 2 changes.
All staged before commit.

---

### T3-A — Categorical Resumes (5 documents)

One per resume group. Always in sync with Master Truth.

| Document | Group | Targeting |
|---|---|---|
| `resumes/group-a.md` | Full-Stack Product Engineering | Horse Platform, Beta Tech, Laravel + Next.js depth |
| `resumes/group-b.md` | Frontend / UI Systems | Nextmark 10yr, component systems, Storybook, React model layer |
| `resumes/group-c.md` | AI Systems Engineering | Smart Form, SAM, MCP server, governance-first AI |
| `resumes/group-d.md` | Technical Leadership | 0→1 SaaS, legacy code restructuring, architecture decisions |
| `resumes/group-e.md` | Technical PM / UI-UX | Product ownership, every feature decision, artist UX instinct |

Each resume exports to: `.md` (source) + `.pdf` (submission)

Rebuild trigger: Master Truth updated → flag resumes as stale → rebuild on demand

---

### T3-B — Per-Application Package

Generated per whitelisted JD. Stored under `/applications/{job-id}/`.

| Document | Description |
|---|---|
| `resume-tailored.md` | Categorical resume customized for this specific JD |
| `resume-tailored.pdf` | PDF export |
| `cover-letter.md` | In Mahdi's voice, derived from Master Truth + Company Profile + JD |
| `interview-prep.md` | JD requirements vs profile, likely questions, talking points, objection responses |
| `application-fields.md` | Pre-filled answers for application form fields, character-limited responses |
| `outreach-draft.md` | Cold/warm/intro message drafts for this opportunity |
| `followup-schedule.md` | Dates and draft messages for follow-up cadence |

Build trigger: Job whitelisted + human initiates package generation
Input required: JD Record + Company Profile + Master Truth + Rules

---

### T3-C — Platform Profiles

Profile content for each external platform.
Rebuilt from Master Truth when projects or experience change.

| Document | Platform |
|---|---|
| `profiles/linkedin.md` | Headline, about section, experience entries |
| `profiles/toptal.md` | Bio + project descriptions (elite audience tone) |
| `profiles/contra.md` | Profile + service descriptions (startup audience tone) |
| `profiles/portfolio-about.md` | blackleadpencil.com about page |
| `profiles/portfolio-cases.md` | Case studies: Horse Platform, Smart Form, SAM |

Rebuild trigger: Master Truth updated with new project or role

---

### T3-D — Strategic Documents

Analysis and planning documents derived from Tier 2 patterns.

| Document | Description | Built From |
|---|---|---|
| `strategy/gap-analysis.md` | Market skill demand vs Master Truth — ranked gaps | Market Intelligence + Master Truth |
| `strategy/portfolio-roadmap.md` | Specific projects/skills to build, prioritized by market signal | Gap Analysis + Outcome patterns |
| `strategy/pipeline-status.md` | Current application pipeline, timing, next actions | JD Registry (applied) + outcome data |
| `strategy/exposure-calendar.md` | LinkedIn content schedule, platform update cadence | Market Intelligence + project milestones |
| `strategy/search-brief.md` | Current search parameters: what I'm looking for, at what rate, when | Master Truth (rules) + Market Intelligence |

Rebuild trigger: Market Intelligence updated, outcomes recorded, or on-demand

---

### T3-E — Exposure Content (Drafts)

LinkedIn posts and articles drafted for publishing.
Derived from Master Truth narrative + current projects + market positioning.

| Document | Description |
|---|---|
| `content/linkedin-drafts.md` | Queue of drafted posts awaiting review and publish |
| `content/published-log.md` | What was published, when, engagement notes |

---

## Tier 4 — Actions & Outcomes

What happened. The record of reality.

| Document | Description |
|---|---|
| `actions/applications.md` | All submitted applications: date, method, contact, status |
| `actions/messages-sent.md` | All outreach sent: to whom, what, when, response |
| `actions/follow-ups.md` | Scheduled and sent follow-ups |
| `actions/interviews.md` | Interview log: company, date, format, notes, outcome |
| `actions/offers.md` | Offers received: terms, counter, final outcome |
| `actions/outcomes.md` | Final results: hired, rejected, passed, ghosted — with notes |

**Tier 4 → Tier 2 feedback paths:**
- Outcome recorded → Company Profile updated (result, notes)
- Rejection with feedback → Market Intelligence updated (gap signal)
- Offer accepted → Master Truth updated (new role, availability changes)
- Interview notes → Company Profile enriched (culture signals, team intel)

---

## The Digestion Pipeline

What happens between a raw dump and updated Tier 2 documents.

```
RAW DUMP (Tier 1)
      ↓
  READ — AI reads entire dump in one pass
      ↓
  ROUTE — Identifies which Tier 2 documents are affected
      ↓
  EXTRACT — Pulls atoms from the dump
      │
      ├── Identity/skill atoms → Master Truth queue
      ├── Job listing atoms → JD Registry queue
      ├── Company atoms → Company Registry queue
      ├── Rate/trend atoms → Market Intelligence queue
      ├── Contact atoms → Network Registry queue
      └── Outcome atoms → Tier 4 queue
      ↓
  CONFLICT CHECK — New atoms vs existing atoms
      │
      ├── Consistent → queue for staging
      └── Conflict → flag for human review
      ↓
  STAGE — Structured report presented for review
      ↓
  REVIEW LOOP — Human refines, excludes, expands
      ↓
  COMMIT — Tier 2 documents updated
      ↓
  REBUILD FLAGS — Which Tier 3 docs are now stale?
      │
      ├── Master Truth changed → all Group resumes flagged stale
      ├── Company Profile changed → any open application packages flagged
      ├── Market Intelligence changed → Gap Analysis + Roadmap flagged
      └── JD Registry updated → Pipeline Status flagged
      ↓
  NOTIFY — "3 documents are stale. Rebuild now or later?"
```

---

## Folder Structure

```
/job-hunt/
│
├── /tier1-inputs/
│   ├── /chips/              # truth chips (drop here)
│   ├── /dumps/              # job/market/company dumps (drop here)
│   ├── /processed/          # moved here after digestion
│   └── /sessions/           # conversation session logs
│
├── /tier2-core/
│   ├── truth.md             # T2-01 Master Truth
│   ├── market-intel.md      # T2-02 Market Intelligence
│   ├── /companies/
│   │   ├── index.md         # Company Registry index
│   │   └── /{slug}.md       # Per-company profiles
│   ├── /jobs/
│   │   ├── index.md         # JD Registry index
│   │   └── /{id}.md         # Per-JD records
│   └── /network/
│       ├── index.md         # Network Registry index
│       └── /{slug}.md       # Per-contact records
│
├── /tier3-derived/
│   ├── /resumes/
│   │   ├── group-a.md       # Categorical resumes (source)
│   │   ├── group-b.md
│   │   ├── group-c.md
│   │   ├── group-d.md
│   │   ├── group-e.md
│   │   └── /pdf/            # Exported PDFs
│   ├── /applications/
│   │   └── /{job-id}/       # Per-application package
│   │       ├── resume-tailored.md
│   │       ├── resume-tailored.pdf
│   │       ├── cover-letter.md
│   │       ├── interview-prep.md
│   │       ├── application-fields.md
│   │       ├── outreach-draft.md
│   │       └── followup-schedule.md
│   ├── /profiles/           # Platform profile content
│   ├── /strategy/           # Gap analysis, roadmap, pipeline, etc.
│   └── /content/            # LinkedIn drafts, published log
│
├── /tier4-outcomes/
│   ├── applications.md
│   ├── messages-sent.md
│   ├── follow-ups.md
│   ├── interviews.md
│   ├── offers.md
│   └── outcomes.md
│
├── /rules/
│   └── config.yaml          # Personal rules engine (rates, location, etc.)
│
└── /tools/
    ├── /mcp/                # MCP server (Claude Code interface)
    ├── /api/                # FastAPI backend
    └── /extension/          # Browser extension
```

---

## Document Lifecycle Summary

```
DOCUMENT          CREATED BY          UPDATED BY                STALE WHEN
──────────────────────────────────────────────────────────────────────────
Master Truth      Initial import      Truth chip commits        New chip arrives
Market Intel      First job dump      Every dump with signals   Weekly at minimum
Company Profile   Job dump (auto)     Research, outcomes        New info arrives
JD Record         Job dump (auto)     Scoring, status changes   Applied/closed
Network Record    Manual / import     Touchpoints, outcomes     30 days no update

Group Resumes     Initial build       Master Truth changes      Truth updated
App Package       Per-job trigger     N/A (point-in-time)       Stale if JD changes
Platform Profiles Initial build       Major project additions   New project ships
Gap Analysis      First job batch     Market Intel changes      Monthly
Portfolio Roadmap Gap Analysis build  Outcomes + new gaps       Monthly
Pipeline Status   First application   Every status change       Daily during search
Exposure Calendar Initial plan        Monthly review            Monthly
```

---

## What's Assumed — Review Before Building

The following decisions are baked into this architecture.
Flag anything you'd change:

1. **Five resume groups (A–E) as defined in your TRUTH.md.** No Bridge Track resume included — flag if you want one.
2. **Company Registry is persistent across job cycles.** A company you see now will still be in the registry in your next search 6 months from now.
3. **JD Records are per-opening, not per-company.** Same company posting 3 roles = 3 JD records, one company profile.
4. **Master Truth is a single file.** Not split by section. If it gets very large, we can discuss splitting.
5. **All documents are Markdown.** Resumes export to PDF for submission but source is always MD.
6. **Rules config is separate from Master Truth.** Rates, location, availability live in `config.yaml`, not embedded in truth prose. This makes them machine-readable.
7. **Network Registry included.** Not in SAM — added here because relationship management is a distinct data type.
8. **No calendar integration at architecture level.** Follow-up scheduling is a document, not a calendar event. Can be upgraded later.
