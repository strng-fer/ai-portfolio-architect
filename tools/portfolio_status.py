#!/usr/bin/env python3
"""One-command project status for every portfolio folder.

Reads the tracker, checks the artifacts on disk, and reports what is missing and
what to run next - without opening a PDF or dumping document contents.

Usage:
  python3 tools/portfolio_status.py                 # all portfolios
  python3 tools/portfolio_status.py <slug|folder>   # one portfolio
  python3 tools/portfolio_status.py --json

Exit codes:
  0 = every selected portfolio is BLUEPRINT_READY and consistent
  1 = something is missing or inconsistent
"""
import csv
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
PORTFOLIOS = ROOT / "portfolios"
TRACKER = ROOT / "portfolio_tracker.csv"

REQUIRED = [
    "00_job_analysis.md",
    "01_project_ideation.md",
    "02_system_blueprint.md",
    "03_references_study.md",
    "04_review_report.md",
]
OPTIONAL = ["05_agent_prompts.md"]
DIAGRAMS = ["diagrams/system_architecture.mmd", "diagrams/user_workflow.mmd"]
GENERATED = ["Blueprint_Final.md", "Blueprint_Final.pdf", "diagrams/system_architecture.png", "diagrams/user_workflow.png"]


def read_tracker():
    if not TRACKER.exists():
        return {}
    with TRACKER.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    return {r.get("output_folder", "").strip("/").split("/")[-1]: r for r in rows if r.get("output_folder")}


def words(path: Path):
    try:
        return len(path.read_text(encoding="utf-8").split())
    except Exception:
        return 0


def status_of(folder: Path, tracker):
    name = folder.name
    row = tracker.get(name, {})
    have = {p: (folder / p).exists() for p in REQUIRED + OPTIONAL + DIAGRAMS}
    gen = {p: (folder / p).exists() for p in GENERATED}
    tests = sorted(p.name for p in (folder / "starter_repo" / "tests").glob("test_*.py")) if (folder / "starter_repo").exists() else []
    benches = sorted(p.name for p in (folder / "starter_repo" / "benchmarks").glob("*.py") if p.name != "eval.py") if (folder / "starter_repo").exists() else []

    missing = [p for p, ok in have.items() if not ok and p not in OPTIONAL]
    raw_status = row.get("status", "").strip()

    if not row:
        status, next_step = "UNTRACKED", "run /applyidea for this job or remove the folder"
    elif missing:
        status, next_step = "INCOMPLETE", f"missing {missing[0]}; rerun the phase that writes it"
    elif not gen["Blueprint_Final.pdf"]:
        status, next_step = "MARKDOWN_ONLY", "run /prompt <slug> then tools/compile_pdf.py"
    elif raw_status == "MARKDOWN_ONLY":
        status, next_step = "STALE_STATUS", "PDF exists but tracker says MARKDOWN_ONLY; update the tracker row"
    elif raw_status != "BLUEPRINT_READY":
        status, next_step = "NEEDS_REVIEW", f"tracker status is '{raw_status or 'empty'}'"
    else:
        prompts_exist = (folder / "05_agent_prompts.md").exists()
        status = "BLUEPRINT_READY"
        next_step = "ready: start P1 from 05_agent_prompts.md" if prompts_exist else "ready: run /prompt to add an executable prompt pack"

    return {
        "slug": name,
        "status": status,
        "tracker_status": raw_status or "-",
        "missing": missing,
        "generated": {k: v for k, v in gen.items()},
        "has_prompts": (folder / "05_agent_prompts.md").exists(),
        "blueprint_words": words(folder / "02_system_blueprint.md"),
        "starter_tests": tests,
        "starter_benchmarks": benches,
        "company": row.get("company", "-"),
        "role": row.get("role", "-"),
        "date": row.get("date", "-"),
        "next": next_step,
    }


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv
    tracker = read_tracker()

    folders = [p for p in sorted(PORTFOLIOS.iterdir()) if p.is_dir() and p.name != ".git"] if PORTFOLIOS.exists() else []
    if args:
        needle = args[0].strip("/").split("/")[-1]
        folders = [p for p in folders if needle in p.name]

    if args and not folders:
        print(f"[!] No portfolio folder matching '{args[0]}'. Run tools/portfolio_status.py to list them.")
        sys.exit(1)
    if not args and not folders:
        print("[!] No portfolio folders yet. Run /scrape then /applyidea.")
        sys.exit(1)

    report = [status_of(f, tracker) for f in folders]

    if as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        for r in report:
            print(f"{r['slug']}  [{r['status']}]")
            print(f"  company/role : {r['company']} / {r['role']}  ({r['date']})")
            print(f"  blueprint    : {r['blueprint_words']} words, prompts={'yes' if r['has_prompts'] else 'no'}")
            print(f"  starter repo : {len(r['starter_tests'])} tests, {len(r['starter_benchmarks'])} benchmarks")
            if r["missing"]:
                print(f"  missing      : {', '.join(r['missing'])}")
            no_png = [k for k, v in r["generated"].items() if not v]
            if no_png:
                print(f"  not built    : {', '.join(no_png)}")
            print(f"  next         : {r['next']}")

    bad = [r for r in report if r["status"] != "BLUEPRINT_READY"]
    print(f"[=] {len(report) - len(bad)}/{len(report)} portfolio(s) BLUEPRINT_READY")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
