# Architecture

## The Three Layers

Everything in this system lives in one of three layers.

```
┌─────────────────────────────────────────────────────┐
│                      TRUTH                          │
│         raw, immutable, append-only                 │
│  truth chips · raw JDs · raw emails · raw anything  │
├─────────────────────────────────────────────────────┤
│                      SAAS                           │
│         structured instances, typed, stored         │
│  jobs · companies · profile · rules · applications  │
├─────────────────────────────────────────────────────┤
│                    ARTIFACTS                        │
│      derived, disposable, always regeneratable      │
│  resumes · cover letters · scores · screens · PDFs  │
└─────────────────────────────────────────────────────┘
```

**Truth is immutable.** What goes in never changes. It is the source of everything else.

**SaaS is structured.** Entities with defined schemas, created in a specific order, stored and queryable. The developer built this layer once. It exists before any data touches it.

**Artifacts are derived.** Produced from truth + instances + rules. Disposable and regeneratable. If rules change, regenerate. If truth grows, regenerate. The artifact is never the source — it is always a product of the sources.

---

## The Full Pipeline

**Classic SaaS:**
```
RAW → User → SaaS → Algorithm → Artifacts
```

**This system:**
```
RAW → User + AI → SaaS → Algorithm + AI → Artifacts
 ↑
 AI also organizes the RAW layer itself
```

The pipeline is identical. AI slots into specific labor points — it does not replace the structure, only the human effort required to move through it.

---

## The Four AI Roles

### 0 — Organize Raw
In classic SaaS the raw data sits on the user's desktop. The user manages it alone. In this system the raw data is exposed to AI. The AI becomes the secretary — ingesting, labeling, bucketing, deduplicating. The user no longer has to hold it all in their head.

Raw truth arrives in any format, any order, any time. AI stores each chip exactly as received — immutable — then reads it and extracts atomic facts into domain buckets:

```
truth chip (immutable, stored as-is)
       ↓
   AI extracts facts → atoms → domain buckets
                        identity/
                        skills/
                        rate/
                        location/
                        contracts/
                        experience/
                        projects/
       ↓
   master truth synthesized from all buckets
   (rewritten every time new atoms arrive)
```

The raw chip answers "what did you tell me."
The atom answers "what does it mean."
The master truth answers "who are you right now."

### 1 — Digest into Instances
In classic SaaS the user reads raw data and types it field by field into forms. In this system AI reads the raw data and fills the form. Same destination, different translator.

A raw JD and a clean JD are two separate jobs:

1. **Raw JD → Clean JD.** Raw stored in truth. AI removes noise, extracts structure. Clean JD written to SaaS storage as an instance.
2. **Clean JD → Score.** AI scores against rules and personal truth. Score stored alongside the clean JD. Both are artifacts — regeneratable any time.

### 2 — Produce Artifacts
In classic SaaS the developer writes algorithms — query, filter, sort, format, render. In this system many of those are prompts instead of code.

Not everything is AI-produced. Both coexist:

| Task | Who does it |
|---|---|
| Archive a job | Algorithm (sets a flag) |
| Digest a JD | LLM |
| Sort by date | Algorithm |
| Write a cover letter | LLM |
| Export to PDF | Algorithm |
| Score a job | Mix — algorithm runs rules, LLM interprets fit |
| Synthesize rules from truth | LLM |
| Filter archived jobs | Algorithm |

The screen is also an artifact. A dashboard, a company page, a job detail view — rendered from instances by the SaaS, just like a PDF. The medium differs, the logic is the same.

### 3 — Advise
The advisor sits on top of everything accumulated and reasons over it. Not a new artifact — pattern recognition over existing instances. The kind of thing a smart secretary who has been watching everything notices and surfaces.

---

## Entities

### Manual input — no prerequisites
| Entity | Fields |
|---|---|
| Profile | name, location, availability, rate_floor, skills[], experience[], education[] |
| Company | name, industry, size, website, status |
| Rules | rate_floor, location_tolerance, contract_types[], remote_policy |
| Strategy | goals, target_roles[], timeline, notes |

### Manual input — requires prerequisite
| Entity | Requires | Fields |
|---|---|---|
| Job | Company | title, company, location, salary, remote_policy, contract_type, requirements[], url |
| Contact | Company | name, role, email, notes |
| Tag | Company | label, note |
| Batch | — | source, date, jobs[] |
| Score | Job + Rules | value, breakdown, recommendation |
| Application | Job + Resume | date_sent, cover_letter, status |
| Outcome | Application | result, date, notes |

### Composition — AI or algorithm combines instances
| Entity | Combined from |
|---|---|
| Resume | Profile + template |
| Cover Letter | Profile + Job + Company |
| Interview Prep | Profile + Job + Score |

### Creation order
```
Profile ────────────────────────────────────────┐
Rules ──────────────────────────── Score ───────┤
Company → Job ──────────────────────────── Application → Outcome
               └── Cover Letter                ↑
               └── Interview Prep           Resume
                                               ↑
                                            Profile
```

---

## Key Principles

### Truth is immutable. Artifacts are not.
Truth never changes. Any artifact can be thrown away and rebuilt from truth + current rules. This means the system gets smarter over time without touching the past — by accumulating more truth and refining the rules.

### Rules are artifacts too.
Rules are not static configuration. They are produced from truth and grow richer as truth accumulates. More truth → better rules → better artifacts everywhere. Every rule traces back to a truth atom, every atom traces back to a raw chip, every chip has a date and origin.

### Everything has a paper trail.
Every instance and artifact records what inputs produced it, when, and from what version of rules. If you ask why a score is what it is, or where a rule came from, or what happened to a JD — the system can answer precisely. A secretary who cannot account for their work is a black box, not a secretary.

### The novel principle.
Truth arrives like pages of a murder mystery novel — out of order, in any format, one at a time. The AI stores each page as-is, extracts atoms from it, and rewrites the master truth to reflect the latest complete picture. Old atoms are superseded, not deleted. The mystery being solved: who are you, what do you want, what is the right job for you.

---

## Skills

### Truth pipeline
| Tool | Role | What it does |
|---|---|---|
| `jh_ingest_truth` | Organize | Store a raw truth chip, immutable |
| `jh_atomize_truth` | Organize | Extract atomic facts from a chip into domain buckets |
| `jh_save_atoms` | Organize | Persist extracted atoms |
| `jh_synthesize_master_truth` | Organize | Rewrite master truth from all atoms |
| `jh_flag_anomalies` | Organize | Surface contradictions in master truth |
| `jh_snapshot_truth` | Organize | Version the master truth before major changes |
| `jh_get_master_truth` | Read | Return current master truth |

### Job pipeline
| Tool | Role | What it does |
|---|---|---|
| `jh_ingest_job` | Digest | Store a raw JD |
| `jh_ingest_job_list` | Digest | Store a batch of raw JDs |
| `jh_digest_job` | Digest | Raw JD → clean structured instance |
| `jh_score_job` | Digest | Clean JD + rules → score |
| `jh_save_score` | Digest | Persist a score |
| `jh_triage_job_list` | Digest | Batch triage a list of JDs |
| `jh_re_evaluate_jobs` | Artifact | Re-score all jobs when rules change |
| `jh_whitelist_job` | Action | Mark a job as active target |
| `jh_archive_job` | Action | Remove from active consideration |

### Company pipeline
| Tool | Role | What it does |
|---|---|---|
| `jh_upsert_company` | Digest | Create or update a company record |
| `jh_get_company` | Read | Return a company record |
| `jh_list_companies` | Read | List all companies |
| `jh_flag_warm_lead` | Action | Mark a company for future outreach |

### Artifact production
| Tool | Role | What it does |
|---|---|---|
| `jh_generate_tailored_resume` | Artifact | Profile + job → tailored resume |
| `jh_generate_categorical_resume` | Artifact | Profile + group → categorical resume |
| `jh_generate_application_package` | Artifact | Job + resume + cover letter → package |
| `jh_generate_interview_prep` | Artifact | Profile + job → prep doc |
| `jh_export_resume_pdf` | Artifact | Resume → PDF |
| `jh_get_opener` | Artifact | Profile + job + company → cover letter |
| `jh_synthesize_rules` | Artifact | Truth atoms → rules document |
| `jh_update_rule` | Action | Update a specific rule |

### Advisor
| Tool | Status | What it does |
|---|---|---|
| `jh_analyze_market_patterns` | Built | Skill frequencies, rate ranges, remote split across jobs |
| `jh_generate_gap_analysis` | Built | Your skills vs what the market wants |
| `jh_get_portfolio_roadmap` | Built | Portfolio enrichment plan |
| `jh_hunt_health` | Needed | Velocity, response rate, activity, energy allocation |
| `jh_detect_stale_jobs` | Needed | Whitelisted jobs open too long |
| `jh_rate_tension` | Needed | Your rate floor vs what jobs actually budget |
| `jh_application_performance` | Needed | Which resume groups and job types get responses |
| `jh_company_signals` | Needed | Companies with repeated outreach, warm patterns |
| `jh_inactivity_alert` | Needed | Days since last application, digest, truth drop |
| `jh_advise` | Needed | Top-level — synthesizes all advisor tools, tells you what to do next |

### UI / session
| Tool | Role | What it does |
|---|---|---|
| `jh_chat_listen` | UI | Wait for next UI command |
| `jh_chat_respond` | UI | Send response to UI |
| `jh_chat_progress` | UI | Send mid-task progress update |
| `jh_chat_ask` | UI | Ask user a question, pause for answer |
| `jh_chat_done` | UI | Signal completion, re-enable input |
| `jh_log_session` | Audit | Record what happened in a session |
| `jh_log_application` | Audit | Record a submitted application |
| `jh_record_outcome` | Audit | Record the result of an application |
| `jh_schedule_followup` | Audit | Schedule a follow-up action |

---

## Data Shape

Data is mostly text — because LLMs consume and produce text. Classic SaaS has typed database fields. Here the database is markdown files with YAML frontmatter. The structure is still there, just expressed differently. The schema is enforced by convention and the tools that write files, not by a database engine.

```
data-storage/
  truth/
    raw/          ← immutable chips, never edited
    atoms/        ← extracted facts, by domain
    master/       ← synthesized truth document
  jobs/
    raw/          ← raw JDs, immutable
    digested/     ← clean structured instances
    whitelisted/  ← active targets
    archived/     ← removed from consideration
  companies/      ← one file per employer
  rules/          ← scoring and filtering config
  blueprints/
    resumes/      ← generated resume artifacts
    cover-letters/
    prep-docs/
    strategy/
  applications/
    active/       ← submitted applications
    outcomes/     ← results
```
