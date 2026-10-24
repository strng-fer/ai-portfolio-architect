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
3. **Select the role pack** from the target role: `python3 tools/pack_load.py --for-role "<target role>"`.
   - On exit 0, write the pack name into the `Active pack:` line of `.claude/config/pack.md`.
   - On exit 1, list packs with `python3 tools/pack_load.py --list` and ask one question: which pack fits? Then write it.
   - Never guess a pack silently; the pack controls which metrics are legitimate.
4. **Write the evidence ledger** `.claude/skills/portfolio-architect/01b-skill-evidence.md`.
   - Keep the existing table shape. One row per skill named in the profile or the documents.
   - Levels come from what the documents prove, not from what the candidate claims. No artifact means `verified: no` and `evidence: -`.
   - Never upgrade a level above `learning` without an artifact. Ask once, in one line, if a claimed level has no artifact.
   - Validate with `python3 tools/skill_evidence.py check`. Warnings are acceptable at onboarding; errors are not.
5. Seed the mechanism history if it is missing: `python3 tools/mechanism_pick.py list` (read-only, creates nothing). Do not record a mechanism until a project is built.
6. Print max 6 lines: 3 summary bullets + 1 next-step line. No opening paragraph.

Write every document in the language from `.claude/config/lang.md`. Keep file names, pack names, and CSV headers in English.
