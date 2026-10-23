# Compact Output Templates (Ideation, Analysis, References, Review)

Every file uses tables and bullets. No opening prose. No repeated conclusions.
Depth rule and word budgets come from `08-token-discipline.md`: concept only, no DDL, no payloads, no code blocks, no folder trees.
Write every generated document, table heading, diagram label, and chat status line in the language from `.claude/config/lang.md` (English default).

## `00_job_analysis.md` - max 450 words
1. `## Posting Summary` - company, role, level, 3 lines of business context.
2. `## Core Requirements` - table: Requirement (from posting) | Weight (high/medium) | Project implication. Max 8 rows.
3. `## Candidate Gap` - table: Area | Status (solid / thin / missing) | How this project closes it.
4. `## Business Problems Worth Attacking` - one paragraph + bullets listing specific technical problems.

## `01_project_ideation.md` - max 550 words
Table of 3 options: Option | Idea (one sentence) | Problem absorbed | New technology | Est. hours | Risk.
- Option 1 = recommended, Option 2 = infra/scalability focus, Option 3 = AI/data/feature focus.
- `## Choice` - one paragraph: why Option 1 wins against the candidate's time limits and gaps.
- `## Deliberately Excluded` - 3 bullets of features not being built.

## `03_references_study.md` - max 400 words
Repo table: Name | Why relevant | Part to study (one line). Max 3.
Paper table: Title | Idea adopted | Part to study. Max 2.
URLs must come from `github_refs.json` / `arxiv_refs.json`. Never invent a URL.

## `04_review_report.md` - max 350 words
Findings table: # | Area | Problem | Severity | Fix. Max 12 rows.
Quality gate (yes/no, one line each): anti-CRUD, realistic within constraints, measurable metrics, diagrams rendered, non-goals explicit, word budgets met.
`## Verdict` - one line (PASS / PATCH) + max 3 bullets of changes applied.

## Review application rule
Minimal diff in failing sections only. Never rewrite a file that already passed.
