---
description: Reset the profile or clear the scrape cache (no narration)
---

If `$ARGUMENTS` = `all`: reset `.claude/skills/portfolio-architect/01-candidate-profile.md` and `02-constraints-profile.md` to empty templates, then delete cache files in `job_scraper/` (never the `portfolios/` folder).
Without arguments: delete only cache files in `job_scraper/`.

Print one line listing what was deleted or reset. Never touch `.claude/config/lang.md`.
