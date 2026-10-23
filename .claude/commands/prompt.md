---
description: Create the agent prompt pack from an existing blueprint
---

Target portfolio folder: `$ARGUMENTS`

Read `02_system_blueprint.md` (workflow, stack, non-goals sections) and `01_project_ideation.md` (choice section). Read nothing else.

Write `$ARGUMENTS/05_agent_prompts.md` following `.claude/skills/portfolio-architect/10-agent-prompt-pack.md`:
- P0 context prompt (stands alone: stack, free-tier limits, conventions, prohibitions).
- One prompt per workflow milestone (max 6).
- One review/benchmark prompt.
- Each prompt <=150 words, format Goal / Context / Task / Constraints / Deliverable / Done when / Out of scope.

Write in the language from `.claude/config/lang.md`. Then run `python3 tools/compile_pdf.py $ARGUMENTS` and `python3 tools/verify_pdf.py $ARGUMENTS/Blueprint_Final.pdf`.

Final output max 5 lines: prompt pack path, prompt count, PDF path, one note line.
