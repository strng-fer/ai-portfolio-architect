#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

def scrape_with_jobspy(query: str, location: str, results: int):
    try:
        from jobspy import scrape_jobs, Site
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
            country_indeed="indonesia" if "indonesia" in location.lower() or "jakarta" in location.lower() else "usa"
        )
        records = []
        for idx, (_, row) in enumerate(jobs.iterrows(), start=1):
            records.append({
                "id": idx,
                "title": str(row.get("title", "")),
                "company": str(row.get("company", "")),
                "location": str(row.get("location", "")),
                "job_url": str(row.get("job_url", "")),
                "description": str(row.get("description", ""))[:4000]
            })
        return records
    except ImportError:
        print("[!] python-jobspy is not installed. Run: pip install python-jobspy")
        return []
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
    out_file.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[+] Saved {len(records)} job records to {out_file}")

if __name__ == "__main__":
    main()
