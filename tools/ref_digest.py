#!/usr/bin/env python3
"""Hemat-token summary of GitHub and ArXiv references.

Ranks repositories by query-term match first, stars second, so the agent cites
relevant references instead of merely popular ones.

Usage:
  python3 tools/ref_digest.py                      # 5 repos + 3 papers
  python3 tools/ref_digest.py --repo 3 --paper 2
  python3 tools/ref_digest.py --query "hybrid retrieval" --min 3

Exit codes:
  0 = enough references (>= --min repos, >= --min_paper papers)
  1 = not enough references or no cache
"""
import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
FILES = {
    "repo": ROOT / "job_scraper" / "github_refs.json",
    "paper": ROOT / "job_scraper" / "arxiv_refs.json",
}


def load(kind):
    path = FILES[kind]
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"[!] {path.name} is corrupt; re-run the miner.", file=sys.stderr)
        return []
    if isinstance(data, dict):
        data = data.get(kind + "s", data.get("results", []))
    if not isinstance(data, list):
        return []
    return [d for d in data if isinstance(d, dict) and not d.get("error")]


def short(text, limit):
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "..."


def relevance(item, terms):
    if not terms:
        return 0
    blob = " ".join(
        str(item.get(k, "")) for k in ("full_name", "description", "title", "summary", "language")
    ).lower()
    return sum(1 for t in terms if t in blob)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=int, default=5)
    ap.add_argument("--paper", type=int, default=3)
    ap.add_argument("--query", default="", help="keywords used to rank by relevance")
    ap.add_argument("--min", dest="min_repo", type=int, default=3)
    ap.add_argument("--min-paper", type=int, default=2)
    args = ap.parse_args()

    terms = [t for t in re.split(r"[^a-z0-9+#]+", args.query.lower()) if len(t) > 2]
    repos = load("repo")
    papers = load("paper")

    if not repos and not papers:
        print("[!] No references yet. Run mine_github.py and mine_arxiv.py first.", file=sys.stderr)
        sys.exit(1)

    repos.sort(key=lambda r: (relevance(r, terms), r.get("stars", 0) or 0), reverse=True)

    print(f"# repo: {len(repos)} | paper: {len(papers)} | ranked by {'relevance' if terms else 'stars'}")
    print("## GitHub")
    for r in repos[: args.repo]:
        print(f"- {r.get('full_name')} | stars {r.get('stars', 0)} | {r.get('language') or '-'} | {r.get('html_url')}")
        print(f"  {short(r.get('description'), 110)}")

    print("## ArXiv")
    for p in papers[: args.paper]:
        link = p.get("url") or p.get("pdf_url") or p.get("entry_id") or p.get("id") or "-"
        print(f"- {short(p.get('title'), 100)} ({short(p.get('published'), 10)}) {link}")
        print(f"  {short(p.get('summary'), 160)}")

    repo_ok = len(repos) >= args.min_repo
    paper_ok = len(papers) >= args.min_paper
    if not repo_ok:
        print(f"[!] Only {len(repos)} repos; need {args.min_repo}. Re-run the miner with broader keywords.", file=sys.stderr)
    if not paper_ok:
        print(f"[!] Only {len(papers)} papers; need {args.min_paper}. Re-run the miner with broader keywords.", file=sys.stderr)
    sys.exit(0 if repo_ok and paper_ok else 1)


if __name__ == "__main__":
    main()
