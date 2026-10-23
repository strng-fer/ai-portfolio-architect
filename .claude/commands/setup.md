---
description: Onboard the candidate profile with compact output
---

Run `/setup`:

1. Check `documents/cv/`, `documents/linkedin/`, `documents/transcripts/`, `documents/past_projects/`.
   - Files found: read them and extract into the profile. Never quote document contents in chat.
   - Empty: ask the 5 questions below **in one message**, numbered, max one line each:
     1. Background + strongest language/framework?
     2. Target role?
     3. Hours per week for portfolio work?
     4. Machine specs + free-tier only?
     5. Preferred industry domain?
2. Write `.claude/skills/portfolio-architect/01-candidate-profile.md` and `02-constraints-profile.md` using compact tables/bullets (max 40 lines each). Do not add new sections.
3. Print max 6 lines: 3 summary bullets + 1 next-step line. No opening paragraph.

Write both files in the language from `.claude/config/lang.md`.
