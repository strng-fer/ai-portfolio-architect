---
description: Generate a starter repo whose tests and benchmarks match the blueprint
---

Target portfolio folder: `$ARGUMENTS`

1. Require `05_agent_prompts.md`. If missing, stop and tell the user to run `/prompt <folder>` first. A scaffold without a prompt pack is guesswork.
2. Run `python3 tools/scaffold_repo.py $ARGUMENTS` (add `--dry-run` first if the user only wants to see the plan, `--force` only when explicitly asked to overwrite).
3. Run `python3 tools/portfolio_status.py $ARGUMENTS` to confirm the generated test and benchmark counts.
4. Print max 5 lines: repo path, file count, test count, benchmark count, one next line pointing at P1 in the prompt pack.

The generated repo is a contract, not an implementation: every test fails on purpose until its milestone is done, and every command named in a "Done when" line already exists.
Do not write business logic here. Implementation belongs to the milestone prompts.
