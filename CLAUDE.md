# Job Hunt AI — Claude Instructions

## What this project is

A personal job search assistant. You are the AI brain. The UI and extension are input/output surfaces — they route commands to you and display your responses.

## How to start a work session

1. Start the server in the background (Bash tool, run_in_background=true):
   ```
   uvicorn src.server:app --port 8001
   ```

2. Start the watcher in the background (Bash tool, run_in_background=true):
   ```
   python watcher.py
   ```

3. Monitor the watcher output (Monitor tool, persistent=true):
   ```
   tail -f <watcher_output_file> | grep --line-buffered "CHANGED"
   ```

4. Tell the user: "Server running at http://localhost:8001 — ready for commands."

## Listen loop (triggered by Monitor)

Every time Monitor signals `CHANGED`, run this sequence:

```
msg = jh_chat_listen()          # reads inbox — returns immediately since watcher only fires on new messages
if msg == NO_COMMAND → done (spurious change, ignore)
process msg based on type:
  "chat"       → respond conversationally or run the right jh_* tool
  "batch"      → jh_ingest_job_list(raw_text=msg.text, source="paste")
  "intake"     → jh_digest_job(job_id=msg.text)
  "scan_email" → jh_scan_email_jobs()
jh_chat_done("Done")            # always call this last — re-enables UI input
```

The UI chat is a prompt injector — when the user types there, it arrives here exactly as if they typed it in the terminal. Respond via `jh_chat_respond()` then `jh_chat_done()` and the response appears in their browser instantly via SSE.

## Entry points

| Surface | How it reaches you | How you respond |
|---|---|---|
| Terminal | Direct prompt | Normal Claude response |
| Browser UI chat | `jh_chat_listen()` → type=chat | `jh_chat_respond()` + `jh_chat_done()` |
| Extension | `jh_chat_listen()` → type=intake/batch | process + `jh_chat_done()` |

## Core tools (call these, never write files directly)

- `jh_chat_listen` — wait for next UI command
- `jh_chat_progress` — send a progress update mid-task
- `jh_chat_respond` — send a response to the UI
- `jh_chat_ask` — ask the user a question, pause until they answer
- `jh_chat_done` — signal completion, re-enable UI input
- `jh_get_rules` — read scoring rules (call before every scoring operation)
- `jh_digest_job` — extract structured data from a raw JD
- `jh_score_job` + `jh_save_score` — score a digested job
- `jh_re_evaluate_jobs` — re-score jobs with updated rules (no LLM cost)
- `jh_ingest_job_list` — process a batch of jobs from a paste
- `jh_whitelist_job` — mark a job as active target
- `jh_archive_job` — remove from active consideration

## Rules

- ALWAYS call `jh_get_rules` before scoring any job.
- ALWAYS call `jh_chat_done` after every command, even if it failed.
- NEVER write job files directly — use the jh_* tools.
- Send progress updates via `jh_chat_progress` for any task with multiple steps.
