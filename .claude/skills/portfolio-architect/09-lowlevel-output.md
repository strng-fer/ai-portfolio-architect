# Compact Output Templates (Ideation, Analysis, References, Review)

Every file uses tables and bullets. No opening prose. No repeated conclusions.
Depth rule and word budgets come from `08-token-discipline.md`: concept only, no DDL, no payloads, no code blocks, no folder trees.

## `00_job_analysis.md` - max 450 words
1. `## Posting Summary` - company, role, level, 3 lines of business context.
2. `## Core Requirements` - table: Requirement (from posting) | Weight (high/medium) | Project implication. Max 8 rows.
3. `## Candidate Gap` - table: Area | Status (solid / thin / missing) | How this project closes it.
4. `## Business Problems Worth Attacking` - one paragraph + bullets listing specific technical problems.

## `01_project_ideation.md` - max 550 words
Table of 3 options: Option | Idea (one sentence) | User (who + what they do today) | Problem absorbed | New technology | Est. hours | Risk.
- Option 1 = recommended, Option 2 = infra/scalability focus, Option 3 = AI/data/feature focus.
- Every row names one audience from `01c-product-intent.md`. "Recruiters" and "everyone" are rejected.
- `## Choice` - one paragraph: why Option 1 wins against the candidate's time limits and gaps.
- `## Deliberately Excluded` - 3 bullets of features not being built.
- In product mode add one line under the table: what the shipped URL does in one sentence, and what the user sees when the mechanism fails.

## `03_references_study.md` - max 400 words
Repo table: Name | Why relevant | Part to study (one line). Max 3.
Paper table: Title | Idea adopted | Part to study. Max 2.
URLs must come from `github_refs.json` / `arxiv_refs.json`. Never invent a URL.
If `ref_digest.py` exits 1 (not enough references), say so in one line instead of padding with popular-but-irrelevant repos.

## `04_review_report.md` - max 350 words
Findings table: # | Area | Problem | Severity | Fix. Max 12 rows.
Quality gate - one line per criterion, and **each line must carry evidence**, not a bare yes/no:

```
- Anti-CRUD: yes - `02_system_blueprint.md` section 8 is built around span verification, not a list view.
- Realistic in time: yes - 24h total vs 32h ceiling in `02-constraints-profile.md`.
- Metrics provable: yes - 2 metrics, both with an instrument and a baseline in section 9.
- Diagrams rendered: yes - `diagrams/system_architecture.png` 51 KB, `user_workflow.png` 57 KB.
- Word budgets: yes - 00=420, 01=530, 02=1480, 03=390, 04=340, 05=880. (Product mode: `02` may reach 1750.)
- `check_portfolio.py`: pass - 0 errors, 1 warning (appendix image).
- `product_fit.py`: pass - 96/100, audience and URL both named (product mode only).
```

`## Verdict` - one line (PASS / PATCH) + max 3 bullets of changes applied.

## Review application rule
Minimal diff in failing sections only. Never rewrite a file that already passed.
A gate line with `no` forces a PATCH verdict.
