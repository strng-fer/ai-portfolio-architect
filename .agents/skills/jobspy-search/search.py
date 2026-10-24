#!/usr/bin/env python3
"""Search job portals for portfolio ideation.

Never destroys an existing cache on failure: writes to a temp file first and only
replaces job_scraper/latest_scrape.json when at least one posting was returned.

Exit codes:
  0 = saved at least one posting
  1 = no postings (existing cache is preserved)
  2 = missing dependency
"""
import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def scrape_with_jobspy(query: str, location: str, results: int):
    try:
        from jobspy import scrape_jobs, Site
    except ImportError:
        print("[!] python-jobspy is not installed. Run: pip install python-jobspy")
        return None

    try:
        valid_sites = {s.name.lower() for s in Site}
        requested = ["linkedin", "indeed", "jobstreet", "glassdoor"]
        sites = [s for s in requested if s in valid_sites]
        skipped = [s for s in requested if s not in valid_sites]
        if skipped:
            print(f"[i] Site not supported by this jobspy version (skipped): {', '.join(skipped)}")
        loc = location.lower()
        if "indonesia" in loc or "jakarta" in loc:
            sites = [s for s in sites if s != "glassdoor"]
        if not sites:
            print("[!] No site supported by this jobspy version.")
            return []

        jobs = scrape_jobs(
            site_name=sites,
            search_term=query,
            location=location,
            results_wanted=results,
            hours_old=336,
            country_indeed="indonesia"
            if "indonesia" in location.lower() or "jakarta" in location.lower()
            else "usa",
        )
        records = []
        for idx, (_, row) in enumerate(jobs.iterrows(), start=1):
            title = str(row.get("title", "") or "").strip()
            if not title or title.lower() == "nan":
                continue
            records.append(
                {
                    "id": idx,
                    "title": title,
                    "company": str(row.get("company", "") or "").strip(),
                    "location": str(row.get("location", "") or "").strip(),
                    "job_url": str(row.get("job_url", "") or "").strip(),
                    "description": str(row.get("description", "") or "")[:4000],
                }
            )
        return records
    except Exception as e:
        print(f"[!] jobspy failed: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(description="Search job portals for portfolio ideation")
    parser.add_argument("--query", required=True, help="e.g. 'Backend Engineer Jakarta'")
    parser.add_argument("--location", default="Indonesia", help="Search location")
    parser.add_argument("--limit", type=int, default=15)
    args = parser.parse_args()

    out_file = Path("job_scraper/latest_scrape.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)

    records = scrape_with_jobspy(args.query, args.location, args.limit)
    if records is None:
        _keep_cache(out_file, "missing dependency")
        sys.exit(2)
    if not records:
        _keep_cache(out_file, "no postings returned")
        sys.exit(1)

    tmp = out_file.with_suffix(".tmp")
    tmp.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(out_file)
    print(f"[+] Saved {len(records)} job records to {out_file}")
    if len(records) < 5:
        print(f"[i] Only {len(records)} postings; narrow the query or widen --limit for a better ranking.")


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
