import json
import re
import yaml
from pathlib import Path
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from .config import JHConfig
from .core import JHCore

mcp = FastMCP("JobHunt")


def _boot(path: str = ".") -> JHCore:
    resolved = Path(path).resolve()
    try:
        config_path = JHConfig.find_config(resolved)
    except FileNotFoundError:
        config_path = JHConfig.find_config(Path.cwd())
    return JHCore.from_config_file(config_path)


def _qdir(core: JHCore) -> Path:
    q = core.config.config_dir / ".jh" / "queue"
    q.mkdir(parents=True, exist_ok=True)
    return q


def _active_session_id(core: JHCore) -> str | None:
    f = _qdir(core) / "active-session.json"
    if not f.exists():
        return None
    try:
        return json.loads(f.read_text(encoding="utf-8")).get("session_id")
    except Exception:
        return None


_CHAT_SERVER = "http://localhost:8001"


def _chat_post(session_id: str, msg_type: str, text: str) -> None:
    """Push a message to the browser via FastAPI SSE. Best-effort — never raises."""
    import urllib.request as _req
    payload = json.dumps({"session_id": session_id, "type": msg_type, "text": text}).encode()
    req = _req.Request(
        f"{_CHAT_SERVER}/api/chat/push",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with _req.urlopen(req, timeout=10):
            pass
    except Exception:
        pass


def _chat_listen(session_id: str, timeout: float = 30.0) -> dict | None:
    """Long-poll the server inbox. Blocks up to timeout seconds. Returns None on timeout."""
    import urllib.request as _req
    url = f"{_CHAT_SERVER}/api/chat/inbox?session_id={session_id}&timeout={timeout}"
    try:
        with _req.urlopen(url, timeout=timeout + 5) as r:
            return json.loads(r.read()).get("message")
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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


_SKILL_STOP_WORDS = {"and", "the", "for", "with", "from", "into", "via", "using",
                     "that", "are", "not", "can", "its", "our", "ability", "experience",
                     "knowledge", "skills", "strong", "proven", "deep", "good"}

def _skill_tokens(phrase: str) -> list[str]:
    """Normalise a skill phrase into matchable tokens.
    Replaces hyphens and slashes with spaces before stripping punctuation,
    so 'full-stack' → ['full', 'stack'] and 'AI/LLM' → ['ai', 'llm'].
    """
    clean = re.sub(r'[^a-z0-9 ]', '', re.sub(r'[-/]', ' ', phrase.lower()))
    return [w for w in clean.split() if len(w) > 2 and w not in _SKILL_STOP_WORDS]

def _skill_matches(phrase: str, truth_lower: str, threshold: float = 0.6) -> bool:
    """Return True if >= threshold fraction of key tokens appear in truth."""
    tokens = _skill_tokens(phrase)
    if not tokens:
        return True
    hits = sum(1 for t in tokens if t in truth_lower)
    return (hits / len(tokens)) >= threshold

def _score_skills(required: list, nice_to_have: list, truth_text: str) -> tuple[float, str]:
    if not required:
        return 75.0, "No required skills listed"
    truth_lower = truth_text.lower()
    matched, missing = [], []
    for skill in required:
        (matched if _skill_matches(skill, truth_lower) else missing).append(skill)
    score = (len(matched) / len(required)) * 100
    nth_matched = [s for s in (nice_to_have or []) if _skill_matches(s, truth_lower)]
    if nice_to_have:
        score = min(100, score + (len(nth_matched) / len(nice_to_have)) * 10)
    note = f"{len(matched)}/{len(required)} required matched"
    if missing:
        note += f". Missing: {', '.join(missing[:3])}"
    if nth_matched:
        note += f". Nice-to-have: {len(nth_matched)}/{len(nice_to_have)}"
    return round(score, 1), note


def _score_rate(rate_str: str, rules: dict, contract_type: str = "") -> tuple[float, str]:
    r_min = rules.get("rate", {}).get("min_hourly", 85)
    r_pref = rules.get("rate", {}).get("preferred_hourly", 120)
    base_rate = _parse_rate(rate_str)
    if base_rate is None:
        default = rules.get("missing_data_defaults", {}).get("rate_unknown", 65)
        return float(default), "Rate not stated — cannot score"

    is_ft = (contract_type or "").lower() == "full-time"
    if is_ft:
        rate = round(base_rate * _FT_BENEFITS_PREMIUM, 2)
        prefix = f"${base_rate}/hr base + 30% benefits = ${rate}/hr total comp equivalent"
    else:
        rate = base_rate
        prefix = f"${rate}/hr"

    if rate >= r_pref:
        return 100.0, f"{prefix} — at or above preferred ${r_pref}/hr"
    if rate >= r_min:
        score = 60 + ((rate - r_min) / (r_pref - r_min)) * 40
        return round(score, 1), f"{prefix} — above minimum (${r_min}) but below preferred (${r_pref})"
    score = max(0, (rate / r_min) * 40)
    return round(score, 1), f"{prefix} — below minimum ${r_min}/hr"


def _score_location(remote_policy: str, location: str, rules: dict) -> tuple[float, str]:
    loc_rules = rules.get("location", {})
    remote_first = loc_rules.get("remote_first", True)
    special_cities = loc_rules.get("special_cities") or {}
    local_cities = loc_rules.get("local_cities") or {}
    onsite_prob = loc_rules.get("onsite_negotiable_probability", 0.0)

    rp = (remote_policy or "").lower()
    loc = (location or "").lower()

    special = next(((c, cfg) for c, cfg in special_cities.items() if c.lower() in loc), None)
    local = next(((c, cfg) for c, cfg in local_cities.items() if c.lower() in loc), None)

    base_loc = rules.get("identity", {}).get("base_location", "")
    home_state = base_loc.split(",")[-1].strip().lower() if "," in base_loc else ""
    is_home_state = bool(home_state and home_state in loc)

    if rp == "remote":
        return 100.0, "Fully remote — perfect match"

    if rp == "hybrid":
        if special:
            return 85.0, f"Hybrid in {special[0].title()} — allowed (special city)"
        if local:
            city, cfg = local
            mins = (cfg or {}).get("commute_minutes", "?")
            return 85.0, f"Hybrid in {city.title()} (~{mins}min) — within commute range"
        if is_home_state:
            return 75.0, "Hybrid in home state — likely commutable"
        return (55.0, "Hybrid in non-preferred location") if remote_first else (75.0, "Hybrid acceptable")

    if rp == "onsite":
        if special:
            cfg = special[1] or {}
            if cfg.get("monthly_visit_ok"):
                return 60.0, f"Onsite in {special[0].title()} — monthly visits OK"
            if cfg.get("hybrid_ok"):
                return 50.0, f"Onsite in {special[0].title()} — hybrid possible"
            return 40.0, f"Onsite in {special[0].title()} — allowed but not ideal"
        if local:
            city, cfg = local
            mins = (cfg or {}).get("commute_minutes", "?")
            if onsite_prob > 0:
                blended = round(onsite_prob * 85.0 + (1 - onsite_prob) * 65.0, 1)
                return blended, (f"Onsite in {city.title()} (~{mins}min) — "
                                 f"{int(onsite_prob * 100)}% likely negotiable to hybrid given local presence")
            return 65.0, f"Onsite in {city.title()} (~{mins}min) — within commute range"
        if is_home_state:
            if onsite_prob > 0:
                blended = round(onsite_prob * 75.0 + (1 - onsite_prob) * 40.0, 1)
                return blended, (f"Onsite in home state ({location}) — "
                                 f"{int(onsite_prob * 100)}% likely negotiable; distance may vary")
            return 50.0, f"Onsite in home state ({location}) — distance unclear"
        return 0.0, f"Onsite-only in non-allowed location ({location})"

    default = rules.get("missing_data_defaults", {}).get("location_unknown", 65)
    return float(default), f"Location policy unclear ({remote_policy})"


def _score_contract_length(duration_months, contract_type: str, rules: dict) -> tuple[float, str]:
    prefs = rules.get("contract_preferences", {})
    type_mults = prefs.get("type_multipliers") or {"contract": 1.0, "fractional": 1.0, "part-time": 0.8, "full-time": 0.8}
    sched_mults = prefs.get("schedule_multipliers") or {3: 1.0, 4: 0.9, 5: 0.8}
    implied_days = prefs.get("implied_schedule_days") or {"full-time": 5, "part-time": 3, "fractional": 3, "contract": 5}
    preferred = prefs.get("preferred_duration_months") or [3, 4, 5, 6]
    min_dur = prefs.get("min_duration_months", 2)
    max_dur = prefs.get("max_duration_months", 12)

    ct = (contract_type or "").lower().strip()
    if ct in ("full_time", "permanent", "salaried", "employed"):
        ct = "full-time"

    type_mult = type_mults.get(ct, 0.8)
    days = implied_days.get(ct, 5)
    sched_mult = sched_mults.get(days, 0.8)
    base = round(type_mult * sched_mult * 100, 1)

    labels = {"contract": "Contract", "fractional": "Fractional", "part-time": "Part-time employed", "full-time": "Full-time employed"}
    label = labels.get(ct, ct.title())
    note = f"{label}, {days}d/wk — {int(type_mult*100)}% × {int(sched_mult*100)}% = {base}/100"

    # For contract/fractional roles also factor in duration fit
    if ct in ("contract", "fractional") and duration_months is not None:
        try:
            dur = int(duration_months)
            if dur in preferred:
                dur_factor, dur_note = 1.0, f"{dur}mo preferred"
            elif min_dur <= dur <= max_dur:
                dur_factor, dur_note = 0.9, f"{dur}mo acceptable"
            elif dur < min_dur:
                dur_factor, dur_note = 0.7, f"{dur}mo short"
            else:
                dur_factor, dur_note = 0.8, f"{dur}mo long"
            base = round(base * dur_factor, 1)
            note = f"{label}, {days}d/wk, {dur_note} = {base}/100"
        except (TypeError, ValueError):
            pass

    return base, note


def _score_timing(rules: dict) -> tuple[float, str]:
    avail = rules.get("availability", {})
    contract_end = avail.get("current_contract_end")
    urgency = avail.get("urgency_window_days", 60)
    if contract_end:
        from datetime import date
        try:
            end = contract_end if isinstance(contract_end, date) else date.fromisoformat(str(contract_end))
            days = (end - date.today()).days
            if days <= 0:
                return 100.0, "Currently available"
            if days <= urgency:
                return 100.0, f"Contract ends in {days} days — actively seeking"
            return 75.0, f"Contract ends in {days} days — planning ahead"
        except Exception:
            pass
    default = rules.get("missing_data_defaults", {}).get("timing_unknown", 75)
    return float(default), "Timing not assessed"


def _score_freshness(posted_date_str: str, rules: dict) -> tuple[float, str]:
    fr = rules.get("freshness") or {}
    if not fr.get("enabled", True):
        return 100.0, "Freshness scoring disabled"
    penalty   = fr.get("penalty_per_week", 5)
    max_weeks = fr.get("max_age_weeks", 12)
    grace     = fr.get("grace_period_days", 3)
    if not posted_date_str:
        default = rules.get("missing_data_defaults", {}).get("freshness_unknown", 70)
        return float(default), "Posted date unknown"
    try:
        from datetime import date as _d
        posted    = _d.fromisoformat(str(posted_date_str))
        days_old  = max(0, (_d.today() - posted).days)
        weeks_old = days_old / 7
        if days_old <= grace:
            return 100.0, f"Posted {days_old}d ago — fresh"
        if weeks_old >= max_weeks:
            return 0.0, f"Posted {days_old}d ago — stale (>{max_weeks} weeks)"
        score = round(max(0.0, 100.0 - weeks_old * penalty), 1)
        return score, f"Posted {days_old}d ago ({weeks_old:.1f}w) — -{penalty}/week"
    except Exception:
        default = rules.get("missing_data_defaults", {}).get("freshness_unknown", 70)
        return float(default), f"Posted date unparseable: {posted_date_str}"


_ANNUAL_HOURS = 2000  # 50 working weeks (52 - 2 vacation)
_FT_BENEFITS_PREMIUM = 1.30  # 401k + health + benefits ≈ 30% on top of salary


def _score_pursuit(meta: dict, rules: dict) -> tuple[float, str]:
    """Benefit-of-doubt pursuit score for partial-info list jobs. Returns (score, bucket)."""
    score = 70.0
    signals = meta.get("signals") or {}

    # Rate
    rate_str = meta.get("salary_stated") or meta.get("rate_stated")
    if rate_str:
        s, _ = _score_rate(str(rate_str), rules, meta.get("contract_type", ""))
        score += (s - 70) * 0.25
    else:
        score += 5

    # Location
    rp = meta.get("remote_policy", "")
    if rp:
        s, _ = _score_location(rp, meta.get("location", ""), rules)
        score += (s - 70) * 0.20
    else:
        score += 3

    # Contract type
    ct = (meta.get("contract_type") or "").lower()
    if ct in ("contract", "fractional"):  score += 5
    elif ct == "full-time":               score -= 5

    # Applicant competition
    n = signals.get("applicant_count")
    if n is not None:
        n = int(n)
        if n > 300:   score -= 20
        elif n > 100: score -= 10
        elif n > 50:  score -=  3
        else:         score +=  8

    # Easy apply (net positive with the app — real role, smaller pool for hard apply)
    ea = signals.get("easy_apply")
    if ea is True:    score +=  3
    elif ea is False: score += 10

    # Post freshness
    d = signals.get("days_since_posted")
    if d is not None:
        d = int(d)
        if d <= 2:    score += 15
        elif d <= 7:  score +=  8
        elif d <= 30: score -=  8
        else:         score -= 15

    if (meta.get("source") or "").lower() == "recruiter":
        score += 15

    score = max(0.0, min(100.0, round(score, 1)))
    bucket = ("pursue" if score >= 78 else "research" if score >= 60
              else "watch" if score >= 42 else "pass")
    return score, bucket


def _parse_rate(rate_str: str) -> float | None:
    """Extract base hourly rate from a string. Returns None if unparseable.
    Handles hourly ($120/hr), annual (/yr, /year), k-shorthand (120k),
    and bare annual salary ranges (175000-225000 — averages the range).
    Uses 2000 hrs/year (50 weeks). Does NOT apply benefits premium here —
    call _apply_ft_premium() separately for full-time roles.
    """
    if not rate_str:
        return None
    s = str(rate_str).lower().strip()
    # Yearly explicit: "$120,000/yr", "150k/year", "per year"
    if any(t in s for t in ("/yr", "/year", "per year")):
        m = re.search(r"(\d[\d,]*)", s)
        if m:
            val = float(m.group(1).replace(",", ""))
            if val < 1000:
                val *= 1000
            return round(val / _ANNUAL_HOURS, 2)
    # k-shorthand: "120k"
    if s.endswith("k") and re.match(r"^\$?\d+k$", s):
        val = float(re.search(r"\d+", s).group()) * 1000
        return round(val / _ANNUAL_HOURS, 2)
    # Hourly: "$120/hr", "100-120/hr"
    if any(t in s for t in ("/hr", "/hour", "per hour")):
        m = re.search(r"\$?(\d+(?:\.\d+)?)", s)
        if m:
            val = float(m.group(1))
            if 15 <= val <= 600:
                return val
    # Bare annual salary range: "175000-225000", "$175,000-$225,000 USD"
    # Detect by extracting all numbers >= 10000 (hourly rates are never this high)
    nums = [float(n.replace(",", "")) for n in re.findall(r"\d[\d,]*", s)
            if float(n.replace(",", "")) >= 10000]
    if nums:
        avg_annual = sum(nums) / len(nums)
        return round(avg_annual / _ANNUAL_HOURS, 2)
    # Bare hourly number
    m = re.search(r"\$?(\d+(?:\.\d+)?)", s)
    if m:
        val = float(m.group(1))
        if 15 <= val <= 600:
            return val
    return None


# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

@mcp.tool()
def jh_get_opener(project_path: str = ".") -> str:
    """
    Return the Job Hunt opener instructions (OPENER.md).

    Call this tool once at the start of a session to load agent instructions.
    After reading the result, follow the instructions it contains.

    ALWAYS call this when starting a new Job Hunt session.
    """
    opener_path = Path(__file__).parent.parent.parent / "OPENER.md"
    if not opener_path.exists():
        return f"ERROR: OPENER.md not found at {opener_path}"
    return opener_path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Truth Intake & Atom Pipeline
# ---------------------------------------------------------------------------

_ATOM_DOMAINS = (
    "identity", "availability", "location", "contracts", "rate",
    "scoring", "company_filters", "skills", "experience", "projects",
)
_SOURCE_TYPES = ("directChat", "email", "resume", "webClip", "file", "recruiter")
_RULES_DOMAINS  = frozenset({"identity", "availability", "location", "contracts", "rate", "scoring", "company_filters"})
_PERSONAL_DOMAINS = frozenset({"identity", "availability", "skills", "experience", "projects"})


@mcp.tool()
def jh_ingest_truth(source: str, text: str, project_path: str = ".") -> str:
    """
    Store a raw truth chunk by source. No domain classification at this stage.

    Use for ANY incoming truth — chat, email, resume, web clip, file drop, recruiter message.
    Text can be messy, mixed, noisy — that is expected and fine. Preserve all meaning.
    Domain classification happens later during atomization.

    ALWAYS call this when:
    - User says anything that could affect rules or personal truth
    - A document is dropped or pasted
    - An email or recruiter message arrives

    source: directChat | email | resume | webClip | file | recruiter
    text:   raw content, verbatim or lightly paraphrased — never summarize away detail.

    After ingesting, call jh_atomize_truth(chunk_id).
    """
    from uuid import uuid4
    if source not in _SOURCE_TYPES:
        return f"ERROR: Unknown source '{source}'. Must be one of: {', '.join(_SOURCE_TYPES)}"

    core = _boot(project_path)
    chunk_dir = core.config.data_path / "truth" / "raw" / source
    chunk_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.now().strftime("%Y%m%d")
    chunk_id = f"chunk_{today}_{uuid4().hex[:6]}"
    chunk_file = chunk_dir / f"{chunk_id}.md"

    chunk_file.write_text(
        f"---\nchunk_id: {chunk_id}\nsource: {source}\n"
        f"date: {datetime.now().strftime('%Y-%m-%d')}\nstatus: raw\n---\n\n{text.strip()}\n",
        encoding="utf-8",
    )

    return json.dumps({
        "chunk_id": chunk_id,
        "source": source,
        "path": str(chunk_file),
        "next": f"Call jh_atomize_truth(chunk_id='{chunk_id}') to extract and classify atoms.",
    }, indent=2)


@mcp.tool()
def jh_atomize_truth(chunk_id: str, project_path: str = ".") -> str:
    """
    Stage a raw truth chunk for LLM atomization and deduplication.

    Finds the chunk, loads existing atoms for dedup context, returns staging JSON.

    After receiving this result:
    1. Read chunk_text carefully — extract every distinct atomic fact
    2. For each atom: assign domain + group from the taxonomy below
    3. Write each atom as one clear sentence or short paragraph
    4. Check existing_atoms[domain] for near-duplicates:
       - Same fact from another source → set deduplicate_of to existing atom_id
       - Adds nuance or updates → new atom, no deduplicate_of
    5. Call jh_save_atoms(atoms_json) to persist

    Atom domain taxonomy:
      identity:         personal_info | contact_info
      availability:     current_engagement | target
      location:         local_cities | commute_tolerance | remote_policy | onsite_negotiability | special_cities | blacklist
      contracts:        type_preference | schedule_preference | scoring_model | duration_preference
      rate:             annual_hours | benefits_premium | floors_and_targets | group_overrides
      scoring:          weights | thresholds | recommendation_bands
      company_filters:  preferred_industries | blacklist | size_preference
      skills:           frontend | backend | ai_llm | devops | database | testing | languages
      experience:       (one atom per employer/engagement)
      projects:         (one atom per project)
    """
    core = _boot(project_path)
    root = core.config.data_path

    chunk_file = None
    chunk_content = ""
    for src in _SOURCE_TYPES:
        f = root / "truth" / "raw" / src / f"{chunk_id}.md"
        if f.exists():
            chunk_file = f
            chunk_content = f.read_text(encoding="utf-8")
            break
    if not chunk_file:
        return f"ERROR: Chunk '{chunk_id}' not found in any truth/raw/ subfolder."

    existing_atoms: dict[str, list] = {}
    atoms_root = root / "truth" / "atoms"
    for domain in _ATOM_DOMAINS:
        domain_dir = atoms_root / domain
        atoms = []
        if domain_dir.exists():
            for af in sorted(domain_dir.glob("*.md")):
                try:
                    ac = af.read_text(encoding="utf-8")
                    am = _parse_frontmatter(ac)
                    body = ac[ac.find("\n---", 3) + 4:].strip() if "\n---" in ac[3:] else ac.strip()
                    atoms.append({"atom_id": am.get("atom_id", af.stem), "group": am.get("group"), "text": body})
                except Exception:
                    pass
        if atoms:
            existing_atoms[domain] = atoms

    meta = _parse_frontmatter(chunk_content)
    body = chunk_content[chunk_content.find("\n---", 3) + 4:].strip() if "\n---" in chunk_content[3:] else chunk_content.strip()

    import datetime as _dt
    def _serial(o):
        if isinstance(o, (_dt.date, _dt.datetime)):
            return o.isoformat()
        raise TypeError(f"Not serializable: {type(o)}")

    return json.dumps({
        "action": "atomize_truth",
        "chunk_id": chunk_id,
        "source": meta.get("source"),
        "date": str(meta.get("date") or ""),
        "chunk_text": body,
        "existing_atoms": existing_atoms,
        "instructions": (
            "Extract every distinct atomic fact from chunk_text. For each atom produce a JSON object with: "
            "domain, group, text (one clear sentence/paragraph), confidence (high/medium/low), "
            "source_chunk_id (this chunk_id), deduplicate_of (null or existing atom_id). "
            "Then call jh_save_atoms(atoms_json) with the full array."
        ),
    }, indent=2)


@mcp.tool()
def jh_save_atoms(atoms_json: str, project_path: str = ".") -> str:
    """
    Persist atoms produced by LLM atomization of a truth chunk.

    atoms_json: JSON array —
    [{"domain":"location","group":"local_cities","text":"...","confidence":"high",
      "source_chunk_id":"chunk_...","deduplicate_of":null}, ...]

    Deduplication: if deduplicate_of is set to an existing atom_id, that atom's
    provenance is updated instead of creating a new file.

    After saving, re-synthesize affected documents:
    - Rules domains touched → jh_synthesize_rules()
    - Personal domains touched → jh_synthesize_master_truth()
    """
    from uuid import uuid4
    core = _boot(project_path)
    atoms_root = core.config.data_path / "truth" / "atoms"

    try:
        atoms = json.loads(atoms_json) if isinstance(atoms_json, str) else atoms_json
    except Exception as e:
        return f"ERROR: atoms_json is not valid JSON: {e}"
    if not isinstance(atoms, list):
        return "ERROR: atoms_json must be a JSON array."

    today = datetime.now().strftime("%Y%m%d")
    today_iso = datetime.now().strftime("%Y-%m-%d")
    saved, skipped, errors = [], [], []
    rules_touched, personal_touched = set(), set()

    for atom in atoms:
        domain = (atom.get("domain") or "").lower()
        if domain not in _ATOM_DOMAINS:
            errors.append(f"Unknown domain '{domain}'")
            continue
        text = (atom.get("text") or "").strip()
        if not text:
            errors.append(f"Empty atom text in domain '{domain}'")
            continue

        atom_dir = atoms_root / domain
        atom_dir.mkdir(parents=True, exist_ok=True)

        dedup_of = atom.get("deduplicate_of")
        if dedup_of:
            existing = atom_dir / f"{dedup_of}.md"
            if existing.exists():
                ec = existing.read_text(encoding="utf-8")
                em = _parse_frontmatter(ec)
                ebody = ec[ec.find("\n---", 3) + 4:] if "\n---" in ec[3:] else ec
                sources = em.get("sources") or []
                new_src = {"chunk_id": atom.get("source_chunk_id"), "date": today_iso}
                if new_src not in sources:
                    sources.append(new_src)
                em["sources"] = sources
                em["last_updated"] = today_iso
                existing.write_text(
                    "---\n" + yaml.dump(em, default_flow_style=False, allow_unicode=True) + "---\n" + ebody,
                    encoding="utf-8",
                )
                skipped.append({"atom_id": dedup_of, "reason": "deduplicated — provenance updated"})
                continue

        atom_id = f"atom_{today}_{uuid4().hex[:6]}"
        atom_meta = {
            "atom_id": atom_id,
            "domain": domain,
            "group": atom.get("group", "general"),
            "confidence": atom.get("confidence", "high"),
            "sources": [{"chunk_id": atom.get("source_chunk_id"), "date": today_iso}],
            "created": today_iso,
            "last_updated": today_iso,
        }
        (atom_dir / f"{atom_id}.md").write_text(
            "---\n" + yaml.dump(atom_meta, default_flow_style=False, allow_unicode=True) + "---\n\n" + text + "\n",
            encoding="utf-8",
        )
        saved.append({"atom_id": atom_id, "domain": domain, "group": atom.get("group")})

        if domain in _RULES_DOMAINS:
            rules_touched.add(domain)
        if domain in _PERSONAL_DOMAINS:
            personal_touched.add(domain)

    next_steps = []
    if rules_touched:
        next_steps.append(f"Call jh_synthesize_rules(domain='all') — rules atoms changed: {sorted(rules_touched)}")
    if personal_touched:
        next_steps.append("Call jh_synthesize_master_truth() — personal atoms changed")

    return json.dumps({"saved": saved, "skipped": skipped, "errors": errors, "next_steps": next_steps}, indent=2)


@mcp.tool()
def jh_synthesize_master_truth(project_path: str = ".") -> str:
    """
    Re-derive truth/master/truth.md from all personal-domain atoms.

    Reads atoms from: identity, availability, skills, experience, projects.
    Returns staging JSON — LLM reads atoms and rewrites master truth.

    ALWAYS call this after jh_save_atoms when personal-domain atoms changed.
    NEVER write to truth/master/truth.md directly — always use this tool.
    """
    core = _boot(project_path)
    root = core.config.data_path
    truth_file = core.truth_path / "master" / "truth.md"

    atoms_by_domain: dict[str, list] = {}
    for d in sorted(_PERSONAL_DOMAINS):
        domain_dir = root / "truth" / "atoms" / d
        atoms = []
        if domain_dir.exists():
            for f in sorted(domain_dir.glob("*.md")):
                try:
                    content = f.read_text(encoding="utf-8")
                    meta = _parse_frontmatter(content)
                    body = content[content.find("\n---", 3) + 4:].strip() if "\n---" in content[3:] else content.strip()
                    atoms.append({"atom_id": meta.get("atom_id", f.stem), "group": meta.get("group"), "text": body})
                except Exception:
                    pass
        atoms_by_domain[d] = atoms

    current_truth = truth_file.read_text(encoding="utf-8") if truth_file.exists() else ""
    total = sum(len(v) for v in atoms_by_domain.values())

    import datetime as _dt
    def _serial(o):
        if isinstance(o, (_dt.date, _dt.datetime)):
            return o.isoformat()
        raise TypeError(f"Not serializable: {type(o)}")

    return json.dumps({
        "action": "synthesize_master_truth",
        "atom_count": total,
        "atoms_by_domain": atoms_by_domain,
        "current_truth": current_truth,
        "output_path": str(truth_file),
        "instructions": (
            "Re-synthesize truth/master/truth.md from all atoms. "
            "Structure: Identity → Core Narrative → Experience → Projects → Skills → "
            "Education → Languages → Resume Groups → Gaps. "
            "Atoms are the only source of truth. For any domain with no atoms, "
            "keep that section from current_truth unchanged. "
            "Do not invent facts. Write the complete document to output_path."
        ),
    }, indent=2, default=_serial)


@mcp.tool()
def jh_flag_anomalies(project_path: str = ".") -> str:
    """
    Surface contradictions in master truth. Writes to truth/master/anomalies.md.

    ALWAYS call this after jh_synthesize_master_truth to catch conflicts.
    Examples of anomalies: date conflicts, skill contradictions, role description mismatches.
    """
    return "STUB: jh_flag_anomalies not yet implemented. Phase 1."


@mcp.tool()
def jh_get_master_truth(project_path: str = ".") -> str:
    """
    Return current master truth content from truth/master/truth.md.

    ALWAYS call this before:
    - Scoring any job
    - Generating any resume or cover letter
    - Running gap analysis
    NEVER use cached truth — always read fresh from this tool.
    """
    core = _boot(project_path)
    truth_file = core.truth_path / "master" / "truth.md"
    if not truth_file.exists():
        return "ERROR: No master truth found. Drop a chip in truth/chips/ and call jh_synthesize_master_truth."
    return truth_file.read_text(encoding="utf-8")


@mcp.tool()
def jh_snapshot_truth(project_path: str = ".") -> str:
    """
    Version the current master truth before any major update.

    ALWAYS call this before jh_synthesize_master_truth to preserve history.
    Creates truth/master/truth.v{n}.md with current content.
    """
    return "STUB: jh_snapshot_truth not yet implemented. Phase 1."


@mcp.tool()
def jh_synthesize_rules(domain: str = "all", project_path: str = ".") -> str:
    """
    Re-derive rules/config.yaml from truth atoms.

    Reads all atoms for the given domain(s) from truth/atoms/ and returns
    staging JSON for LLM to re-evaluate and rewrite rules/config.yaml.

    ALWAYS call this after jh_save_atoms when rules-domain atoms changed.
    One new atom may cascade to change many rules — all are re-evaluated together.

    domain: location | contracts | rate | identity | availability | scoring | company_filters | all
    """
    core = _boot(project_path)
    root = core.config.data_path
    rules_file = root / "rules" / "config.yaml"

    if domain == "all":
        domains = sorted(_RULES_DOMAINS)
    else:
        if domain not in _RULES_DOMAINS:
            return f"ERROR: Unknown rules domain '{domain}'. Valid: {', '.join(sorted(_RULES_DOMAINS))}"
        domains = [domain]

    atoms_by_domain: dict[str, list] = {}
    for d in domains:
        domain_dir = root / "truth" / "atoms" / d
        atoms = []
        if domain_dir.exists():
            for f in sorted(domain_dir.glob("*.md")):
                try:
                    content = f.read_text(encoding="utf-8")
                    meta = _parse_frontmatter(content)
                    body = content[content.find("\n---", 3) + 4:].strip() if "\n---" in content[3:] else content.strip()
                    atoms.append({"atom_id": meta.get("atom_id", f.stem), "group": meta.get("group"), "text": body})
                except Exception:
                    pass
        atoms_by_domain[d] = atoms

    current_rules = rules_file.read_text(encoding="utf-8") if rules_file.exists() else ""
    total = sum(len(v) for v in atoms_by_domain.values())

    import datetime as _dt
    def _serial(o):
        if isinstance(o, (_dt.date, _dt.datetime)):
            return o.isoformat()
        raise TypeError(f"Not serializable: {type(o)}")

    return json.dumps({
        "action": "synthesize_rules",
        "domains": domains,
        "atom_count": total,
        "atoms_by_domain": atoms_by_domain,
        "current_rules_yaml": current_rules,
        "rules_output_path": str(rules_file),
        "instructions": (
            f"Re-synthesize rules/config.yaml from all atoms. "
            f"Atoms in atoms_by_domain are the ONLY source of truth — do not carry over old values blindly. "
            f"One new atom may change many values — re-evaluate ALL rules holistically. "
            f"For domains NOT in {domains}, copy their section from current_rules_yaml unchanged. "
            f"Write complete YAML to rules_output_path. "
            f"File must start with:\n"
            f"# GENERATED — do not edit directly.\n"
            f"# Source: data-storage/truth/atoms/ + data-storage/truth/raw/\n"
            f"# To add truth: jh_ingest_truth(source, text) → jh_atomize_truth() → jh_save_atoms()\n"
            f"# To regenerate: jh_synthesize_rules()"
        ),
    }, indent=2, default=_serial)


# ---------------------------------------------------------------------------
# Rules Module
# ---------------------------------------------------------------------------

@mcp.tool()
def jh_get_rules(project_path: str = ".") -> str:
    """
    Return parsed personal rules config from rules/config.yaml.

    ALWAYS call this before scoring any job.
    Rules include: rate floors, location constraints, contract type preferences,
    company filters, scoring weights.
    NEVER bypass or assume rules — always read fresh from this tool.
    """
    core = _boot(project_path)
    rules = core.load_rules()
    if not rules:
        return "ERROR: No rules config found. Check rules/config.yaml."
    import datetime
    def _default(obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        raise TypeError(f"Not serializable: {type(obj)}")
    return json.dumps(rules, indent=2, default=_default)


@mcp.tool()
def jh_validate_rules(project_path: str = ".") -> str:
    """
    Check rules/config.yaml for missing required fields and logical conflicts.

    ALWAYS call this when:
    - User updates rules/config.yaml
    - A job scores unexpectedly (rules might be misconfigured)
    - Starting a new session for the first time
    """
    return "STUB: jh_validate_rules not yet implemented. Phase 2."


@mcp.tool()
def jh_update_rule(field_path: str, value: str, project_path: str = ".") -> str:
    """
    Update a specific rule field in rules/config.yaml.

    field_path: dot-notation path (e.g. "rate.min_hourly", "availability.target_start")
    value: new value as a string (will be parsed to correct type)

    NEVER edit rules/config.yaml directly — always use this tool so validation runs.
    """
    return "STUB: jh_update_rule not yet implemented. Phase 2."


# ---------------------------------------------------------------------------
# Resume Module
# ---------------------------------------------------------------------------

@mcp.tool()
def jh_get_categorical_template(group: str, project_path: str = ".") -> str:
    """
    Return the resume template for a group (A, B, C, D, or E).

    Lookup order: blueprints/resumes/templates/group_{x}.md → default.md
    group: A=Full-Stack, B=Frontend, C=AI/ML, D=Leadership, E=Product/UX

    ALWAYS call this before jh_generate_categorical_resume to inspect or edit the template.
    """
    core = _boot(project_path)
    templates_dir = core.blueprints_path / "resumes" / "templates"
    group_file = templates_dir / f"group_{group.lower()}.md"
    default_file = templates_dir / "default.md"

    if group_file.exists():
        return group_file.read_text(encoding="utf-8")
    if default_file.exists():
        return f"# Using default template (no group_{group.lower()}.md found)\n\n" + default_file.read_text(encoding="utf-8")
    return f"ERROR: No template found at {group_file} or {default_file}. Create blueprints/resumes/templates/default.md first."


@mcp.tool()
def jh_generate_categorical_resume(group: str, project_path: str = ".") -> str:
    """
    Return everything needed to generate a Group resume from master truth.

    Returns a JSON payload containing: the template, master truth, group strategy,
    output path, and generation instructions. After receiving this:
    1. Fill every {{PLACEHOLDER}} in template using ONLY facts from master_truth
    2. Apply the group strategy (lead with the right projects/experience)
    3. Write the completed resume to output_path
    4. NEVER add skills or experience not present in master_truth

    group: A=Full-Stack, B=Frontend, C=AI/ML, D=Leadership, E=Product/UX
    """
    core = _boot(project_path)
    group_upper = group.upper()

    # Template: group-specific or default fallback
    templates_dir = core.blueprints_path / "resumes" / "templates"
    group_file = templates_dir / f"group_{group.lower()}.md"
    default_file = templates_dir / "default.md"

    if group_file.exists():
        template = group_file.read_text(encoding="utf-8")
        template_source = f"group_{group.lower()}.md"
    elif default_file.exists():
        template = default_file.read_text(encoding="utf-8")
        template_source = "default.md (no group-specific template found)"
    else:
        return f"ERROR: No template found. Create blueprints/resumes/templates/default.md first."

    # Master truth
    truth_file = core.truth_path / "master" / "truth.md"
    if not truth_file.exists():
        return "ERROR: No master truth found. Call jh_synthesize_master_truth first."
    master_truth = truth_file.read_text(encoding="utf-8")

    # Output path
    output_path = core.blueprints_path / "resumes" / "generated" / f"group_{group.lower()}" / "resume.md"

    return json.dumps({
        "action": "generate_resume",
        "group": group_upper,
        "template_source": template_source,
        "template": template,
        "master_truth": master_truth,
        "output_path": str(output_path),
        "instructions": (
            f"Generate a Group {group_upper} resume. "
            f"Fill every {{PLACEHOLDER}} in the template using ONLY facts from master_truth. "
            f"The Group {group_upper} strategy is in the 'Resume Groups > Group {group_upper}' section of master_truth — "
            f"lead with the projects and experience it specifies. "
            f"Do not invent or add any skills, experience, or facts not present in master_truth. "
            f"Write the completed resume markdown to output_path. "
            f"Ensure output_path parent directory exists before writing."
        )
    }, indent=2)


@mcp.tool()
def jh_generate_tailored_resume(group: str, job_id: str, project_path: str = ".") -> str:
    """
    Customize a group resume for a specific job ID.

    Reads job record + master truth + rules, then tailors language
    and emphasis to match the JD without adding unverified skills.

    NEVER claim skills not in master truth. Tailor emphasis, not facts.
    """
    core = _boot(project_path)
    root = core.config.data_path
    group_upper = group.upper()

    # Find job record — whitelisted first, then digested
    job_content = None
    for subfolder in ("whitelisted", "digested"):
        jf = root / "jobs" / subfolder / f"{job_id}.md"
        if jf.exists():
            job_content = jf.read_text(encoding="utf-8")
            break
    if job_content is None:
        return f"ERROR: Job {job_id} not found in whitelisted or digested. Run jh_whitelist_job first."

    job_meta = _parse_frontmatter(job_content)

    # Template: group-specific → default
    tpl_dir = root / "blueprints" / "resumes" / "templates"
    group_tpl = tpl_dir / f"group_{group_upper.lower()}.md"
    default_tpl = tpl_dir / "default.md"
    if group_tpl.exists():
        template = group_tpl.read_text(encoding="utf-8")
        template_source = f"group_{group_upper.lower()}.md"
    elif default_tpl.exists():
        template = default_tpl.read_text(encoding="utf-8")
        template_source = "default.md (fallback)"
    else:
        return "ERROR: No resume template found. Create blueprints/resumes/templates/default.md first."

    truth_file = root / "truth" / "master" / "truth.md"
    master_truth = truth_file.read_text(encoding="utf-8") if truth_file.exists() else ""
    if not master_truth:
        return "ERROR: master truth not found at truth/master/truth.md."

    output_path = root / "applications" / job_id / "resume.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    required_skills = job_meta.get("required_skills") or []
    nice_to_have = job_meta.get("nice_to_have_skills") or []
    title = job_meta.get("title", "")
    company = job_meta.get("company", "")

    return json.dumps({
        "action": "generate_tailored_resume",
        "job_id": job_id,
        "group": group_upper,
        "template_source": template_source,
        "template": template,
        "master_truth": master_truth,
        "job_meta": job_meta,
        "output_path": str(output_path),
        "instructions": (
            f"Generate a tailored Group {group_upper} resume for the '{title}' role at '{company}'. "
            f"Fill every {{PLACEHOLDER}} in the template using ONLY facts from master_truth. "
            f"Emphasize skills that match the job requirements — required: {required_skills[:5]}, "
            f"nice-to-have: {nice_to_have[:5]}. "
            f"Reorder bullet points to surface the most relevant experience first. "
            f"Do NOT add any skill, tool, or experience not present in master_truth. "
            f"Tailor phrasing and emphasis; never change facts. "
            f"Write the completed resume markdown to output_path."
        )
    }, indent=2)


@mcp.tool()
def jh_export_resume_pdf(job_id: str, project_path: str = ".") -> str:
    """
    Convert a generated MD resume to PDF.

    Requires the resume to exist in blueprints/resumes/{job_id}/.
    Uses pandoc or weasyprint. Reports path to generated PDF.
    """
    return f"STUB: jh_export_resume_pdf (job={job_id}) not yet implemented. Phase 3."


# ---------------------------------------------------------------------------
# Job Module
# ---------------------------------------------------------------------------

@mcp.tool()
def jh_ingest_job(
    raw_text: str,
    source_url: str = "",
    job_type: str = "single",
    batch_id: str = "",
    project_path: str = "."
) -> str:
    """
    Store a raw job description and assign a job ID.

    ALWAYS call this when:
    - User pastes a job description (job_type='single')
    - Browser extension POSTs a captured JD
    - Processing items from a list batch (job_type='list_item', batch_id=<id>)

    job_type: 'single' (full JD) | 'list_item' (from a list batch)
    batch_id: required when job_type='list_item'

    Returns job_id. Call jh_digest_job next for single jobs.
    For list_item jobs, call jh_triage_job_list after all items are ingested.
    NEVER skip ingestion — raw text must be preserved before any processing.
    """
    from uuid import uuid4
    core = _boot(project_path)
    root = core.config.data_path

    today = datetime.now().strftime("%Y%m%d")
    job_id = f"job_{today}_{uuid4().hex[:8]}"

    # Duplicate check by source_url
    if source_url:
        raw_dir = root / "jobs" / "raw"
        if raw_dir.exists():
            for f in sorted(raw_dir.glob("*.md")):
                try:
                    meta = _parse_frontmatter(f.read_text(encoding="utf-8"))
                    if meta.get("source_url") == source_url:
                        return f"DUPLICATE: source_url already ingested as {f.stem}. Use jh_get_job to review it."
                except Exception:
                    pass

    meta = {
        "id": job_id,
        "type": job_type,
        "intake_date": datetime.now().strftime("%Y-%m-%d"),
        "source_url": source_url,
        "status": "raw",
        "title": None,
        "company": None,
        "company_slug": None,
        "location": None,
        "remote_policy": None,
        "contract_type": None,
        "duration_months": None,
        "rate_stated": None,
        "posted_date": None,
        "score": None,
        "recommendation": None,
        "group_fit": [],
    }
    if job_type == "list_item":
        meta["batch_id"] = batch_id
        meta["triage_result"] = None
        meta["exclude_reason"] = None
        meta["bucket"] = None
        meta["signals"] = {}  # populated by Claude after ingestion: easy_apply, applicant_count, days_since_posted

    raw_dir = root / "jobs" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    content = "---\n" + yaml.dump(meta, default_flow_style=False, allow_unicode=True) + "---\n\n" + raw_text
    (raw_dir / f"{job_id}.md").write_text(content, encoding="utf-8")

    next_step = (
        f"Call jh_triage_job_list(batch_id='{batch_id}') after all list items are ingested."
        if job_type == "list_item"
        else f"Call jh_digest_job(job_id='{job_id}') to extract structured fields."
    )
    return json.dumps({"job_id": job_id, "status": "raw", "type": job_type, "next": next_step})


@mcp.tool()
def jh_ingest_job_list(raw_text: str, source: str = "", project_path: str = ".") -> str:
    """
    Ingest a batch of jobs from a list (LinkedIn search, email digest, etc.).

    Use this when the user pastes multiple job listings at once.
    Each item in the list gets a shallow record; triage filters out bad matches
    automatically before any full digestion happens.

    ALWAYS call this (not jh_ingest_job) when input contains multiple jobs.
    After this, Claude parses the list and calls jh_ingest_job for each item,
    then calls jh_triage_job_list to auto-filter based on rules.

    raw_text: the raw pasted list (LinkedIn results, email, etc.)
    source: where it came from (e.g. 'linkedin', 'email', 'wellfound')
    """
    from uuid import uuid4
    core = _boot(project_path)
    root = core.config.data_path

    today = datetime.now().strftime("%Y%m%d")
    batch_id = f"batch_{today}_{uuid4().hex[:8]}"

    batches_dir = root / "jobs" / "batches"
    batches_dir.mkdir(parents=True, exist_ok=True)

    batch_meta = {
        "batch_id": batch_id,
        "source": source,
        "intake_date": datetime.now().strftime("%Y-%m-%d"),
        "status": "raw",
        "job_count": None,
        "passed_count": None,
        "excluded_count": None,
    }
    content = "---\n" + yaml.dump(batch_meta, default_flow_style=False, allow_unicode=True) + "---\n\n" + raw_text
    (batches_dir / f"{batch_id}.md").write_text(content, encoding="utf-8")

    # Load rules for triage preview
    rules_file = root / "rules" / "config.yaml"
    rules = {}
    if rules_file.exists():
        try:
            rules = yaml.safe_load(rules_file.read_text(encoding="utf-8")) or {}
        except Exception:
            pass

    triage_rules = {
        "rate_min_hourly": rules.get("rate", {}).get("min_hourly", 85),
        "remote_first": rules.get("location", {}).get("remote_first", True),
        "full_time_permanent_ok": rules.get("contract_preferences", {}).get("full_time_permanent", False),
        "accepted_contract_types": rules.get("contract_preferences", {}).get("types", ["contract"]),
        "special_cities": list((rules.get("location", {}).get("special_cities") or {}).keys()),
    }

    return json.dumps({
        "action": "parse_job_list",
        "batch_id": batch_id,
        "source": source,
        "raw_text": raw_text,
        "triage_rules": triage_rules,
        "instructions": (
            f"Parse each individual job listing from raw_text. For each job:\n"
            f"1. Extract structured fields:\n"
            f"   - title, company, company_slug (lowercase-hyphenated), location\n"
            f"   - remote_policy: 'remote' | 'hybrid' | 'onsite' | null\n"
            f"   - contract_type: 'contract' | 'full-time' | 'part-time' | null\n"
            f"   - salary_stated or rate_stated (preserve original string, or null)\n"
            f"   - source_url (if present, else '')\n"
            f"   - signals dict: {{\n"
            f"       easy_apply: true/false/null (is there a one-click apply option?),\n"
            f"       applicant_count: int/null (e.g. '47 applicants' → 47),\n"
            f"       days_since_posted: int/null (e.g. '3 days ago'→3, '2 weeks ago'→14, 'Just posted'→0)\n"
            f"     }}\n"
            f"2. Call jh_ingest_job(raw_text=<snippet>, source_url=<url>, job_type='list_item', batch_id='{batch_id}')\n"
            f"3. Immediately write all extracted fields + signals into the frontmatter of the returned job file.\n"
            f"After ALL items are ingested, call jh_triage_job_list(batch_id='{batch_id}').\n"
            f"Signals are critical for pursuit scoring — extract them even if approximate."
        )
    }, indent=2)


@mcp.tool()
def jh_triage_job_list(batch_id: str, project_path: str = ".") -> str:
    """
    Score and bucket all jobs in a list batch using pursuit scoring model.

    Assigns each job a bucket based on available signals + rules:
    - pursue:   high priority — get the full JD now (score >= 78)
    - research: interesting but need more company/role info (score 60-77)
    - watch:    low priority, may become relevant (score 42-59)
    - pass:     soft skip — stays visible for manual review (score < 42)
    - suspect:  flagged — resume farm, ghost role, pattern anomaly

    Hard-archives only truly disqualified jobs: rate < 50% of minimum.
    Everything else stays in raw/ with a bucket label — user reviews in UI.

    ALWAYS call this after jh_ingest_job_list + parsing all items.
    Returns bucket distribution summary.
    """
    core = _boot(project_path)
    root = core.config.data_path

    rules_file = root / "rules" / "config.yaml"
    rules = {}
    if rules_file.exists():
        try:
            rules = yaml.safe_load(rules_file.read_text(encoding="utf-8")) or {}
        except Exception:
            pass

    rate_min = rules.get("rate", {}).get("min_hourly", 85)
    raw_dir = root / "jobs" / "raw"
    archived_dir = root / "jobs" / "archived"
    archived_dir.mkdir(parents=True, exist_ok=True)

    bucket_counts: dict[str, int] = {}
    summary: dict = {"batch_id": batch_id, "total": 0, "hard_archived": 0,
                     "buckets": bucket_counts, "jobs": []}

    for f in sorted(raw_dir.glob("*.md")):
        try:
            content = f.read_text(encoding="utf-8")
        except Exception:
            continue
        meta = _parse_frontmatter(content)
        if meta.get("batch_id") != batch_id:
            continue

        summary["total"] += 1
        job_id = meta.get("id", f.stem)
        body = content[content.find("\n---", 3) + 4:] if "\n---" in content[3:] else content

        # Hard-archive only when rate is clearly disqualifying (< 50% of minimum)
        rate_num = _parse_rate(str(meta.get("rate_stated") or meta.get("salary_stated") or ""))
        if rate_num is not None and rate_num < rate_min * 0.5:
            meta["triage_result"] = "exclude"
            meta["exclude_reason"] = f"Rate ${rate_num}/hr — less than half of minimum ${rate_min}/hr"
            meta["status"] = "archived"
            meta["bucket"] = "pass"
            (archived_dir / f.name).write_text(
                "---\n" + yaml.dump(meta, default_flow_style=False, allow_unicode=True) + "---\n" + body,
                encoding="utf-8")
            f.unlink()
            summary["hard_archived"] += 1
            summary["jobs"].append({"id": job_id, "result": "hard_archived",
                                    "reason": meta["exclude_reason"],
                                    "title": meta.get("title"), "company": meta.get("company")})
            continue

        # Compute pursuit score and assign bucket
        pursuit_score, bucket = _score_pursuit(meta, rules)
        meta["triage_result"] = "pass"
        meta["bucket"] = bucket
        meta["pursuit_score"] = pursuit_score
        f.write_text(
            "---\n" + yaml.dump(meta, default_flow_style=False, allow_unicode=True) + "---\n" + body,
            encoding="utf-8")

        bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1
        summary["jobs"].append({"id": job_id, "result": "pass", "bucket": bucket,
                                "pursuit_score": pursuit_score,
                                "title": meta.get("title"), "company": meta.get("company")})

    # Update batch record with bucket distribution
    batch_file = root / "jobs" / "batches" / f"{batch_id}.md"
    if batch_file.exists():
        bc = batch_file.read_text(encoding="utf-8")
        bm = _parse_frontmatter(bc)
        bbody = bc[bc.find("\n---", 3) + 4:] if "\n---" in bc[3:] else bc
        active = summary["total"] - summary["hard_archived"]
        bm.update({"status": "triaged", "job_count": summary["total"],
                   "passed_count": active, "excluded_count": summary["hard_archived"],
                   "bucket_counts": bucket_counts})
        batch_file.write_text(
            "---\n" + yaml.dump(bm, default_flow_style=False, allow_unicode=True) + "---\n" + bbody,
            encoding="utf-8")

    return json.dumps(summary, indent=2)


@mcp.tool()
def jh_digest_job(job_id: str, project_path: str = ".") -> str:
    """
    Return everything needed to extract structured fields from a raw job record.

    Returns a JSON payload with raw content and instructions.
    Claude extracts the fields and writes the digested record to jobs/digested/.
    ALWAYS call jh_score_job after digestion.
    NEVER modify the raw file — the digested record is a separate file.
    """
    core = _boot(project_path)
    root = core.config.data_path

    raw_file = root / "jobs" / "raw" / f"{job_id}.md"
    if not raw_file.exists():
        return f"ERROR: Job {job_id} not found in jobs/raw/. Check jobs/digested/ — it may already be digested."

    raw_content = raw_file.read_text(encoding="utf-8")
    meta = _parse_frontmatter(raw_content)
    job_type = meta.get("type", "single")
    output_path = root / "jobs" / "digested" / f"{job_id}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    return json.dumps({
        "action": "digest_job",
        "job_id": job_id,
        "job_type": job_type,
        "raw_content": raw_content,
        "output_path": str(output_path),
        "instructions": (
            f"Extract structured fields from raw_content. Write to output_path with this YAML front matter:\n"
            f"  id: {job_id}\n"
            f"  type: {job_type}\n"
            f"  status: digested\n"
            f"  title: <extracted>\n"
            f"  company: <extracted>\n"
            f"  company_slug: <kebab-case>\n"
            f"  location: <city, state or 'Remote'>\n"
            f"  remote_policy: remote | hybrid | onsite\n"
            f"  contract_type: contract | full-time | part-time\n"
            f"  duration_months: <number or null>\n"
            f"  rate_stated: <'$120/hr' or null>\n"
            f"  posted_date: <YYYY-MM-DD or null>\n"
            f"  intake_date: {meta.get('intake_date', datetime.now().strftime('%Y-%m-%d'))}\n"
            f"  source_url: {meta.get('source_url', '')}\n"
            f"  required_skills: [list of strings]\n"
            f"  nice_to_have_skills: [list of strings]\n"
            f"  red_flags: [list of strings — anything concerning]\n"
            f"  application_url: <direct apply URL or null>\n"
            f"  score: null\n"
            f"  recommendation: null\n"
            f"  group_fit: [A, B, C, D, or E — which groups fit best]\n\n"
            f"After the front matter, write:\n"
            f"## Summary\n(2-3 paragraph role overview)\n\n"
            f"## Key Requirements\n(bullet list)\n\n"
            f"## Responsibilities\n(bullet list)\n\n"
            f"## Red Flags\n(bullet list, or 'None identified')\n\n"
            f"After writing, also call jh_upsert_company to create/update the company record."
        )
    }, indent=2)


@mcp.tool()
def jh_score_job(job_id: str, project_path: str = ".") -> str:
    """
    Stage a job for scoring. Computes mechanical scores and returns master truth
    + required skills for LLM semantic skill evaluation.

    Mechanical dimensions computed here: rate, location, contract type, timing.
    Skill match is intentionally NOT computed algorithmically — the LLM must
    evaluate it semantically from the returned master_truth and skills lists.

    ALWAYS call this after jh_digest_job.
    After receiving this result:
      1. Read master_truth and evaluate each required skill semantically.
         Consider synonyms, related experience, and implied skills — not literal strings.
      2. Call jh_save_score(job_id, skill_score, skill_note) with your evaluation.
    """
    core = _boot(project_path)
    root = core.config.data_path

    job_file = root / "jobs" / "digested" / f"{job_id}.md"
    if not job_file.exists():
        return f"ERROR: {job_id} not found in jobs/digested/. Run jh_digest_job first."

    content = job_file.read_text(encoding="utf-8")
    meta = _parse_frontmatter(content)

    rules_file = root / "rules" / "config.yaml"
    rules = yaml.safe_load(rules_file.read_text(encoding="utf-8")) if rules_file.exists() else {}

    truth_text = ""
    truth_file = root / "truth" / "master" / "truth.md"
    if truth_file.exists():
        truth_text = truth_file.read_text(encoding="utf-8")

    weights = rules.get("scoring_weights") or {
        "skill_match": 0.28, "rate_match": 0.25, "location_match": 0.20,
        "contract_length_match": 0.14, "timing_match": 0.08, "freshness_match": 0.05,
    }

    rate_input = str(meta.get("rate_stated") or meta.get("salary_stated") or "")
    s_rate,  n_rate  = _score_rate(rate_input, rules, meta.get("contract_type", ""))
    s_loc,   n_loc   = _score_location(meta.get("remote_policy", ""), meta.get("location", ""), rules)
    s_dur,   n_dur   = _score_contract_length(meta.get("duration_months"), meta.get("contract_type", ""), rules)
    s_time,  n_time  = _score_timing(rules)
    s_fresh, n_fresh = _score_freshness(meta.get("posted_date", ""), rules)

    return json.dumps({
        "action": "score_job_staged",
        "job_id": job_id,
        "title": meta.get("title"),
        "company": meta.get("company"),
        "mechanical_scores": {
            "rate_match":            {"score": s_rate,  "weight": weights.get("rate_match", 0.25),            "note": n_rate},
            "location_match":        {"score": s_loc,   "weight": weights.get("location_match", 0.20),        "note": n_loc},
            "contract_length_match": {"score": s_dur,   "weight": weights.get("contract_length_match", 0.14), "note": n_dur},
            "timing_match":          {"score": s_time,  "weight": weights.get("timing_match", 0.08),          "note": n_time},
            "freshness_match":       {"score": s_fresh, "weight": weights.get("freshness_match", 0.05),       "note": n_fresh},
        },
        "skill_weight": weights.get("skill_match", 0.28),
        "required_skills":    meta.get("required_skills") or [],
        "nice_to_have_skills": meta.get("nice_to_have_skills") or [],
        "master_truth": truth_text,
        "instructions": (
            "Evaluate skill match semantically. For each required skill, decide whether "
            "the candidate's master_truth demonstrates that skill — considering synonyms, "
            "adjacent experience, and implied competence, not just literal strings. "
            "Score 0–100 overall for skill match. Write a concise note listing which skills "
            "are clearly demonstrated, which are implied, and which are genuinely absent. "
            "Then call jh_save_score(job_id, skill_score, skill_note) to finalise."
        ),
    }, indent=2)


@mcp.tool()
def jh_save_score(job_id: str, skill_score: float, skill_note: str, project_path: str = ".") -> str:
    """
    Persist the LLM skill evaluation and compute the final composite score.

    Call this immediately after evaluating skill match from jh_score_job.
    skill_score: 0–100 float from your semantic skill evaluation.
    skill_note:  concise explanation of matched / implied / absent skills.

    Computes weighted composite, writes score + recommendation back to job file.
    Call jh_whitelist_job next if recommendation is apply or monitor.
    """
    core = _boot(project_path)
    root = core.config.data_path

    job_file = root / "jobs" / "digested" / f"{job_id}.md"
    if not job_file.exists():
        return f"ERROR: {job_id} not found in jobs/digested/."

    content = job_file.read_text(encoding="utf-8")
    meta = _parse_frontmatter(content)
    body = content[content.find("\n---", 3) + 4:] if "\n---" in content[3:] else content

    rules_file = root / "rules" / "config.yaml"
    rules = yaml.safe_load(rules_file.read_text(encoding="utf-8")) if rules_file.exists() else {}

    weights = rules.get("scoring_weights") or {
        "skill_match": 0.28, "rate_match": 0.25, "location_match": 0.20,
        "contract_length_match": 0.14, "timing_match": 0.08, "freshness_match": 0.05,
    }
    bands = rules.get("recommendation_bands") or {"apply": 80, "monitor": 65, "stretch": 45}

    rate_input = str(meta.get("rate_stated") or meta.get("salary_stated") or "")
    s_rate,  n_rate  = _score_rate(rate_input, rules, meta.get("contract_type", ""))
    s_loc,   n_loc   = _score_location(meta.get("remote_policy", ""), meta.get("location", ""), rules)
    s_dur,   n_dur   = _score_contract_length(meta.get("duration_months"), meta.get("contract_type", ""), rules)
    s_time,  n_time  = _score_timing(rules)
    s_fresh, n_fresh = _score_freshness(meta.get("posted_date", ""), rules)

    composite = round(
        skill_score * weights.get("skill_match", 0.28) +
        s_rate      * weights.get("rate_match", 0.25) +
        s_loc       * weights.get("location_match", 0.20) +
        s_dur       * weights.get("contract_length_match", 0.14) +
        s_time      * weights.get("timing_match", 0.08) +
        s_fresh     * weights.get("freshness_match", 0.05), 1)

    rec = (
        "apply"   if composite >= bands.get("apply", 80) else
        "monitor" if composite >= bands.get("monitor", 65) else
        "stretch" if composite >= bands.get("stretch", 45) else
        "pass"
    )

    meta["score"] = composite
    meta["recommendation"] = rec
    meta["score_breakdown"] = {
        "skill_match":           {"score": skill_score, "note": skill_note},
        "rate_match":            {"score": s_rate,      "note": n_rate},
        "location_match":        {"score": s_loc,       "note": n_loc},
        "contract_length_match": {"score": s_dur,       "note": n_dur},
        "timing_match":          {"score": s_time,      "note": n_time},
        "freshness_match":       {"score": s_fresh,     "note": n_fresh},
    }
    job_file.write_text(
        "---\n" + yaml.dump(meta, default_flow_style=False, allow_unicode=True) + "---\n" + body,
        encoding="utf-8")

    return json.dumps({
        "job_id": job_id,
        "title": meta.get("title"),
        "company": meta.get("company"),
        "score": composite,
        "recommendation": rec,
        "breakdown": {
            "skill_match":           {"score": skill_score, "weight": weights.get("skill_match", 0.28),            "note": skill_note},
            "rate_match":            {"score": s_rate,      "weight": weights.get("rate_match", 0.25),             "note": n_rate},
            "location_match":        {"score": s_loc,       "weight": weights.get("location_match", 0.20),         "note": n_loc},
            "contract_length_match": {"score": s_dur,       "weight": weights.get("contract_length_match", 0.14),  "note": n_dur},
            "timing_match":          {"score": s_time,      "weight": weights.get("timing_match", 0.08),           "note": n_time},
            "freshness_match":       {"score": s_fresh,     "weight": weights.get("freshness_match", 0.05),        "note": n_fresh},
        },
    }, indent=2)


@mcp.tool()
def jh_re_evaluate_jobs(jobs: str, project_path: str = ".") -> str:
    """
    Re-score jobs using current rules — zero LLM cost, uses stored skill scores.

    Recomputes all mechanical dimensions (rate, location, contract, timing, freshness)
    and the composite using current weights, missing_data_defaults, and recommendation_bands.
    Skill match keeps the stored score from the last LLM evaluation.

    jobs: one or more job IDs (comma-separated), OR a time filter:
      "today"      — jobs whose files were modified today
      "yesterday"  — modified yesterday
      "this_week"  — modified in the last 7 days

    Examples:
      jh_re_evaluate_jobs("job_20260530_abc123")
      jh_re_evaluate_jobs("job_20260530_abc, job_20260530_def")
      jh_re_evaluate_jobs("today")
      jh_re_evaluate_jobs("this_week")
    """
    from datetime import date as _date, timedelta

    core = _boot(project_path)
    root = core.config.data_path
    rules_file = root / "rules" / "config.yaml"
    rules = yaml.safe_load(rules_file.read_text(encoding="utf-8")) if rules_file.exists() else {}

    today = _date.today()
    token = jobs.strip().lower()

    if token in ("today", "yesterday", "this_week"):
        cutoff = today if token == "today" else today - timedelta(days=1 if token == "yesterday" else 7)
        job_ids = []
        for folder in ("digested", "whitelisted"):
            fp = root / "jobs" / folder
            if not fp.exists():
                continue
            for f in fp.glob("*.md"):
                if f.name == ".gitkeep":
                    continue
                try:
                    if _date.fromtimestamp(f.stat().st_mtime) >= cutoff:
                        job_ids.append(f.stem)
                except Exception:
                    pass
    else:
        job_ids = [j.strip() for j in jobs.split(",") if j.strip()]

    if not job_ids:
        return "No jobs matched."

    weights = rules.get("scoring_weights") or {
        "skill_match": 0.28, "rate_match": 0.25, "location_match": 0.20,
        "contract_length_match": 0.14, "timing_match": 0.08, "freshness_match": 0.05,
    }
    bands = rules.get("recommendation_bands") or {"apply": 80, "monitor": 65, "stretch": 45}

    results = []
    for job_id in job_ids:
        job_file = next(
            (root / "jobs" / f / f"{job_id}.md"
             for f in ("digested", "whitelisted")
             if (root / "jobs" / f / f"{job_id}.md").exists()),
            None,
        )
        if not job_file:
            results.append({"job_id": job_id, "status": "not found in digested or whitelisted"})
            continue

        content = job_file.read_text(encoding="utf-8")
        meta = _parse_frontmatter(content)
        body = content[content.find("\n---", 3) + 4:] if "\n---" in content[3:] else content

        stored_skill = (meta.get("score_breakdown") or {}).get("skill_match", {}).get("score")
        if stored_skill is None:
            results.append({"job_id": job_id, "status": "no stored skill score — run jh_score_job first"})
            continue

        skill_note = (meta.get("score_breakdown") or {}).get("skill_match", {}).get("note", "")
        rate_input = str(meta.get("rate_stated") or meta.get("salary_stated") or "")
        s_rate,  n_rate  = _score_rate(rate_input, rules, meta.get("contract_type", ""))
        s_loc,   n_loc   = _score_location(meta.get("remote_policy", ""), meta.get("location", ""), rules)
        s_dur,   n_dur   = _score_contract_length(meta.get("duration_months"), meta.get("contract_type", ""), rules)
        s_time,  n_time  = _score_timing(rules)
        s_fresh, n_fresh = _score_freshness(meta.get("posted_date", ""), rules)

        composite = round(
            stored_skill * weights.get("skill_match", 0.28) +
            s_rate       * weights.get("rate_match", 0.25) +
            s_loc        * weights.get("location_match", 0.20) +
            s_dur        * weights.get("contract_length_match", 0.14) +
            s_time       * weights.get("timing_match", 0.08) +
            s_fresh      * weights.get("freshness_match", 0.05), 1)

        rec = (
            "apply"   if composite >= bands.get("apply", 80) else
            "monitor" if composite >= bands.get("monitor", 65) else
            "stretch" if composite >= bands.get("stretch", 45) else
            "pass"
        )

        old_score = meta.get("score")
        old_rec   = meta.get("recommendation")

        meta["score"] = composite
        meta["recommendation"] = rec
        meta["score_breakdown"] = {
            "skill_match":           {"score": stored_skill, "note": skill_note},
            "rate_match":            {"score": s_rate,       "note": n_rate},
            "location_match":        {"score": s_loc,        "note": n_loc},
            "contract_length_match": {"score": s_dur,        "note": n_dur},
            "timing_match":          {"score": s_time,       "note": n_time},
            "freshness_match":       {"score": s_fresh,      "note": n_fresh},
        }
        job_file.write_text(
            "---\n" + yaml.dump(meta, default_flow_style=False, allow_unicode=True) + "---\n" + body,
            encoding="utf-8")

        results.append({
            "job_id":      job_id,
            "title":       meta.get("title"),
            "score_before": old_score,
            "score_after":  composite,
            "rec_before":   old_rec,
            "rec_after":    rec,
            "changed":      old_score != composite,
        })

    changed = sum(1 for r in results if r.get("changed"))
    return json.dumps({"re_evaluated": len(results), "changed": changed, "results": results}, indent=2)


@mcp.tool()
def jh_whitelist_job(job_id: str, project_path: str = ".") -> str:
    """
    Move a job to whitelisted status — mark as active target.

    Moves record from jobs/digested/ to jobs/whitelisted/.
    ALWAYS score the job first with jh_score_job.
    Call jh_generate_application_package when ready to apply.
    """
    core = _boot(project_path)
    root = core.config.data_path
    for src_folder in ("digested", "raw"):
        src = root / "jobs" / src_folder / f"{job_id}.md"
        if src.exists():
            content = src.read_text(encoding="utf-8")
            meta = _parse_frontmatter(content)
            body = content[content.find("\n---", 3) + 4:] if "\n---" in content[3:] else content
            meta["status"] = "whitelisted"
            dest = root / "jobs" / "whitelisted"
            dest.mkdir(parents=True, exist_ok=True)
            (dest / f"{job_id}.md").write_text(
                "---\n" + yaml.dump(meta, default_flow_style=False, allow_unicode=True) + "---\n" + body,
                encoding="utf-8")
            src.unlink()
            return json.dumps({"job_id": job_id, "status": "whitelisted",
                               "score": meta.get("score"), "recommendation": meta.get("recommendation"),
                               "next": "Call jh_generate_application_package when ready to apply."})
    return f"ERROR: Job {job_id} not found in digested or raw."


@mcp.tool()
def jh_archive_job(job_id: str, reason: str = "", project_path: str = ".") -> str:
    """
    Remove a job from the active pipeline.

    Moves from whitelisted/digested/raw to jobs/archived/.
    reason: why it was passed on (feeds into gap analysis later).
    """
    core = _boot(project_path)
    root = core.config.data_path
    for src_folder in ("whitelisted", "digested", "raw"):
        src = root / "jobs" / src_folder / f"{job_id}.md"
        if src.exists():
            content = src.read_text(encoding="utf-8")
            meta = _parse_frontmatter(content)
            body = content[content.find("\n---", 3) + 4:] if "\n---" in content[3:] else content
            meta["status"] = "archived"
            if reason:
                meta["archive_reason"] = reason
            dest = root / "jobs" / "archived"
            dest.mkdir(parents=True, exist_ok=True)
            (dest / f"{job_id}.md").write_text(
                "---\n" + yaml.dump(meta, default_flow_style=False, allow_unicode=True) + "---\n" + body,
                encoding="utf-8")
            src.unlink()
            return json.dumps({"job_id": job_id, "status": "archived", "reason": reason})
    return f"ERROR: Job {job_id} not found."


@mcp.tool()
def jh_list_whitelisted_jobs(project_path: str = ".") -> str:
    """
    Return all active target jobs (whitelisted, not yet applied).

    ALWAYS call this when:
    - User asks "what jobs am I targeting?"
    - Before running generate_application_package to see what's ready
    """
    core = _boot(project_path)
    root = core.config.data_path
    wl_dir = root / "jobs" / "whitelisted"
    if not wl_dir.exists():
        return json.dumps({"whitelisted": [], "count": 0})
    jobs = []
    for f in sorted(wl_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True):
        meta = _parse_frontmatter(f.read_text(encoding="utf-8"))
        jobs.append({
            "job_id": f.stem,
            "title": meta.get("title"),
            "company": meta.get("company"),
            "location": meta.get("location"),
            "rate_stated": meta.get("rate_stated"),
            "score": meta.get("score"),
            "recommendation": meta.get("recommendation"),
            "group_fit": meta.get("group_fit") or [],
        })
    return json.dumps({"whitelisted": jobs, "count": len(jobs)}, indent=2)


@mcp.tool()
def jh_get_job(job_id: str, project_path: str = ".") -> str:
    """
    Return the full job record by job ID. Searches raw, digested, whitelisted, archived.
    """
    core = _boot(project_path)
    root = core.config.data_path
    for subfolder in ("whitelisted", "digested", "raw", "archived"):
        f = root / "jobs" / subfolder / f"{job_id}.md"
        if f.exists():
            return json.dumps({"job_id": job_id, "status": subfolder,
                               "content": f.read_text(encoding="utf-8")})
    return f"ERROR: Job {job_id} not found in any jobs/ subfolder."


# ---------------------------------------------------------------------------
# Company Module
# ---------------------------------------------------------------------------

@mcp.tool()
def jh_upsert_company(company_slug: str, data_json: str, project_path: str = ".") -> str:
    """
    Create or update a company intelligence record.

    Auto-called during jh_digest_job. Can also be called manually to enrich
    a company record with research, notes, or warm lead status.

    data_json: JSON with fields to upsert (name, size, industry, website,
               contacts, notes, status, job_id to associate).
    """
    core = _boot(project_path)
    root = core.config.data_path
    companies_dir = root / "companies"
    companies_dir.mkdir(parents=True, exist_ok=True)

    try:
        incoming = json.loads(data_json) if isinstance(data_json, str) else data_json
    except Exception:
        return f"ERROR: data_json is not valid JSON. Got: {str(data_json)[:100]}"

    company_file = companies_dir / f"{company_slug}.md"
    today = datetime.now().strftime("%Y-%m-%d")

    # Load existing or create fresh skeleton
    if company_file.exists():
        content = company_file.read_text(encoding="utf-8")
        meta = _parse_frontmatter(content)
        body = content[content.find("\n---", 3) + 4:] if "\n---" in content[3:] else content
    else:
        meta = {
            "slug": company_slug,
            "name": company_slug.replace("-", " ").title(),
            "status": "cold",
            "industry": None,
            "size": None,
            "website": None,
            "contacts": [],
            "jobs": [],
            "notes": "",
            "warm_lead_since": None,
            "warm_lead_resurface": None,
            "warm_lead_note": "",
            "blacklist_reason": "",
            "created": today,
        }
        body = "\n## Notes\n\n"

    # Merge incoming fields
    simple_fields = {"name", "status", "industry", "size", "website", "notes",
                     "blacklist_reason", "warm_lead_note"}
    for k, v in incoming.items():
        if k in simple_fields and v:
            meta[k] = v
        elif k == "contacts" and isinstance(v, list):
            existing = meta.get("contacts") or []
            meta["contacts"] = list(dict.fromkeys(existing + v))
        elif k == "job_id" and v:
            existing = meta.get("jobs") or []
            if v not in existing:
                existing.append(v)
            meta["jobs"] = existing

    meta["last_updated"] = today

    company_file.write_text(
        "---\n" + yaml.dump(meta, default_flow_style=False, allow_unicode=True) + "---\n" + body,
        encoding="utf-8"
    )

    return json.dumps({
        "company_slug": company_slug,
        "name": meta.get("name"),
        "status": meta.get("status"),
        "jobs": meta.get("jobs") or [],
        "action": "created" if not (companies_dir / f"{company_slug}.md").exists() else "updated",
    }, indent=2)


@mcp.tool()
def jh_get_company(company_slug: str, project_path: str = ".") -> str:
    """
    Return a company intelligence record from companies/{slug}.md.

    company_slug: kebab-case company name (e.g. acme-corp)
    """
    core = _boot(project_path)
    root = core.config.data_path
    company_file = root / "companies" / f"{company_slug}.md"
    if not company_file.exists():
        return f"ERROR: No record for company '{company_slug}'. Run jh_upsert_company to create one."
    content = company_file.read_text(encoding="utf-8")
    meta = _parse_frontmatter(content)
    return json.dumps({"company_slug": company_slug, "meta": meta, "content": content}, indent=2)


@mcp.tool()
def jh_list_companies(status: str = "", project_path: str = ".") -> str:
    """
    Return all tracked companies, optionally filtered by status.

    status: cold | warm | active | blacklisted | '' (all)
    ALWAYS call this when user asks about companies or market landscape.
    """
    core = _boot(project_path)
    root = core.config.data_path
    companies_dir = root / "companies"
    if not companies_dir.exists():
        return json.dumps({"companies": [], "count": 0}, indent=2)

    companies = []
    for f in sorted(companies_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True):
        meta = _parse_frontmatter(f.read_text(encoding="utf-8"))
        if status and meta.get("status") != status:
            continue
        companies.append({
            "slug": f.stem,
            "name": meta.get("name"),
            "status": meta.get("status", "cold"),
            "industry": meta.get("industry"),
            "size": meta.get("size"),
            "jobs": meta.get("jobs") or [],
            "job_count": len(meta.get("jobs") or []),
            "contacts": meta.get("contacts") or [],
            "warm_lead_resurface": meta.get("warm_lead_resurface"),
            "last_updated": meta.get("last_updated"),
        })

    return json.dumps({"companies": companies, "count": len(companies)}, indent=2)


@mcp.tool()
def jh_flag_warm_lead(company_slug: str, note: str = "", project_path: str = ".") -> str:
    """
    Mark a company as a warm lead for future outreach.

    Use when a company is interesting but timing is wrong.
    Company will be surfaced again after 60 days.
    Creates the company record if it doesn't exist yet.
    """
    from datetime import timedelta, date
    core = _boot(project_path)
    root = core.config.data_path
    companies_dir = root / "companies"
    companies_dir.mkdir(parents=True, exist_ok=True)

    company_file = companies_dir / f"{company_slug}.md"
    today = date.today()
    resurface = (today + timedelta(days=60)).isoformat()

    if company_file.exists():
        content = company_file.read_text(encoding="utf-8")
        meta = _parse_frontmatter(content)
        body = content[content.find("\n---", 3) + 4:] if "\n---" in content[3:] else content
    else:
        meta = {
            "slug": company_slug,
            "name": company_slug.replace("-", " ").title(),
            "jobs": [],
            "contacts": [],
            "created": today.isoformat(),
        }
        body = "\n## Notes\n\n"

    meta["status"] = "warm"
    meta["warm_lead_since"] = today.isoformat()
    meta["warm_lead_resurface"] = resurface
    meta["last_updated"] = today.isoformat()
    if note:
        meta["warm_lead_note"] = note

    company_file.write_text(
        "---\n" + yaml.dump(meta, default_flow_style=False, allow_unicode=True) + "---\n" + body,
        encoding="utf-8"
    )

    return json.dumps({
        "company_slug": company_slug,
        "name": meta.get("name"),
        "status": "warm",
        "warm_lead_since": today.isoformat(),
        "resurface_date": resurface,
        "note": note,
    }, indent=2)


# ---------------------------------------------------------------------------
# Application Module
# ---------------------------------------------------------------------------

@mcp.tool()
def jh_generate_application_package(job_id: str, project_path: str = ".") -> str:
    """
    Generate a full application package for a whitelisted job.

    Steps:
    1. Reads job record + master truth + rules
    2. Selects best group fit
    3. Generates tailored resume for that group
    4. Generates cover letter in Mahdi's voice
    5. Saves both to docs/{job_id}/

    ALWAYS call jh_get_master_truth and jh_get_rules first.
    NEVER claim skills not in master truth.
    NEVER explain Boston angle in cover letter unless explicitly asked.

    ERROR POLICY — if this returns an error, STOP and report to user.
    """
    core = _boot(project_path)
    root = core.config.data_path

    # Job must be whitelisted
    job_file = root / "jobs" / "whitelisted" / f"{job_id}.md"
    if not job_file.exists():
        return f"ERROR: Job {job_id} not found in jobs/whitelisted/. Run jh_whitelist_job first."

    job_content = job_file.read_text(encoding="utf-8")
    meta = _parse_frontmatter(job_content)
    body = job_content[job_content.find("\n---", 3) + 4:] if "\n---" in job_content[3:] else job_content

    # Select group: first in group_fit, or A
    group_fit = meta.get("group_fit") or ["A"]
    group = group_fit[0].upper() if group_fit else "A"

    # Template
    tpl_dir = root / "blueprints" / "resumes" / "templates"
    group_tpl = tpl_dir / f"group_{group.lower()}.md"
    default_tpl = tpl_dir / "default.md"
    if group_tpl.exists():
        template = group_tpl.read_text(encoding="utf-8")
        template_source = f"group_{group.lower()}.md"
    elif default_tpl.exists():
        template = default_tpl.read_text(encoding="utf-8")
        template_source = "default.md (fallback)"
    else:
        return "ERROR: No resume template found. Create blueprints/resumes/templates/default.md."

    truth_file = root / "truth" / "master" / "truth.md"
    master_truth = truth_file.read_text(encoding="utf-8") if truth_file.exists() else ""
    if not master_truth:
        return "ERROR: master truth not found at truth/master/truth.md."

    rules_file = root / "rules" / "config.yaml"
    rules = yaml.safe_load(rules_file.read_text(encoding="utf-8")) if rules_file.exists() else {}

    docs_dir = root / "applications" / job_id
    docs_dir.mkdir(parents=True, exist_ok=True)
    resume_path = docs_dir / "resume.md"
    cover_path = docs_dir / "cover_letter.md"

    title = meta.get("title", "the role")
    company = meta.get("company", "the company")
    required_skills = meta.get("required_skills") or []
    nice_to_have = meta.get("nice_to_have_skills") or []
    identity = rules.get("identity", {})
    rate_pref = rules.get("rate", {}).get("preferred_hourly", 120)

    return json.dumps({
        "action": "generate_application_package",
        "job_id": job_id,
        "group": group,
        "template_source": template_source,
        "template": template,
        "master_truth": master_truth,
        "job_content": job_content,
        "job_meta": meta,
        "output": {
            "resume_path": str(resume_path),
            "cover_letter_path": str(cover_path),
        },
        "resume_instructions": (
            f"Generate a tailored Group {group} resume for '{title}' at '{company}'. "
            f"Fill every {{PLACEHOLDER}} in the template using ONLY facts from master_truth. "
            f"Emphasize skills matching: required={required_skills[:6]}, nice-to-have={nice_to_have[:4]}. "
            f"Reorder bullets to surface most relevant experience first. "
            f"Do NOT add any skill or experience not in master_truth. "
            f"Write the completed resume markdown to output.resume_path."
        ),
        "cover_letter_instructions": (
            f"Write a cover letter for '{title}' at '{company}'. "
            f"Voice: confident, direct, technically grounded — Mahdi's authentic voice. No corporate fluff. "
            f"Structure: (1) opening hook — specific reason this role fits right now, "
            f"(2) strongest 2 relevant projects/wins from master_truth that match the JD, "
            f"(3) rate expectation (${rate_pref}/hr contract) woven in naturally if applicable, "
            f"(4) brief close with call to action. "
            f"Do NOT mention Boston commute or location logistics unless the job is hybrid/onsite. "
            f"Do NOT invent experience. Length: ~250-300 words. "
            f"Write as markdown to output.cover_letter_path."
        ),
    }, indent=2)


@mcp.tool()
def jh_generate_interview_prep(job_id: str, project_path: str = ".") -> str:
    """
    Generate an interview prep document for a job.

    Maps JD requirements to master truth, surfaces likely questions,
    identifies strongest talking points and potential gaps.
    """
    core = _boot(project_path)
    root = core.config.data_path

    job_content = None
    for subfolder in ("whitelisted", "digested"):
        jf = root / "jobs" / subfolder / f"{job_id}.md"
        if jf.exists():
            job_content = jf.read_text(encoding="utf-8")
            break
    if job_content is None:
        return f"ERROR: Job {job_id} not found in whitelisted or digested."

    meta = _parse_frontmatter(job_content)
    truth_file = root / "truth" / "master" / "truth.md"
    master_truth = truth_file.read_text(encoding="utf-8") if truth_file.exists() else ""

    output_path = root / "applications" / job_id / "interview_prep.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    title = meta.get("title", "the role")
    company = meta.get("company", "the company")
    required_skills = meta.get("required_skills") or []
    red_flags = meta.get("red_flags") or []

    return json.dumps({
        "action": "generate_interview_prep",
        "job_id": job_id,
        "job_meta": meta,
        "job_content": job_content,
        "master_truth": master_truth,
        "output_path": str(output_path),
        "instructions": (
            f"Generate an interview prep guide for '{title}' at '{company}'. "
            f"Write to output_path as markdown with these sections:\n"
            f"## Role Overview\n(2 sentences on what the role is and why it fits)\n\n"
            f"## Strongest Talking Points\n"
            f"(3–5 bullet points — map required_skills={required_skills} to specific projects/wins in master_truth. "
            f"For each: skill → project or achievement → 1-sentence story)\n\n"
            f"## Likely Technical Questions\n"
            f"(5–8 questions derived from the JD requirements, with a concise answer grounded in master_truth)\n\n"
            f"## Likely Behavioral Questions\n"
            f"(3–5 questions with STAR-format answer outlines using real experience from master_truth)\n\n"
            f"## Potential Gaps / Watch Out\n"
            f"(Skills in JD not clearly covered by master_truth, and how to frame them honestly. "
            f"Red flags from JD: {red_flags})\n\n"
            f"## Questions to Ask Them\n"
            f"(4–6 sharp questions that demonstrate technical depth and due diligence)\n\n"
            f"Stick to facts in master_truth. Never fabricate experience."
        ),
    }, indent=2)


@mcp.tool()
def jh_log_application(job_id: str, method: str, contacts: str = "", notes: str = "", project_path: str = ".") -> str:
    """
    Record an application submission.

    ALWAYS call this immediately after submitting an application.
    Records: submission date, method, contacts, notes.
    Auto-schedules follow-up at 5 days.

    method: linkedin | email | direct | recruiter | referral
    """
    core = _boot(project_path)
    root = core.config.data_path

    # Find job record
    job_content = None
    job_src = None
    for subfolder in ("whitelisted", "digested", "raw"):
        jf = root / "jobs" / subfolder / f"{job_id}.md"
        if jf.exists():
            job_content = jf.read_text(encoding="utf-8")
            job_src = jf
            break
    if job_content is None:
        return f"ERROR: Job {job_id} not found."

    meta = _parse_frontmatter(job_content)
    body = job_content[job_content.find("\n---", 3) + 4:] if "\n---" in job_content[3:] else job_content

    today = datetime.now().strftime("%Y-%m-%d")
    follow_up = datetime.now().replace(
        day=min(datetime.now().day + 5, 28)
    ).strftime("%Y-%m-%d")
    # Proper 5-day calc
    from datetime import timedelta
    follow_up = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")

    # Update job record status → applied
    meta["status"] = "applied"
    meta["applied_date"] = today
    meta["application_method"] = method
    if job_src:
        job_src.write_text(
            "---\n" + yaml.dump(meta, default_flow_style=False, allow_unicode=True) + "---\n" + body,
            encoding="utf-8"
        )

    # Move to whitelisted if not already (keeps it visible)
    wl_dir = root / "jobs" / "whitelisted"
    wl_dir.mkdir(parents=True, exist_ok=True)
    wl_file = wl_dir / f"{job_id}.md"
    if job_src and job_src != wl_file:
        wl_file.write_text(
            "---\n" + yaml.dump(meta, default_flow_style=False, allow_unicode=True) + "---\n" + body,
            encoding="utf-8"
        )
        job_src.unlink(missing_ok=True)

    # Create application log record
    app_dir = root / "applications" / "active"
    app_dir.mkdir(parents=True, exist_ok=True)
    app_record = {
        "job_id": job_id,
        "title": meta.get("title"),
        "company": meta.get("company"),
        "status": "applied",
        "applied_date": today,
        "method": method,
        "contacts": contacts,
        "follow_up_date": follow_up,
        "notes": notes,
    }
    (app_dir / f"{job_id}.md").write_text(
        "---\n" + yaml.dump(app_record, default_flow_style=False, allow_unicode=True) +
        "---\n\n## Application Log\n\n"
        f"- **{today}** — Applied via {method}." +
        (f" Contacts: {contacts}." if contacts else "") +
        (f" Notes: {notes}" if notes else "") + "\n",
        encoding="utf-8"
    )

    return json.dumps({
        "job_id": job_id,
        "title": meta.get("title"),
        "company": meta.get("company"),
        "applied_date": today,
        "method": method,
        "follow_up_date": follow_up,
        "next": f"Follow up on {follow_up}. Call jh_schedule_followup to set a reminder."
    }, indent=2)


@mcp.tool()
def jh_schedule_followup(job_id: str, days: int = 5, project_path: str = ".") -> str:
    """
    Set or reschedule a follow-up reminder for an application.

    Default: 5 days from today.
    Writes follow-up date to applications/active/{job_id}.md.
    """
    from datetime import timedelta, date
    core = _boot(project_path)
    root = core.config.data_path

    app_file = root / "applications" / "active" / f"{job_id}.md"
    if not app_file.exists():
        return f"ERROR: No active application record for {job_id}. Run jh_log_application first."

    content = app_file.read_text(encoding="utf-8")
    meta = _parse_frontmatter(content)
    body = content[content.find("\n---", 3) + 4:] if "\n---" in content[3:] else content

    follow_up = (date.today() + timedelta(days=days)).isoformat()
    meta["follow_up_date"] = follow_up

    app_file.write_text(
        "---\n" + yaml.dump(meta, default_flow_style=False, allow_unicode=True) + "---\n" + body,
        encoding="utf-8"
    )

    return json.dumps({
        "job_id": job_id,
        "title": meta.get("title"),
        "company": meta.get("company"),
        "follow_up_date": follow_up,
        "days_from_today": days,
    }, indent=2)


@mcp.tool()
def jh_record_outcome(job_id: str, result: str, notes: str = "", rate_offered: str = "", project_path: str = ".") -> str:
    """
    Log the outcome of an application.

    result: no_response | interview | offer | rejected | withdrew
    Moves record to applications/outcomes/ and feeds result into gap analysis.
    """
    valid = {"no_response", "interview", "offer", "rejected", "withdrew"}
    if result not in valid:
        return f"ERROR: result must be one of {sorted(valid)}. Got: '{result}'"

    core = _boot(project_path)
    root = core.config.data_path

    app_file = root / "applications" / "active" / f"{job_id}.md"
    if not app_file.exists():
        return f"ERROR: No active application record for {job_id}."

    content = app_file.read_text(encoding="utf-8")
    meta = _parse_frontmatter(content)
    body = content[content.find("\n---", 3) + 4:] if "\n---" in content[3:] else content

    today = datetime.now().strftime("%Y-%m-%d")
    meta["status"] = result
    meta["outcome_date"] = today
    if notes:
        meta["outcome_notes"] = notes
    if rate_offered:
        meta["rate_offered"] = rate_offered

    outcomes_dir = root / "applications" / "outcomes"
    outcomes_dir.mkdir(parents=True, exist_ok=True)

    log_line = f"\n- **{today}** — Outcome: `{result}`." + \
               (f" Notes: {notes}" if notes else "") + \
               (f" Rate offered: {rate_offered}" if rate_offered else "")
    body = body.rstrip() + log_line + "\n"

    (outcomes_dir / f"{job_id}.md").write_text(
        "---\n" + yaml.dump(meta, default_flow_style=False, allow_unicode=True) + "---\n" + body,
        encoding="utf-8"
    )
    app_file.unlink()

    # Also archive the job from whitelisted
    wl_file = root / "jobs" / "whitelisted" / f"{job_id}.md"
    if wl_file.exists():
        jmeta = _parse_frontmatter(wl_file.read_text(encoding="utf-8"))
        jbody = wl_file.read_text(encoding="utf-8")
        jbody_text = jbody[jbody.find("\n---", 3) + 4:] if "\n---" in jbody[3:] else jbody
        jmeta["status"] = f"applied-{result}"
        arc_dir = root / "jobs" / "archived"
        arc_dir.mkdir(parents=True, exist_ok=True)
        (arc_dir / f"{job_id}.md").write_text(
            "---\n" + yaml.dump(jmeta, default_flow_style=False, allow_unicode=True) + "---\n" + jbody_text,
            encoding="utf-8"
        )
        wl_file.unlink()

    return json.dumps({
        "job_id": job_id,
        "title": meta.get("title"),
        "company": meta.get("company"),
        "result": result,
        "outcome_date": today,
    }, indent=2)


@mcp.tool()
def jh_list_active_applications(project_path: str = ".") -> str:
    """
    Return all in-flight applications with days-since-submission and follow-up status.

    ALWAYS call this when:
    - User asks "what needs follow-up today?"
    - User asks "what's in my pipeline?"
    - At the start of a job search session
    """
    from datetime import date
    core = _boot(project_path)
    root = core.config.data_path

    active_dir = root / "applications" / "active"
    if not active_dir.exists():
        return json.dumps({"applications": [], "overdue": [], "due_today": [], "upcoming": []}, indent=2)

    today = date.today()
    overdue, due_today, upcoming = [], [], []

    for f in sorted(active_dir.glob("*.md"), key=lambda x: x.stat().st_mtime):
        meta = _parse_frontmatter(f.read_text(encoding="utf-8"))
        applied_str = meta.get("applied_date", "")
        followup_str = meta.get("follow_up_date", "")

        try:
            days_since = (today - date.fromisoformat(applied_str)).days if applied_str else None
        except ValueError:
            days_since = None

        try:
            followup_date = date.fromisoformat(followup_str) if followup_str else None
            days_until_followup = (followup_date - today).days if followup_date else None
        except ValueError:
            followup_date = None
            days_until_followup = None

        entry = {
            "job_id": f.stem,
            "title": meta.get("title"),
            "company": meta.get("company"),
            "applied_date": applied_str,
            "method": meta.get("method"),
            "follow_up_date": followup_str,
            "days_since_applied": days_since,
            "days_until_followup": days_until_followup,
        }

        if followup_date:
            if followup_date < today:
                overdue.append(entry)
            elif followup_date == today:
                due_today.append(entry)
            else:
                upcoming.append(entry)
        else:
            upcoming.append(entry)

    all_apps = overdue + due_today + upcoming
    return json.dumps({
        "applications": all_apps,
        "overdue": overdue,
        "due_today": due_today,
        "upcoming": upcoming,
        "summary": f"{len(overdue)} overdue, {len(due_today)} due today, {len(upcoming)} upcoming",
    }, indent=2)


# ---------------------------------------------------------------------------
# Strategy Module
# ---------------------------------------------------------------------------

@mcp.tool()
def jh_analyze_market_patterns(project_path: str = ".") -> str:
    """
    Find skill and type patterns across all whitelisted + digested jobs.

    Computes deterministically: skill frequencies, rate ranges, remote split,
    contract length distribution, resume group fit frequency.
    Returns a JSON payload — Claude writes the patterns doc to disk.

    Run on demand or after every 5 new whitelisted jobs.
    """
    core = _boot(project_path)
    root = core.config.data_path

    # Collect metadata from whitelisted + digested jobs
    jobs = []
    for subfolder in ("whitelisted", "digested"):
        folder = root / "jobs" / subfolder
        if not folder.exists():
            continue
        for f in folder.glob("*.md"):
            meta = _parse_frontmatter(f.read_text(encoding="utf-8"))
            if meta.get("type") == "list_item":
                continue
            jobs.append(meta)

    if not jobs:
        return "ERROR: No whitelisted or digested jobs found. Add and digest some jobs first."

    # Skill frequency
    skill_freq: dict[str, int] = {}
    nth_freq: dict[str, int] = {}
    for j in jobs:
        for s in (j.get("required_skills") or []):
            skill_freq[s] = skill_freq.get(s, 0) + 1
        for s in (j.get("nice_to_have_skills") or []):
            nth_freq[s] = nth_freq.get(s, 0) + 1

    top_required = sorted(skill_freq.items(), key=lambda x: x[1], reverse=True)[:20]
    top_nth = sorted(nth_freq.items(), key=lambda x: x[1], reverse=True)[:10]

    # Rate analysis
    rates = [_parse_rate(str(j.get("rate_stated") or "")) for j in jobs]
    rates = [r for r in rates if r is not None]
    rate_stats = {}
    if rates:
        rate_stats = {
            "min": round(min(rates), 0),
            "max": round(max(rates), 0),
            "median": round(sorted(rates)[len(rates) // 2], 0),
            "sample_size": len(rates),
        }

    # Remote policy split
    remote_counts: dict[str, int] = {}
    for j in jobs:
        rp = (j.get("remote_policy") or "unknown").lower()
        remote_counts[rp] = remote_counts.get(rp, 0) + 1

    # Contract length distribution
    duration_counts: dict[str, int] = {}
    for j in jobs:
        d = j.get("duration_months")
        if d:
            key = f"{d}mo"
            duration_counts[key] = duration_counts.get(key, 0) + 1

    # Group fit frequency
    group_counts: dict[str, int] = {}
    for j in jobs:
        for g in (j.get("group_fit") or []):
            group_counts[g] = group_counts.get(g, 0) + 1

    # Score distribution
    scored = [j for j in jobs if j.get("score") is not None]
    rec_counts: dict[str, int] = {}
    for j in scored:
        r = j.get("recommendation", "unknown")
        rec_counts[r] = rec_counts.get(r, 0) + 1

    patterns = {
        "total_jobs_analyzed": len(jobs),
        "top_required_skills": [{"skill": s, "count": c} for s, c in top_required],
        "top_nice_to_have_skills": [{"skill": s, "count": c} for s, c in top_nth],
        "rate_stats": rate_stats,
        "remote_policy_split": remote_counts,
        "duration_distribution": duration_counts,
        "group_fit_frequency": group_counts,
        "score_distribution": rec_counts,
    }

    output_path = root / "blueprints" / "strategy" / "market-patterns.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    return json.dumps({
        "action": "analyze_market_patterns",
        "patterns": patterns,
        "output_path": str(output_path),
        "instructions": (
            f"Write a market patterns analysis to output_path. Use the data in 'patterns'. "
            f"Structure:\n"
            f"# Market Patterns — {datetime.now().strftime('%Y-%m-%d')}\n\n"
            f"## Overview\n(1 paragraph: total jobs, overall picture, key takeaways)\n\n"
            f"## Top Required Skills\n(table or ranked list with counts. Group by category: "
            f"languages, frameworks, infrastructure, practices)\n\n"
            f"## Nice-to-Have Skills\n(ranked list)\n\n"
            f"## Rate Landscape\n(min/max/median, what the market is paying, "
            f"whether it aligns with target rate)\n\n"
            f"## Work Model Split\n(remote vs hybrid vs onsite breakdown with commentary)\n\n"
            f"## Contract Length Patterns\n(distribution, what's most common)\n\n"
            f"## Resume Group Demand\n(which groups are most in demand)\n\n"
            f"## Key Insights\n(3-5 bullet points of actionable observations)\n\n"
            f"Write to output_path, then call jh_generate_gap_analysis."
        ),
    }, indent=2)


@mcp.tool()
def jh_generate_gap_analysis(project_path: str = ".") -> str:
    """
    Map market skill demand against master truth to identify gaps.

    Reads whitelisted job skills + master truth. Splits into:
    - covered: skills the market wants that truth verifies
    - gaps: skills the market wants that are NOT in truth
    Gaps ranked by market frequency and weighted by recurrence.

    ALWAYS call jh_analyze_market_patterns before this.
    """
    core = _boot(project_path)
    root = core.config.data_path

    truth_file = root / "truth" / "master" / "truth.md"
    if not truth_file.exists():
        return "ERROR: master truth not found. Run jh_synthesize_truth first."
    truth_text = truth_file.read_text(encoding="utf-8").lower()

    # Collect all required skills from whitelisted + digested
    skill_freq: dict[str, int] = {}
    jobs_checked = 0
    for subfolder in ("whitelisted", "digested"):
        folder = root / "jobs" / subfolder
        if not folder.exists():
            continue
        for f in folder.glob("*.md"):
            meta = _parse_frontmatter(f.read_text(encoding="utf-8"))
            if meta.get("type") == "list_item":
                continue
            jobs_checked += 1
            for s in (meta.get("required_skills") or []):
                skill_freq[s] = skill_freq.get(s, 0) + 1
            for s in (meta.get("nice_to_have_skills") or []):
                skill_freq[s] = skill_freq.get(s, 0) + 0.5

    if not skill_freq:
        return "ERROR: No skills found. Digest some jobs first with jh_digest_job."

    # Split into covered vs gaps
    covered, gaps = [], []
    for skill, freq in sorted(skill_freq.items(), key=lambda x: x[1], reverse=True):
        words = re.sub(r'[^a-z0-9 ]', '', skill.lower()).split()
        in_truth = all(w in truth_text for w in words if len(w) > 2)
        entry = {"skill": skill, "frequency": round(freq, 1), "pct_of_jobs": round(freq / jobs_checked * 100, 0)}
        if in_truth:
            covered.append(entry)
        else:
            gaps.append(entry)

    gap_data = {
        "jobs_analyzed": jobs_checked,
        "total_skills_seen": len(skill_freq),
        "covered_count": len(covered),
        "gap_count": len(gaps),
        "top_gaps": gaps[:15],
        "top_covered": covered[:10],
    }

    output_path = root / "blueprints" / "strategy" / "gap-analysis.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    master_truth = truth_file.read_text(encoding="utf-8")

    return json.dumps({
        "action": "generate_gap_analysis",
        "gap_data": gap_data,
        "master_truth": master_truth,
        "output_path": str(output_path),
        "instructions": (
            f"Write a skill gap analysis to output_path. Use 'gap_data' and 'master_truth'.\n"
            f"Structure:\n"
            f"# Gap Analysis — {datetime.now().strftime('%Y-%m-%d')}\n\n"
            f"## Summary\n(1 paragraph: {jobs_checked} jobs analyzed, {len(covered)} skills covered, "
            f"{len(gaps)} gaps identified)\n\n"
            f"## Critical Gaps (High Frequency)\n"
            f"(Gaps appearing in >30% of jobs. For each: skill name, frequency, "
            f"honest assessment — is this a real gap or just missing from the truth doc? "
            f"If it IS in Mahdi's experience but not in truth, note that and flag for truth update.)\n\n"
            f"## Moderate Gaps\n(Gaps appearing in 10-30% of jobs)\n\n"
            f"## Low-Priority Gaps\n(<10% of jobs — likely niche)\n\n"
            f"## Strong Coverage\n(Top 10 skills Mahdi clearly covers — confidence builders)\n\n"
            f"## Recommended Actions\n"
            f"(For each critical gap: (1) Add to truth doc if already known, "
            f"(2) Build a proof project if genuinely missing, "
            f"(3) Skip if too niche. Be ruthless — not every gap needs to be closed.)\n\n"
            f"After writing, call jh_update_portfolio_roadmap."
        ),
    }, indent=2)


@mcp.tool()
def jh_update_portfolio_roadmap(project_path: str = ".") -> str:
    """
    Rewrite blueprints/strategy/portfolio-roadmap.md from gap analysis.

    Includes: specific gaps to close, effort estimates, suggested projects to build,
    prioritized by market signal not intuition.

    ALWAYS call jh_generate_gap_analysis before this.
    """
    core = _boot(project_path)
    root = core.config.data_path

    gap_file = root / "blueprints" / "strategy" / "gap-analysis.md"
    patterns_file = root / "blueprints" / "strategy" / "market-patterns.md"
    truth_file = root / "truth" / "master" / "truth.md"

    if not gap_file.exists():
        return "ERROR: No gap analysis found. Run jh_generate_gap_analysis first."

    gap_content = gap_file.read_text(encoding="utf-8")
    patterns_content = patterns_file.read_text(encoding="utf-8") if patterns_file.exists() else ""
    master_truth = truth_file.read_text(encoding="utf-8") if truth_file.exists() else ""

    rules_file = root / "rules" / "config.yaml"
    rules = yaml.safe_load(rules_file.read_text(encoding="utf-8")) if rules_file.exists() else {}
    avail = rules.get("availability", {})

    output_path = root / "blueprints" / "strategy" / "portfolio-roadmap.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    return json.dumps({
        "action": "update_portfolio_roadmap",
        "gap_analysis": gap_content,
        "market_patterns": patterns_content,
        "master_truth": master_truth,
        "availability": avail,
        "output_path": str(output_path),
        "instructions": (
            f"Write a prioritized portfolio enrichment roadmap to output_path.\n"
            f"Base it on gap_analysis and market_patterns. Use master_truth to understand what already exists.\n"
            f"Structure:\n"
            f"# Portfolio Roadmap — {datetime.now().strftime('%Y-%m-%d')}\n\n"
            f"## Current Position\n(2-3 sentences: strongest areas, most competitive group, "
            f"market fit score estimate)\n\n"
            f"## Priority 1 — Close These Gaps (High ROI)\n"
            f"For each critical gap that can be closed:\n"
            f"- **Skill**: what it is\n"
            f"- **Market signal**: how often it appears\n"
            f"- **Action**: add to truth OR build proof project\n"
            f"- **Project idea**: concrete 1-2 week project that demonstrates this\n"
            f"- **Effort**: estimated days\n\n"
            f"## Priority 2 — Quick Truth Updates\n"
            f"(Skills likely already known but not in truth.md — just needs a truth chip)\n\n"
            f"## Priority 3 — Skip (Not Worth It)\n"
            f"(Niche or low-frequency gaps — honest call on what NOT to chase)\n\n"
            f"## 30-Day Sprint Plan\n"
            f"(Concrete week-by-week plan to close Priority 1 gaps. "
            f"Realistic given contract ending {avail.get('current_contract_end', 'soon')})\n\n"
            f"## Success Metrics\n"
            f"(How to know when the roadmap is working: score distribution shift, "
            f"interview rate, group fit breadth)\n\n"
            f"Be opinionated. Skip vague advice. Every recommendation must be specific and actionable."
        ),
    }, indent=2)


@mcp.tool()
def jh_get_portfolio_roadmap(project_path: str = ".") -> str:
    """
    Return the current portfolio enrichment plan.
    """
    core = _boot(project_path)
    roadmap = core.blueprints_path / "strategy" / "portfolio-roadmap.md"
    if not roadmap.exists():
        return "No portfolio roadmap yet. Run jh_update_portfolio_roadmap after whitelisting 10+ jobs."
    return roadmap.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Chat / Queue tools
# ---------------------------------------------------------------------------

@mcp.tool()
def jh_chat_listen(project_path: str = ".") -> str:
    """
    Wait for the next message from the UI (blocks up to 30 seconds).

    ALWAYS call this tool when you are ready to receive a UI command.
    Returns the message JSON or NO_COMMAND if nothing arrived within the timeout.

    MESSAGE ROUTING by type field:
    - "chat"       → respond conversationally or run the appropriate jh_* tool
    - "batch"      → the user pasted a multi-job list; call jh_ingest_job_list(raw_text=text, source="paste")
    - "scan_email" → call jh_scan_email_jobs() to pull from Gmail
    - "intake"     → a job was auto-captured; call jh_digest_job(job_id=text)
    """
    core = _boot(project_path)
    session_id = _active_session_id(core)
    if not session_id:
        return "NO_COMMAND: no active session"
    msg = _chat_listen(session_id, timeout=30.0)
    if msg is None:
        return "NO_COMMAND"
    return json.dumps(msg, indent=2, ensure_ascii=False)


@mcp.tool()
def jh_chat_progress(text: str, project_path: str = ".") -> str:
    """
    Report a progress update to the UI during a long-running operation.
    Call after each significant step.
    ERROR POLICY: if this returns an error, stop and report to the user.
    """
    core = _boot(project_path)
    session_id = _active_session_id(core)
    if session_id:
        _chat_post(session_id, "progress", text)
    return f"Progress: {text}"


@mcp.tool()
def jh_chat_ask(question: str, project_path: str = ".") -> str:
    """
    Ask the user a question via the UI and pause execution.
    After calling this tool: STOP. Do not continue until the user answers.
    ERROR POLICY: if this returns an error, stop and report to the user.
    """
    core = _boot(project_path)
    session_id = _active_session_id(core)
    if session_id:
        _chat_post(session_id, "question", question)
    return "Question sent to UI. STOP here and wait for the user's answer."


@mcp.tool()
def jh_chat_done(text: str, project_path: str = ".") -> str:
    """
    Signal that the current command is complete.
    ALWAYS call this as the final step after any command finishes.
    Resets status to idle so the user can send the next message.
    ERROR POLICY: if this returns an error, stop and report to the user.
    """
    core = _boot(project_path)
    session_id = _active_session_id(core)
    if session_id:
        _chat_post(session_id, "done", text)
    return f"Done: {text}"


@mcp.tool()
def jh_chat_respond(text: str, project_path: str = ".") -> str:
    """
    Send a chat response to the UI.
    Use for conversational replies. After sending, call jh_chat_done.
    ERROR POLICY: if this returns an error, stop and report to the user.
    """
    core = _boot(project_path)
    session_id = _active_session_id(core)
    if session_id:
        _chat_post(session_id, "response", text)
    return "Response sent to UI."


@mcp.tool()
def jh_log_session(content: str, project_path: str = ".") -> str:
    """
    Append content to today's session log in truth/logs/sessions/.
    NEVER write session logs directly to files — always use this tool.

    Log format tags (use these for structured entries):
      new-truth:     a new fact added to master truth
      job-added:     a new job ingested
      decided:       a decision made during this session
      criteria-update: a change to scoring criteria or rules
    """
    core = _boot(project_path)
    today = datetime.now().strftime("%Y-%m-%d")
    log_dir = core.truth_path / "logs" / "sessions"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"jh_log_{today}.md"

    if log_file.exists():
        existing = log_file.read_text(encoding="utf-8")
        log_file.write_text(existing + "\n" + content, encoding="utf-8")
    else:
        log_file.write_text(content, encoding="utf-8")

    return f"Session log updated: {log_file}"


@mcp.tool()
def jh_scan_email_jobs(
    max_emails: int = 20,
    label_filter: str = "",
    project_path: str = "."
) -> str:
    """
    Scan Gmail for job alert emails and ingest each one as a batch.

    Searches for emails from LinkedIn, Indeed, Glassdoor, ZipRecruiter, and
    recruiter outreach. For each email found, extracts the job listings and
    calls jh_ingest_job_list to create a batch.

    WORKFLOW — after calling this tool:
    1. This returns a list of email subjects + bodies Claude should process.
    2. For each email that contains job listings, call jh_ingest_job_list(raw_text=<body>, source=<sender>).
    3. Then call jh_triage_job_list for each batch.
    4. Report a summary: N emails scanned, M batches created, total jobs found.

    REQUIRES: Gmail MCP tools to be authenticated (mcp__claude_ai_Gmail__*).
    If not authenticated, tell the user to run /mcp → claude.ai Gmail.

    max_emails: how many recent matching emails to scan (default 20)
    label_filter: optional Gmail label to restrict search (e.g. 'jobs', 'INBOX')
    """
    core = _boot(project_path)

    # Build the search query for job-related emails
    senders = [
        "jobalerts-noreply@linkedin.com",
        "jobs-listings@linkedin.com",
        "noreply@indeed.com",
        "alert@glassdoor.com",
        "noreply@ziprecruiter.com",
        "noreply@wellfound.com",
        "jobs@lever.co",
    ]
    sender_query = " OR ".join(f"from:{s}" for s in senders)
    subject_keywords = "subject:(job OR engineer OR developer OR opportunity OR role OR hiring OR position)"
    query = f"({sender_query}) OR {subject_keywords}"
    if label_filter:
        query = f"label:{label_filter} ({query})"

    # Load existing batch dates to avoid re-ingesting the same email
    batches_dir = core.config.data_path / "jobs" / "batches"
    existing_subjects: set[str] = set()
    if batches_dir.exists():
        for bf in batches_dir.glob("*.md"):
            try:
                meta = yaml.safe_load(bf.read_text(encoding="utf-8").split("---")[1])
                if meta and meta.get("email_subject"):
                    existing_subjects.add(meta["email_subject"])
            except Exception:
                pass

    return json.dumps({
        "action": "scan_email_jobs",
        "gmail_query": query,
        "max_emails": max_emails,
        "existing_subjects": list(existing_subjects),
        "instructions": (
            "Use Gmail MCP tools to search for emails matching gmail_query.\n"
            "For each email returned (up to max_emails):\n"
            "  1. Skip if subject is in existing_subjects (already ingested).\n"
            "  2. Read the email body.\n"
            "  3. Check if it contains job listings (title + company + location patterns).\n"
            "     If it's a recruiter outreach for a single role, treat as a single-job batch.\n"
            "  4. Call jh_ingest_job_list(raw_text=<body>, source=<sender_domain>).\n"
            "     Set source to the sending domain, e.g. 'linkedin', 'indeed', 'recruiter'.\n"
            "  5. Store the email subject in the batch frontmatter as email_subject so we\n"
            "     can skip it next time. Write it directly to the batch .md file frontmatter.\n"
            "  6. After all items in a batch are ingested, call jh_triage_job_list.\n"
            "After all emails: call jh_chat_respond with a summary:\n"
            "  '📧 Scanned N emails → M batches, X jobs total. [pursue/research/watch/pass counts]'"
        ),
    }, indent=2)


if __name__ == "__main__":
    mcp.run()
