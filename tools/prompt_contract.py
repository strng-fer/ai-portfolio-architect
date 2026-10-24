#!/usr/bin/env python3
"""Extract the executable contract from a blueprint prompt pack.

The blueprint's "Done when" lines and the blueprint's metric table are the only
things that make a portfolio verifiable. `scaffold_repo.py` turns them into
actual files, so the generated starter repo already contains the tests and
benchmark entry points the prompts refer to.

Usage:
  python3 tools/prompt_contract.py portfolios/<slug>            # human readable
  python3 tools/prompt_contract.py portfolios/<slug> --json     # machine readable

Exit codes:
  0 = contract extracted
  1 = no prompt pack found
"""
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROMPT_HEAD = re.compile(r"^##\s+(P\d+)\s+-\s+(.+)$", re.M)
DONE_WHEN = re.compile(r"\*\*Done when\*\*:\s*(.+)", re.I)
DELIVERABLE = re.compile(r"\*\*Deliverable\*\*:\s*(.+)", re.I)
BUTTON = r"`([^`]+)`"


def parse_prompts(text):
    heads = list(PROMPT_HEAD.finditer(text))
    prompts = []
    for i, m in enumerate(heads):
        body = text[m.end(): heads[i + 1].start() if i + 1 < len(heads) else len(text)]
        done = DONE_WHEN.search(body)
        deliverable = DELIVERABLE.search(body)
        prompts.append(
            {
                "id": m.group(1),
                "title": m.group(2).strip(),
                "done_when": done.group(1).strip() if done else "",
                "deliverable": deliverable.group(1).strip() if deliverable else "",
            }
        )
    return prompts


def parse_metrics(text):
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.lstrip().startswith("#") and "metrics" in line.lower():
            start = i + 1
            break
    if start is None:
        return []
    rows, header_seen = [], False
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.startswith("#"):
            break
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if all(set(c) <= set("-: ") for c in cells):
            continue
        if not header_seen:
            header_seen = True
            continue
        if len(cells) >= 4:
            rows.append({"metric": cells[0], "target": cells[1], "instrument": cells[2], "baseline": cells[3]})
    return rows


def extract(folder: Path):
    prompt_file = folder / "05_agent_prompts.md"
    blueprint = folder / "02_system_blueprint.md"
    prompts = parse_prompts(prompt_file.read_text(encoding="utf-8")) if prompt_file.exists() else []
    metrics = parse_metrics(blueprint.read_text(encoding="utf-8")) if blueprint.exists() else []

    commands = []
    for p in prompts:
        for cmd in re.findall(BUTTON, p["done_when"]):
            if any(k in cmd for k in ("pytest", "make ", "python", "docker", "curl", "npm", "go test")):
                commands.append({"prompt": p["id"], "command": cmd})

    instruments = []
    for m in metrics:
        for cmd in re.findall(BUTTON, m["instrument"]):
            instruments.append({"metric": m["metric"], "command": cmd})

    tests = sorted({c["command"] for c in commands if "pytest" in c["command"]})
    benchmarks = sorted({i["command"] for i in instruments})
    makefile_targets = sorted({c["command"].split()[1] for c in commands + instruments
                               if c["command"].startswith("make ") and len(c["command"].split()) > 1})

    return {
        "prompts": prompts,
        "metrics": metrics,
        "test_commands": tests,
        "benchmark_commands": benchmarks,
        "make_targets": makefile_targets,
    }


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv
    if not args:
        print("Usage: python3 tools/prompt_contract.py <portfolio_folder> [--json]")
        sys.exit(1)

    folder = Path(args[0])
    if not folder.is_dir():
        print(f"[X] Folder not found: {folder}")
        sys.exit(1)
    if not (folder / "05_agent_prompts.md").exists():
        print(f"[X] No 05_agent_prompts.md in {folder}. Run /prompt first.")
        sys.exit(1)

    contract = extract(folder)
    if as_json:
        print(json.dumps(contract, indent=2, ensure_ascii=False))
        return

    print(f"# contract for {folder.name}")
    print(f"## prompts ({len(contract['prompts'])})")
    for p in contract["prompts"]:
        print(f"- {p['id']} {p['title']}: {p['done_when'][:90]}")
    print(f"## tests ({len(contract['test_commands'])})")
    for t in contract["test_commands"]:
        print(f"- {t}")
    print(f"## benchmarks ({len(contract['benchmark_commands'])})")
    for b in contract["benchmark_commands"]:
        print(f"- {b}")
    print(f"## make targets ({len(contract['make_targets'])})")
    for m in contract["make_targets"]:
        print(f"- {m}")


if __name__ == "__main__":
    main()
