#!/usr/bin/env python3
"""Ringkasan referensi GitHub & ArXiv hemat token.

Agent tidak perlu membaca github_refs.json / arxiv_refs.json secara utuh.

Usage:
  python3 tools/ref_digest.py            # 5 repo + 3 paper teratas
  python3 tools/ref_digest.py --repo 3 --paper 2
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

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
        return []
    if isinstance(data, dict):
        data = data.get(kind + "s", data.get("results", []))
    return data or []


def short(text, limit):
    text = re.sub(r"\s+", " ", (text or "")).strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=int, default=5)
    ap.add_argument("--paper", type=int, default=3)
    args = ap.parse_args()

    repos = sorted(load("repo"), key=lambda r: r.get("stars", 0), reverse=True)
    papers = load("paper")
    if not repos and not papers:
        print("[!] Belum ada referensi. Jalankan mine_github.py dan mine_arxiv.py dulu.", file=sys.stderr)
        sys.exit(1)

    print(f"# repo: {len(repos)} | paper: {len(papers)}")
    print("## GitHub (urut bintang)")
    for r in repos[: args.repo]:
        print(f"- {r.get('full_name')} | stars {r.get('stars', 0)} | {r.get('language') or '-'} | {r.get('html_url')}")
        print(f"  {short(r.get('description'), 110)}")

    print("## ArXiv")
    for p in papers[: args.paper]:
        link = p.get("url") or p.get("pdf_url") or p.get("entry_id") or p.get("id") or "-"
        print(f"- {short(p.get('title'), 100)} ({short(p.get('published'), 10)}) {link}")
        print(f"  {short(p.get('summary'), 160)}")


if __name__ == "__main__":
    main()
