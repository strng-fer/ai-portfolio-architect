#!/usr/bin/env python3
"""Validate a compiled blueprint PDF.

Checks that the PDF is not just "a file with some bytes":
  - exists and is at least 5 KB
  - has at least --min-pages pages (counts /Type /Page objects, no deps)
  - the merged Markdown contains every section that exists in 00-05
  - no unresolved image reference (markdown pointing at a missing PNG)

Usage:
  python3 tools/verify_pdf.py portfolios/<slug>/Blueprint_Final.pdf
  python3 tools/verify_pdf.py <pdf> --min-pages 3

Exit codes:
  0 = valid, 1 = invalid
"""
import argparse
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SOURCES = [
    "00_job_analysis.md",
    "01_project_ideation.md",
    "02_system_blueprint.md",
    "03_references_study.md",
    "04_review_report.md",
    "05_agent_prompts.md",
]


def count_pages(data: bytes) -> int:
    return len(re.findall(rb"/Type\s*/Page[^s]", data))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--min-pages", type=int, default=2)
    args = ap.parse_args()

    pdf = Path(args.pdf)
    if not pdf.exists():
        print(f"[X] PDF file not found: {pdf}")
        sys.exit(1)

    data = pdf.read_bytes()
    size_kb = len(data) / 1024
    if size_kb < 5:
        print(f"[X] PDF too small ({size_kb:.1f} KB), probably corrupt.")
        sys.exit(1)

    pages = count_pages(data)
    if pages < args.min_pages:
        print(f"[X] PDF has {pages} page(s); expected at least {args.min_pages}. Content likely missing.")
        sys.exit(1)

    folder = pdf.parent
    merged = folder / "Blueprint_Final.md"
    if merged.exists():
        text = merged.read_text(encoding="utf-8")
        for name in SOURCES:
            src = folder / name
            if not src.exists():
                continue
            first_heading = next((l.strip() for l in src.read_text(encoding="utf-8").splitlines() if l.startswith("#")), "")
            if first_heading and first_heading.lstrip("# ").strip() not in text:
                print(f"[X] {name} content missing from Blueprint_Final.md ({first_heading[:50]})")
                sys.exit(1)
        for img in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text):
            if img.startswith("http"):
                continue
            if not (folder / img).exists():
                print(f"[X] Broken image reference in merged document: {img}")
                sys.exit(1)

    print(f"[+] PDF verified: {pdf} ({size_kb:.1f} KB, {pages} pages)")
    sys.exit(0)


if __name__ == "__main__":
    main()
