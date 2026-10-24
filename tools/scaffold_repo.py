#!/usr/bin/env python3
"""Generate a starter repo whose tests and benchmarks match the blueprint.

This is the implementation of `/scaffold`. It reads the blueprint and the prompt
pack, extracts the executable contract (see tools/prompt_contract.py), then writes
a repo skeleton where every command referenced by a "Done when" line already
exists and fails with a clear message until the milestone is implemented.

Usage:
  python3 tools/scaffold_repo.py portfolios/<slug> [--force] [--dry-run]

Exit codes:
  0 = repo generated (or already existed with --dry-run)
  1 = nothing to scaffold or target exists without --force
"""
import argparse
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prompt_contract import extract  # noqa: E402

TEST_TEMPLATE = '''"""Milestone contract test: {milestone}.

This test exists because the blueprint's prompt pack promises that
`{command}` passes. It is intentionally failing: implement {area} first,
then replace the assertions below with the real checks.
"""
import pytest


def test_{slug}_implemented():
    pytest.fail(
        "Not implemented yet. Milestone {milestone} ({area}) must make this pass.\\n"
        "Requirement: {requirement}"
    )
'''

BENCH_TEMPLATE = '''#!/usr/bin/env python3
"""Benchmark entry point for metric: {metric}

Target:   {target}
Baseline: {baseline}

Prints a single row so the evaluation harness can collect it. Implement the
measurement, then compare against the baseline before claiming the target.
"""
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main():
    print("metric,target,baseline,actual")
    print("{metric},{target},{baseline},")
    print("[!] actual value not measured yet: implement this benchmark", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
'''

MAKEFILE_TEMPLATE = """.PHONY: install data demo eval test clean

install:
\tpip install -r requirements.txt

data:
\tpython -m app.data.generate

demo:
\tpython -m app.demo

eval:
\tpython benchmarks/eval.py

test:
\tpython -m pytest -q

clean:
\trm -rf .pytest_cache __pycache__
"""

README_TEMPLATE = """# {title}

{summary}

## What it does
<Two sentences: the problem, and the one hard mechanism you built.>

## How to run
```bash
make install
make data
make demo
```

## How to see the demo
<One command or endpoint a reviewer can run in under two minutes.>

## Benchmark
```bash
make eval
```
Metrics come from `02_system_blueprint.md` section 9. Fill the table after measuring.

| Metric | Target | Baseline | Actual |
|---|---|---|---|
{metric_rows}
"""


def slugify(text, limit=40):
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug[:limit] or "test"


def write(path: Path, content: str, created: list):
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    created.append(str(path))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--force", action="store_true", help="overwrite an existing starter_repo")
    ap.add_argument("--dry-run", action="store_true", help="print the plan without writing")
    args = ap.parse_args()

    folder = Path(args.folder)
    if not folder.is_dir():
        print(f"[X] Folder not found: {folder}")
        sys.exit(1)
    if not (folder / "05_agent_prompts.md").exists():
        print(f"[X] No prompt pack. Run /prompt {folder} first; a scaffold without a contract is guesswork.")
        sys.exit(1)

    contract = extract(folder)
    blueprint = (folder / "02_system_blueprint.md").read_text(encoding="utf-8")
    title_match = re.search(r"^#\s+(.+)$", blueprint, re.M)
    title = title_match.group(1).strip() if title_match else folder.name

    repo = folder / "starter_repo"
    if repo.exists() and not args.force and not args.dry_run:
        print(f"[X] {repo} already exists. Use --force to regenerate.")
        sys.exit(1)
    if repo.exists() and args.force:
        import shutil
        shutil.rmtree(repo)

    prompt_by_id = {p["id"]: p for p in contract["prompts"]}
    created = []

    def emit(rel, content):
        if args.dry_run:
            print(f"[plan] {repo / rel}")
            return
        write(repo / rel, content, created)

    # tests from "Done when" commands
    for cmd in contract["test_commands"]:
        match = re.search(r"tests/(test_[a-z0-9_]+)\.py", cmd)
        if not match:
            continue
        name = match.group(1)
        owner = next((p for p in contract["prompts"] if cmd in p["done_when"]), None)
        emit(
            f"tests/{name}.py",
            TEST_TEMPLATE.format(
                milestone=owner["id"] if owner else "Pn",
                area=owner["title"] if owner else "the milestone",
                command=cmd,
                slug=slugify(name.replace("test_", "")),
                requirement=(owner["done_when"] if owner else cmd)[:300],
            ),
        )

    # benchmarks from metric instruments
    seen = set()
    for metric in contract["metrics"]:
        for cmd in re.findall(r"`([^`]+)`", metric["instrument"]):
            if not cmd.startswith("python "):
                continue
            path = cmd.split("python ", 1)[1].split()[0]
            if path in seen or not path.endswith(".py") or path.startswith("benchmarks/eval.py"):
                continue
            seen.add(path)
            emit(
                path,
                BENCH_TEMPLATE.format(
                    metric=metric["metric"], target=metric["target"], baseline=metric["baseline"]
                ),
            )

    # benchmark aggregator required by "make eval"
    emit(
        "benchmarks/eval.py",
        '''#!/usr/bin/env python3
"""Collect every benchmark into one table and apply the blueprint targets."""
import subprocess
import sys
from pathlib import Path

BENCHMARKS = [
{bench_list}
]


def main():
    rows = []
    failed = 0
    for bench in BENCHMARKS:
        res = subprocess.run([sys.executable, bench], capture_output=True, text=True)
        rows.append((bench, res.returncode, res.stdout.strip().splitlines()[-1:] or [""]))
        if res.returncode != 0:
            failed += 1
    for bench, code, last in rows:
        print(f"{{'ok ' if code == 0 else 'fail'}} {{bench}} {{last[0]}}")
    print(f"[=] {{len(rows) - failed}}/{{len(rows)}} benchmarks measured")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
'''.format(
            bench_list="\n".join(
                f'    "{b.split("python ", 1)[1].strip()}",'
                for b in contract["benchmark_commands"]
                if b.startswith("python ") and b.split("python ", 1)[1].strip() != "benchmarks/eval.py"
            )
            or "    # add benchmark scripts here"
        ),
    )

    # Makefile targets referenced by prompts
    if contract["make_targets"]:
        emit("Makefile", MAKEFILE_TEMPLATE)

    # README with the metric table
    metric_rows = "\n".join(
        f"| {m['metric']} | {m['target']} | {m['baseline']} | _to measure_ |" for m in contract["metrics"]
    ) or "| _no metrics in blueprint_ | | | |"
    emit(
        "README.md",
        README_TEMPLATE.format(
            title=title,
            summary=f"Portfolio project blueprint: `{folder.name}`. See `../02_system_blueprint.md`.",
            metric_rows=metric_rows,
        ),
    )

    # TODO derived from the prompt pack, one item per milestone
    todo = ["# TODO - milestone checklist", ""]
    for p in contract["prompts"]:
        todo.append(f"- [ ] {p['id']} {p['title']}")
        if p["done_when"]:
            todo.append(f"  - Done when: {p['done_when']}")
    emit("TODO.md", "\n".join(todo) + "\n")

    if args.dry_run:
        return

    print(f"[+] starter repo written to {repo}")
    print(f"[+] {len(created)} files: {len(contract['test_commands'])} tests, "
          f"{len(contract['benchmark_commands'])} benchmarks, {len(contract['prompts'])} milestones")
    print("[i] Every generated test fails on purpose until its milestone is implemented.")


if __name__ == "__main__":
    main()
