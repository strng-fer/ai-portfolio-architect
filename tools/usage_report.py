#!/usr/bin/env python3
"""Turn the product's own usage log into the evidence table the README quotes.

Product mode is not proven by a deployment; it is proven by people using it. The
app writes an append-only log (default `usage.json` in this folder); this script
reports users, completed actions, completion rate, and time to first value.

Accepted shapes (first match wins):
  1. JSON array of events
  2. JSON object with "events" or "sessions"
  3. JSONL, one event per line

Event fields (missing fields are tolerated, blanks are reported):
  user    - anonymous id, required for the user count
  action  - "view" | "complete" | "error" (free text accepted)
  ts      - epoch milliseconds, epoch seconds, or ISO-8601
  ms      - duration in milliseconds since the user's first action in the session
  error   - error code or message, for the failure-state metric

Usage:
  python3 tools/usage_report.py portfolios/<slug>
  python3 tools/usage_report.py usage.json --min-users 5 --min-sessions 20
  python3 tools/usage_report.py portfolios/<slug> --json

Exit codes:
  0 = adoption bar met
  1 = adoption bar not met
  2 = log not found
"""
import argparse
import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CANDIDATES = ("usage.json", "usage.jsonl", "data/usage.json", "logs/usage.json")


def load_events(path: Path):
    raw = path.read_text(encoding="utf-8", errors="replace").strip()
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except ValueError:
        events = []
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except ValueError:
                continue
            if isinstance(item, dict):
                events.append(item)
        return events

    if isinstance(data, list):
        return [e for e in data if isinstance(e, dict)]
    if isinstance(data, dict):
        for key in ("events", "sessions", "data"):
            if isinstance(data.get(key), list):
                return [e for e in data[key] if isinstance(e, dict)]
        return [data]
    return []


def to_ms(value):
    if isinstance(value, (int, float)):
        return int(value * 1000) if value < 1e11 else int(value)
    if isinstance(value, str):
        try:
            return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp() * 1000)
        except (ValueError, TypeError):
            return None
    return None


def is_complete(event):
    blob = f"{event.get('action', '')} {event.get('event', '')} {event.get('type', '')}".lower()
    return any(k in blob for k in ("complete", "success", "done", "result", "answer"))


def is_view(event):
    blob = f"{event.get('action', '')} {event.get('event', '')} {event.get('type', '')}".lower()
    return any(k in blob for k in ("view", "load", "start", "open", "ask", "upload", "submit"))


def main():
    parser = argparse.ArgumentParser(description="Report product adoption from the app's usage log")
    parser.add_argument("target", help="Portfolio folder or path to the usage log")
    parser.add_argument("--min-users", type=int, default=5)
    parser.add_argument("--min-sessions", type=int, default=20)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    target = Path(args.target)
    log = target if target.is_file() else next((target / c for c in CANDIDATES if (target / c).is_file()), None)
    if log is None:
        print(f"[X] ERROR no usage log found in {target}")
        print(f"[i] expected one of: {', '.join(CANDIDATES)}")
        return 2

    events = load_events(log)
    if not events:
        print(f"[X] {log} is empty; no user has reached the product yet")
        return 1

    users = {str(e.get("user") or e.get("uid") or e.get("session")) for e in events if e.get("user") or e.get("uid") or e.get("session")}
    users.discard("None")

    completed = [e for e in events if is_complete(e)]
    completing_users = {
        str(e.get("user") or e.get("uid") or e.get("session"))
        for e in completed
        if e.get("user") or e.get("uid") or e.get("session")
    }

    sessions = {}
    for e in events:
        key = str(e.get("session") or e.get("user") or e.get("uid") or "")
        if not key:
            continue
        ts = to_ms(e.get("ts") or e.get("timestamp") or e.get("time"))
        if ts is not None:
            sessions.setdefault(key, []).append(ts)

    durations = [
        max(ms) - min(ms) for ms in sessions.values() if len(ms) > 1
    ]
    views = sum(1 for e in events if is_view(e))
    errors = sum(1 for e in events if e.get("error") or "error" in str(e.get("action", "")).lower())

    completion_rate = (len(completed) / views) if views else 0.0
    ttfv = statistics.median(durations) / 1000 if durations else None

    passed = len(completing_users) >= args.min_users and len(completed) >= args.min_sessions

    report = {
        "log": str(log),
        "events": len(events),
        "users": len(users),
        "completing_users": len(completing_users),
        "sessions": len(sessions),
        "completions": len(completed),
        "completion_rate": round(completion_rate, 3),
        "median_time_to_first_value_s": round(ttfv, 1) if ttfv is not None else None,
        "errors_seen": errors,
        "bar": {"min_users": args.min_users, "min_sessions": args.min_sessions, "passed": passed},
    }

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0 if passed else 1

    print(f"log: {log}")
    print("metric | value | bar")
    print(f"external users | {len(completing_users)} | >= {args.min_users}")
    print(f"completed sessions | {len(completed)} | >= {args.min_sessions}")
    print(f"completion rate | {completion_rate:.0%} | reported, not targeted")
    print(f"median time to first value | {report['median_time_to_first_value_s'] or '-'} s | <= 60 s")
    print(f"errors seen | {errors} | reported, not hidden")
    print(f"[=] {'PASS' if passed else 'FAIL'} adoption bar")
    if not passed:
        if len(completing_users) < args.min_users:
            print(f"[!] need {args.min_users - len(completing_users)} more user(s) who complete the primary action")
        if len(completed) < args.min_sessions:
            print(f"[!] need {args.min_sessions - len(completed)} more completed session(s)")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
