"""
Job Hunt UI Server
Start: python -m uvicorn src.server:app --port 8001 --reload
UI:    http://localhost:8001
"""

from __future__ import annotations

import json
import re
import yaml
from datetime import datetime
from pathlib import Path

import asyncio
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response, StreamingResponse
from pydantic import BaseModel

from src.core.config import JHConfig

_ROOT = Path(__file__).parent.parent.resolve()
_UI   = Path(__file__).parent / "ui"

_active_project_path: Path | None = None


def _get_active_path() -> Path:
    if _active_project_path is not None:
        return _active_project_path
    return _ROOT


def _load_config() -> JHConfig:
    return JHConfig.load(_get_active_path() / "job-hunt.config.yaml")


def _get_data_path() -> Path:
    return _load_config().data_path


app = FastAPI(title="Job Hunt", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ── Static ───────────────────────────────────────────────────────────────────

@app.get("/static/{filename}")
def serve_static(filename: str):
    path = _UI / "static" / filename
    if not path.exists():
        raise HTTPException(404)
    mt = "text/css" if filename.endswith(".css") else "application/javascript"
    return Response(path.read_text(encoding="utf-8"), media_type=mt)


# ── SPA ──────────────────────────────────────────────────────────────────────

def _spa():
    path = _UI / "index.html"
    if not path.exists():
        return HTMLResponse("<h1>Job Hunt UI not found</h1>", status_code=404)
    return HTMLResponse(path.read_text(encoding="utf-8"))

@app.get("/")
def serve_home(): return _spa()

@app.get("/jobs")
def serve_jobs(): return _spa()

@app.get("/applications")
def serve_applications(): return _spa()

@app.get("/companies")
def serve_companies(): return _spa()

@app.get("/strategy")
def serve_strategy(): return _spa()

@app.get("/resumes")
def serve_resumes(): return _spa()

@app.get("/docs")
def serve_docs(): return _spa()

@app.get("/settings")
def serve_settings(): return _spa()


# ── Config ───────────────────────────────────────────────────────────────────

@app.get("/api/config")
def get_config():
    cfg = _load_config()
    return {
        "project_name": cfg.get("project", "Job Hunt"),
        "project_path": str(_get_active_path()),
        "ai_model": cfg.ai_model,
        "truth_path": cfg.get("truth-path", "truth"),
        "blueprints_path": cfg.get("blueprints-path", "blueprints"),
        "rules_path": cfg.get("rules-path", "rules/config.yaml"),
    }


# ── Rules ────────────────────────────────────────────────────────────────────

@app.get("/api/rules")
def get_rules():
    cfg = _load_config()
    rules_file = cfg.rules_path
    if not rules_file.exists():
        return {"rules": None, "error": "rules/config.yaml not found"}
    try:
        rules = yaml.safe_load(rules_file.read_text(encoding="utf-8"))
        return {"rules": rules}
    except Exception as e:
        return {"rules": None, "error": str(e)}


# ── Jobs ─────────────────────────────────────────────────────────────────────

def _parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    try:
        return yaml.safe_load(text[3:end]) or {}
    except Exception:
        return {}


def _parse_rate(s: str) -> float | None:
    if not s: return None
    s = str(s).lower().strip()
    if any(t in s for t in ("/yr", "/year", "per year")):
        m = re.search(r"(\d[\d,]*)", s)
        if m:
            v = float(m.group(1).replace(",", ""))
            return round((v if v >= 1000 else v * 1000) / 2000, 2)
    if re.match(r"^\$?\d+k$", s):
        return round(float(re.search(r"\d+", s).group()) * 1000 / 2000, 2)
    if any(t in s for t in ("/hr", "/hour")):
        m = re.search(r"\$?(\d+(?:\.\d+)?)", s)
        if m:
            v = float(m.group(1)); return v if 15 <= v <= 600 else None
    nums = [float(n.replace(",", "")) for n in re.findall(r"\d[\d,]*", s)
            if float(n.replace(",", "")) >= 10000]
    if nums: return round(sum(nums) / len(nums) / 2000, 2)
    m = re.search(r"\$?(\d+(?:\.\d+)?)", s)
    if m:
        v = float(m.group(1)); return v if 15 <= v <= 600 else None
    return None


def _load_rules() -> dict:
    f = _get_data_path() / "rules" / "config.yaml"
    if not f.exists(): return {}
    try: return yaml.safe_load(f.read_text(encoding="utf-8")) or {}
    except Exception: return {}


def _load_company_tags() -> dict:
    f = _get_data_path() / "companies" / "tags.json"
    if not f.exists(): return {}
    try: return json.loads(f.read_text(encoding="utf-8"))
    except Exception: return {}


def _save_company_tags(tags: dict):
    f = _get_data_path() / "companies" / "tags.json"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(tags, indent=2, ensure_ascii=False), encoding="utf-8")


def _compute_pursuit(meta: dict, rules: dict, company_tags: dict) -> tuple[float, str, str]:
    """Benefit-of-doubt pursuit score for partial-info list jobs.
    Returns (pursuit_score, bucket, notes)."""
    score = 70.0
    notes = []
    signals = meta.get("signals") or {}
    loc_rules = rules.get("location", {})
    local_cities = list((loc_rules.get("local_cities") or {}).keys())
    special_cities = list((loc_rules.get("special_cities") or {}).keys())
    base_loc = rules.get("identity", {}).get("base_location", "")
    home_state = base_loc.split(",")[-1].strip().lower() if "," in base_loc else ""

    # Rate: known → score it; unknown → small benefit-of-doubt boost
    rate_str = meta.get("salary_stated") or meta.get("rate_stated")
    r = _parse_rate(str(rate_str)) if rate_str else None
    if r is not None:
        if (meta.get("contract_type") or "").lower() == "full-time":
            r = round(r * 1.30, 2)
        r_min  = rules.get("rate", {}).get("min_hourly", 85)
        r_pref = rules.get("rate", {}).get("preferred_hourly", 120)
        if r >= r_pref:   score += 15; notes.append(f"${r:.0f}/hr — at preferred")
        elif r >= r_min:  score +=  0; notes.append(f"${r:.0f}/hr — above minimum")
        else:             score -= 20; notes.append(f"${r:.0f}/hr — below minimum")
    else:
        score += 5; notes.append("Rate unknown — benefit of doubt")

    # Location
    rp  = (meta.get("remote_policy") or "").lower()
    loc = (meta.get("location") or "").lower()
    if rp == "remote":
        score += 15; notes.append("Remote")
    elif rp == "hybrid":
        is_near = any(c.lower() in loc for c in local_cities + special_cities)
        score += 8 if is_near else 3
        notes.append("Hybrid" + (" (local)" if is_near else ""))
    elif rp == "onsite":
        is_local   = any(c.lower() in loc for c in local_cities)
        is_special = any(c.lower() in loc for c in special_cities)
        p = loc_rules.get("onsite_negotiable_probability", 0.0)
        if is_local or is_special:
            score += round(p * 10 - 5, 1); notes.append(f"Onsite local — {int(p*100)}% hybrid likely")
        elif home_state and home_state in loc:
            score -= 5; notes.append("Onsite home state")
        else:
            score -= 20; notes.append(f"Onsite {loc or '?'} — not local")
    else:
        score += 3; notes.append("Location unknown — assumed hybrid")

    # Contract
    ct = (meta.get("contract_type") or "").lower()
    if ct in ("contract", "fractional"):   score += 5;  notes.append("Contract")
    elif ct == "full-time":                score -= 5;  notes.append("Full-time (prefer contract)")

    # Signals: applicant competition
    n_apps = signals.get("applicant_count")
    if n_apps is not None:
        n = int(n_apps)
        if n > 300:   score -= 20; notes.append(f"{n} applicants — very competitive")
        elif n > 100: score -= 10; notes.append(f"{n} applicants — competitive")
        elif n > 50:  score -=  3; notes.append(f"{n} applicants — moderate")
        else:         score +=  8; notes.append(f"{n} applicants — low competition")

    # Signals: easy apply (net positive with the app — real role + fast execution)
    ea = signals.get("easy_apply")
    if ea is True:   score += 3;  notes.append("Easy Apply (real role, fast execution)")
    elif ea is False: score += 10; notes.append("Hard apply — smaller applicant pool")

    # Signals: post freshness
    d = signals.get("days_since_posted")
    if d is not None:
        d = int(d)
        if d <= 2:    score += 15; notes.append(f"Posted {d}d ago — fresh")
        elif d <= 7:  score +=  8; notes.append(f"Posted {d}d ago — recent")
        elif d <= 30: score -=  8; notes.append(f"Posted {d}d ago — aging")
        else:         score -= 15; notes.append(f"Posted {d}d ago — stale")

    # Source bonus
    if (meta.get("source") or "").lower() == "recruiter":
        score += 15; notes.append("Recruiter outreach")

    # Company intelligence
    slug  = meta.get("company_slug") or (meta.get("company") or "").lower().replace(" ", "-")
    ctag  = (company_tags.get(slug) or {}).get("tag", "")
    if ctag == "preferred":                score += 20; notes.append("Preferred company")
    elif ctag in ("suspect", "resume_farmer"): score -= 35; notes.append(f"⚠ {ctag.replace('_', ' ')}")
    elif ctag == "slow_process":           score -=  5; notes.append("Known slow process")
    elif ctag == "blacklisted":            score -= 50; notes.append("Blacklisted company")

    score = max(0.0, min(100.0, round(score, 1)))

    # Explicit bucket in file overrides auto-assignment
    explicit_bucket = meta.get("bucket")
    if explicit_bucket:
        return score, explicit_bucket, "; ".join(notes)

    # Auto-assign bucket
    if ctag in ("suspect", "resume_farmer", "blacklisted"):
        bucket = "suspect"
    elif score >= 78: bucket = "pursue"
    elif score >= 60: bucket = "research"
    elif score >= 42: bucket = "watch"
    else:             bucket = "pass"

    return score, bucket, "; ".join(notes)


def _list_job_files(subfolder: str, rules: dict | None = None, company_tags: dict | None = None) -> list[dict]:
    folder = _get_data_path() / "jobs" / subfolder
    if not folder.exists():
        return []
    if rules is None:        rules = _load_rules()
    if company_tags is None: company_tags = _load_company_tags()
    jobs = []
    for f in sorted(folder.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True):
        if f.name == ".gitkeep": continue
        stat = f.stat()
        try:
            meta = _parse_frontmatter(f.read_text(encoding="utf-8"))
        except Exception:
            meta = {}

        # Compute pursuit score for batch list items that haven't been fully scored
        pursuit_score, bucket, pursuit_notes = None, meta.get("bucket"), None
        if meta.get("batch_id") and meta.get("score") is None:
            pursuit_score, bucket, pursuit_notes = _compute_pursuit(meta, rules, company_tags)

        jobs.append({
            "id": f.stem,
            "filename": f.name,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()[:16],
            "type": meta.get("type", "single"),
            "title": meta.get("title"),
            "company": meta.get("company"),
            "company_slug": meta.get("company_slug"),
            "batch_id": meta.get("batch_id"),
            "triage_result": meta.get("triage_result"),
            "score": meta.get("score"),
            "recommendation": meta.get("recommendation"),
            "source": meta.get("source"),
            "source_url": meta.get("source_url"),
            "location": meta.get("location"),
            "remote_policy": meta.get("remote_policy"),
            "contract_type": meta.get("contract_type"),
            "salary_stated": meta.get("salary_stated"),
            "rate_stated": meta.get("rate_stated"),
            "intake_date": meta.get("intake_date"),
            "bucket": bucket,
            "pursuit_score": pursuit_score,
            "pursuit_notes": pursuit_notes,
            "signals": meta.get("signals") or {},
        })
    return jobs


@app.get("/api/jobs")
def list_jobs(status: str = "all"):
    rules = _load_rules()
    company_tags = _load_company_tags()
    if status == "all":
        return {
            "raw":         _list_job_files("raw",         rules, company_tags),
            "digested":    _list_job_files("digested",    rules, company_tags),
            "whitelisted": _list_job_files("whitelisted", rules, company_tags),
            "archived":    _list_job_files("archived",    rules, company_tags),
        }
    return {"jobs": _list_job_files(status, rules, company_tags)}


@app.get("/api/jobs/stats")
def job_stats():
    return {
        "raw":         len(_list_job_files("raw")),
        "digested":    len(_list_job_files("digested")),
        "whitelisted": len(_list_job_files("whitelisted")),
        "archived":    len(_list_job_files("archived")),
    }


class JobIntake(BaseModel):
    text: str
    html: str = ""             # raw HTML of selection — preserves links and structure
    source_url: str = ""
    job_type: str = "single"   # "single" | "list"
    links: list[str] = []      # href links extracted by extension (job card URLs)


async def _queue_claude(msg_text: str, msg_type: str = "intake") -> bool:
    """Put a message in the active session inbox. Returns True if queued."""
    if _active_session is None or _active_session.status == "busy":
        return False
    from uuid import uuid4
    msg_id = f"MSG-{uuid4().hex[:8].upper()}"
    msg = {"id": msg_id, "type": msg_type, "text": msg_text,
           "sent_at": datetime.now().isoformat()}
    await _active_session.inbox.put(msg)
    return True


@app.post("/api/jobs/intake")
async def intake_job(body: JobIntake):
    """Browser extension / paste endpoint. job_type='single' for one JD, 'list' for batch."""
    from uuid import uuid4
    today = datetime.now().strftime("%Y%m%d")

    if body.job_type == "list":
        batch_id = f"batch_{today}_{uuid4().hex[:8]}"
        batches_dir = _get_data_path() / "jobs" / "batches"
        batches_dir.mkdir(parents=True, exist_ok=True)
        meta = {
            "batch_id": batch_id,
            "source": body.source_url or "extension",
            "source_page_url": body.source_url,
            "intake_date": datetime.now().strftime("%Y-%m-%d"),
            "status": "raw",
            "job_count": None,
            "passed_count": None,
            "excluded_count": None,
        }
        # Append extracted links to the text so Claude can match them to jobs
        extra = ""
        if body.links:
            extra = "\n\n--- Extracted Job Links ---\n" + "\n".join(body.links)
        content = "---\n" + yaml.dump(meta, default_flow_style=False) + "---\n\n" + body.text + extra
        (batches_dir / f"{batch_id}.md").write_text(content, encoding="utf-8")
        auto_queued = await _queue_claude(
            f"triage batch {batch_id}", msg_type="batch"
        )
        return {"batch_id": batch_id, "status": "raw", "type": "list",
                "auto_queued": auto_queued,
                "message": f"List captured — {batch_id}"}

    job_id = f"job_{today}_{uuid4().hex[:8]}"
    raw_dir = _get_data_path() / "jobs" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "id": job_id,
        "type": "single",
        "intake_date": datetime.now().strftime("%Y-%m-%d"),
        "source_url": body.source_url,
        "status": "raw",
        "title": None, "company": None, "company_slug": None,
        "location": None, "remote_policy": None, "contract_type": None,
        "duration_months": None, "rate_stated": None, "posted_date": None,
        "score": None, "recommendation": None, "group_fit": [],
    }
    content = "---\n" + yaml.dump(meta, default_flow_style=False) + "---\n\n" + body.text
    (raw_dir / f"{job_id}.md").write_text(content, encoding="utf-8")
    auto_queued = await _queue_claude(
        f"digest {job_id}", msg_type="intake"
    )
    return {"job_id": job_id, "status": "raw", "type": "single",
            "auto_queued": auto_queued,
            "message": f"Job captured — {job_id}"}


@app.get("/api/jobs/batches")
def list_batches():
    batches_dir = _get_data_path() / "jobs" / "batches"
    if not batches_dir.exists():
        return {"batches": []}
    rules = _load_rules()
    company_tags = _load_company_tags()
    # Pre-scan all job files once to build batch→bucket counts
    batch_buckets: dict[str, dict[str, int]] = {}
    for subfolder in ["raw", "archived"]:
        folder = _get_data_path() / "jobs" / subfolder
        if not folder.exists():
            continue
        for jf in folder.glob("*.md"):
            if jf.name == ".gitkeep":
                continue
            try:
                jmeta = _parse_frontmatter(jf.read_text(encoding="utf-8"))
            except Exception:
                continue
            bid = jmeta.get("batch_id")
            if not bid:
                continue
            _, bucket, _ = _compute_pursuit(jmeta, rules, company_tags)
            bc = batch_buckets.setdefault(bid, {})
            bc[bucket] = bc.get(bucket, 0) + 1

    batches = []
    for f in sorted(batches_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True):
        try:
            meta = _parse_frontmatter(f.read_text(encoding="utf-8"))
        except Exception:
            meta = {}
        bid = f.stem
        batches.append({
            "batch_id": bid,
            "source": meta.get("source", ""),
            "intake_date": meta.get("intake_date", ""),
            "status": meta.get("status", "raw"),
            "job_count": meta.get("job_count"),
            "passed_count": meta.get("passed_count"),
            "excluded_count": meta.get("excluded_count"),
            "bucket_counts": batch_buckets.get(bid) or meta.get("bucket_counts") or {},
        })
    return {"batches": batches}


@app.get("/api/jobs/batches/{batch_id}")
def get_batch(batch_id: str):
    batches_dir = _get_data_path() / "jobs" / "batches"
    f = batches_dir / f"{batch_id}.md"
    if not f.exists():
        raise HTTPException(404, f"Batch {batch_id} not found")
    meta = _parse_frontmatter(f.read_text(encoding="utf-8"))
    rules = _load_rules()
    company_tags = _load_company_tags()
    jobs = []
    for subfolder in ["raw", "digested", "whitelisted", "archived"]:
        folder = _get_data_path() / "jobs" / subfolder
        if not folder.exists(): continue
        for jf in sorted(folder.glob("*.md"), key=lambda x: x.stat().st_mtime):
            if jf.name == ".gitkeep": continue
            try:
                content = jf.read_text(encoding="utf-8")
                jmeta = _parse_frontmatter(content)
            except Exception:
                continue
            if jmeta.get("batch_id") != batch_id:
                continue
            pursuit_score, bucket, pursuit_notes = _compute_pursuit(jmeta, rules, company_tags)
            jobs.append({
                "id": jf.stem,
                "stage": subfolder,
                "title": jmeta.get("title"),
                "company": jmeta.get("company"),
                "company_slug": jmeta.get("company_slug"),
                "location": jmeta.get("location"),
                "remote_policy": jmeta.get("remote_policy"),
                "contract_type": jmeta.get("contract_type"),
                "salary_stated": jmeta.get("salary_stated"),
                "rate_stated": jmeta.get("rate_stated"),
                "source_url": jmeta.get("source_url"),
                "triage_result": jmeta.get("triage_result"),
                "exclude_reason": jmeta.get("exclude_reason"),
                "score": jmeta.get("score"),
                "recommendation": jmeta.get("recommendation"),
                "bucket": bucket,
                "pursuit_score": pursuit_score,
                "pursuit_notes": pursuit_notes,
                "signals": jmeta.get("signals") or {},
            })
    return {"batch_id": batch_id, "meta": meta, "jobs": jobs}


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    for subfolder in ["whitelisted", "digested", "raw", "archived"]:
        f = _get_data_path() / "jobs" / subfolder / f"{job_id}.md"
        if f.exists():
            content = f.read_text(encoding="utf-8")
            meta = _parse_frontmatter(content)
            return {"job_id": job_id, "status": subfolder, "content": content, "meta": meta}
    raise HTTPException(404, f"Job {job_id} not found")


class DimOverride(BaseModel):
    dimension: str
    score: float

@app.patch("/api/jobs/{job_id}/score")
def patch_score(job_id: str, body: DimOverride):
    job_file = None
    for subfolder in ["whitelisted", "digested"]:
        f = _get_data_path() / "jobs" / subfolder / f"{job_id}.md"
        if f.exists():
            job_file = f
            break
    if not job_file:
        raise HTTPException(404, f"Job {job_id} not in digested or whitelisted")

    content = job_file.read_text(encoding="utf-8")
    meta = _parse_frontmatter(content)
    body_text = content[content.find("\n---", 3) + 4:] if "\n---" in content[3:] else content

    breakdown = meta.get("score_breakdown") or {}
    dim = body.dimension
    if dim not in breakdown:
        breakdown[dim] = {}
    breakdown[dim]["score"] = round(max(0, min(100, body.score)), 1)
    breakdown[dim]["override"] = True
    meta["score_breakdown"] = breakdown

    rules_file = _get_data_path() / "rules" / "config.yaml"
    rules = yaml.safe_load(rules_file.read_text(encoding="utf-8")) if rules_file.exists() else {}
    weights = rules.get("scoring_weights") or {
        "skill_match": 0.30, "rate_match": 0.25, "location_match": 0.20,
        "contract_length_match": 0.15, "timing_match": 0.10,
    }
    composite = round(sum(
        breakdown.get(d, {}).get("score", 0) * w for d, w in weights.items()
    ), 1)
    rec = "apply" if composite >= 80 else "monitor" if composite >= 65 else "stretch" if composite >= 45 else "pass"
    meta["score"] = composite
    meta["recommendation"] = rec

    job_file.write_text(
        "---\n" + yaml.dump(meta, default_flow_style=False, allow_unicode=True) + "---\n" + body_text,
        encoding="utf-8",
    )
    return {"score": composite, "recommendation": rec, "dimension": dim, "dim_score": breakdown[dim]["score"]}


class BucketUpdate(BaseModel):
    bucket: str

_VALID_BUCKETS = {"pursue", "research", "watch", "pass", "suspect", "signal_play", "intelligence"}

@app.patch("/api/jobs/{job_id}/bucket")
def patch_bucket(job_id: str, body: BucketUpdate):
    if body.bucket not in _VALID_BUCKETS:
        raise HTTPException(400, f"Invalid bucket. Valid: {', '.join(sorted(_VALID_BUCKETS))}")
    for subfolder in ["raw", "digested", "whitelisted", "archived"]:
        f = _get_data_path() / "jobs" / subfolder / f"{job_id}.md"
        if f.exists():
            content = f.read_text(encoding="utf-8")
            meta = _parse_frontmatter(content)
            body_text = content[content.find("\n---", 3) + 4:] if "\n---" in content[3:] else content
            meta["bucket"] = body.bucket
            f.write_text(
                "---\n" + yaml.dump(meta, default_flow_style=False, allow_unicode=True) + "---\n" + body_text,
                encoding="utf-8",
            )
            return {"job_id": job_id, "bucket": body.bucket}
    raise HTTPException(404, f"Job {job_id} not found")


class StageAction(BaseModel):
    reason: str = ""

@app.patch("/api/jobs/{job_id}/archive")
def patch_archive(job_id: str, body: StageAction = StageAction()):
    root = _get_data_path() / "jobs"
    for subfolder in ("whitelisted", "digested", "raw"):
        src = root / subfolder / f"{job_id}.md"
        if src.exists():
            content = src.read_text(encoding="utf-8")
            meta = _parse_frontmatter(content)
            body_text = content[content.find("\n---", 3) + 4:] if "\n---" in content[3:] else content
            meta["status"] = "archived"
            meta["_pre_archive_stage"] = subfolder
            if body.reason:
                meta["archive_reason"] = body.reason
            dest = root / "archived"
            dest.mkdir(parents=True, exist_ok=True)
            (dest / f"{job_id}.md").write_text(
                "---\n" + yaml.dump(meta, default_flow_style=False, allow_unicode=True) + "---\n" + body_text,
                encoding="utf-8",
            )
            src.unlink()
            return {"job_id": job_id, "stage": "archived"}
    raise HTTPException(404, f"Job {job_id} not found in active folders")


@app.patch("/api/jobs/{job_id}/unarchive")
def patch_unarchive(job_id: str):
    src = _get_data_path() / "jobs" / "archived" / f"{job_id}.md"
    if not src.exists():
        raise HTTPException(404, f"Job {job_id} not in archived")
    content = src.read_text(encoding="utf-8")
    meta = _parse_frontmatter(content)
    body_text = content[content.find("\n---", 3) + 4:] if "\n---" in content[3:] else content
    restore_to = meta.pop("_pre_archive_stage", "raw")
    meta.pop("archive_reason", None)
    meta["status"] = restore_to
    dest = _get_data_path() / "jobs" / restore_to
    dest.mkdir(parents=True, exist_ok=True)
    (dest / f"{job_id}.md").write_text(
        "---\n" + yaml.dump(meta, default_flow_style=False, allow_unicode=True) + "---\n" + body_text,
        encoding="utf-8",
    )
    src.unlink()
    return {"job_id": job_id, "stage": restore_to}


@app.get("/api/companies/tags")
def get_company_tags():
    return _load_company_tags()


class CompanyTag(BaseModel):
    company: str
    company_slug: str = ""
    tag: str  # preferred | suspect | resume_farmer | slow_process | blacklisted
    note: str = ""

@app.post("/api/companies/tag")
def tag_company(body: CompanyTag):
    VALID_TAGS = {"preferred", "suspect", "resume_farmer", "slow_process", "blacklisted"}
    if body.tag not in VALID_TAGS:
        raise HTTPException(400, f"Invalid tag. Valid: {', '.join(sorted(VALID_TAGS))}")
    tags = _load_company_tags()
    slug = body.company_slug or re.sub(r"[^a-z0-9]+", "-", body.company.lower()).strip("-")
    tags[slug] = {
        "company": body.company,
        "tag": body.tag,
        "note": body.note,
        "tagged_at": datetime.now().strftime("%Y-%m-%d"),
    }
    _save_company_tags(tags)
    return {"slug": slug, "tag": body.tag}


# ── Truth ────────────────────────────────────────────────────────────────────

@app.get("/api/truth/chips")
def list_chips():
    cfg = _load_config()
    chips_dir = cfg.truth_path / "chips"
    if not chips_dir.exists():
        return {"chips": []}
    chips = []
    for f in sorted(chips_dir.iterdir()):
        if f.is_file() and not f.name.startswith("."):
            stat = f.stat()
            chips.append({
                "name": f.name,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()[:16],
            })
    return {"chips": chips}


@app.get("/api/truth/master")
def get_master_truth():
    cfg = _load_config()
    truth_file = cfg.truth_path / "master" / "truth.md"
    if not truth_file.exists():
        return {"content": None, "exists": False}
    return {"content": truth_file.read_text(encoding="utf-8"), "exists": True}


# ── Companies ────────────────────────────────────────────────────────────────

@app.get("/api/companies")
def list_companies(status: str = ""):
    companies_dir = _get_data_path() / "companies"
    if not companies_dir.exists():
        return {"companies": []}
    companies = []
    for f in sorted(companies_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True):
        try:
            meta = _parse_frontmatter(f.read_text(encoding="utf-8"))
        except Exception:
            meta = {}
        if status and meta.get("status") != status:
            continue
        companies.append({
            "slug": f.stem,
            "name": meta.get("name", f.stem),
            "status": meta.get("status", "cold"),
            "industry": meta.get("industry"),
            "size": meta.get("size"),
            "job_count": len(meta.get("jobs") or []),
            "warm_lead_resurface": meta.get("warm_lead_resurface"),
            "last_updated": meta.get("last_updated"),
        })
    return {"companies": companies}


@app.get("/api/companies/warm-leads")
def get_warm_leads():
    """Return warm companies due for resurfacing (resurface_date <= today)."""
    from datetime import date
    companies_dir = _get_data_path() / "companies"
    if not companies_dir.exists():
        return {"due": [], "upcoming": []}
    today = date.today()
    due, upcoming = [], []
    for f in companies_dir.glob("*.md"):
        try:
            meta = _parse_frontmatter(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if meta.get("status") != "warm":
            continue
        rs = meta.get("warm_lead_resurface")
        if not rs:
            continue
        try:
            rs_date = date.fromisoformat(str(rs))
        except ValueError:
            continue
        entry = {
            "slug": f.stem,
            "name": meta.get("name", f.stem),
            "warm_lead_note": meta.get("warm_lead_note", ""),
            "warm_lead_since": meta.get("warm_lead_since"),
            "resurface_date": str(rs),
        }
        if rs_date <= today:
            due.append(entry)
        else:
            upcoming.append(entry)
    return {"due": due, "upcoming": upcoming}


@app.get("/api/companies/{slug}")
def get_company(slug: str):
    company_file = _get_data_path() / "companies" / f"{slug}.md"
    if not company_file.exists():
        raise HTTPException(404, f"Company '{slug}' not found")
    content = company_file.read_text(encoding="utf-8")
    meta = _parse_frontmatter(content)
    return {"slug": slug, "meta": meta, "content": content}


# ── Strategy ─────────────────────────────────────────────────────────────────

@app.get("/api/strategy")
def list_strategy_docs():
    cfg = _load_config()
    strategy_dir = cfg.blueprints_path / "strategy"
    docs = [
        {"name": "market-patterns",   "label": "Market Patterns",   "slug": "market-patterns.md"},
        {"name": "gap-analysis",       "label": "Gap Analysis",       "slug": "gap-analysis.md"},
        {"name": "portfolio-roadmap",  "label": "Portfolio Roadmap",  "slug": "portfolio-roadmap.md"},
    ]
    for doc in docs:
        path = strategy_dir / doc["slug"]
        doc["exists"] = path.exists()
        if path.exists():
            doc["modified"] = datetime.fromtimestamp(path.stat().st_mtime).isoformat()[:16]
        else:
            doc["modified"] = None
    return {"docs": docs}


# ── Blueprints ───────────────────────────────────────────────────────────────

@app.get("/api/blueprints")
def list_blueprints():
    cfg = _load_config()
    bp_root = cfg.blueprints_path
    if not bp_root.exists():
        return {"types": []}

    types = []
    for folder in sorted(bp_root.iterdir()):
        if not folder.is_dir() or folder.name.startswith("."):
            continue
        files = []
        for f in sorted(folder.glob("*.md")):
            stat = f.stat()
            files.append({
                "name": f.stem,
                "filename": f.name,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()[:16],
            })
        if files:
            types.append({"type": folder.name, "count": len(files), "files": files})
    return {"types": types}


@app.get("/api/blueprints/{bp_type}/{filename}")
def get_blueprint(bp_type: str, filename: str):
    cfg = _load_config()
    path = cfg.blueprints_path / bp_type / filename
    if not path.exists():
        raise HTTPException(404, f"Blueprint not found: {bp_type}/{filename}")
    return {"type": bp_type, "filename": filename, "content": path.read_text(encoding="utf-8")}


@app.get("/api/resumes")
def list_resumes():
    cfg = _load_config()
    generated_dir = cfg.blueprints_path / "resumes" / "generated"
    if not generated_dir.exists():
        return {"resumes": []}
    resumes = []
    for group_dir in sorted(generated_dir.iterdir()):
        if not group_dir.is_dir():
            continue
        resume_file = group_dir / "resume.md"
        if resume_file.exists():
            stat = resume_file.stat()
            resumes.append({
                "group": group_dir.name,
                "label": "Group " + group_dir.name.replace("group_", "").upper(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()[:16],
            })
    return {"resumes": resumes}


@app.get("/api/resumes/{group}")
def get_resume(group: str):
    cfg = _load_config()
    resume_file = cfg.blueprints_path / "resumes" / "generated" / group / "resume.md"
    if not resume_file.exists():
        raise HTTPException(404, f"Resume not found: {group}")
    return {"group": group, "content": resume_file.read_text(encoding="utf-8")}


# ── Docs ─────────────────────────────────────────────────────────────────────

@app.get("/api/docs")
def list_all_docs():
    """List all jobs that have generated application docs."""
    apps_root = _get_data_path() / "applications"
    if not apps_root.exists():
        return {"jobs": []}
    jobs = []
    for job_dir in sorted(apps_root.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        if not job_dir.is_dir() or job_dir.name in ("active", "outcomes"):
            continue
        files = [f.name for f in sorted(job_dir.glob("*.md"))]
        if files:
            jobs.append({"job_id": job_dir.name, "files": files})
    return {"jobs": jobs}


@app.get("/api/docs/{job_id}")
def list_job_docs(job_id: str):
    """List available docs for a specific job."""
    docs_dir = _get_data_path() / "applications" / job_id
    if not docs_dir.exists():
        return {"job_id": job_id, "files": []}
    files = []
    for f in sorted(docs_dir.glob("*.md")):
        stat = f.stat()
        files.append({
            "filename": f.name,
            "label": f.stem.replace("_", " ").title(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()[:16],
        })
    return {"job_id": job_id, "files": files}


@app.get("/api/docs/{job_id}/{filename}")
def get_job_doc(job_id: str, filename: str):
    """Return the content of a specific generated doc."""
    doc_path = _get_data_path() / "applications" / job_id / filename
    if not doc_path.exists():
        raise HTTPException(404, f"Doc not found: {job_id}/{filename}")
    return {"job_id": job_id, "filename": filename, "content": doc_path.read_text(encoding="utf-8")}


# ── Applications ─────────────────────────────────────────────────────────────

@app.get("/api/applications/followups")
def get_followups():
    """Return overdue + due-today applications."""
    from datetime import date
    folder = _get_data_path() / "applications" / "active"
    if not folder.exists():
        return {"overdue": [], "due_today": [], "count": 0}
    today = date.today()
    overdue, due_today = [], []
    for f in sorted(folder.glob("*.md"), key=lambda x: x.stat().st_mtime):
        try:
            meta = _parse_frontmatter(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        fu_str = meta.get("follow_up_date", "")
        if not fu_str:
            continue
        try:
            fu = date.fromisoformat(str(fu_str))
        except ValueError:
            continue
        entry = {
            "job_id": f.stem,
            "title": meta.get("title"),
            "company": meta.get("company"),
            "applied_date": meta.get("applied_date"),
            "follow_up_date": fu_str,
            "days_overdue": (today - fu).days if fu < today else 0,
        }
        if fu < today:
            overdue.append(entry)
        elif fu == today:
            due_today.append(entry)
    return {"overdue": overdue, "due_today": due_today, "count": len(overdue) + len(due_today)}


@app.get("/api/applications")
def list_applications(status: str = "active"):
    folder = _get_data_path() / "applications" / status
    if not folder.exists():
        return {"applications": []}
    apps = []
    for f in sorted(folder.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True):
        stat = f.stat()
        try:
            meta = _parse_frontmatter(f.read_text(encoding="utf-8"))
        except Exception:
            meta = {}
        apps.append({
            "job_id": f.stem,
            "title": meta.get("title"),
            "company": meta.get("company"),
            "applied_date": meta.get("applied_date"),
            "method": meta.get("method"),
            "follow_up_date": meta.get("follow_up_date"),
            "outcome_date": meta.get("outcome_date"),
            "status": meta.get("status", "applied"),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()[:16],
        })
    return {"applications": apps}


# ── UI State ─────────────────────────────────────────────────────────────────

@app.get("/api/ui-state")
def get_ui_state():
    f = _get_active_path() / ".jh" / "ui-state.json"
    if not f.exists():
        return {}
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        return {}


class UiStatePatch(BaseModel):
    data: dict

@app.post("/api/ui-state")
def save_ui_state(body: UiStatePatch):
    jh_dir = _get_active_path() / ".jh"
    jh_dir.mkdir(parents=True, exist_ok=True)
    f = jh_dir / "ui-state.json"
    existing: dict = {}
    if f.exists():
        try:
            existing = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            pass
    existing.update(body.data)
    f.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    return existing


# ── Chat / SSE ───────────────────────────────────────────────────────────────

class _Session:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.started_at = datetime.now().isoformat()
        self.outbox: list[dict] = []
        self._subscribers: list[asyncio.Queue] = []
        self.inbox: asyncio.Queue = asyncio.Queue()
        self.status: str = "idle"  # idle | busy | waiting

    def push(self, msg: dict) -> None:
        self.outbox.append(msg)
        for q in self._subscribers:
            q.put_nowait(msg)

    def subscribe(self, since: int = 0) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._subscribers.append(q)
        for msg in self.outbox[since:]:
            q.put_nowait(msg)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        try:
            self._subscribers.remove(q)
        except ValueError:
            pass


_sessions: dict[str, _Session] = {}
_active_session: _Session | None = None


def _qdir() -> Path:
    q = _ROOT / ".jh" / "queue"
    q.mkdir(parents=True, exist_ok=True)
    return q


@app.post("/api/chat/session/start")
async def start_session():
    global _active_session
    session_id = f"session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    session = _Session(session_id)
    _sessions[session_id] = session
    _active_session = session
    active = {"session_id": session_id, "started_at": session.started_at}
    (_qdir() / "active-session.json").write_text(
        json.dumps(active, indent=2), encoding="utf-8"
    )
    return active


@app.get("/api/chat/stream")
async def chat_stream(session_id: str, request: Request):
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(404, "Session not found — reload the page.")
    last_id = request.headers.get("last-event-id", "")
    since = int(last_id) + 1 if last_id.isdigit() else 0
    q = session.subscribe(since)

    async def generator():
        pos = since
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    msg = await asyncio.wait_for(q.get(), timeout=20.0)
                    yield f"id: {pos}\ndata: {json.dumps(msg)}\n\n"
                    pos += 1
                except asyncio.TimeoutError:
                    yield ": keep-alive\n\n"
        finally:
            session.unsubscribe(q)

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


class ChatSend(BaseModel):
    text: str
    type: str = "chat"


@app.post("/api/chat/send")
async def chat_send(body: ChatSend):
    from uuid import uuid4
    session = _active_session
    if not session:
        raise HTTPException(400, "No active session — reload the UI.")
    if session.status == "busy":
        raise HTTPException(409, "Claude is busy — wait for the current command to finish.")
    msg_id = f"MSG-{uuid4().hex[:8].upper()}"
    msg = {"id": msg_id, "type": body.type, "text": body.text,
           "sent_at": datetime.now().isoformat()}
    session.status = "busy"
    await session.inbox.put(msg)
    # Write trigger file so file watcher can signal Claude Code
    (_qdir() / f"inbox-{session.session_id}.json").write_text(
        json.dumps(msg, indent=2), encoding="utf-8"
    )
    return {"id": msg_id}


@app.get("/api/chat/inbox")
async def chat_inbox(session_id: str, timeout: float = 30.0):
    """Long-poll for MCP agent — blocks until a message arrives or timeout."""
    session = _sessions.get(session_id)
    if not session:
        return {"message": None}
    try:
        msg = await asyncio.wait_for(session.inbox.get(), timeout=min(timeout, 60.0))
        session.status = "busy"
        return {"message": msg}
    except asyncio.TimeoutError:
        return {"message": None}


class ChatPush(BaseModel):
    session_id: str
    type: str
    text: str


@app.post("/api/chat/push")
async def chat_push(body: ChatPush):
    """MCP agent pushes a message to the browser via the SSE stream."""
    from uuid import uuid4
    session = _sessions.get(body.session_id)
    if not session:
        raise HTTPException(404, "Session not found.")
    msg = {
        "id": f"OUT-{uuid4().hex[:8].upper()}",
        "type": body.type,
        "text": body.text,
        "ts": datetime.now().isoformat(),
    }
    session.push(msg)
    if body.type == "done":
        session.status = "idle"
    elif body.type == "question":
        session.status = "waiting"
    else:
        session.status = "busy"
    return {"ok": True}


@app.post("/api/chat/reset")
async def chat_reset():
    """Reset session status to idle and drain stuck inbox messages."""
    if _active_session:
        while not _active_session.inbox.empty():
            try:
                _active_session.inbox.get_nowait()
            except Exception:
                break
        _active_session.status = "idle"
    return {"ok": True}


@app.delete("/api/chat/messages")
async def clear_chat():
    if _active_session:
        _active_session.outbox.clear()
        _active_session.push({"type": "clear", "ts": datetime.now().isoformat()})
    return {"cleared": True}
