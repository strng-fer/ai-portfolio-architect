#!/usr/bin/env python3
"""Validate the skill evidence ledger and score gaps against a posting.

The ledger is a markdown table in `.claude/skills/portfolio-architect/01b-skill-evidence.md`.
Rows carry an artifact, so a gap verdict can cite evidence instead of opinion.

Usage:
  python3 tools/skill_evidence.py check
  python3 tools/skill_evidence.py gap --needs "python,fastapi,qdrant"
  python3 tools/skill_evidence.py gap --needs "python,fastapi" --json

Exit codes:
  0 = ledger valid / gap computed
  1 = ledger malformed, or a posting needs three or more missing skills
  2 = ledger file not found
"""
import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_LEDGER = Path(".claude/skills/portfolio-architect/01b-skill-evidence.md")

LEVELS = ("none", "learning", "working", "strong")
VERIFIED = ("yes", "no", "stale")

# A skill at this level or above is reusable without a new build.
REUSABLE = ("working", "strong")

# Hard ceiling: more missing skills than this makes the posting out of reach.
MAX_MISSING = 2


def parse_ledger(path: Path) -> tuple[list[dict], list[str]]:
    """Return (rows, errors). Only the table under '## Inventory' is read."""
    errors: list[str] = []
    if not path.exists():
        return [], [f"ledger not found: {path}"]

    lines = path.read_text(encoding="utf-8").splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip().lower().startswith("## inventory"):
            start = i + 1
            break
    if start is None:
        return [], ["no '## Inventory' heading found"]

    rows: list[dict] = []
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.startswith("#"):
            break
        if not (stripped.startswith("|") and stripped.endswith("|")):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) < 5:
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue
        if cells[0].lower() == "skill":
            continue
        rows.append(
            {
                "skill": cells[0],
                "level": cells[1].lower(),
                "evidence": cells[2],
                "last_used": cells[3],
                "verified": cells[4].lower(),
            }
        )
    return rows, errors


def validate(rows: list[dict]) -> tuple[list[str], list[str]]:
    """Return (errors, warnings).

    Errors mean the table is malformed. Warnings mean a row is honest but not yet
    proven: a level is claimed with no artifact. Warnings become fatal only under
    --strict, so a fresh ledger can be scaffolded before the first repo exists.
    """
    errors: list[str] = []
    warnings: list[str] = []
    seen: set[str] = set()

    for row in rows:
        name = row["skill"]
        key = name.lower()
        if key in seen:
            errors.append(f"duplicate skill row: {name}")
        seen.add(key)

        if row["level"] not in LEVELS:
            errors.append(f"{name}: level '{row['level']}' not in {', '.join(LEVELS)}")
            continue

        if row["level"] == "none":
            if row["evidence"] not in {"-", ""}:
                errors.append(f"{name}: level 'none' must not claim evidence ('{row['evidence']}')")
            if row["verified"] not in {"-", "no"}:
                errors.append(f"{name}: level 'none' must use verified '-' or 'no'")
            continue

        if row["verified"] not in VERIFIED:
            errors.append(f"{name}: verified '{row['verified']}' not in {', '.join(VERIFIED)}")

        if row["evidence"] in {"-", ""}:
            if row["verified"] == "yes":
                errors.append(f"{name}: verified 'yes' with no artifact")
            else:
                warnings.append(f"{name}: level '{row['level']}' has no evidence artifact yet")

        if row["last_used"] in {"-", ""}:
            warnings.append(f"{name}: level '{row['level']}' has no last_used month")
        elif not re.fullmatch(r"\d{4}-\d{2}", row["last_used"]):
            errors.append(f"{name}: last_used '{row['last_used']}' is not YYYY-MM")

    return errors, warnings


def normalise(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def find_row(rows: list[dict], need: str) -> dict | None:
    """Match a posting requirement against ledger rows by token containment."""
    target = normalise(need)
    if not target:
        return None
    best = None
    best_len = 0
    for row in rows:
        name = normalise(row["skill"])
        if not name:
            continue
        if name == target or name in target or target in name:
            if len(name) > best_len:
                best, best_len = row, len(name)
    return best


def gap_status(row: dict | None) -> str:
    if row is None or row["level"] == "none":
        return "missing"
    if row["level"] == "learning":
        return "thin"
    if row["level"] in REUSABLE and row["verified"] == "yes":
        return "solid"
    return "thin"


def cmd_check(args) -> int:
    rows, parse_errors = parse_ledger(Path(args.ledger))
    errors, warnings = validate(rows)
    errors = parse_errors + errors

    for w in warnings:
        print(f"[!] WARN {w}")
    for e in errors:
        print(f"[X] ERROR {e}")

    if not rows and not errors:
        print("[X] ERROR ledger has no rows")
        return 1

    counts = {level: sum(1 for r in rows if r["level"] == level) for level in LEVELS}
    summary = ", ".join(f"{k}={v}" for k, v in counts.items())
    proven = sum(1 for r in rows if r["verified"] == "yes")
    print(f"[=] {len(rows)} skill row(s): {summary}; proven={proven}")
    print(f"[=] {len(errors)} error(s), {len(warnings)} warning(s)")

    blocking = bool(errors) or (args.strict and bool(warnings))
    if blocking:
        if args.strict and warnings and not errors:
            print("[!] --strict: unproven rows block. Add an artifact or lower the level.")
        return 1
    print("[+] ledger valid")
    return 0


def cmd_gap(args) -> int:
    rows, parse_errors = parse_ledger(Path(args.ledger))
    errors, _ = validate(rows)
    if parse_errors or errors:
        for e in parse_errors + errors:
            print(f"[X] ERROR {e}")
        return 1

    needs = [n.strip() for n in args.needs.split(",") if n.strip()]
    if not needs:
        print("[X] ERROR --needs is empty")
        return 1

    results = []
    for need in needs:
        row = find_row(rows, need)
        status = gap_status(row)
        results.append(
            {
                "need": need,
                "skill": row["skill"] if row else None,
                "level": row["level"] if row else None,
                "verified": row["verified"] if row else None,
                "evidence": row["evidence"] if row else None,
                "status": status,
            }
        )

    missing = [r for r in results if r["status"] == "missing"]
    thin = [r for r in results if r["status"] == "thin"]
    solid = [r for r in results if r["status"] == "solid"]

    if args.json:
        print(
            json.dumps(
                {
                    "needs": results,
                    "missing": len(missing),
                    "thin": len(thin),
                    "solid": len(solid),
                    "verdict": "out_of_reach" if len(missing) > MAX_MISSING else "workable",
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        print(f"need | ledger row | level | verified | status")
        for r in results:
            print(
                f"{r['need']} | {r['skill'] or '-'} | {r['level'] or '-'} | "
                f"{r['verified'] or '-'} | {r['status']}"
            )
        print(
            f"[=] solid={len(solid)} thin={len(thin)} missing={len(missing)} "
            f"(ceiling {MAX_MISSING} missing)"
        )
        if len(missing) > MAX_MISSING:
            print(f"[!] out of reach: {len(missing)} missing skills, lower the score instead of building it")
        elif missing:
            print(f"[i] new-technology axis: {', '.join(r['need'] for r in missing)}")
        else:
            print("[i] no missing skill: pick a mechanism, not a new stack")

    return 1 if len(missing) > MAX_MISSING else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate skill evidence and score gaps")
    parser.add_argument("--ledger", default=str(DEFAULT_LEDGER), help="Path to the ledger markdown")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("check", help="Validate the ledger table").add_argument(
        "--strict", action="store_true", help="Treat unproven rows as errors"
    )

    gap = sub.add_parser("gap", help="Score a posting's requirements against the ledger")
    gap.add_argument("--needs", required=True, help="Comma-separated requirements")
    gap.add_argument("--json", action="store_true", help="Machine-readable output")

    args = parser.parse_args()
    if args.command == "check":
        return cmd_check(args)
    return cmd_gap(args)


if __name__ == "__main__":
    sys.exit(main())
