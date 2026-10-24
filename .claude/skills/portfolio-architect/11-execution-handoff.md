# Execution Handoff: From Blueprint to Working Repo

A blueprint that only reads well is still a failure. This module defines the last mile: how the documents become a repo that proves its own claims.

## 1. The contract is extracted, not invented
`tools/prompt_contract.py` reads two files and produces the executable contract:
- every `Done when` line in `05_agent_prompts.md` (commands),
- every metric row in `02_system_blueprint.md` section 9 (target, instrument, baseline).

If a command in a `Done when` line does not exist yet, the milestone must create it. Never soften the line to a description.

## 2. Starter repo is a skeleton of promises
`tools/scaffold_repo.py` writes:
- one failing test per milestone, whose message names the milestone and its requirement,
- one benchmark script per metric instrument,
- `benchmarks/eval.py` that collects every benchmark into one table,
- `Makefile` with every target the prompts reference (`make data`, `make demo`, `make eval`, `make test`),
- `README.md` with the three presentation sections and the metric table,
- `TODO.md` with one checkbox per milestone.

Rules:
- Tests fail on purpose. A test that passes before implementation is a fake test.
- No business logic in the scaffold. Implementation belongs to milestone prompts.
- Regenerating with `--force` deletes the previous `starter_repo/`; never do it after work has started without asking.

## 3. Milestone order and stopping points
Execute prompts in order (P1, P2, ...). A milestone is done only when its `Done when` command exits 0. Stop there and report - do not start the next milestone in the same session.

## 4. What "portfolio-ready" means
All of the following, verifiable by a stranger in ten minutes:
1. `make install && make data && make demo` works from a clean clone.
2. `make test` passes and the tests assert behaviour, not existence.
3. `make eval` prints every metric with target, baseline, and measured value.
4. `README.md` states what it does, how to run it, and how to see the demo.
5. At least one documented experiment where a weaker variant loses, proving the mechanism matters.

## 5. Status reporting
`tools/portfolio_status.py` is the only source of truth for project state. It reports BLUEPRINT_READY, MARKDOWN_ONLY, INCOMPLETE, UNTRACKED, STALE_STATUS, or NEEDS_REVIEW, plus the next action. Never summarise a portfolio from memory.

## 6. Failure handling
- If a benchmark cannot run in the free tier, replace the metric - do not fake the number.
- If a milestone overruns its estimate by more than 50%, cut a non-goal rather than shrinking the metric.
- If the contract and the blueprint disagree, the blueprint wins; regenerate the scaffold.
