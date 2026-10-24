#!/usr/bin/env python3
"""Search job portals for portfolio ideation.

Never destroys an existing cache on failure: writes to a temp file first and only
replaces job_scraper/latest_scrape.json when at least one posting was returned.

Boards:
  jobspy native : linkedin, indeed, google, glassdoor, zip_recruiter,
                  bayt, naukri, bdjobs, hellowork
  direct API    : jobstreet, kalibrr   (see boards.py)
  unsupported   : jobindo, glints      (reported, never faked)

Each board runs in isolation, so one 429 or timeout never kills the batch.

LinkedIn rate-limits most consumer IPs (HTTP 429). Supply a proxy to use it:
  --proxies "http://user:pass@host:port"    or    JOBSPY_PROXIES

Exit codes:
  0 = saved at least one posting
  1 = no postings (existing cache is preserved)
  2 = missing dependency
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from boards import DIRECT_BOARDS, UNSUPPORTED_BOARDS
except ImportError:  # run from another cwd
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from boards import DIRECT_BOARDS, UNSUPPORTED_BOARDS

# Boards jobspy can scrape directly.
JOBSPY_SITES = {
    "linkedin",
    "indeed",
    "google",
    "glassdoor",
    "zip_recruiter",
    "bayt",
    "naukri",
    "bdjobs",
    "hellowork",
}

DEFAULT_SITES = "jobstreet,kalibrr,indeed,linkedin"

COUNTRY_HINTS = {
    "indonesia": "indonesia",
    "jakarta": "indonesia",
    "bandung": "indonesia",
    "surabaya": "indonesia",
    "yogyakarta": "indonesia",
    "semarang": "indonesia",
    "medan": "indonesia",
    "singapore": "singapore",
    "malaysia": "malaysia",
    "kuala lumpur": "malaysia",
    "usa": "usa",
    "united states": "usa",
}


def parse_sites(raw: str) -> tuple[list[str], list[str], list[str]]:
    """Split requested boards into jobspy sites, direct boards, unsupported."""
    requested = [s.strip().lower() for s in raw.split(",") if s.strip()]
    jobspy, direct, blocked, unknown = [], [], [], []
    for s in requested:
        if s in JOBSPY_SITES:
            jobspy.append(s)
        elif s in DIRECT_BOARDS:
            direct.append(s)
        elif s in UNSUPPORTED_BOARDS:
            blocked.append(s)
        else:
            unknown.append(s)
    if unknown:
        known = sorted(JOBSPY_SITES | set(DIRECT_BOARDS) | set(UNSUPPORTED_BOARDS))
        print(f"[i] Unknown board(s) skipped: {', '.join(unknown)}")
        print(f"[i] Known boards: {', '.join(known)}")
    for b in blocked:
        print(f"[i] {b}: {UNSUPPORTED_BOARDS[b]} - skipped")
    return jobspy, direct, blocked


def parse_proxies(raw: str | None) -> list[str] | None:
    if not raw:
        return None
    items = [p.strip() for p in raw.split(",") if p.strip()]
    return items or None


def country_for(location: str) -> str:
    loc = (location or "").lower()
    for hint, country in COUNTRY_HINTS.items():
        if hint in loc:
            return country
    return "usa"


def to_records(jobs, source: str) -> list[dict]:
    records = []
    if jobs is None or not hasattr(jobs, "iterrows"):
        return records
    for _, row in jobs.iterrows():
        title = str(row.get("title", "") or "").strip()
        if not title or title.lower() == "nan":
            continue
        records.append(
            {
                "title": title,
                "company": str(row.get("company", "") or "").strip(),
                "location": str(row.get("location", "") or "").strip(),
                "job_url": str(row.get("job_url", "") or "").strip(),
                "description": str(row.get("description", "") or "")[:4000],
                "source": source,
            }
        )
    return records


def scrape_with_jobspy(
    query: str,
    location: str,
    results: int,
    sites_raw: str,
    proxies: list[str] | None,
):
    try:
        from jobspy import scrape_jobs
    except ImportError:
        print("[!] python-jobspy is not installed. Run: pip install python-jobspy")
        return None

    jobspy_sites, direct_sites, _ = parse_sites(sites_raw)
    if not jobspy_sites and not direct_sites:
        print("[!] No usable board requested.")
        return []

    country = country_for(location)
    per_site = max(5, results)
    collected: list[dict] = []
    failures: list[str] = []

    for board in direct_sites:
        try:
            got = DIRECT_BOARDS[board](query, location, per_site)
            collected.extend(got)
            print(f"[+] {board}: {len(got)} posting(s)")
        except Exception as e:
            failures.append(board)
            print(f"[!] {board}: {str(e).splitlines()[0][:120]}")

    for site in jobspy_sites:
        kwargs = dict(
            site_name=[site],
            search_term=query,
            location=location,
            results_wanted=per_site,
            hours_old=336,
            country_indeed=country,
            verbose=0,
        )
        if site == "google":
            kwargs["google_search_term"] = f"{query} jobs {location}"
        if proxies:
            kwargs["proxies"] = proxies
        try:
            jobs = scrape_jobs(**kwargs)
            got = to_records(jobs, site)
            collected.extend(got)
            print(f"[+] {site}: {len(got)} posting(s)")
        except Exception as e:
            failures.append(site)
            print(f"[!] {site}: {str(e).splitlines()[0][:120]}")

    if failures:
        print(f"[i] Failed board(s): {', '.join(failures)}")
        if "linkedin" in failures and not proxies:
            print("[i] LinkedIn blocks most consumer IPs (429). Set JOBSPY_PROXIES or pass --proxies.")

    return collected


def dedupe(records: list[dict]) -> list[dict]:
    seen = set()
    out = []
    for r in records:
        key = (
            re.sub(r"\W+", "", (r.get("title") or "").lower())[:60],
            re.sub(r"\W+", "", (r.get("company") or "").lower())[:40],
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def round_robin(records: list[dict], total: int) -> list[dict]:
    """Interleave boards so a global cap never truncates the last board away."""
    buckets: dict[str, list[dict]] = {}
    for r in records:
        buckets.setdefault(r.get("source", "unknown"), []).append(r)
    out: list[dict] = []
    while len(out) < total and any(buckets.values()):
        for source in list(buckets):
            if not buckets[source]:
                continue
            out.append(buckets[source].pop(0))
            if len(out) >= total:
                break
    return out


def main():
    parser = argparse.ArgumentParser(description="Search job portals for portfolio ideation")
    parser.add_argument("--query", required=True, help="e.g. 'AI Engineer'")
    parser.add_argument("--location", default="Indonesia", help="Search location")
    parser.add_argument("--limit", type=int, default=15, help="Target postings per board")
    parser.add_argument(
        "--sites",
        default=os.environ.get("JOBSPY_SITES", DEFAULT_SITES),
        help=f"Comma-separated boards. Default: {DEFAULT_SITES}",
    )
    parser.add_argument(
        "--proxies",
        default=os.environ.get("JOBSPY_PROXIES"),
        help="Comma-separated proxy URLs. Env: JOBSPY_PROXIES",
    )
    args = parser.parse_args()

    out_file = Path("job_scraper/latest_scrape.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)

    records = scrape_with_jobspy(
        args.query,
        args.location,
        args.limit,
        args.sites,
        parse_proxies(args.proxies),
    )
    if records is None:
        _keep_cache(out_file, "missing dependency")
        sys.exit(2)

    records = dedupe(records)
    if not records:
        _keep_cache(out_file, "no postings returned")
        sys.exit(1)

    records = round_robin(records, args.limit * 3)
    normalized = []
    for idx, r in enumerate(records, start=1):
        normalized.append(
            {
                "id": idx,
                "title": r["title"],
                "company": r["company"],
                "location": r["location"],
                "job_url": r["job_url"],
                "description": r["description"],
                "source": r["source"],
            }
        )

    tmp = out_file.with_suffix(".tmp")
    tmp.write_text(json.dumps(normalized, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(out_file)

    by_source: dict[str, int] = {}
    for r in normalized:
        by_source[r["source"]] = by_source.get(r["source"], 0) + 1
    summary = ", ".join(f"{k}={v}" for k, v in sorted(by_source.items()))
    print(f"[+] Saved {len(normalized)} job records to {out_file} ({summary})")
    if len(normalized) < 5:
        print(f"[i] Only {len(normalized)} postings; narrow the query or widen --limit.")


def _keep_cache(out_file: Path, reason: str) -> None:
    if out_file.exists():
        try:
            existing = json.loads(out_file.read_text(encoding="utf-8"))
            n = len(existing) if isinstance(existing, list) else 0
        except Exception:
            n = 0
        print(f"[!] {reason}. Keeping existing cache ({n} records) at {out_file}")
    else:
        print(f"[!] {reason}. No cache written.")


if __name__ == "__main__":
    main()
