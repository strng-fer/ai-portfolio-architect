#!/usr/bin/env python3
import argparse
import json
import urllib.parse
import urllib.request
from pathlib import Path

def search_github(query: str, limit: int = 8):
    url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(query)}&sort=stars&order=desc&per_page={limit}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "AI-Portfolio-Architect/1.0",
            "Accept": "application/vnd.github.v3+json"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            data = json.loads(res.read().decode("utf-8"))
            items = []
            for item in data.get("items", []):
                items.append({
                    "full_name": item.get("full_name"),
                    "html_url": item.get("html_url"),
                    "stars": item.get("stargazers_count"),
                    "language": item.get("language"),
                    "description": item.get("description"),
                    "topics": item.get("topics", [])
                })
            return items
    except Exception as e:
        return [{"error": str(e)}]

def main():
    parser = argparse.ArgumentParser(description="Cari referensi repositori di GitHub")
    parser.add_argument("--query", required=True, help="Kata kunci teknis")
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args()

    results = search_github(args.query, args.limit)
    out_path = Path("job_scraper/github_refs.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[+] Berhasil menyimpan {len(results)} referensi GitHub ke {out_path}")

if __name__ == "__main__":
    main()
