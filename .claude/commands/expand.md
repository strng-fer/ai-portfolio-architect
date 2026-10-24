---
description: Enrich the candidate profile from new documents or GitHub (minimal patch)
---

New source: `$ARGUMENTS` (GitHub URL, file name in `documents/`, or free text).

1. Read that source. For a GitHub URL, take only the repo summary/README, not full history.
2. Patch `.claude/skills/portfolio-architect/01-candidate-profile.md` additively: add or update relevant lines. Do not rewrite the file, do not delete valid data.
3. Patch `.claude/skills/portfolio-architect/01b-skill-evidence.md`:
   - New skill found: add one row. Level starts at `learning` unless the source proves shipping use.
   - Existing skill now has an artifact: fill `evidence`, set `last_used` to the source's month, set `verified: yes`.
   - Never raise a level by more than one step, and never above `working` without a second artifact.
   - Keep the table under 60 rows. Merge synonyms instead of adding near-duplicates.
   - Validate with `python3 tools/skill_evidence.py check`.
4. Print max 4 lines: what was added + 1 next-step line.

Match the file's existing language. If the profile is still empty, use the language from `.claude/config/lang.md`.
