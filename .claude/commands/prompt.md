---
description: Create the agent prompt pack from an existing blueprint
---

Target portfolio folder: `$ARGUMENTS`

Read `02_system_blueprint.md` (workflow, stack, non-goals, metrics sections) and `01_project_ideation.md` (choice section). Read nothing else.

Write `$ARGUMENTS/05_agent_prompts.md` following `.claude/skills/portfolio-architect/10-agent-prompt-pack.md`:
- P0 context prompt (stands alone: stack, free-tier limits, conventions, prohibitions, README rule).
- One prompt per workflow milestone (max 6).
- One review/benchmark prompt (baseline vs new, 3 runs, median, findings table).
- Each prompt <=150 words, format Goal / Context / Task / Constraints / Deliverable / Done when / Out of scope.
- `Done when` must be a runnable command with an expected result in every prompt.

Write in the language from `.claude/config/lang.md`. Then run:
1. `python3 tools/check_portfolio.py $ARGUMENTS` (must exit 0)
2. `python3 tools/compile_pdf.py $ARGUMENTS`
3. `python3 tools/verify_pdf.py $ARGUMENTS/Blueprint_Final.pdf`

Final output max 5 lines: prompt pack path, prompt count, check result, PDF path, one note line.
