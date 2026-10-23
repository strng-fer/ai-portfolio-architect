---
description: Enrich the candidate profile from new documents or GitHub (minimal patch)
---

New source: `$ARGUMENTS` (GitHub URL, file name in `documents/`, or free text).

1. Read that source. For a GitHub URL, take only the repo summary/README, not full history.
2. Patch `.claude/skills/portfolio-architect/01-candidate-profile.md` additively: add or update relevant lines. Do not rewrite the file, do not delete valid data.
3. Print max 4 lines: what was added + 1 next-step line.

Match the file's existing language. If the profile is still empty, use the language from `.claude/config/lang.md`.
