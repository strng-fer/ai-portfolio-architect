---
description: Re-rank scraped jobs by learning ROI (no narration)
---

Read only the digest: `python3 tools/job_digest.py list --top 20`.
If needed, read `.claude/skills/portfolio-architect/04-gap-evaluation.md` (rubric) and `01-candidate-profile.md`.

Recompute scores, write `job_scraper/ranked_jobs.json` (`score` + short idea field, max 12 words per job).
Print a 10-row table: `ID | Company | Role | Score | Short idea`. Nothing else except one next-step line.

Write the short idea field and the table in the language from `.claude/config/lang.md`.
