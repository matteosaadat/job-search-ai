# Mental Model: SaaS vs AI System

A SaaS, with or without AI, has the same foundation.

The developer builds the structure once — entities, schemas, forms, relationships, creation order. This is the product. It exists before any user touches it.

The user brings **raw data** — sitting on their desktop in folders. Resume drafts, spreadsheets, PDFs, copy-pasted job descriptions, emails, screenshots. Messy, unstructured, scattered. This is the source of everything.

The user bridges the gap — reading the raw data and entering it piece by piece into the SaaS structure, field by field, in the right order. This creates **instances**. The screen shows instances rendered through structure.

The SaaS can also take those instances and produce **artifacts** — formatted outputs exported back to the user's desktop. Resumes, cover letters, reports, packages. Raw ingredients go into the machine, a finished product comes out. The quality of the product depends on the machine (developer) and the ingredients (raw data the user brings).

Not all artifacts are exported files. Some artifacts are just the screen itself. A dashboard, a company page, a job detail view — the screen is a rendered artifact. The SaaS produced it from instances, just like it produces a PDF. The medium is different, the logic is the same.

---

## The Pipeline

**SaaS:**
```
RAW → User → SaaS → Algorithm → Artifacts
```

**AI System:**
```
RAW → User + AI → SaaS → Algorithm + AI → Artifacts
 ↑
 AI also organizes and manages the RAW layer itself
```

Same pipeline. AI slots into two places. Everything else unchanged.

---

## AI as Secretary

In classic SaaS the raw data stays on the user's desktop — the SaaS never touches it. The user is the only bridge between the raw pile and the system. They hold everything in their head, manage the folders, know where things are.

In an AI system the raw data is exposed to AI. The AI becomes the secretary — organizing the raw data, keeping it tidy, knowing what's in it. The user no longer has to wade through the pile alone.

The AI operates at every stage now, including before the SaaS even sees the data. The user and AI collaborate on the raw layer together. The secretary has already sorted it, labeled it, and knows what's in it — so when it's time to create an instance, the ingredients are already prepared.

This is the third place AI helps, before the two already described:

**0. Organizing RAW data.**
In classic SaaS the user manages their own folders. In an AI system the AI is the secretary — ingesting, labeling, deduplicating, and organizing the raw data so both the user and the AI can work from it cleanly.

---

## Where AI Replaces Labor

An AI system has all the same parts as a SaaS — the structure, the entities, the instances, the artifacts, the raw data on the desktop. AI replaces three specific labor points:

**0. Organizing RAW data.**
In classic SaaS the user manages their own folders. In an AI system the AI acts as secretary — ingesting, labeling, and organizing the raw data so it is ready to work with.

**1. Raw data → Instances.**
In classic SaaS the user reads the raw data and types it in field by field. In an AI system the AI digests the raw data and fills the form. Same destination, different translator.

**2. Instances → Artifacts.**
In classic SaaS the developer writes algorithms — query the data, filter, sort, format, render to PDF. In an AI system many of these are prompts instead of code. "Give me last week's JDs" instead of `WHERE date > today-7`.

---

## But Not Everything Is Replaced

| Task | Who does it |
|---|---|
| Archive a job | Algorithm (sets a flag) |
| Digest a JD | LLM |
| Sort by date | Algorithm |
| Write a cover letter | LLM |
| Export to PDF | Algorithm |
| Score a job | Mix — algorithm runs rules, LLM interprets fit |

Some instances are AI-produced, some are algorithmic. Some artifacts are AI-produced, some are algorithmic. Both coexist in the same system.

---

## Data Shape

Data is mostly text — because LLMs consume and produce text. Classic SaaS has typed database fields. Here the database is markdown files with frontmatter. The structure is still there, just expressed differently.

---

## Truth is Immutable. Artifacts Are Not.

This is the most important architectural principle in the system.

**Truth is immutable.** Raw data goes in and stays. It is never edited, never cleaned, never improved. Raw JDs, raw personal info, raw anything — stored in truth exactly as received. The pages of the novel are never rewritten.

**Artifacts are derived and disposable.** They are produced from truth + rules and can be remade at any time. A clean JD is an artifact. A score is an artifact. A resume is an artifact. A company page is an artifact. If the rules change, throw the artifact away and regenerate it. The truth did not change — only the lens.

A raw JD and a clean JD are two separate jobs, often done together but distinct:

1. **Raw JD → Clean JD.** The raw JD is stored in truth. The AI removes noise and formats it into what the system expects. The clean JD goes into SaaS storage as an instance.
2. **Clean JD → Score.** Using rules and personal truth, the AI scores the job. The score is stored alongside the clean JD. Both are artifacts — regeneratable any time.

**Rules are also artifacts.** They are not static configuration. Rules are produced from truth and grow richer as truth accumulates — exactly like character bios getting more accurate as new pages of the novel arrive. More truth → better rules → better artifacts everywhere.

```
TRUTH (immutable)
  raw JDs
  raw personal info
  raw anything
       ↓
       + Rules (artifact, derived from truth, evolves over time)
       ↓
ARTIFACTS (derived, disposable, regeneratable)
  clean JD
  score
  resume
  cover letter
  company page
  rules themselves
```

The system gets smarter over time without touching the past — by accumulating more truth and refining the rules. Any artifact can be thrown away and rebuilt. The truth is the only thing that cannot.

---

## The Novel Analogy

Think of a 1000-page murder mystery novel. You receive one page per day, out of order, in any format — text, image, audio. Your job:

- Write a **bio for every character** — getting richer with each new page
- Record each **event separately** as it appears
- Maintain a **running summary** of everything known so far
- Connect events to **solve the mystery**

The pages are truth — immutable, arriving messy, stored as received. The bios, event reports, and summary are artifacts — remade every time a new page arrives, always reflecting the latest state of knowledge.

In this project the novel is the user's life and the job market. The murder mystery to solve is: who are you, what do you want, and what is the right job for you. Every page of truth moves the AI closer to that answer.

---

The SaaS is fully present. AI is layered on top of it, not replacing it.

---

## The Advisor Role

The first three AI roles are mechanical — organize, digest, produce. The fourth is different.

The advisor sits on top of everything accumulated — all truth, all jobs, all scores, all companies, all applications, all outcomes — and reasons over it to give guidance. Not a new artifact. Pattern recognition over existing instances. The kind of thing a smart secretary who has been watching everything notices and surfaces.

- You have applied to 12 jobs this month, heard back from 2 — your resume for group B is underperforming
- Three whitelisted jobs have been open 30 days — stale or slow process
- Your rate floor is $90 but 80% of the jobs you want are budgeted at $70-80 — there is a tension worth discussing
- This company reached out twice in 6 months — that is a warm signal, not a coincidence
- You have not applied anywhere in 10 days — is that intentional?
- Your strongest matches are all mid-size product companies, not staffing agencies — your energy may be misallocated

**Skills already built:**

| Tool | What it does |
|---|---|
| `jh_analyze_market_patterns` | Skill frequencies, rate ranges, remote split across jobs |
| `jh_generate_gap_analysis` | Your skills vs what the market wants |
| `jh_flag_anomalies` | Contradictions in your truth |
| `jh_get_portfolio_roadmap` | Portfolio enrichment plan |
| `jh_flag_warm_lead` | Mark a company for future outreach |

**Skills still needed:**

| Tool | What it would do |
|---|---|
| `jh_hunt_health` | Overall status — velocity, response rate, activity, where energy is going |
| `jh_detect_stale_jobs` | Whitelisted jobs open too long — stale or slow process |
| `jh_rate_tension` | Your rate floor vs what whitelisted jobs actually budget |
| `jh_application_performance` | Which resume groups and job types are getting responses |
| `jh_company_signals` | Companies that reached out multiple times, warm patterns |
| `jh_inactivity_alert` | Days since last application, last digest, last truth drop |
| `jh_advise` | Top-level — reads all of the above and gives a prioritized recommendation |

`jh_advise` is the entry point. It calls the others, synthesizes, and tells you what to do next and why.
