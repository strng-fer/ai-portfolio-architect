#!/usr/bin/env python3
"""Local dashboard for this project's agent workflow.

Scope: sessions whose directory is this repository, plus the portfolio
pipeline artifacts (job data, blueprints, gates, PDFs, tracker).
Reads ~/.local/share/opencode/opencode.db read-only. Stdlib only.
"""
from __future__ import annotations

import ast
import csv
import json
import os
import re
import sqlite3
import sys
import webbrowser
from collections import Counter, defaultdict
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
STATIC = ROOT / "static"
DEFAULT_DB = Path(
    os.environ.get("OPENCODE_DB")
    or Path.home() / ".local" / "share" / "opencode" / "opencode.db"
)
PORT = int(os.environ.get("DASHBOARD_PORT", "8770"))
HOST = os.environ.get("DASHBOARD_HOST", "127.0.0.1")

BUDGETS = {
    "00_job_analysis.md": 450,
    "01_project_ideation.md": 550,
    "02_system_blueprint.md": 1500,
    "03_references_study.md": 400,
    "04_review_report.md": 350,
    "05_agent_prompts.md": 900,
}

MIME = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
}


def norm(path):
    return str(path or "").replace("\\", "/").rstrip("/").lower()


PROJECT_KEY = norm(PROJECT)


def in_scope(directory, scope_all=False):
    if scope_all:
        return True
    return norm(directory) == PROJECT_KEY


def as_dict(raw):
    if isinstance(raw, dict):
        return raw
    if not raw:
        return {}
    try:
        value = json.loads(raw)
        if isinstance(value, dict):
            return value
    except (ValueError, TypeError):
        pass
    try:
        value = ast.literal_eval(raw)
        if isinstance(value, dict):
            return value
    except (ValueError, SyntaxError, TypeError):
        pass
    return {}


def model_label(raw):
    data = as_dict(raw)
    mid = data.get("id") or "unknown"
    provider = data.get("providerID") or ""
    return f"{provider}/{mid}" if provider else mid


def connect(db_path: Path):
    if not db_path.exists():
        raise FileNotFoundError(f"database not found: {db_path}")
    con = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True, timeout=5.0)
    con.row_factory = sqlite3.Row
    return con


def collect(db_path: Path, scope_all=False):
    con = connect(db_path)
    try:
        session_rows = con.execute(
            "SELECT id, parent_id, title, agent, model, directory, cost,"
            " tokens_input, tokens_output, tokens_reasoning,"
            " tokens_cache_read, tokens_cache_write,"
            " time_created, time_updated FROM session_v2"
        ).fetchall()
        message_rows = con.execute(
            "SELECT session_id, type, time_created, data FROM session_message"
        ).fetchall()
    finally:
        con.close()

    sessions = {}
    for row in session_rows:
        if not in_scope(row["directory"], scope_all):
            continue
        sessions[row["id"]] = {
            "id": row["id"],
            "parent_id": row["parent_id"],
            "title": row["title"] or "(untitled)",
            "agent": row["agent"] or "-",
            "model": model_label(row["model"]),
            "directory": (row["directory"] or "-").replace("\\", "/"),
            "cost": float(row["cost"] or 0.0),
            "tokens": {
                "input": int(row["tokens_input"] or 0),
                "output": int(row["tokens_output"] or 0),
                "reasoning": int(row["tokens_reasoning"] or 0),
                "cache_read": int(row["tokens_cache_read"] or 0),
                "cache_write": int(row["tokens_cache_write"] or 0),
            },
            "created": int(row["time_created"] or 0),
            "updated": int(row["time_updated"] or 0),
            "tools": Counter(),
            "tool_errors": 0,
            "steps": [],
            "messages": 0,
        }

    daily = defaultdict(lambda: {"input": 0, "output": 0, "reasoning": 0, "cache_read": 0, "tools": 0})
    tool_stats = defaultdict(lambda: {"count": 0, "errors": 0, "durations": []})

    for row in message_rows:
        sess = sessions.get(row["session_id"])
        if sess is None or row["type"] != "assistant":
            continue
        ts = int(row["time_created"] or 0)
        day = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).astimezone().strftime("%Y-%m-%d")
        data = as_dict(row["data"])
        sess["messages"] += 1
        tokens = data.get("tokens") or {}
        daily[day]["input"] += int(tokens.get("input") or 0)
        daily[day]["output"] += int(tokens.get("output") or 0)
        daily[day]["reasoning"] += int(tokens.get("reasoning") or 0)
        daily[day]["cache_read"] += int(tokens.get("cacheRead") or 0)

        for part in data.get("content") or []:
            if not isinstance(part, dict) or part.get("type") != "tool":
                continue
            name = part.get("name") or "unknown"
            state = as_dict(part.get("state"))
            status = state.get("status") or "unknown"
            timing = as_dict(part.get("time"))
            start = timing.get("created") or timing.get("ran")
            end = timing.get("completed") or timing.get("end")
            duration = int(end - start) if start and end else None

            args = state.get("input") or {}
            hint = ""
            for key in ("command", "filePath", "path", "pattern", "query", "url", "description"):
                if isinstance(args.get(key), str):
                    hint = args[key].replace("\n", " ").strip()
                    break
            if not hint and isinstance(args, dict) and args:
                hint = f"{next(iter(args))}: {str(next(iter(args.values())))[:80]}"

            meta = state.get("metadata") or {}
            exit_code = meta.get("exit") if isinstance(meta, dict) else None
            failed = status == "error"
            nonzero = isinstance(exit_code, int) and exit_code != 0

            sess["tools"][name] += 1
            if failed:
                sess["tool_errors"] += 1
            stats = tool_stats[name]
            stats["count"] += 1
            if failed:
                stats["errors"] += 1
            if duration is not None:
                stats["durations"].append(duration)
            daily[day]["tools"] += 1
            sess["steps"].append(
                {
                    "ts": ts,
                    "tool": name,
                    "status": "error" if failed else status,
                    "nonzero_exit": nonzero,
                    "duration_ms": duration,
                    "hint": hint[:160],
                }
            )

    return sessions, daily, tool_stats


def pct(values, q):
    if not values:
        return None
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(round((len(ordered) - 1) * q)))]


def build_overview(db_path: Path, scope_all=False):
    sessions, daily, tool_stats = collect(db_path, scope_all)
    items = list(sessions.values())

    totals = {
        "sessions": len(items),
        "messages": sum(s["messages"] for s in items),
        "tool_calls": sum(sum(s["tools"].values()) for s in items),
        "tool_errors": sum(s["tool_errors"] for s in items),
        "cost": round(sum(s["cost"] for s in items), 6),
    }
    for key in ("input", "output", "reasoning", "cache_read", "cache_write"):
        totals[f"tokens_{key}"] = sum(s["tokens"][key] for s in items)
    totals["tokens_fresh"] = totals["tokens_input"] + totals["tokens_output"] + totals["tokens_reasoning"]

    cache_denom = totals["tokens_cache_read"] + totals["tokens_input"]
    now_ms = datetime.now(tz=timezone.utc).timestamp() * 1000

    day_series = []
    for day in sorted(daily)[-14:]:
        b = daily[day]
        day_series.append({"date": day, **b, "tokens": b["input"] + b["output"] + b["reasoning"]})

    tools = [
        {
            "name": name,
            "count": st["count"],
            "errors": st["errors"],
            "p50_ms": pct(st["durations"], 0.5),
            "p95_ms": pct(st["durations"], 0.95),
        }
        for name, st in sorted(tool_stats.items(), key=lambda kv: kv[1]["count"], reverse=True)
    ]

    current = max(items, key=lambda s: s["updated"], default=None)
    return {
        "generated_at": int(now_ms),
        "scope": {"all": scope_all, "project": str(PROJECT).replace("\\", "/"), "name": PROJECT.name},
        "totals": totals,
        "cache_hit_rate": round(totals["tokens_cache_read"] / cache_denom, 4) if cache_denom else 0.0,
        "active_24h": sum(1 for s in items if now_ms - s["updated"] < 86_400_000),
        "daily": day_series,
        "tools": tools,
        "current": (
            {"id": current["id"], "title": current["title"], "updated": current["updated"]} if current else None
        ),
    }


def session_payload(sess):
    return {
        "id": sess["id"],
        "title": sess["title"],
        "agent": sess["agent"],
        "model": sess["model"],
        "directory": sess["directory"],
        "cost": round(sess["cost"], 6),
        "tokens": sess["tokens"],
        "created": sess["created"],
        "updated": sess["updated"],
        "tool_calls": sum(sess["tools"].values()),
        "tool_errors": sess["tool_errors"],
        "messages": sess["messages"],
        "sub": bool(sess["parent_id"]),
        "tools": dict(sess["tools"]),
    }


def build_sessions(db_path: Path, limit=200, scope_all=False):
    sessions, _, _ = collect(db_path, scope_all)
    items = sorted(sessions.values(), key=lambda s: s["updated"], reverse=True)[:limit]
    return [session_payload(s) for s in items]


def build_session(db_path: Path, session_id: str, scope_all=False):
    sessions, _, _ = collect(db_path, scope_all)
    sess = sessions.get(session_id)
    if sess is None:
        return None
    data = session_payload(sess)
    data["steps"] = sorted(sess["steps"], key=lambda s: s["ts"])[-250:]
    return data


def word_count(path: Path):
    try:
        return len(path.read_text(encoding="utf-8").split())
    except OSError:
        return 0


def first_heading(path: Path):
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    except OSError:
        pass
    return ""


def mechanism_history():
    path = PROJECT / "portfolios" / "_history.json"
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    out = {}
    for proj in data.get("projects") or []:
        if isinstance(proj, dict) and proj.get("slug"):
            out[proj["slug"]] = proj
    return out


def tracker_rows():
    path = PROJECT / "portfolio_tracker.csv"
    if not path.is_file():
        return []
    try:
        with path.open(encoding="utf-8", newline="") as fh:
            return [row for row in csv.DictReader(fh)]
    except OSError:
        return []


def portfolio_state(folder: Path, history, tracker):
    docs = {}
    over = []
    for name, budget in BUDGETS.items():
        path = folder / name
        if path.is_file():
            count = word_count(path)
            docs[name] = {"words": count, "budget": budget, "over": count > budget}
            if count > budget:
                over.append(f"{name} +{count - budget}w")
    required = ["00_job_analysis.md", "01_project_ideation.md", "02_system_blueprint.md", "03_references_study.md"]
    missing = [n for n in required if n not in docs]

    diagrams = sorted(p.name for p in (folder / "diagrams").glob("*.png")) if (folder / "diagrams").is_dir() else []
    mmd = sorted(p.name for p in (folder / "diagrams").glob("*.mmd")) if (folder / "diagrams").is_dir() else []
    pdf = folder / "Blueprint_Final.pdf"
    pdf_size = pdf.stat().st_size if pdf.is_file() else 0

    blueprint = folder / "02_system_blueprint.md"
    metric_rows = 0
    if blueprint.is_file():
        text = blueprint.read_text(encoding="utf-8")
        block = re.search(r"## 9\. Metrics.*?(?=\n## |\Z)", text, re.S)
        if block:
            metric_rows = sum(1 for ln in block.group(0).splitlines() if ln.strip().startswith("|")) - 2

    entry = history.get(folder.name) or {}
    tracked = next((t for t in tracker if t.get("output_folder", "").endswith(folder.name)), None)

    if pdf_size:
        status = "READY"
    elif docs:
        status = "MARKDOWN"
    else:
        status = "DRAFT"

    return {
        "slug": folder.name,
        "title": first_heading(blueprint) or folder.name,
        "mechanism": entry.get("mechanism") or "-",
        "hours": entry.get("hours"),
        "status": status,
        "docs": docs,
        "missing": missing,
        "over_budget": over,
        "diagrams": diagrams,
        "mmd": mmd,
        "pdf_bytes": pdf_size,
        "prompts": (folder / "05_agent_prompts.md").is_file(),
        "metrics": metric_rows,
        "updated": int(max((p.stat().st_mtime for p in folder.rglob("*") if p.is_file()), default=0) * 1000),
        "tracker": (tracked or {}).get("status") or "-",
        "tracker_date": (tracked or {}).get("date") or "",
        "tracker_title": (tracked or {}).get("project_title") or "",
    }


def build_workflow():
    scraper = PROJECT / "job_scraper"
    portfolios_dir = PROJECT / "portfolios"
    history = mechanism_history()
    tracker = tracker_rows()

    jobs = 0
    scrape_file = scraper / "latest_scrape.json"
    if scrape_file.is_file():
        try:
            raw = json.loads(scrape_file.read_text(encoding="utf-8"))
            jobs = len(raw) if isinstance(raw, list) else len(raw.get("jobs") or raw.get("results") or [])
        except (OSError, ValueError):
            jobs = 0

    portfolios = []
    if portfolios_dir.is_dir():
        for folder in sorted(portfolios_dir.iterdir()):
            if folder.is_dir() and not folder.name.startswith("_"):
                portfolios.append(portfolio_state(folder, history, tracker))

    ready = [p for p in portfolios if p["status"] == "READY"]
    gated = [p for p in portfolios if p["status"] in ("READY", "MARKDOWN") and not p["missing"] and not p["over_budget"]]

    stages = [
        {
            "id": "scrape",
            "label": "Scrape & rank",
            "state": "done" if scrape_file.is_file() else "pending",
            "detail": f"{jobs} jobs cached" if jobs else "no scrape yet",
        },
        {
            "id": "draft",
            "label": "Blueprint draft",
            "state": "done" if portfolios else "pending",
            "detail": f"{len(portfolios)} blueprint folder(s)",
        },
        {
            "id": "gate",
            "label": "Validation gate",
            "state": "done" if gated else ("warn" if portfolios else "pending"),
            "detail": f"{len(gated)}/{len(portfolios)} pass budgets" if portfolios else "not run",
        },
        {
            "id": "render",
            "label": "Render & PDF",
            "state": "done" if ready else ("warn" if portfolios else "pending"),
            "detail": f"{len(ready)}/{len(portfolios)} PDFs" if portfolios else "not run",
        },
        {
            "id": "track",
            "label": "Tracker & history",
            "state": "done" if tracker else "pending",
            "detail": f"{len(tracker)} tracker row(s)",
        },
    ]

    return {
        "project": {"name": PROJECT.name, "path": str(PROJECT).replace("\\", "/")},
        "stages": stages,
        "portfolios": sorted(portfolios, key=lambda p: p["updated"], reverse=True),
        "counts": {
            "portfolios": len(portfolios),
            "ready": len(ready),
            "tracker": len(tracker),
            "jobs": jobs,
        },
        "tracker": tracker,
    }


class Handler(BaseHTTPRequestHandler):
    db_path = DEFAULT_DB

    def log_message(self, fmt, *args):
        return

    def _send(self, status, body, content_type):
        payload = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def _json(self, status, obj):
        self._send(status, json.dumps(obj, ensure_ascii=False), "application/json; charset=utf-8")

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        scope_all = query.get("all", ["0"])[0] in ("1", "true")

        try:
            if path == "/api/overview":
                return self._json(200, build_overview(self.db_path, scope_all))
            if path == "/api/sessions":
                limit = int(query.get("limit", ["200"])[0])
                return self._json(200, build_sessions(self.db_path, limit, scope_all))
            if path == "/api/session":
                sid = query.get("id", [""])[0]
                data = build_session(self.db_path, sid, scope_all)
                if data is None:
                    return self._json(404, {"error": "session not found in this project"})
                return self._json(200, data)
            if path == "/api/workflow":
                return self._json(200, build_workflow())
            if path == "/api/health":
                return self._json(
                    200,
                    {"ok": True, "db": str(self.db_path), "exists": self.db_path.exists(), "project": str(PROJECT)},
                )
        except FileNotFoundError as exc:
            return self._json(503, {"error": str(exc)})
        except Exception as exc:
            return self._json(500, {"error": f"{type(exc).__name__}: {exc}"})

        if path == "/":
            path = "/index.html"
        target = (STATIC / path.lstrip("/")).resolve()
        if STATIC not in target.parents and target != STATIC:
            return self._send(403, "forbidden", "text/plain; charset=utf-8")
        if not target.is_file():
            return self._send(404, "not found", "text/plain; charset=utf-8")
        self._send(200, target.read_bytes(), MIME.get(target.suffix, "application/octet-stream"))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    db_path = Path(args[0]).expanduser() if args else DEFAULT_DB
    if not db_path.exists():
        print(f"[X] database not found: {db_path}")
        print("    set OPENCODE_DB or pass a path: python3 dashboard/server.py <db>")
        return 1

    Handler.db_path = db_path
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}/"
    print(f"[+] project   {PROJECT}")
    print(f"[+] database  {db_path}")
    print(f"[+] dashboard {url}")
    print("[+] ctrl+c to stop")
    if "--no-open" not in sys.argv:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[+] stopped")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
