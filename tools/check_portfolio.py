#!/usr/bin/env python3
"""Preflight: validate the numbers a generated blueprint claims.

A blueprint is only useful if its targets are reproducible. This script makes
every metric row prove itself: each row needs a concrete target, an instrument
(visible tool/artifact name), a measured baseline, and a matching validation step.

Usage:
  python3 tools/check_portfolio.py portfolios/<company>_<role>
  python3 tools/check_portfolio.py <folder> --strict   # warnings become errors

Exit codes:
  0 = all checks pass
  1 = blocking errors found (fix before compiling the PDF)
"""
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BUDGETS = {
    "00_job_analysis.md": 450,
    "01_project_ideation.md": 550,
    "02_system_blueprint.md": 1500,
    "03_references_study.md": 400,
    "04_review_report.md": 350,
    "05_agent_prompts.md": 900,
}

# Product mode adds two sections to the blueprint, so it gets the headroom.
PRODUCT_BUDGET_OVERRIDES = {"02_system_blueprint.md": 1750}
IPAD = Path(".claude/skills/portfolio-architect/01c-product-intent.md")


def product_mode():
    try:
        text = IPAD.read_text(encoding="utf-8")
    except OSError:
        return False
    return bool(re.search(r"\|\s*Mode\s*\|\s*`product`", text))


def budgets():
    table = dict(BUDGETS)
    if product_mode():
        table.update(PRODUCT_BUDGET_OVERRIDES)
    return table

REQUIRED_SECTIONS = [
    "Problem & Relevance",
    "Goals & Non-Goals",
    "Design Alternatives",
    "Architecture & Flow",
    "Tech Stack",
    "Key Theory",
    "Data & Interfaces",
    "Technical Challenges",
    "Metrics & Validation",
    "Workflow",
    "Risks",
    "CV Bullet",
]

VAGUE_METRICS = {"good", "fast", "better", "improved", "high", "low", "optimized", "scalable", "reliable", "efficient"}
CODE_FENCE = re.compile(r"```")


def words(text):
    return len(text.split())


def table_rows(text, heading_keyword):
    """Extract markdown table rows under the first heading containing the keyword."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.lstrip().startswith("#") and heading_keyword.lower() in line.lower():
            start = i + 1
            break
    if start is None:
        return []
    rows = []
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.startswith("#"):
            break
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if all(set(c) <= set("-: ") for c in cells):
                continue
            rows.append(cells)
    return rows[1:] if rows else rows


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    strict = "--strict" in sys.argv
    if not args:
        print("Usage: python3 tools/check_portfolio.py <portfolio_folder> [--strict]")
        sys.exit(1)

    folder = Path(args[0])
    errors, warnings = [], []

    if not folder.is_dir():
        print(f"[X] Folder not found: {folder}")
        sys.exit(1)

    # 1. required files
    limits = budgets()
    for name, limit in limits.items():
        path = folder / name
        if not path.exists():
            if name == "05_agent_prompts.md":
                warnings.append(f"{name}: missing (optional, only created with --prompts)")
            else:
                errors.append(f"{name}: missing required document")
            continue
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            errors.append(f"{name}: empty file")
            continue
        # 2. word budget
        count = words(text)
        if count > limit:
            errors.append(f"{name}: {count} words exceeds budget {limit}")
        # 3. no long code blocks
        fence_count = len(CODE_FENCE.findall(text))
        if fence_count:
            for block in re.findall(r"```.*?```", text, re.S):
                if len(block.strip().splitlines()) > 6:
                    errors.append(f"{name}: code block over 5 lines (implementation detail is not allowed)")
                    break

    blueprint = folder / "02_system_blueprint.md"
    if blueprint.exists():
        bp = blueprint.read_text(encoding="utf-8")
        # 4. required sections
        for section in REQUIRED_SECTIONS:
            if section.lower() not in bp.lower():
                errors.append(f"02_system_blueprint.md: missing section '{section}'")

        # 5. metrics must be concrete and provable
        rows = table_rows(bp, "Metrics")
        if not rows:
            errors.append("02_system_blueprint.md: metric table missing or empty")
        for row in rows:
            if len(row) < 4:
                errors.append(f"02_system_blueprint.md: metric row has fewer than 4 columns: {row}")
                continue
            metric, target, instrument, baseline = row[:4]
            if not re.search(r"\d", target):
                errors.append(f"metric '{metric}': target has no number ('{target}')")
            if any(v in target.lower().split() for v in VAGUE_METRICS):
                errors.append(f"metric '{metric}': target is vague ('{target}')")
            if instrument.lower() in {"-", "n/a", "na", "?", ""}:
                errors.append(f"metric '{metric}': instrument missing (name the tool or artifact)")
            if baseline.lower() in {"-", "na", "?", ""} or baseline.strip() == "N/A":
                errors.append(f"metric '{metric}': baseline missing (state the naive/single-call reference)")

        # 6. diagrams referenced and present
        for img in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", bp):
            if not (folder / img).exists():
                warnings.append(f"02_system_blueprint.md: referenced image missing on disk: {img}")
        if "diagrams/system_architecture.png" not in bp and "diagrams/system_architecture.mmd" in "".join(
            p.name for p in (folder / "diagrams").glob("*")
        ):
            warnings.append("02_system_blueprint.md: architecture diagram not embedded")

    # 7. review report must have evidence, not bare yes/no
    review = folder / "04_review_report.md"
    if review.exists():
        rv = review.read_text(encoding="utf-8")
        for line in rv.splitlines():
            low = line.lower()
            if re.match(r"^\s*[-*]\s*(anti-crud|realistic|measurable|diagrams|non-goals|budgets)", low):
                if not re.search(r"\b(yes|no)\b", low):
                    warnings.append(f"04_review_report.md: gate line lacks yes/no verdict: {line.strip()[:60]}")
                elif not re.search(r"`|\.md|\.py|:\d|\d", low):
                    warnings.append(f"04_review_report.md: gate line lacks evidence: {line.strip()[:60]}")

    # 8. prompt pack must have runnable "Done when" criteria
    prompts = folder / "05_agent_prompts.md"
    if prompts.exists():
        pp = prompts.read_text(encoding="utf-8")
        done_blocks = re.findall(r"\*\*Done when\*\*:?\s*(.+)", pp)
        if pp and not done_blocks:
            warnings.append("05_agent_prompts.md: no 'Done when' criteria found")
        for block in done_blocks:
            if not re.search(r"`|\bpython|-m pytest|make |docker |curl ", block):
                warnings.append(f"05_agent_prompts.md: 'Done when' is not a runnable command: {block.strip()[:60]}")

    for w in warnings:
        print(f"[!] WARN {w}")
    for e in errors:
        print(f"[X] ERROR {e}")

    blocking = errors or (strict and warnings)
    print(f"[=] {len(errors)} error(s), {len(warnings)} warning(s) in {folder}")
    sys.exit(1 if blocking else 0)


if __name__ == "__main__":
    main()
