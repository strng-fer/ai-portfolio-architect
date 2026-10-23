# Candidate Documents Folder (`/setup`)

Put your career documents in these subfolders before running `/setup`:

- `cv/` : latest CV (`.pdf`, `.md`, or `.tex`)
- `linkedin/` : exported PDF of your LinkedIn profile
- `transcripts/` : grade transcripts or list of courses/certifications
- `past_projects/` : `README.md` or a short description of projects you have built

If this folder is empty, `/setup` starts an interactive interview instead.

Detected files are read into `.claude/skills/portfolio-architect/01-candidate-profile.md` and are never printed to chat in full.
