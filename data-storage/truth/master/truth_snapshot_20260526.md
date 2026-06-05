# Master Truth — Mahdi Saadat
> Synthesized from all truth chips. Do NOT edit directly.
> Last synthesized: 2026-05-26
> Source chips: Mahdi_Saadat_TRUTH.md

---

## Identity

| Field | Value |
|---|---|
| Name | Mahdi Saadat |
| Location | Hardwick, VT, USA |
| Citizenship | US Citizen |
| Phone | (415) 368-7981 |
| Email | mahdi.saadat.work@gmail.com |
| Portfolio | www.blackleadpencil.com |
| LinkedIn | linkedin.com/in/matteo-saadat |
| GitHub | Horse Platform and SAM are private. Smart Form can be made public. Proof strategy relies on live URLs, not code. |

---

## Core Narrative

**Who he is:** Senior Full-Stack Software Engineer, 10+ years of experience. Strong front-end foundation built over a decade of production work. After layoff (Feb 2025), rapidly expanded into full-stack, backend, databases, AI systems, and developer tooling — shipped production-grade software in all of them within 12 months.

**The transformation:** 10 years at Nextmark as Senior Frontend Engineer with constrained tools — no React, no TypeScript, no backend access. Layoff Feb 2025. In the 12 months after:
- Learned React, TypeScript, Next.js, Laravel, MySQL, Python, FastAPI, MCP protocol
- Shipped 3 production-grade systems: Horse Platform (live SaaS), Smart Form (live AI product), SAM (production pipeline engine)
- Landed contract at Beta Technology: React component library + Java API for enterprise PLM

**Fast learner proof:**
- No React at Nextmark → now shipping React in production with TypeScript strict mode, Storybook, Redux Toolkit
- No TypeScript → now using strict mode across entire codebase
- No backend/DB → built full Laravel API with 45+ migrations, RBAC, state machines
- No Java → restructured a 39-API Java file into services/models at Beta Technology
- No Python → built SAM in Python 3.13 with FastAPI and MCP protocol
- No formal AI/LLM training → shipping AI-integrated production products with provenance-first governance

**The artist / UX angle:** Is an artist with strong innate visual and UX instincts. Intentionally did not learn Figma — shipping a working app is more valuable than a wireframe. More technical than a UI/UX designer but produces better UX than most engineers.

**AI as a tool, not a crutch:** Uses AI as a force multiplier for implementation. All system design, architecture decisions, and product thinking are his own. SAM itself is his thinking about how AI should be governed in engineering workflows.

**Infrastructure philosophy:** Resourcefulness as a strength. $3/month shared hosting + custom ZIP/FTP/unzip deploy pipeline instead of $100+/month AWS. Matched infrastructure cost to product stage. Good engineering judgment, not a gap.

---

## Experience

### Beta Technology — Contract Full-Stack Engineer
- **Duration:** Feb 2026 – Present (ongoing; 3-month renewal underway)
- **Contract through:** Black Lead Pencil
- **Location:** Remote
- **Domain:** Enterprise PLM (Product Lifecycle Management) on Dassault Systèmes' 3DExperience platform

**What he does:**
- Building React widgets for 3DExperience PLM system
- Designed and building a React component library for team consistency
- Building Java API for new React widget — learned Java in production
- Inherited Java codebase with 39 APIs in one file — refactored into services/models/separation of concerns
- Brings system thinking and software engineering fundamentals to a team learning best practices

**Technologies:** React, TypeScript, Java, 3DExperience PLM (Dassault Systèmes), REST APIs

**What this proves:** Adaptability, system thinking, team collaboration, enterprise software experience

---

### Black Lead Pencil — Freelance Full-Stack Developer & UI/UX Designer
- **Duration:** 2011 – Present
- **Location:** VT / NH
- Full-stack SaaS systems, front-end architectures, Laravel + React/Next.js, workflow-driven UI design, AI-integrated product development, prompt engineering, end-to-end ownership

---

### Nextmark Inc. — Senior Front-End Software Engineer
- **Duration:** 2015 – Feb 2025 (10 years)
- **Location:** NH (www.nextmark.com)
- **Laid off:** Feb 2025
- **Domain:** B2B advertising data platform (Bionic media planning SaaS)

**What he did:**
- Front-end architecture for Bionic, a production media planning SaaS
- Refactored 14,000+ lines of CSS into scalable modular architecture
- Reduced page load time from ~9s to under 5s
- Modernized 50+ legacy pages
- Built pagination, infinite scroll, bulk-edit workflows
- Cross-functional collaboration; mentored junior engineers; established coding standards
- Learned component-based thinking without React (proved the concept before having the tool)

**Constraints:** No React, no TypeScript, no backend access. 10 years of working within constraints made learning the modern stack fast after layoff.

---

### MYSys Inc. — Software Developer Intern
- **Duration:** 2014 – 2015
- **Location:** VT (www.misysinc.com)
- UI tools for industrial ERP systems, AngularJS + HTML5 API documentation, Google Drive/Dropbox/Stripe integrations, marketing-to-CRM automation pipelines

---

## Projects

### Horse Competition Platform (Fire Horse App)
- **Status:** Live in production — launched May 2026
- **URLs:** ge-pc.org (production), stage.ge-pc.org (staging)
- **Built:** Solo with AI assistance (Claude Code), ~3–4 months active development
- **Role:** Sole developer — all architecture, design, and implementation decisions

**What it is:** Full-stack SaaS platform for managing horse show competitions. Multi-organization, multi-show. Virtual, in-person, and hybrid shows. Show creation, scheduling, class management, entries, judging, results publishing.

**Scale:** ~150 source files, ~12,000 lines of application code, 45+ SQL migrations, 20+ database tables, live in production on shared hosting via custom FTP deploy pipeline.

**Backend (Laravel 10 + PHP + MySQL/MariaDB):**
- `BaseModel` — custom Eloquent base with fieldMap (camelCase API input → snake_case columns), eliminates boilerplate
- `BaseResource` — multi-mode API resource (compact/summary/full via `?mode=`) with `resolveData()`
- `PermissionService` — scope-aware RBAC with named roles expanding to atomic permission strings (platform/org/show level, designed for Redis)
- Show status state machine — 3 stored ENUM values + 10 computed `displayStatus` values (server-side); frontend never replicates business logic
- `cor_files` unified file table — images, PDFs, video, HTML via one polymorphic table
- Soft deletes with `deleted_by` audit trail on all major entities
- Laravel Sanctum token auth
- Custom Node.js/zx build pipeline (`_migrate.mjs`, `_deploy-ftp.mjs`, `_build-all.mjs`)

**Database design:** Domain prefix naming (`cor_`, `comp_`, `fin_`). Key tables: cor_users, cor_organizations, cor_org_members, cor_groups, comp_shows, comp_show_classes, comp_entries, fin_invoices, cor_files, cor_access_control. Incremental migration log tracking.

**Frontend (Next.js 14 + React 18 + TypeScript 5.8 strict mode):**
- Material UI v7, Redux Toolkit (session state)
- TypeScript model layer — static factory methods + instance action methods. All API through typed models, not raw fetch.
- Centralized Axios wrapper with `getPaginated<T>` generic and `CollectionResponse<T>`
- 3-tab wizard form with dirty-state tracking via `computeShowFormDirtyDigest()`
- Programmatic modal stack via `useModal()` context (supports stacking)
- Tree-based class builder with palette, canvas, drag-to-group UX (NRHA, AQHA catalogs)
- `use-permission.ts` — frontend permission guard mirroring backend PermissionService
- Storybook 8, Vitest + React Testing Library, Playwright E2E scaffold

**What's functional:** Full show lifecycle, class management, entry submission, file management, user auth, horse CRUD, org membership with invite flow, materialized permissions.

**Known gaps (honest):** Permissions not fully enforced on all routes. Fees/judges/awards/scorecards scaffolded but not wired. No real-time. No email notifications yet (Resend configured). Multi-tenancy designed for V3.

---

### Smart Form — AI-Powered Data Intake Layer
- **Status:** Live — www.blackleadpencil.com/portfolio/smart-form
- **Built:** Solo with AI assistance

**What it is:** AI input layer that sits on top of any legacy form. Users paste messy unstructured data; LLM extracts, normalizes, and maps to form fields. Human reviews and submits.

**Core insight:** "Bulk isn't the problem. The problem is bulk that requires a second clean spreadsheet first." Smart Form bridges the gap without replacing the legacy system.

**Capabilities:** Multi-record detection, phone splitting, email inference, noise filtering (webpage copy-paste), field mapping by semantic meaning (not position), typo tolerance with deterministic messages, bulk entry (thousands of records from one paste), dual-mode editing.

**Five live test datasets** demonstrating edge cases.

**Technical:** React frontend, schema-aware LLM prompting, structured JSON extraction from unstructured input, post-processing layer (AI cannot directly mutate form state until user confirms).

**What this proves:** LLM prompt engineering for deterministic schema-constrained output, HITL system design, AI governance thinking, enterprise-grade problem identification, UX thinking.

---

### SAM — Software Architecture Manager
- **Status:** Active development, ~80% of MVP complete. In production use on Horse Platform.
- **Stack:** Python 3.13, FastAPI, MCP (Model Context Protocol), Vanilla JS SPA, file-based state, YAML config

**What it is:** Pipeline engine that converts raw developer notes (Truths) into formal specification documents (Blueprints) through AI-assisted atomization-and-synthesis. Provenance-first architecture governance system.

**Core differentiator:** Every atom in every Blueprint traces back to a specific source file. AI synthesizes only from verified Truths — it cannot invent.

**Four-tier model (original design):**
- Tier 1 — Truths: raw notes, analysis reports, session logs
- Tier 2 — Blueprints: SRS, DB schema, API contracts (SAM output)
- Tier 3 — Source Code: implementation
- Tier 4 — Results: docs, reports, logs
- Hard rule: Results cannot flow back into Blueprints. Enforced by the system.

**Three interfaces over the same Core engine:** Web UI (HTML/JS SPA), CLI, MCP server (primary — AI agents call SAM tools mid-workflow without leaving the IDE).

**What's built:** Config + Core, Analyse (5-step pipeline), Digest (incremental, crash-resilient, envelope-based storage), Build SRS (autonomous, IEEE 830, 3 zoom levels), DB Schema Blueprint (algorithmic extraction, no AI), MCP Interface (20+ tools, bidirectional chat), Web App.

**Technical decisions:** SAM/AI separation is a hard rule. MCP tool descriptions contain explicit routing instructions. Confidence scoring by source type. Entirely file-based state (killed sessions resume, no DB).

**Known gaps:** API Contract synthesis designed but not implemented. Conflict resolution cycle informal. No approval/gates. Minimal test coverage. Zoom-level UI rendering unverified.

---

## Skills

### Verified in Production

**Languages:** JavaScript (ES6+, 10+ yrs), TypeScript (strict mode), PHP (Laravel 10), Python (3.13, FastAPI, MCP), Java (contributing at Beta Technology — learning in production), SQL (MySQL/MariaDB, 45+ migrations), HTML5 (career-long), CSS3/Sass (14,000+ lines refactored)

**Frameworks & Libraries:** React 18, Next.js 14 (App Router), Laravel 10, Node.js (build scripting), FastAPI, Material UI v7, Redux Toolkit, Axios (centralized wrapper with generics)

**Testing & Quality:** Storybook 8, Vitest + React Testing Library, Playwright (E2E scaffold), Jest, Jasmine, Chrome DevTools / Lighthouse

**AI & LLM Systems:** Prompt engineering (production), HITL system design, AI governance (provenance tracking, validation layers, output isolation), structured AI outputs (schema-constrained extraction), MCP (Model Context Protocol, 20+ tools), Claude/Anthropic API (production), AI-assisted development at scale (12,000-line codebase solo)

**Architecture & System Design:** SaaS architecture (full stack), REST API design (FE + BE), RBAC/permissions (scope-aware), state machine design (server-side derived status), component systems, database schema design (20+ tables, domain prefixing, soft deletes, audit trails), custom build pipelines, file-based resilient state

**DevOps & Tooling:** Git/GitHub, custom automated build+deploy pipeline (AI build → ZIP → FTP → server-side unzip via HTTP trigger), stage + production environment management, Vite, Webpack, npm, Composer, Postman, FTP deploy pipeline, shared hosting deployment

**Specialized:** 3DExperience PLM (Dassault Systèmes), enterprise widget development (Beta Technology)

### Learning / Improving
- Docker / containerization — aware, not yet in own projects
- Cloud platforms (AWS / GCP) — aware, not yet used in production
- RAG / vector databases — planned (Group C gap)
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

## Resume Groups

| Group | Title | Hirability | Rate |
|---|---|---|---|
| A — Full-Stack Product Engineering | Senior Full-Stack Software Engineer | 9/10 | $95–135/hr contract · $140–195k annual |
| B — Frontend / UI Systems Engineering | Senior Frontend Engineer | 9/10 | $85–125/hr contract · $125–175k annual |
| C — AI Systems Engineering | AI Systems Engineer / AI Solutions Engineer | 8/10 | $120–175/hr contract · $160–225k annual |
| D — Technical Leadership & Strategy | Fractional Software Engineer · Technical Advisor | 8/10 | $100–175/hr contract · $120–260k annual |
| E — Technical Product Management & UI/UX | Technical Product Manager / Senior UI Engineer | 7/10 | $100–160/hr contract · $130–200k annual |
| Bridge — SMB Technical Partner | SMB Technical Partner / Fractional Technical Advisor | 9/10 | $65–100/hr |

### Group A — Full-Stack Product Engineering
Lead with: Horse Platform (live production SaaS), Beta Technology (full-stack + Java), Laravel + Next.js depth, end-to-end ownership.
Differentiator: Builds complete systems solo — data model through deployment — and improves legacy codebases.

### Group B — Frontend / UI Systems Engineering
Lead with: Nextmark (10yr, 14k CSS lines, 9s→5s load, 50+ pages), Beta Technology (React component library), Horse Platform (TypeScript strict, Storybook 8, React model layer).
Differentiator: 10+ years of component thinking + modern React stack + artist's UX instinct.

### Group C — AI Systems Engineering
Lead with: Smart Form (live AI product — schema-aware LLM, noise filtering, HITL), SAM (production MCP server, provenance-first governance, 20+ tools), AI-assisted SaaS at scale.
Differentiator: Governance-first AI thinking — not "uses AI" but designs systems that control AI with explicit contracts, validation layers, and human checkpoints.

### Group D — Technical Leadership & Strategy
Lead with: Horse Platform (0→1 solo SaaS, all architecture decisions), Beta Technology (joins team, identifies structural problems, restructures legacy code), Smart Form (product insight + execution), SAM (original system design).
Differentiator: Independent operator who thinks in systems, ships products, and improves whatever codebase he touches.

### Group E — Technical Product Management & UI/UX
Lead with: Horse Platform (sole product owner — every feature, every UX, every architecture tradeoff), Smart Form (identified pain, designed solution, shipped it), 10+ years of frontend work.
Differentiator: Engineer-turned-PM who understands both sides. Can evaluate technical feasibility, talk to engineers, design UX without Figma, make product decisions grounded in implementation reality.
Honest: Not a graphic designer, not a formal user researcher. Strong on product thinking, feature prioritization, technical tradeoffs, UX in code, translating between engineering and business.

### Bridge Track — SMB Technical Partner
Purpose: Income while filling gaps, builds portfolio proof, generates referral relationships. Rate: $65–100/hr.

---

## Gaps (Honest Inventory)

| Gap | Affects | Status |
|---|---|---|
| Docker / containers | A | Add Dockerfile to Horse Platform when moving to cloud |
| Cloud (AWS/GCP) | A | Small AWS project (S3 + Lambda) to close |
| RAG / vector DB | C | Build a small RAG app |
| No agent framework exp (LangGraph etc.) | C | SAM MCP work partially covers this |
| No public writing / thought leadership | C, D | 2–3 LinkedIn articles on AI governance |
| No formal leadership title | D | Covered by narrative + project ownership |
| Permissions not fully wired (Horse Platform) | A | Next sprint |
| No email notifications (Horse Platform) | A | Resend integration partially done |
| Java still learning | A | Beta Technology covers this in progress |

**Not a gap:** CI/CD — has a custom automated pipeline: AI build → ZIP → FTP → server-side unzip via HTTP trigger. Shared hosting intentional ($3/mo vs $100+/mo cloud, pre-traction stage).

---

## Resume Writing Rules

### What to claim
- Java: "contributing to Java API" or "Java API development" — real, in production, just new
- Horse Platform: "shipped production SaaS" — it is LIVE
- Smart Form: "live AI product demo"
- SAM: "in active development, in production use on Horse Platform, 80% of MVP"
- 3DExperience / PLM: real working knowledge from Beta Technology

### What NOT to claim
- Docker, AWS, GCP, RAG, LangGraph — not yet in production
- Figma — intentional choice, do not list

### Framing guidance
- Layoff (Feb 2025): frame as end of Nextmark tenure + beginning of independent work and upskilling. Not a gap.
- AI-assisted development: force multiplier, not crutch. He designs systems; AI accelerates implementation.
- Figma absence: efficiency, not laziness. "I design in Claude browser / build directly in code. When there's no handoff, there's no need for a design file."
- Custom CI/CD: "I practice lean development as a solo engineer. I adopt tools when the benefit justifies the overhead. I'll use GitHub Actions, Figma, and traditional PM workflows on a team where they serve their purpose."
- Infrastructure ($3/mo hosting): resourcefulness and good engineering judgment — matched cost to product stage.

### The Solo Developer Philosophy
Solo developers practice lean, pragmatic engineering. Tools exist to solve coordination problems. When you are all the people, many team tools produce negative value. No Figma, no GitHub Issues / daily commits, custom CI/CD — all intentional. Uses SAM to produce SRS documents, DB schemas, API contracts — the discipline is there, just not the bureaucratic overhead.
