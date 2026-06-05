# Project Instructions

## Starting Point

- Starting from scratch — do NOT build on top of anything in `/old`
- `/old` folder contains prior work kept for reference only; delete later
- Roadmap: `docs/job-hunt-system-roadmap.md`

---

## SAM — The Foundation

SAM (System Architecture Manager) is the reference implementation for this project.

- **Location:** `../SAM` (sibling directory, one level up)
- **Status:** ~80% MVP-ready, includes working web UI
- **Original purpose:** Software documentation and architecture management
- **Our use:** Adapt SAM's architecture, MCP server, pipeline, and UI for job hunting — adapt, don't rebuild

### SAM Structure (what we're borrowing)

```
SAM/
├── src/
│   ├── core/
│   │   ├── config.py       # Config loading & boot validation
│   │   ├── core.py         # SamCore bootstrap class
│   │   ├── mcp.py          # MCP tools (FastMCP server)
│   │   └── actions/        # Pipeline actions
│   ├── server.py           # FastAPI UI server (port 8001)
│   └── ui/
│       ├── index.html      # Vanilla JS SPA (no framework)
│       └── static/sam.css  # Dark theme, CSS Grid
├── truth/                  # Source of truth (raw input files + digests)
├── blueprints/             # Generated output docs
├── .sam/                   # Runtime state (queue, tracking, UI state)
├── sam.config.yaml         # Project config
└── watcher.py              # File watcher for queue-based IPC
```

### Key Patterns from SAM to Follow

**MCP tools (FastMCP):**
- One function = one tool, docstring format:
  ```
  """One-liner action.
  ALWAYS call this tool when: [intents]
  NEVER [anti-patterns]
  ERROR POLICY — [what to do on failure]
  """
  ```
- Tools return error strings starting with `ERROR:`, never raise exceptions

**Digest pipeline (incremental, stage-by-stage):**
1. Discover new/modified files (mtime tracking)
2. Read one file → return prompt for Claude
3. Claude extracts atoms (JSON)
4. Save atoms to domain file
5. Loop → finalize

**File-based state:**
- Atoms stored as JSON per domain in `truth/digests/srs/{domain}.json`
- Envelope format: each digest run wraps atoms with source metadata + digest ID
- Tracking in `.sam/tracking/` using mtime to skip unchanged files
- Queue-based IPC: `.sam/queue/inbox.json` (UI → Claude), `outbox-{session}.jsonl` (Claude → UI)

**Config (sam.config.yaml):**
- Required fields: `truth-path`, `blueprints-path`
- Boot validates paths exist; fails loud if missing
- All paths resolved relative to config file location

**Web UI:**
- Vanilla JS SPA, no build step, served by FastAPI on port 8001
- Two-pane layout: file tree left, content/detail right
- Chat sidebar (right, collapsible) polling every 2s
- Tabs: Home (stats), Truths, Blueprints, Settings
- Uses `marked.js` for markdown rendering

**Launch commands:**
```bash
# UI server
python -m uvicorn src.server:app --port 8001 --reload

# File watcher (queue IPC)
python watcher.py .sam/queue

# MCP server (for Claude Code)
# Registered in .mcp.json
```

---

## Job Hunt System — Domain Mapping

| SAM Concept | Job Hunt Equivalent |
|---|---|
| `truth/` (design docs, notes) | `truth/` (job posts, chips, company notes) |
| `truth/digests/srs/{domain}.json` | `truth/digests/jobs/{domain}.json` |
| SRS domains (core, config, etc.) | Job domains (companies, roles, rates, timing) |
| `blueprints/srs/` (spec docs) | `blueprints/` (resumes, cover letters, prep docs) |
| Atom (extracted spec fact) | Atom (extracted job/truth fact) |
| Blueprint build pipeline | Resume / cover letter generation pipeline |
| `.sam/queue/` | Same — UI ↔ Claude IPC |
| `sam.config.yaml` | `job-hunt.config.yaml` (adds rate, location, rules) |

---

## Truth System — How It Works

### What is a truth file?
Any file dropped in `truth/chips/` gets digested. No schema, no format requirement. One file can contain a mix of experience, skills, constraints, achievements, goals — whatever. The AI reads it and extracts what's relevant.

**Valid chips:**
- An old resume (paste the whole thing)
- A paragraph: "I just wrapped a 6-month contract at Acme, built a RAG pipeline, team of 4"
- A bullet list of skills
- A LinkedIn bio
- A quick note dictated mid-session

The system does NOT enforce one-topic-per-file. Messy is fine.

### Two ways to add truth

1. **Drop a file** into `truth/chips/` — any `.md` or `.txt` file. Tell Claude and it runs `jh_synthesize_master_truth`.

2. **Chat** — say it in the UI chat or Claude Code chat. Claude writes the chip directly and merges it. No file needed. Example: "add to my truth: I finished the AWS cert last week"

### What gets built
All chips merge into `truth/master/truth.md` — the single source of record. Claude never edits this directly; it only rewrites it by synthesizing all chips. Before every rewrite, `jh_snapshot_truth` versions the current master.

Contradictions (e.g. two different dates for the same job) go to `truth/master/anomalies.md` for review — never silently resolved.

---

## Personal Rules (rules/config.yaml)

See full rules template in `docs/job-hunt-system-roadmap.md`. Key fields:

```yaml
identity:
  name: Mahdi Saadat
  base_location: Hardwick, VT

availability:
  current_contract_end: 2026-07-31
  target_start: 2026-08-01

contract_preferences:
  types: [contract, fractional, part-time]
  full_time_permanent: false

rate:
  min_hourly: 85
  preferred_hourly: 120

location:
  remote_first: true
  special_cities:
    boston:
      allowed: true
      short_term_only: true
      hybrid_ok: true
```
