---
description: Build a conceptual blueprint + diagrams + PDF from one job posting (token-lean)
---

Target: `$ARGUMENTS`

Format: `<url|job_id>` with optional `--prompts` to also write the agent prompt pack, and `--no-pdf` to write Markdown only.

**Obey `.claude/skills/portfolio-architect/08-token-discipline.md`.**
Write documents to files. Chat gets one status line per phase, max 10 lines at the end.

### PHASE 1 - Data & references (no dumps)
1. If the argument is a number/ID: `python3 tools/job_digest.py detail <id>`.
   If it is a URL: `python3 tools/fetch_page.py "<url>" > job_scraper/current_job_raw.txt`, then `python3 tools/posting_guard.py job_scraper/current_job_raw.txt > job_scraper/current_job_clean.md`, then read the clean file.
2. Read only `00-language.md`, `01-candidate-profile.md`, `02-constraints-profile.md`, `03-architecture-style.md`.
3. Derive 1-2 technical keywords from the posting's main responsibilities.
4. Run `mine_github.py --query "<keywords>" --limit 6` and `mine_arxiv.py --query "<keywords>" --limit 4`, then `python3 tools/ref_digest.py`.
   Never read `github_refs.json` / `arxiv_refs.json` raw.

### PHASE 2 - Conceptual draft (single pass)
Create `portfolios/<company_slug>_<role_slug>/` with a `diagrams/` subfolder. Write:

| File | Rule |
|---|---|
| `00_job_analysis.md` | per `09-lowlevel-output.md`, <=450 words |
| `01_project_ideation.md` | 3 options + choice + non-goals, <=550 words |
| `02_system_blueprint.md` | structure from `05-blueprint-templates.md`, <=1500 words |
| `03_references_study.md` | 3 repos + 2 papers from the digest, <=400 words |
| `diagrams/system_architecture.mmd` | `flowchart`, max 15 nodes, per `06-diagram-rules.md` |
| `diagrams/user_workflow.mmd` | `sequenceDiagram`, max 6 actors/main messages |
| `05_agent_prompts.md` | only with `--prompts`, per `10-agent-prompt-pack.md`, <=900 words |

Depth rules (hard): no DDL, no JSON payloads, no code blocks over 5 lines, no folder trees, no install tutorials. Write concept, theory, problem, solution, and design decisions. Execution detail may appear only in `05_agent_prompts.md` as short instructions.

Write every document in the language from `.claude/config/lang.md`.

### PHASE 3 - Review gate (minimal patch)
Score the 6 criteria in `09-lowlevel-output.md`. Patch only failing sections. Write `04_review_report.md` (<=350 words, max 12 findings).

### PHASE 4 - Render & PDF
1. `python3 tools/compile_diagrams.py portfolios/<slug>/diagrams/` (fix `.mmd` only on failure).
2. `python3 tools/compile_pdf.py portfolios/<slug>/` - PDF includes 00-05 when present.
3. `python3 tools/verify_pdf.py portfolios/<slug>/Blueprint_Final.pdf`.
4. Append one row to `portfolio_tracker.csv` (date, company, role, project title, folder, `BLUEPRINT_READY`).

Skip steps 2-3 when `--no-pdf` is set.

Language: write 00-05 and diagram labels in the language from `.claude/config/lang.md`. Keep file names, folder slugs, and CSV headers in English.

### Final output (max 10 lines)
```
PDF: portfolios/<slug>/Blueprint_Final.pdf
Prompt pack: portfolios/<slug>/05_agent_prompts.md  (or "-")
Idea: <1 line>
Main gap: <1 line>
Key metric: <1 line>
Next: /prompt <slug> | /scaffold <slug>
```
No section summaries, no document quotes.
