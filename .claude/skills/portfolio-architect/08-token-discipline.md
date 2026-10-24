# Token Discipline & Output Contract

Goal: keep quality high while burning as few tokens as possible. Documents are the product. Chat is only status.

## 1. Chat rules (applies to every command)

- **Never** print drafts, file contents, long tables, or reasoning in chat.
- One status line per phase. Example: `[1/4] job data + references ready`.
- Final output max **10 lines**: PDF path, prompt pack path (or `-`), 3 bullets, 1 next step.
- Do not restate the user's request, do not summarize the document you just wrote, do not offer extra help.
- Never copy file contents into chat "for confirmation". Write the file, name the path.
- No emoji, no banners, no decorative tables.

## 2. Read rules (input tokens)

- **Never** read `latest_scrape.json`, `github_refs.json`, or `arxiv_refs.json` in full. They are tens of KB.
  Use `python3 tools/job_digest.py` and `python3 tools/ref_digest.py`.
- Read long files by line range (`offset`/`limit`) or with `grep`. Read in full only if under 150 lines.
- Never re-read a file you just wrote.
- Never read `PLAN.md` or `README.md` to perform a task. Need a rule? Read the relevant skill module.
- Read a reference file once per session. Keep a 1-line takeaway internally, not in chat.

## 3. Write rules (output tokens)

Word ceilings per file. Hard limits, not suggestions.

| File | Max words | Contents |
|---|---|---|
| `00_job_analysis.md` | 450 | posting requirements, gap, one business-problem paragraph |
| `01_project_ideation.md` | 550 | 3 compact options + choice + non-goals |
| `02_system_blueprint.md` | 1500 | concept architecture, data, metrics, workflow |
| `03_references_study.md` | 400 | 3 repos + 2 papers, 1-2 lines each |
| `04_review_report.md` | 350 | max 12 findings, table format |
| `05_agent_prompts.md` | 900 | 1 context prompt + 1 per milestone + 1 review prompt, each with a runnable "Done when" |

Additional rules:
- No duplication across files. State a fact once, where it matters most.
- No restating conclusions at the end of every section.
- No filler openers ("Sure", "Here is"). Go straight to content.
- Tables are cheaper than repeated prose. Use them for comparisons.

## 4. Depth rules (concept, not code)

A blueprint is a **decision and understanding document**, not an implementation tutorial.

Forbidden inside a blueprint:
- Code blocks longer than 5 lines, long pseudocode, `CREATE TABLE` DDL, full JSON payloads.
- Per-file folder trees, complete dependency lists, Docker configuration.
- Install steps, shell commands, or step-by-step tutorials.
- Internal function or class names. Describe component responsibilities, not symbols.

Required: problem, actors, flow, components + responsibilities, data concepts, interface concepts, key theory, metrics, risks, non-goals, workflow, CV bullets.

Code detail belongs in `05_agent_prompts.md` (as short instructions for another agent) or in `/scaffold` (optional).

## 5. Budget per `/applyidea` phase

| Phase | Work limit |
|---|---|
| 1. Acquire + research | 3 digest tool calls, no dumps |
| 2. Draft | write all files in one pass, no style revisions |
| 3. Review | minimal diff patch, not a rewrite |
| 4. Render + PDF | run the tool, report 1 line |

The reviewer may only change sections that failed the quality gate. Never rewrite a file that already passed.

## 6. Tool execution
- One call per step, once per phase. Do not re-run a tool just to display its output again.
- Always run `python3 tools/check_portfolio.py <folder>` before rendering. It enforces budgets, required sections, and provable metrics. Exit code 1 blocks the PDF.
- Never open or read a finished PDF or PNG. Trust `verify_pdf.py`.
- Quote at most the last 5 lines of an error log.

## 7. General prohibitions

- Never repeat PDF contents in chat after compiling.
- Never add a second executive summary inside a document.
- Never add sections outside the template.
- Never ask for confirmation mid-flow unless data is genuinely missing.
- Never write in a language other than the one configured in `.claude/config/lang.md`.
