# Mahdi Saadat — Master Truth Document
> Source of record for all resumes, cover letters, and job applications.
> Last updated: May 2026
> Do not edit layout here. This is truth only.

---

## Identity

- **Name:** Mahdi Saadat
- **Location:** Hardwick, VT, USA
- **Citizenship:** US Citizen
- **Phone:** (415) 368-7981
- **Email:** mahdi.saadat.work@gmail.com
- **Portfolio:** www.blackleadpencil.com
- **LinkedIn:** linkedin.com/in/matteo-saadat
- **GitHub repos:** Horse Platform and SAM are private. Smart Form can be made public. Proof strategy relies on live URLs, not code visibility.
- **Resourcefulness is a strength to highlight:** $3/month shared hosting + custom ZIP/FTP/unzip deploy pipeline instead of $100+/month AWS. Matched infrastructure cost to product stage. This is good engineering judgment, not a gap.

---

## The Core Narrative

### Who he is
Senior Full-Stack Software Engineer with 10+ years of experience. Strong front-end foundation built over a decade of production work. Post-layoff (Feb 2025) rapidly expanded into full-stack, backend, databases, AI systems, and developer tooling — and shipped production-grade software in all of them within 12 months.

### The transformation story (important — use carefully per context)
Spent 10 years at Nextmark as a Senior Frontend Engineer working with limited, legacy tools. No React. No TypeScript. No backend access. Learned component-based thinking without React, type discipline without TypeScript, API intuition without touching a database. When laid off Feb 2025, these foundations meant the modern stack was fast to learn.

In the 12 months after layoff:
- Learned React, TypeScript, Next.js, Laravel, MySQL, Python, FastAPI, MCP protocol
- Used AI (ChatGPT, then Claude, then Claude Code) as a force multiplier — not to write code for him, but to accelerate implementation of his own architectural thinking
- Shipped 3 production-grade systems: Horse Platform (live SaaS), Smart Form (live AI product), SAM (production pipeline engine)
- Landed a contract at Beta Technology building React component library and Java API for enterprise PLM software

### The fast learner proof
- Never used React at Nextmark → now shipping React in production with TypeScript strict mode, Storybook, Redux Toolkit
- Never used TypeScript → now using strict mode across entire codebase
- Never touched backend or DB → built full Laravel API with 45+ migrations, RBAC, state machines
- Never wrote Java → restructured a 39-API Java file into services/models architecture at Beta Technology
- Never used Python → built SAM in Python 3.13 with FastAPI and MCP protocol
- Never formally learned AI/LLM → shipping AI-integrated production products with provenance-first governance model

### The artist / UX angle
Is an artist. Has strong innate visual and UX instincts. Builds UI/UX in his head before wireframing. Chose NOT to learn Figma intentionally — because shipping a working app is more valuable than a wireframe, and his instincts produce strong UX without the extra step. More technical than a UI/UX designer but produces better UX than most engineers.

### AI as a tool, not a crutch
Uses AI as a force multiplier for implementation. All system design, architecture decisions, and product thinking are his own. AI helps write code faster — he decides what to build and how to structure it. SAM itself is his thinking about how AI should be governed in engineering workflows.

---

## Experience

### Beta Technology — Contract Full-Stack Engineer
**Duration:** Feb 2026 – Present (3 months + 3 month renewal = 6 months total, ongoing)
**Contract through:** Black Lead Pencil (his freelance entity)
**Location:** Remote

**What they do:** Enterprise PLM (Product Lifecycle Management) software built on Dassault Systèmes' 3DExperience platform.

**What he does:**
- Building React widgets for the 3DExperience PLM system
- Designed and building a React component library so the growing team can build future widgets consistently and efficiently
- Building a Java API for a new React widget — no prior Java experience; learned on the job with help from a Java teammate
- Inherited a Java codebase with 39 APIs stacked in a single file — refactored into proper services, models, and separation of concerns
- Brings system thinking and software engineering fundamentals to a team learning best practices
- They teach him 3DExperience and Java; he brings architecture, structure, and React expertise

**Technologies:** React, TypeScript, Java, 3DExperience PLM (Dassault Systèmes), REST APIs

**What this proves:**
- Adaptability: joined team, immediately productive, learned Java in production
- System thinking: identified and fixed structural problems in legacy code
- Collaboration: effective in a team environment, not just solo
- Enterprise software experience (PLM is a specialized, high-value domain)

---

### Black Lead Pencil — Freelance Full-Stack Developer & UI/UX Designer
**Duration:** 2011 – Present
**Location:** VT / NH

**What it is:** His freelance entity. All freelance and contract work runs through here.

**What he does:**
- Full-stack SaaS systems and front-end architectures
- Laravel + React / Next.js applications
- Workflow-driven UI design for data-heavy products
- End-to-end ownership from requirements to deployment
- AI-integrated product development
- Prompt engineering for production-grade systems
- Client work + own products (Horse Platform, Smart Form, SAM)

---

### Nextmark Inc. — Senior Front-End Software Engineer
**Duration:** 2015 – Feb 2025 (10 years)
**Location:** NH (www.nextmark.com)
**Laid off:** Feb 2025

**What they do:** B2B advertising data platform. Bionic is their media planning SaaS product.

**What he did:**
- Front-end architecture for Bionic, a production media planning SaaS
- Modular Sass and component-based UI systems — learned component thinking without React
- Refactored 14,000+ lines of CSS into scalable, modular architecture
- Reduced page load time from ~9 seconds to under 5 seconds
- Modernized 50+ legacy pages
- Built pagination, infinite scroll, and bulk-edit workflows
- Cross-functional collaboration with design, product, and back-end teams
- Mentored junior engineers
- Established front-end coding standards

**Important context:**
- No React (used their own older stack)
- No TypeScript
- No backend access
- Built component-based thinking manually — proved the concept before having the tool
- 10 years of working with constraints made learning the modern stack much faster after layoff

---

### MYSys Inc. — Software Developer Intern
**Duration:** 2014 – 2015
**Location:** VT (www.misysinc.com)

**What he did:**
- UI tools for industrial ERP systems
- AngularJS + HTML5 API documentation
- Google Drive, Dropbox, Stripe integrations
- Marketing-to-CRM automation pipelines

---

## Projects

### Horse Competition Platform (Fire Horse App)
**Status:** Live in production — launching this week (May 2026)
**URLs:** ge-pc.org (production), stage.ge-pc.org (staging)
**Built:** Solo with AI assistance (Claude Code), ~3–4 months active development
**Role:** Sole developer — all architecture, design, and implementation decisions

**What it is:**
Full-stack SaaS platform for managing horse show competitions. Multi-organization, multi-show. Supports virtual, in-person, and hybrid shows. Show creation, scheduling, class management, entries, judging, results publishing.

**Scale:**
- ~150 source files
- ~12,000 lines of application code (excluding vendor)
- 45+ SQL migrations
- 20+ database tables
- Live in production on shared hosting via custom FTP deploy pipeline

**Backend (Laravel 10 + PHP + MySQL/MariaDB):**
- `BaseModel` — custom Eloquent base with `fieldMap` accepting camelCase API input, writing snake_case columns. Eliminates boilerplate across all controllers.
- `BaseResource` — multi-mode API resource (compact / summary / full) controlled by `?mode=` query param. Each resource declares field arrays and a `resolveData()` method.
- `PermissionService` — scope-aware RBAC with named roles (show_organizer, org_admin, judge) that expand to atomic permission strings. Scoped at platform, org, and show level. Designed for Redis caching.
- Show status state machine — 3 stored ENUM values (draft, published, cancelled) + 10 computed `displayStatus` values derived server-side from date cascade logic. Frontend never replicates business logic.
- `cor_files` unified file table — images, PDFs, video, HTML all through one polymorphic table with `type` and `scope_type/scope_id`.
- Soft deletes on all major entities with `deleted_by` audit trail.
- Laravel Sanctum token authentication.
- Custom Node.js/zx build pipeline (`_migrate.mjs`, `_deploy-ftp.mjs`, `_build-all.mjs`) — incremental SQL migrations, FTP deploy, environment-specific config.

**Database design:**
- Domain prefix naming: `cor_` (core/identity), `comp_` (competition), `fin_` (finance)
- Key tables: cor_users, cor_organizations, cor_org_members, cor_groups, comp_shows, comp_show_classes, comp_entries, fin_invoices, cor_files, cor_access_control
- Incremental migration log tracking — reproducible on any environment

**Frontend (Next.js 14 + React 18 + TypeScript 5.8 strict mode):**
- Material UI v7
- Redux Toolkit (user session state)
- TypeScript model layer — static factory methods (`Show.fetchAll`, `Show.getShow`, `Show.createShow`) and instance action methods (`show.publish()`, `show.archive()`). All API interaction through typed models, not raw fetch.
- Centralized Axios wrapper with `getPaginated<T>` generic and typed `CollectionResponse<T>`.
- 3-tab wizard form (ShowDetails → ShowClasses → ShowSettings) with dirty-state tracking via `computeShowFormDirtyDigest()`.
- Programmatic modal stack via `useModal()` context. Supports stacking (parent stays visible while child modal opens).
- Tree-based class builder (class-builder/) with palette, canvas, drag-to-group UX. NRHA and AQHA catalogs seeded.
- `use-permission.ts` — frontend permission guard mirroring backend PermissionService structure.
- **Storybook 8** — component documentation.
- **Vitest + React Testing Library** — unit tests.
- **Playwright** — E2E scaffold.

**What's functional today:**
- Full show lifecycle: create → edit → publish (now or scheduled) → cancel → archive
- Show class management with hierarchical catalog (NRHA/AQHA) or custom
- Entry submission and listing
- File management: upload images, PDFs, video with scoped ownership
- Document library: org-wide and show-specific with picker in show creation
- User auth: register, login, logout, password change, avatar upload
- Horse profile CRUD
- Org membership with invite-flow status
- Materialized permissions resolved at login to flat permission object

**Architecture strengths:**
- Clean API contract — camelCase on wire, snake_case in DB, no internal structure leaking
- Type safety end-to-end — TypeScript strict mode, model interfaces match API contract, `tsc --noEmit` runs clean
- Separation of concerns — resource modes keep list responses light
- State machine server-side — frontend never replicates business logic
- Incremental logged migrations — reproducible on any environment

**Known gaps (honest):**
- No GitHub Actions / traditional CI/CD — intentional: shared hosting ($3/month vs $100+/month cloud) is right for pre-traction stage
- Has a custom automated build and deploy pipeline instead: AI-assisted build → ZIP compression → FTP transfer → server-side unzip via HTTP GET trigger → auto-cleanup. Fast, automated, works.
- Permissions not fully enforced on all routes (PermissionService built, partially wired)
- Fees, judges, awards, scorecards — scaffolded but not backend-wired yet
- No real-time (no websockets)
- No email notifications yet (Resend configured, WelcomeUserMail exists)
- Multi-tenancy designed for V3

---

### Smart Form — AI-Powered Data Intake Layer
**Status:** Live on portfolio — www.blackleadpencil.com/portfolio/smart-form
**Built:** Solo with AI assistance

**What it is:**
An AI input layer that sits on top of any legacy form. Users paste messy, unstructured real-world data — from emails, spreadsheets, webpages, colleague notes — and the LLM extracts, normalizes, and maps it to the correct form fields. User reviews, edits if needed, submits.

**The core product insight:**
"Bulk isn't the problem. The problem is 'bulk' that requires a second clean spreadsheet first." Legacy forms demand perfect input. Real-world data is always messy. Smart Form bridges that gap without replacing the legacy system.

**What it handles:**
- Multi-record detection — "John and Jane Smith" → two separate records
- Phone splitting — `"415 369 7881 & 82"` → two phone numbers
- Email inference — `"john.smith and jane.smith@gmail.com"` → two addresses
- Noise filtering — webpage copy-paste includes button text, tooltips, footers, banners. Smart Form ignores all of it.
- Field mapping by semantic meaning, not position — out-of-order columns still map correctly
- Typo tolerance — `"examp1e.com"`, `"01O2"` — flags with specific messages, doesn't silently fail
- Deterministic validation messages — tells you exactly what was normalized, what's missing, what's invalid
- Bulk entry — hundreds or thousands of records from one paste, no pre-clean required
- Dual-mode editing — bulk paste view + legacy form layout for precision editing on individual records
- No lock-in — user can still use the legacy form the normal way at any time

**Five live test datasets demonstrating edge cases:**
1. Two people from one entry, combined names, mixed separators
2. 10-record Excel dump with extra columns, typos, no clean template
3. Unstructured colleague email with narrative text
4. Webpage copy-paste with UI noise (buttons, badges, footers)
5. Intentionally broken data → shows deterministic validation messages

**Technical layer:**
- React frontend with smart overlay component
- Schema-aware LLM prompting — form field schema passed as context
- Structured JSON output extraction from unstructured input
- Output maps to form field state — populates form without mutating it
- Human-in-the-loop by design — AI fills, human confirms, human submits
- Post-processing layer keeps AI output isolated from form state until user confirms

**What this proves:**
- LLM prompt engineering for deterministic, schema-constrained output
- Human-in-the-loop system design
- AI governance thinking — AI cannot directly mutate application state
- Enterprise-grade problem identification (data import friction is universal)
- UX thinking — solves the problem without replacing the existing system

---

### SAM — Software Architecture Manager
**Status:** Active development, ~80% of MVP complete. In production use on Horse Platform.
**Stack:** Python 3.13, FastAPI, MCP (Model Context Protocol), Vanilla JS SPA, file-based state, YAML config

**What it is:**
A pipeline engine that converts raw developer notes (Truths) into formal specification documents (Blueprints) through an AI-assisted atomization-and-synthesis workflow. Not a chat wrapper. Not a documentation generator. A provenance-first architecture governance system.

**The core differentiator:**
Every atom in every Blueprint can be traced back to a specific source file. This is a direct engineering response to AI hallucination in specification work. The AI synthesizes only from verified Truths — it cannot invent.

**Four-tier model (original design, not borrowed from any framework):**
- Tier 1 — **Truths**: raw notes, analysis reports, session logs
- Tier 2 — **Blueprints**: SRS, DB schema, API contracts (SAM output)
- Tier 3 — **Source Code**: implementation
- Tier 4 — **Results**: docs, reports, logs

**Hard architectural rule:** Results cannot flow back into Blueprints. Code produced without a Blueprint is not a source of truth. The invalid loop is enforced by the system, not just a guideline.

**Three interfaces over the same Core engine:**
1. Web UI (HTML/JS SPA)
2. CLI
3. MCP server (primary interface — AI agents call SAM tools mid-workflow without leaving the IDE)

**What's built (phases complete):**
- Config + Core: boot validation, required-key enforcement, multi-provider AI (Anthropic, Google, Ollama)
- Analyse: 5-step code analysis pipeline (structure → entry-points → contracts → patterns → comments)
- Digest: Incremental (mtime tracking), crash-resilient (per-file atomic processing, envelope-based storage), session log pre-filtering to reduce token cost
- Build SRS: Autonomous multi-domain, incremental, IEEE 830 structure, three zoom levels per section (zoom:0/1/2)
- DB Schema Blueprint: migration-aware, algorithmic table extraction (no AI — pure regex), selective rebuild from any checkpoint
- MCP Interface: 20+ MCP tools, bidirectional chat protocol (UI ↔ AI agent via session-scoped inbox/outbox files)
- Web App: API layer complete, frontend HTML/JS/CSS exists

**Technical decisions worth noting:**
- SAM/AI separation is a hard rule: routing, file selection, scope grouping, table extraction — all deterministic Python before any AI call
- MCP tool descriptions double as AI routing instructions: each tool docstring contains explicit `ALWAYS call this when:` and `NEVER` clauses — prompt engineering embedded in the tool layer
- Confidence scoring calibrated by source type: session logs cap at 65, plain logs cap at 50, code analysis starts at 70, hard rules require ≥80
- State is entirely file-based: killed sessions resume from last saved file, no database dependency

**Being used in production** on the Horse Platform project — not a theoretical tool.

**Known gaps:**
- API Contract synthesis — designed, not yet implemented
- Conflict resolution cycle — informal today
- Approval/gates — not yet implemented
- Test coverage — minimal smoke tests
- Zoom-level UI rendering — spec and data exist, rendering unverified

---

## Skills

### Verified (used in production)

**Languages:**
- JavaScript (ES6+) — 10+ years production
- TypeScript — strict mode, full model layer (Horse Platform)
- PHP — Laravel 10 (Horse Platform)
- Python — 3.13, FastAPI, MCP protocol (SAM)
- Java — contributing to API at Beta Technology (learning in production, restructured legacy code)
- SQL — MySQL/MariaDB, 45+ migrations, schema design (Horse Platform)
- HTML5 — career-long
- CSS3 / Sass — 14,000+ lines refactored, modular architecture (Nextmark)

**Frameworks & Libraries:**
- React 18 — production (Horse Platform, Beta Technology, Smart Form)
- Next.js 14 (App Router) — production (Horse Platform)
- Laravel 10 — production backend (Horse Platform)
- Node.js — build pipeline scripting (Horse Platform)
- FastAPI — production (SAM)
- Material UI v7 — production (Horse Platform)
- Redux Toolkit — production (Horse Platform)
- Axios — centralized wrapper with generics (Horse Platform)

**Testing & Quality:**
- Storybook 8 — production component documentation (Horse Platform)
- Vitest + React Testing Library — unit tests (Horse Platform)
- Playwright — E2E scaffold (Horse Platform)
- Jest — previous projects
- Jasmine — previous projects
- Chrome DevTools, Lighthouse — performance optimization

**AI & LLM Systems:**
- Prompt Engineering — production (Smart Form, SAM)
- Human-in-the-Loop system design — Smart Form, SAM
- AI Governance — provenance tracking, validation layers, output isolation
- Structured AI outputs — schema-constrained extraction, deterministic validation
- MCP (Model Context Protocol) — SAM has a production MCP server with 20+ tools
- Claude API / Anthropic API — production use (Smart Form, SAM)
- AI-assisted development at scale — 12,000-line codebase built solo with Claude Code

**Architecture & System Design:**
- SaaS architecture — full stack (Horse Platform)
- REST API design — from both FE and BE perspective
- RBAC / permissions systems — scope-aware (Horse Platform PermissionService)
- State machine design — server-side derived status (Horse Platform show status)
- Component systems — built conceptually at Nextmark, in React at Beta/Horse Platform
- Database schema design — 20+ tables, domain prefixing, soft deletes, audit trails
- Custom build pipelines — Node.js/zx (Horse Platform)
- File-based resilient state — SAM architecture

**DevOps & Tooling:**
- Git, GitHub
- Custom automated build and deploy pipeline (AI-assisted build → ZIP → FTP → server-side unzip via HTTP trigger, Horse Platform)
- Stage and production environment management (ge-pc.org + stage.ge-pc.org)
- Vite, Webpack
- npm, Composer
- Postman
- FTP deploy pipeline (custom, Horse Platform)
- Shared hosting deployment

**Specialized:**
- 3DExperience PLM (Dassault Systèmes) — working knowledge from Beta Technology
- Enterprise widget development — Beta Technology

### Learning / Improving
- Docker / containerization — aware, not yet in own projects
- Cloud platforms (AWS / GCP) — aware, not yet used in production
- RAG / vector databases — planned (gap for Group C)
- Agent frameworks (LangGraph, LangChain) — aware via SAM/MCP work
- GraphQL — aware, not used

---

## Education

**Vermont Technical College — Randolph, VT**
B.S. in Software Engineering, 2015

---

## Languages

- English — Fluent
- Italian — Fluent
- Farsi — Native

---

## Resume Groups (for reference)

### Group A — Full-Stack Product Engineering
**Default title:** Senior Full-Stack Software Engineer
**Hirability:** 9/10
**Salary:** $95–135/hr contract · $140–195k annual
**Lead with:** Horse Platform (live production SaaS), Beta Technology (full-stack + Java), Laravel + Next.js depth, end-to-end ownership
**Key differentiator:** Builds complete systems solo — data model through deployment — and improves legacy codebases

### Group B — Frontend / UI Systems Engineering
**Default title:** Senior Frontend Engineer
**Hirability:** 9/10
**Salary:** $85–125/hr contract · $125–175k annual
**Lead with:** Nextmark (10yr, 14k CSS lines, 9s→5s load time, 50+ pages), Beta Technology (React component library), Horse Platform (TypeScript strict, Storybook 8, React model layer)
**Key differentiator:** 10+ years of component thinking + modern React stack + artist's UX instinct

### Group C — AI Systems Engineering
**Default title:** AI Systems Engineer / AI Solutions Engineer
**Hirability:** 8/10
**Salary:** $120–175/hr contract · $160–225k annual
**Lead with:** Smart Form (live AI product — schema-aware LLM, noise filtering, HITL), SAM (production MCP server, provenance-first AI governance, 20+ tools), AI-assisted SaaS at scale
**Key differentiator:** Governance-first AI thinking — not "uses AI" but designs systems that control AI with explicit contracts, validation layers, and human checkpoints

### Group D — Technical Leadership & Strategy
**Default title:** Fractional Software Engineer · Technical Advisor
**Hirability:** 8/10
**Salary:** $100–175/hr contract · $120–260k annual
**Lead with:** Horse Platform (0→1 solo SaaS, all architecture decisions), Beta Technology (joins team, identifies structural problems, restructures legacy code), Smart Form (product insight + execution), SAM (original system design)
**Key differentiator:** Independent operator who thinks in systems, ships products, and improves whatever codebase he touches

### Group E — Technical Product Management & UI/UX
**Default title:** Technical Product Manager / Senior UI Engineer
**Hirability:** 7/10
**Salary:** $100–160/hr contract · $130–200k annual
**Lead with:** Horse Platform (sole product owner — every feature decision, every UX decision, every architecture tradeoff), Smart Form (identified real user pain, designed solution, shipped it), 10+ years of frontend work at pixel/click precision, artist background with strong visual instinct
**Key differentiator:** Engineer-turned-PM who understands both sides of the table. Can evaluate technical feasibility, talk to engineers without losing them, design UX without Figma, and make product decisions grounded in implementation reality.

**Honest positioning:**
- Not a graphic designer — does not work in Figma, does not produce pixel-perfect mockups as deliverables
- Not a traditional user researcher — has not run formal user studies
- IS an engineer who made every product decision on a production SaaS: what to build, what to cut, what to defer, why
- IS an artist with strong innate visual instinct — produces strong UX from deep understanding, not from tooling
- Strong on: product thinking, feature prioritization, technical tradeoff evaluation, UX in code, translating between engineering and business
- Needs to develop: formal PM team experience, user research practice, Figma if required

**Target job titles:**
- Technical Product Manager
- Product Engineer (hybrid PM + engineer)
- UI/UX Engineer (design-capable developer)
- Product-Minded Engineer
- Head of Product (early-stage startup)

---

### Bridge Track — SMB Technical Partner
**Default title:** SMB Technical Partner / Fractional Technical Advisor
**Hirability:** 9/10 (easy to land, high demand)
**Rate:** $65–100/hr
**Purpose:** Income while filling gaps, builds portfolio proof, generates referral relationships

---

## Gaps (honest inventory)

| Gap | Affects | How to close |
|---|---|---|
| CI/CD | NOT a gap — custom automated pipeline: AI build → ZIP → FTP → server-side unzip via HTTP trigger. Shared hosting intentional ($3/mo vs $100+/mo cloud, pre-traction). |
| Docker / containers | A | Add Dockerfile to Horse Platform when moving to cloud |
| Cloud (AWS/GCP) | A | Small AWS project (S3 + Lambda) |
| RAG / vector DB | C | Build a small RAG app |
| No agent framework exp (LangGraph etc.) | C | SAM MCP work partially covers this |
| No public writing / thought leadership | C, D | 2–3 LinkedIn articles on AI governance |
| No formal leadership title | D | Covered by narrative + project ownership |
| Permissions not fully wired (Horse Platform) | A | Next sprint |
| No email notifications (Horse Platform) | A | Resend integration (partially done) |
| Java still learning | A | Beta Technology covers this in progress |

---

## Notes for Resume Writing

### The Solo Developer Philosophy (important for interviews and cover letters)
Solo developers practice lean, pragmatic engineering. Tools exist to solve coordination problems. When you are all the people, many team tools produce negative value:
- **No Figma:** Designs in Claude browser / builds directly in code. When there's no handoff to a developer, there's no need for a design file. This is efficiency, not laziness.
- **No GitHub Issues / daily commits:** Issue trackers coordinate across people. Feature branches manage parallel development. Solo = no coordination overhead needed. Commits when work is stable, not as a daily ritual.
- **Custom CI/CD instead of GitHub Actions:** Shared hosting at $3/month is the right infrastructure for a pre-traction product. GitHub Actions can't deploy to shared hosting easily. His ZIP/FTP/unzip pipeline is faster and costs nothing.
- **Writes specs anyway:** Uses SAM to produce SRS documents, DB schemas, API contracts. The discipline is there — just not the bureaucratic overhead.

Frame this in interviews as: "I practice lean development as a solo engineer. I adopt tools when the benefit justifies the overhead for my context. I know GitHub Actions, Figma, and traditional PM workflows — I'll use them on a team where they serve their purpose."

- **Do not claim** Docker, AWS, GCP, RAG, LangGraph as skills — not yet in production
- **Do claim** Java as "contributing to Java API" or "Java API development" — it's real, in production, just new
- **The layoff** is Feb 2025. Frame it as: end of Nextmark tenure, beginning of independent work and upskilling. Not a gap.
- **AI-assisted development** — frame as force multiplier, not crutch. He designs systems; AI accelerates implementation.
- **Figma** — do not list. Intentional choice.
- **Horse Platform** — it is LIVE and LAUNCHING this week. Not WIP. Call it a shipped production SaaS.
- **Smart Form** — live on portfolio. Call it a live AI product demo.
- **SAM** — in active development, in production use on Horse Platform. 80% of MVP.
- **3DExperience / PLM** — real working knowledge from Beta Technology. List it.
