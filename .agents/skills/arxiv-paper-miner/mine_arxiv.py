#!/usr/bin/env python3
import argparse
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

def search_arxiv(query: str, limit: int = 5):
    encoded = urllib.parse.quote(query)
    url = f"http://export.arxiv.org/api/query?search_query=all:{encoded}&start=0&max_results={limit}&sortBy=relevance"
    req = urllib.request.Request(url, headers={"User-Agent": "AI-Portfolio-Architect/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            xml_data = res.read()
            root = ET.fromstring(xml_data)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            papers = []
            for entry in root.findall("atom:entry", ns):
                title = entry.find("atom:title", ns)
                summary = entry.find("atom:summary", ns)
                link = entry.find("atom:id", ns)
                published = entry.find("atom:published", ns)
                papers.append({
                    "title": title.text.strip().replace("\n", " ") if title is not None else "",
                    "summary": summary.text.strip().replace("\n", " ")[:800] if summary is not None else "",
                    "url": link.text.strip() if link is not None else "",
                    "published": published.text[:10] if published is not None else ""
                })
            return papers
    except Exception as e:
        return [{"error": str(e)}]

def main():
    parser = argparse.ArgumentParser(description="Search ArXiv for scientific paper references")
    parser.add_argument("--query", required=True, help="Algorithm or architecture keywords")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    results = search_arxiv(args.query, args.limit)
    out_path = Path("job_scraper/arxiv_refs.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[+] Saved {len(results)} ArXiv references to {out_path}")

if __name__ == "__main__":
    main()
