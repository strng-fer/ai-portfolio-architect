---
description: Generate a starter repo from the blueprint (optional, outside the main flow)
---

Target: `$ARGUMENTS`

If `05_agent_prompts.md` exists, the prompt pack is already enough for execution - ask in one line whether scaffolding is still wanted.

Steps:
1. Read `02_system_blueprint.md` sections 5 (stack), 7 (data & interfaces), 10 (workflow). Read nothing else.
2. Create `$ARGUMENTS/starter_repo/` containing: folder skeleton, `docker-compose.yml`/`Dockerfile`, dependency files, 2-3 core boilerplate files, a short `README.md` (max 40 lines), and `TODO.md` per milestone.
3. Do not write tests or full business logic. Implementation is the job of the milestones in the prompt pack.
4. Print max 5 lines: repo path, file count, one note line.
