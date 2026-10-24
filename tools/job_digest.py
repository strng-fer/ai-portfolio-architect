#!/usr/bin/env python3
"""Hemat-token summary of scraped jobs.

Run before reading latest_scrape.json / ranked_jobs.json. The agent reads this
compact output instead of the raw JSON.

Usage:
  python3 tools/job_digest.py list                 # top 10 jobs, one line each
  python3 tools/job_digest.py detail <id>          # one job, description truncated
  python3 tools/job_digest.py detail <id> --full   # full description (only if needed)

Exit codes:
  0 = output produced
  1 = no cache or unknown id
"""
import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
CANDIDATES = [
    ROOT / "job_scraper" / "ranked_jobs.json",
    ROOT / "job_scraper" / "latest_scrape.json",
]

TECH_HINTS = [
    "python", "go", "golang", "java", "typescript", "javascript", "rust", "sql",
    "fastapi", "django", "flask", "spring", "node", "react", "pytorch", "tensorflow",
    "sklearn", "postgres", "postgresql", "mysql", "mongo", "redis", "kafka", "rabbitmq",
    "docker", "kubernetes", "aws", "gcp", "azure", "airflow", "spark", "mlflow",
    "llm", "rag", "langchain", "vector", "pgvector", "qdrant", "opencv", "yolo",
    "pandas", "numpy", "tableau", "looker", "dbt", "snowflake", "bigquery",
]


def load():
    for path in CANDIDATES:
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"[!] Cache is corrupt ({path.name}): {e}. Re-run /scrape.", file=sys.stderr)
            sys.exit(1)
        if isinstance(data, dict):
            data = data.get("jobs", data.get("results", []))
        if data:
            return data, path
    print("[!] No job_scraper/*.json found. Run /scrape first.", file=sys.stderr)
    sys.exit(1)


def short(text, limit):
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    if not text or text.lower() == "none":
        return "-"
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "..."


def score(job):
    for key in ("score", "leverage_score", "portfolio_leverage_score"):
        val = job.get(key)
        if isinstance(val, (int, float)):
            return val
    return None


def stack(text):
    low = str(text or "").lower()
    found = [t for t in TECH_HINTS if re.search(rf"\b{re.escape(t)}\b", low)]
    return ", ".join(found[:6]) or "-"


def cmd_list(top):
    jobs, path = load()
    print(f"# source: {path.name} | total {len(jobs)} | showing {min(top, len(jobs))}")
    for job in jobs[:top]:
        s = score(job)
        print(
            f"{job.get('id', '-')} | {short(job.get('company'), 24)} | "
            f"{short(job.get('title'), 40)} | {short(job.get('location'), 22)} | "
            f"score={s if s is not None else '-'} | stack: {stack(job.get('description'))}"
        )


def cmd_detail(job_id, full):
    jobs, _ = load()
    for job in jobs:
        if str(job.get("id")) == str(job_id):
            desc = str(job.get("description") or "")
            print(f"id: {job.get('id')}")
            print(f"company: {job.get('company') or '-'}")
            print(f"role: {job.get('title') or '-'}")
            print(f"location: {job.get('location') or '-'}")
            print(f"url: {job.get('job_url') or '-'}")
            print(f"detected stack: {stack(desc)}")
            print(f"description length: {len(desc)} chars")
            print("--- description ---")
            if not desc.strip():
                print("(empty description; use the url with tools/fetch_page.py)")
                return
            print(desc if full else short(desc, 1800))
            if not full and len(desc) > 1800:
                print("--- truncated: use --full only if truly needed ---")
            return
    print(f"[!] id {job_id} not found", file=sys.stderr)
    sys.exit(1)


def main():
    ap = argparse.ArgumentParser(add_help=True)
    sub = ap.add_subparsers(dest="cmd")
    p_list = sub.add_parser("list")
    p_list.add_argument("--top", type=int, default=10)
    p_detail = sub.add_parser("detail")
    p_detail.add_argument("id")
    p_detail.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.cmd == "detail":
        cmd_detail(args.id, args.full)
    else:
        cmd_list(getattr(args, "top", 10))


if __name__ == "__main__":
    main()
