#!/usr/bin/env python3
"""Pick a build mechanism for a posting, from the catalogue and the build history.

Ideation quality comes from choosing a mechanism, not inventing one. This script
does the choosing with three inputs: posting signals, mechanisms already built, and
the remaining hour budget.

Usage:
  python3 tools/mechanism_pick.py --signals "audit,extraction,ocr" --hours 34
  python3 tools/mechanism_pick.py --signals "latency,cost" --hours 20 --top 5
  python3 tools/mechanism_pick.py --list
  python3 tools/mechanism_pick.py --record --slug my_project --mechanism span-grounding --hours 34

Exit codes:
  0 = candidates found / action done
  1 = no candidate matched the signals
  2 = catalogue file missing
"""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_CATALOGUE = Path(".claude/skills/portfolio-architect/12-mechanism-catalogue.md")
DEFAULT_HISTORY = Path("portfolios/_history.json")

COST_RANGE = {"S": (6, 12), "M": (12, 24), "L": (24, 40)}

# Scoring weights. Novelty dominates so a portfolio does not become five remixes
# of the same mechanism.
W_SIGNAL = 3.0
W_NOVEL = 2.0
W_USED = -3.0
W_COST_FIT = 2.0
W_COST_OVER = -2.5


def parse_catalogue(path: Path) -> tuple[list[dict], str | None]:
    if not path.exists():
        return [], f"catalogue not found: {path}"

    lines = path.read_text(encoding="utf-8").splitlines()
    rows: list[dict] = []
    header_seen = False

    for line in lines:
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|")):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) < 7:
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue
        if cells[0].lower() == "id":
            header_seen = True
            continue
        if not header_seen:
            continue
        mech_id = cells[0].strip("`")
        if not re.fullmatch(r"[a-z0-9-]+", mech_id):
            continue
        cost = cells[4].strip().upper()
        if cost not in COST_RANGE:
            continue
        rows.append(
            {
                "id": mech_id,
                "name": cells[1],
                "domains": [d.strip() for d in cells[2].split(",") if d.strip()],
                "signals": tokenise(cells[3].replace(",", " ")),
                "cost": cost,
                "metrics": cells[5],
                "fails": cells[6],
            }
        )

    if not rows:
        return [], "no mechanism rows parsed (check the table header and 7 columns)"
    return rows, None


def load_history(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if isinstance(data, dict):
        data = data.get("projects", [])
    return [d for d in data if isinstance(d, dict)]


def save_history(path: Path, entries: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "note": "Mechanisms already built. Read by tools/mechanism_pick.py to favour novelty.",
        "projects": entries,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def tokenise(text: str) -> set[str]:
    return {t for t in re.split(r"[^a-z0-9]+", text.lower()) if len(t) >= 2}


def score(mech: dict, signals: set[str], hours: int, history: list[dict]) -> tuple[float, list[str]]:
    why: list[str] = []
    total = 0.0

    hit = sorted(set(mech["signals"]) & signals)
    if hit:
        total += W_SIGNAL * len(hit)
        why.append("signals: " + ",".join(hit))

    used = [h for h in history if h.get("mechanism") == mech["id"]]
    if used:
        total += W_USED
        why.append(f"used {len(used)}x")
    else:
        total += W_NOVEL
        why.append("new")

    low, high = COST_RANGE[mech["cost"]]
    if hours >= high:
        total += W_COST_FIT
        why.append(f"fits {mech['cost']}")
    elif hours >= low:
        total += W_COST_FIT / 2
        why.append(f"tight {mech['cost']}")
    else:
        total += W_COST_OVER
        why.append(f"over budget {mech['cost']}")

    return total, why


def cmd_pick(args) -> int:
    catalogue, err = parse_catalogue(Path(args.catalogue))
    if err:
        print(f"[X] ERROR {err}")
        return 2

    signals = tokenise(args.signals or "")
    if not signals:
        print("[X] ERROR --signals is empty")
        return 1

    history = load_history(Path(args.history))

    scored = []
    for mech in catalogue:
        if args.domain and not any(args.domain.lower() in d.lower() for d in mech["domains"]):
            continue
        total, why = score(mech, signals, args.hours, history)
        if not (set(mech["signals"]) & signals):
            continue
        scored.append((total, mech, why))

    if not scored:
        print(f"[!] no mechanism matched signals: {', '.join(sorted(signals))}")
        print("[i] broaden the signals, or add a row to 12-mechanism-catalogue.md")
        return 1

    scored.sort(key=lambda x: (-x[0], x[1]["id"]))

    print("id | mechanism | score | cost | why")
    for total, mech, why in scored[: args.top]:
        print(f"{mech['id']} | {mech['name']} | {total:.1f} | {mech['cost']} | {'; '.join(why)}")

    if args.json:
        print()
        print(
            json.dumps(
                [
                    {"id": m["id"], "score": round(t, 2), "cost": m["cost"], "metrics": m["metrics"]}
                    for t, m, _ in scored[: args.top]
                ],
                indent=2,
                ensure_ascii=False,
            )
        )
    return 0


def cmd_list(args) -> int:
    catalogue, err = parse_catalogue(Path(args.catalogue))
    if err:
        print(f"[X] ERROR {err}")
        return 2
    history = load_history(Path(args.history))
    used = {h.get("mechanism") for h in history}
    print("id | mechanism | cost | domains | used")
    for mech in catalogue:
        print(
            f"{mech['id']} | {mech['name']} | {mech['cost']} | "
            f"{','.join(mech['domains'])} | {'yes' if mech['id'] in used else '-'}"
        )
    print(f"[=] {len(catalogue)} mechanism(s), {len(used & {m['id'] for m in catalogue})} already built")
    return 0


def cmd_record(args) -> int:
    catalogue, err = parse_catalogue(Path(args.catalogue))
    if err:
        print(f"[X] ERROR {err}")
        return 2
    known = {m["id"] for m in catalogue}
    if args.mechanism not in known:
        print(f"[X] ERROR unknown mechanism '{args.mechanism}'")
        print(f"[i] known: {', '.join(sorted(known))}")
        return 1

    path = Path(args.history)
    entries = load_history(path)
    entries = [e for e in entries if e.get("slug") != args.slug]
    entries.append(
        {
            "slug": args.slug,
            "mechanism": args.mechanism,
            "hours": args.hours,
            "date": date.today().isoformat(),
        }
    )
    save_history(path, entries)
    print(f"[+] recorded {args.mechanism} for {args.slug} ({len(entries)} project(s) in history)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Pick a build mechanism for a posting")
    parser.add_argument("--catalogue", default=str(DEFAULT_CATALOGUE))
    parser.add_argument("--history", default=str(DEFAULT_HISTORY))

    sub = parser.add_subparsers(dest="command")

    pick = sub.add_parser("pick", help="Rank mechanisms for posting signals")
    pick.add_argument("--signals", required=True, help="Comma-separated posting signals")
    pick.add_argument("--hours", type=int, default=30, help="Available hours for the project")
    pick.add_argument("--domain", default=None, help="Filter by domain (llm, cv, backend, data, mlops)")
    pick.add_argument("--top", type=int, default=3)
    pick.add_argument("--json", action="store_true")

    sub.add_parser("list", help="List the catalogue")

    rec = sub.add_parser("record", help="Record a built mechanism")
    rec.add_argument("--slug", required=True)
    rec.add_argument("--mechanism", required=True)
    rec.add_argument("--hours", type=int, default=0)

    # Bare invocation keeps the documented one-liner working: default to pick.
    argv = sys.argv[1:]
    if argv and not argv[0].startswith("-") and argv[0] not in {"pick", "list", "record"}:
        argv.insert(0, "pick")
    elif argv and argv[0].startswith("-"):
        argv.insert(0, "pick")

    args = parser.parse_args(argv)
    if args.command == "list":
        return cmd_list(args)
    if args.command == "record":
        return cmd_record(args)
    return cmd_pick(args)


if __name__ == "__main__":
    sys.exit(main())
