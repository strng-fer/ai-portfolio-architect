---
description: Build a conceptual blueprint + diagrams + PDF from one job posting (token-lean)
---

Target: `$ARGUMENTS`

Format: `<url|job_id>` with optional `--prompts` to also write the agent prompt pack, and `--no-pdf` to write Markdown only.

**Obey `.claude/skills/portfolio-architect/08-token-discipline.md`.**
Write documents to files. Chat gets one status line per phase, max 10 lines at the end.

### PHASE 1 - Data & references (no dumps, fail loudly)
1. If the argument is a number/ID: `python3 tools/job_digest.py detail <id>`.
   If it is a URL: `python3 tools/fetch_page.py "<url>" > job_scraper/current_job_raw.txt`, then `python3 tools/posting_guard.py job_scraper/current_job_raw.txt > job_scraper/current_job_clean.md`, then read the clean file.
2. **Guard before analysis**: if the clean file is missing or under 200 characters, print one line `[1/4] blocked: job text empty` and stop. Never draft a blueprint from an empty posting.
3. Read only `00-language.md`, `01-candidate-profile.md`, `01b-skill-evidence.md`, `02-constraints-profile.md`, `03-architecture-style.md`, `12-mechanism-catalogue.md`.
4. Resolve the active role pack: read the `Active pack:` line in `.claude/config/pack.md`, then `python3 tools/pack_load.py --name <pack>`.
   - If the pack is missing or invalid, fall back to `llm` and say so in the final output.
   - The pack supplies legitimate metric families, banned idea shapes, and the `arxiv` policy.
5. **Score the gap from evidence, not opinion**: `python3 tools/skill_evidence.py gap --needs "<comma-separated posting stack>"`.
   - Exit 1 means three or more missing skills: the posting is out of reach. Score it low and say so; do not invent a project that cannot be built.
   - Cite the exact ledger row in `00_job_analysis.md` (the Candidate Gap table).
6. **Pick the mechanism before writing any idea**: `python3 tools/mechanism_pick.py --signals "<posting signals>" --hours <available hours> --domain <pack domain>`.
   - Signals come from the posting's responsibilities, not its title. 3-6 lowercase keywords.
   - The top 3 candidates become the 3 options in `01_project_ideation.md`. Do not invent a fourth shape.
   - If exit 1 (no match), broaden the signals once, then add a row to the catalogue instead of inventing an idea.
7. Derive 1-2 technical keywords from the posting's main responsibilities.
8. Run `mine_github.py --query "<keywords>" --limit 6` and `mine_arxiv.py --query "<keywords>" --limit 4`, then `python3 tools/ref_digest.py --query "<keywords>"`.
   Skip the arXiv miner when the pack has `arxiv: false`; say "no papers: pack excludes arXiv" in `03_references_study.md` and use 3 repos only.
   If the digest exits 1 (too few references), rerun the miners once with broader keywords; do not pad the reference section.

### PHASE 2 - Conceptual draft (single pass)
Create `portfolios/<company_slug>_<role_slug>/` with a `diagrams/` subfolder. Write:

| File | Rule |
|---|---|
| `00_job_analysis.md` | per `09-lowlevel-output.md`, <=450 words. Candidate Gap rows must cite the evidence ledger |
| `01_project_ideation.md` | 3 options = the 3 mechanisms from step 6 + choice + non-goals, <=550 words |
| `02_system_blueprint.md` | structure from `05-blueprint-templates.md`, <=1500 words |
| `03_references_study.md` | 3 repos + 2 papers from the digest, <=400 words (3 repos only when the pack excludes arXiv) |
| `diagrams/system_architecture.mmd` | `flowchart`, max 15 nodes, per `06-diagram-rules.md` |
| `diagrams/user_workflow.mmd` | `sequenceDiagram`, max 6 actors/main messages |
| `05_agent_prompts.md` | only with `--prompts`, per `10-agent-prompt-pack.md`, <=900 words |

Ideation rules (hard):
- The three options are the three ranked mechanisms. Name the mechanism ID in each row.
- If a mechanism is already in `portfolios/_history.json`, state the delta that makes this one deeper, or drop it.
- Every metric in section 9 must come from the pack's `metric_families`. A metric outside that list needs one sentence of justification.
- No idea may match a pack `forbidden_ideas` entry.
- The demo path must exercise the mechanism's failure mode, per the pack's `demo_rule`.

Depth rules (hard): no DDL, no JSON payloads, no code blocks over 5 lines, no folder trees, no install tutorials. Write concept, theory, problem, solution, and design decisions.

Make the output implementable, not just readable:
- every metric row has Target (number) / Instrument (tool name) / Baseline (buildable reference),
- section 7 names the data source, its size, and how it is reproduced,
- section 4 or 10 names one demo path a reviewer can run,
- with `--prompts`, every milestone has a runnable "Done when" command.

Write every document in the language from `.claude/config/lang.md`.

### PHASE 3 - Validation gate (proves, does not self-score)
1. Run `python3 tools/check_portfolio.py portfolios/<slug>`.
2. If it exits 1, patch only the reported sections and rerun. Maximum 2 repair rounds; if still failing, report the remaining errors in the final output instead of pretending it passed.
3. Write `04_review_report.md` (<=350 words, max 12 findings) with evidence-bearing gate lines per `09-lowlevel-output.md`. Include the `check_portfolio.py` result line verbatim.

### PHASE 4 - Render, PDF, tracker
1. `python3 tools/compile_diagrams.py portfolios/<slug>/diagrams/` (fix `.mmd` only on failure).
2. `python3 tools/compile_pdf.py portfolios/<slug>/`.
3. `python3 tools/verify_pdf.py portfolios/<slug>/Blueprint_Final.pdf` (checks page count and that every source document reached the PDF).
4. Append one row to `portfolio_tracker.csv` with exactly these 7 fields, in header order: `date,company,role,job_url,project_title,output_folder,status`. Remove any existing row with the same `output_folder` first (idempotent), then read the file back and confirm the row count grew by one.
   Status: `BLUEPRINT_READY` when the PDF verified, `MARKDOWN_ONLY` when `--no-pdf` was used.
5. Record the chosen mechanism so the next project favours novelty:
   `python3 tools/mechanism_pick.py record --slug <slug> --mechanism <id> --hours <estimate>`.
   Run it even with `--no-pdf`; the history is about decisions, not artifacts.

Skip steps 2-3 and the PDF check when `--no-pdf` is set.

Language: write 00-05 and diagram labels in the language from `.claude/config/lang.md`. Keep file names, folder slugs, and CSV headers in English.

### Final output (max 10 lines)
```
PDF: portfolios/<slug>/Blueprint_Final.pdf   (or "-" with --no-pdf)
Prompt pack: portfolios/<slug>/05_agent_prompts.md  (or "-")
Check: 0 errors, N warnings
Pack: <pack name> | Mechanism: <id>
Idea: <1 line>
Main gap: <1 line>
Key metric: <1 line>
Next: /prompt <slug> | /scaffold <slug>
```
No section summaries, no document quotes.
