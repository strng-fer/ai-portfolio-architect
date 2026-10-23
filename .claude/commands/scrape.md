---
description: Scrape jobs and score portfolio potential (10-line output, token-lean)
---

Search parameters: `$ARGUMENTS`

1. Run `python3 .agents/skills/jobspy-search/search.py --query "$ARGUMENTS" --location "<location or Indonesia>" --limit 15`.
2. Run `python3 tools/job_digest.py list --top 15`. **Never** read `latest_scrape.json` raw.
3. Read only `.claude/skills/portfolio-architect/01-candidate-profile.md` and `04-gap-evaluation.md`.
4. Score each candidate 0-100 with the 40/30/30 rubric. Score from title + stack + short description; do not open `detail` for every job - at most 3 details for the top candidates.
5. Write `job_scraper/ranked_jobs.json` (same array plus `score` and `short_idea`, max 12 words).
6. Print **only a 10-row table**: `ID | Company | Role | Score | Short idea`. No explanatory prose.
7. Close with one line: `Next: /applyidea <ID> --prompts`.

Write the table and the short idea field in the language from `.claude/config/lang.md`.
