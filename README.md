# AI Portfolio Architect

An AI-agent system ([CC] / OpenCode / other AI CLIs) that analyzes real job postings, maps skill gaps, mines GitHub and ArXiv references, then designs a **production-grade Portfolio Project Blueprint** - with architecture diagrams, conceptual Markdown documents, and a PDF.

**Languages:** English (default, this file) | [Bahasa Indonesia](README.id.md)
Switch output language with `/lang en` or `/lang id`.

---

## Core Concepts

| Component | Role |
|---|---|
| **Portfolio Leverage Score** | 0-100 fit score for a job posting (weights: Skill-Bridge 40, Problem Clarity 30, Reusability 30) |
| **Drafter-Reviewer Loop** | A draft is produced, then critiqued by a "Staff Engineer" reviewer persona before finalization |
| **Anti-CRUD Rule** | No generic CRUD ideas (to-do apps, e-commerce catalogs, social clones). Every idea must attack a specific technical challenge from the posting |
| **Google XYZ Formula** | CV bullet formula: *"Achieved [X] as measured by [Y], by doing [Z]"* |
| **Concept, Not Code** | Blueprints carry ideas, design, theory, problems, solutions, metrics, and workflow. Implementation detail goes to `05_agent_prompts.md` or `/scaffold` |
| **Token-Lean** | Chat is status only, documents have word budgets, input goes through digest scripts. Rules: `.claude/skills/portfolio-architect/08-token-discipline.md` |
| **Agent Prompt Pack** | `05_agent_prompts.md` holds a P0 context prompt + one prompt per milestone + a review prompt, ready for Cursor/[CC]/Codex |

## Workflow Architecture

```
documents/ (CV, LinkedIn, transcripts)
        |
        v
     /setup --------------> .claude/skills/portfolio-architect/
        |                    01-candidate-profile.md
        |                    02-constraints-profile.md
        v
   /scrape "<role>" "<location>" --> .agents/skills/jobspy-search/search.py
        |                                   |
        v                                   v
  job_scraper/latest_scrape.json <---- Indeed / LinkedIn / Glassdoor
        |
        v
      /rank ---------------> job_scraper/ranked_jobs.json
        |
        v
  /applyidea <URL | ID> [--prompts] --> job_scraper/current_job_raw.txt
        |                                    | posting_guard.py (prompt injection filter)
        |                                    v
        |                             current_job_clean.md
        |--> .agents/skills/github-repo-miner/mine_github.py --> github_refs.json
        |--> .agents/skills/arxiv-paper-miner/mine_arxiv.py  --> arxiv_refs.json
        |                                    | tools/ref_digest.py (compact summary)
        v                                    v
  portfolios/<company>_<role>/
        |-- 00_job_analysis.md
        |-- 01_project_ideation.md     (3 project options)
        |-- 02_system_blueprint.md     (concept architecture, data, theory, metrics, workflow, CV bullets)
        |-- 03_references_study.md     (3 GitHub repos, 2 ArXiv papers)
        |-- 04_review_report.md        (quality gate, max 12 findings)
        |-- 05_agent_prompts.md        (optional --prompts: executable prompts)
        `-- diagrams/
              |-- *.mmd                (Mermaid source)
              `-- *.png                (rendered by compile_diagrams.py)
        |
        v
  tools/compile_pdf.py --> Blueprint_Final.md --> Blueprint_Final.pdf
        |                        (verify_pdf.py)
        v
  portfolio_tracker.csv  (status: BLUEPRINT_READY)
        |
        v
   /prompt ------------> 05_agent_prompts.md   (for another agent)
   /scaffold ----------> starter_repo/         (optional boilerplate)
```

## Directory Structure

```
ai-portfolio-architect/
|-- CLAUDE.md                          # System rules (read by the AI agent)
|-- AGENTS.md                          # Mirror of CLAUDE.md (OpenCode standard)
|-- README.md                          # English docs (default)
|-- README.id.md                       # Indonesian docs
|-- PLAN.md                            # Original build spec (legacy, gitignored)
|-- setup_cli_links.sh                 # Cross-CLI integration script
|-- portfolio_tracker.csv              # Tracker of all generated blueprints
|-- .claude/
|   |-- settings.json                  # Bash permission whitelist
|   |-- config/lang.md                 # Output language setting (single source of truth)
|   |-- commands/                      # 9 slash commands
|   `-- skills/portfolio-architect/    # 11 knowledge modules (SKILL + 00-10)
|-- .agents/skills/                    # 3 CLI miners (external data)
|   |-- jobspy-search/search.py        # Job scraper (indeed/LinkedIn/glassdoor)
|   |-- github-repo-miner/mine_github.py   # GitHub repo references
|   `-- arxiv-paper-miner/mine_arxiv.py    # ArXiv paper references
|-- tools/
|   |-- fetch_page.py                  # Fetch a web page (via Jina Reader)
|   |-- posting_guard.py               # Prompt injection filter for job ads
|   |-- job_digest.py                  # Token-lean job summary (replaces raw JSON reads)
|   |-- ref_digest.py                  # Token-lean repo/paper summary
|   |-- compile_diagrams.py            # Render .mmd -> .png (mermaid-cli / Kroki fallback)
|   |-- compile_pdf.py                 # Merge Markdown + render PDF (md-to-pdf)
|   |-- verify_pdf.py                  # Validate PDF existence and size
|   `-- .puppeteer-config.json         # (auto-generated) Chrome/Edge executablePath
|-- documents/                         # Candidate documents (cv/, linkedin/, transcripts/, past_projects/)
|-- job_scraper/                       # Scrape cache (latest_scrape.json, ranked_jobs.json, *_refs.json)
|-- portfolios/                        # Blueprint output per job
|-- templates/                         # Boilerplate assets (used by /scaffold, prompt pack example)
`-- .opencode/command -> .claude/commands   # Mirror (so slash commands work in OpenCode)
```

---

## Prerequisites

| Component | Requirement | Notes |
|---|---|---|
| **Python** | >= 3.10 | On Windows set up a `%APPDATA%\npm\python3.cmd` shim (see Troubleshooting) |
| **Node.js** | >= 18 (npx available) | Renders Mermaid diagrams and converts to PDF |
| **Google Chrome / MS Edge** | At least one installed | Puppeteer engine for mermaid-cli and md-to-pdf |
| **Git Bash (Windows)** | Optional | To run `setup_cli_links.sh` |
| **Internet access** | Required | Job scraping, GitHub API, ArXiv API |

## Setup

### 1. Install Python dependencies

```bash
pip install python-jobspy
```

### 2. Install global Node packages (diagram + PDF rendering)

```bash
npm install -g --allow-scripts=puppeteer @mermaid-js/mermaid-cli
npm install -g --allow-scripts=puppeteer md-to-pdf
```

> `--allow-scripts=puppeteer` matters so the Chromium postinstall runs.
> If Chromium fails to launch on Windows (code `0xC000007B`), the system falls back automatically to the installed Chrome/Edge via `tools/.puppeteer-config.json`.

### 3. Run the integration script (CLI linkage)

**Linux / macOS:**
```bash
bash setup_cli_links.sh
```

**Windows (Git Bash):**
```bash
"C:\Program Files\Git\bin\bash.exe" setup_cli_links.sh
```

The script does four things:
1. Copies `CLAUDE.md` -> `AGENTS.md` -> modern AI CLIs read agent config from `AGENTS.md`. A plain copy is used (not a symlink) because it works on every filesystem, including Windows without developer mode. Re-run the script after editing `CLAUDE.md`.
2. Copies `.claude/commands/*.md` -> `.opencode/command/` -> slash commands work in OpenCode.
3. `chmod +x tools/*.py .agents/skills/*/*.py` -> scripts are executable.
4. Creates `.claude/config/lang.md` with `Output language: English` if missing.

### 4. Verify the installation

```bash
python tools/fetch_page.py "https://example.com"              # must exit 0
python .agents/skills/github-repo-miner/mine_github.py --query "python" --limit 2
python .agents/skills/arxiv-paper-miner/mine_arxiv.py --query "rag" --limit 2
python .agents/skills/jobspy-search/search.py --query "backend engineer jakarta" --limit 5
```

---

## Usage

All interaction goes through slash commands in [CC] / OpenCode:

| Command | Function |
|---|---|
| `/setup` | Onboarding: read `documents/` or ask 5 questions. Writes the competency and constraint profiles |
| `/scrape "<role>" "<location>"` | Scrape jobs -> compute Portfolio Leverage Score -> compact top 10 table |
| `/rank` | Re-rank using the `04-gap-evaluation.md` rubric |
| `/applyidea <URL or ID> [--prompts] [--no-pdf]` | Main flow: job analysis -> GitHub/ArXiv research -> 3 options -> conceptual blueprint -> diagrams -> PDF -> tracker. `--prompts` also writes the agent prompt pack |
| `/prompt <portfolio_folder>` | Create or refresh `05_agent_prompts.md`: executable instructions for another agent |
| `/scaffold <portfolio_folder>` | Optional. Compact starter repo (skeleton, docker, TODO) |
| `/lang <en\|id>` | Switch output language (default English) |
| `/expand` | Scan new documents/repos to enrich the candidate profile |
| `/reset` | Clear the `job_scraper/` cache (`all` also resets the profile) |

### End-to-End Example

```
1. /setup
   -> "Role: Backend Engineer, 15 h/week, 16GB RAM, fintech interest"

2. /scrape "Backend Engineer" "Jakarta"
   -> 10-row table, for example:
     ID | Company | Role                | Score | Idea
     7  | Kredivo | Backend Eng (Golang)| 82    | Distributed rate-limiter

3. /applyidea 7 --prompts
   -> 4 phases, chat shows status only:
     [1/4] job data + references ready
     [2/4] draft 00-03 + 05 + 2 diagrams
     [3/4] review gate passed
     [4/4] PDF + tracker

4. Execute with another agent using portfolios/<slug>/05_agent_prompts.md
   -> /scaffold portfolios/<slug> only if you want a starter repo
```

> What the agent reads: `job_digest.py` (10 lines) + `ref_digest.py` (5 lines) + 3 skill modules. Not a 96 KB JSON file.

---

## Blueprint Output Specification

Each `portfolios/<company>_<role>/` folder contains:

| File | Required content | Budget |
|---|---|---|
| `00_job_analysis.md` | Responsibilities/requirements breakdown, business problem, skill-vs-need table | 450 words |
| `01_project_ideation.md` | 3 options: (1) primary recommendation, (2) infrastructure focus, (3) AI/data focus + non-goals | 550 words |
| `02_system_blueprint.md` | Per `05-blueprint-templates.md`: problem, design alternatives, concept architecture (embedded PNG), stack, data & interface concepts, key theory, challenges, metrics, workflow, CV bullets. **No implementation detail** | 1500 words |
| `03_references_study.md` | 3 GitHub repos + 2 ArXiv papers with the part worth studying (1-2 lines each) | 400 words |
| `04_review_report.md` | Quality gate: max 12 findings table + verdict | 350 words |
| `05_agent_prompts.md` | (optional) Agent prompt pack: P0 context + one prompt per milestone + review prompt | 900 words |
| `diagrams/*.mmd` | Mermaid source (`flowchart` for `system_architecture`, `sequenceDiagram` for `user_workflow`) | max 15 nodes |
| `diagrams/*.png` | Rendered automatically from `.mmd` | - |
| `Blueprint_Final.md` | Combined document (auto-generated, includes 04 & 05) | - |
| `Blueprint_Final.pdf` | Final PDF | - |
| `starter_repo/` | (if `/scaffold` ran) compact boilerplate | - |

**What is committed:** the Markdown sources (`00`-`05`), `.mmd` diagram sources, and `portfolio_tracker.csv`.
**What is regenerated locally (gitignored):** `Blueprint_Final.pdf`, `Blueprint_Final.md`, and `diagrams/*.png`. Run `tools/compile_diagrams.py` and `tools/compile_pdf.py` to rebuild them after a clone.

**Forbidden in a blueprint:** code blocks over 5 lines, `CREATE TABLE` DDL, full JSON payloads, per-file folder trees, install tutorials, internal function names. Execution detail moves to `05_agent_prompts.md` or `/scaffold`.

## Mermaid Rules (required for a clean PNG)

1. `system_architecture.mmd` -> `flowchart TD` or `flowchart LR`
2. `user_workflow.mmd` -> `sequenceDiagram`
3. **Wrap labels containing parentheses or special characters in double quotes:**
   - Correct: `A["FastAPI (Backend)"] --> B["PostgreSQL / pgvector"]`
   - Wrong: `A[FastAPI (Backend)] --> B[PostgreSQL / pgvector]`
4. No HTML tags (`<br/>`) inside `sequenceDiagram`

---

## Engine Details (Data, Scraper, Limits)

### Data Sources

| Source | Endpoint / Library | Output |
|---|---|---|
| Job postings | `python-jobspy` (indeed, LinkedIn, glassdoor*; jobstreet when the library supports it) | `job_scraper/latest_scrape.json` |
| GitHub repositories | GitHub Search API `api.github.com/search/repositories` | `job_scraper/github_refs.json` |
| Scientific papers | ArXiv API `export.arxiv.org/api/query` | `job_scraper/arxiv_refs.json` |
| Web pages | Jina Reader `r.jina.ai/<url>` -> direct GET fallback | stdout |

> \* Glassdoor is **dropped automatically** when the location contains "indonesia"/"jakarta", because the country is unsupported.

### `python-jobspy` 1.4.0 Limits (current release)

- `jobstreet` is **not supported** on PyPI (valid sites: linkedin, indeed, zip_recruiter, glassdoor, google, bayt, naukri, bdjobs, hellowork).
- The script reports new versions automatically if `python-jobspy` adds jobstreet support - no code edit needed.
- For a custom JobStreet scraper, watch the upstream repo: https://github.com/cullenwatson/jobs-scraper

### Anti Prompt Injection

All job text from the internet **must** pass through:

```bash
python tools/posting_guard.py <file_raw> > <file_clean>
```

Lines matching these patterns are dropped:
- `ignore (all) previous/prior instructions`
- `system prompt`
- `you are now a ...`
- `disregard above`

### Token-Lean Digests

| Script | Function | Output |
|---|---|---|
| `tools/job_digest.py list --top 10` | One line per job: id, company, role, location, score, detected stack | ~10 lines |
| `tools/job_digest.py detail <id>` | One job's detail, description cut at 1800 chars (`--full` for the whole text) | ~15 lines |
| `tools/ref_digest.py --repo 3 --paper 2` | Repos by stars + ArXiv papers | ~12 lines |

Without the digests, the agent reads 20-100 KB of raw JSON per call. With them, a few KB.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `python3: command not found` / Windows Store opens | Windows stub alias intercepts | Create a `python3.cmd` shim in `%APPDATA%\npm` pointing at the real `python.exe`; or remove the alias in `%LOCALAPPDATA%\Microsoft\WindowsApps\python3.exe` |
| `ModuleNotFoundError: jobspy` | Module not installed | `pip install python-jobspy` |
| `Invalid site_name: 'jobstreet'` (older jobspy) | Library lacks support | Handled automatically - invalid sites are skipped (`[i] Site not supported ... skipped`) |
| Chromium launch fail `0xC000007B` / `2147483651` | Downloaded puppeteer Chromium cannot run here | Already automatic: uses `tools/.puppeteer-config.json` + `PUPPETEER_EXECUTABLE_PATH` pointing at installed Chrome/Edge |
| `npx` not found by Python (WinError 2) | On Windows `subprocess` needs `.cmd`; npx is `npx.cmd` | Handled - scripts use `shutil.which("npx")` |
| `UnicodeEncodeError: cp1252` when printing web text | Windows console is not UTF-8 by default | Handled in `fetch_page.py`, `posting_guard.py`, `job_digest.py`, `ref_digest.py` - `sys.stdout.reconfigure(encoding="utf-8")` |
| `HTTP Error 403` when rendering via Kroki | Cloudflare blocks the network/IP | Automatic fallback to mermaid-cli (npx) |
| ArXiv timeout on the first attempt | Slow network/relay; timeout is 30s | Run the command again - manual retry |
| PDF missing or failed | Node/npx not running, or Chromium failed to launch | `compile_pdf.py` exits 1 - run `verify_pdf.py` to diagnose |
| Slash commands missing in OpenCode | `.opencode/command` mirror not created | Run `bash setup_cli_links.sh` (or the Windows shortcut) |
| WSL error `Windows Subsystem for Linux has no installed distributions` | Default bash points at WSL | Use Git Bash: `"C:\Program Files\Git\bin\bash.exe" setup_cli_links.sh` |

---

## View Layer Detail

- **Compile diagrams:** `tools/compile_diagrams.py <diagrams_folder>` - renders every `.mmd` to `.png`, in priority order: (1) `npx mermaid-cli` + puppeteer config pointing at installed Chrome/Edge; (2) Kroki API fallback; (3) exit 1 if both fail.
- **Compile PDF:** `tools/compile_pdf.py <portfolio_folder>` - merges `00...05 .md`, appends a visual diagram appendix when the blueprint does not embed images, then renders via `md-to-pdf` (`PUPPETEER_EXECUTABLE_PATH` auto-detected from Chrome/Edge).
- **Verify PDF:** `tools/verify_pdf.py <pdf>` - checks the file exists and is >= 5 KB.

## Practical Tips

- Empty `documents/` -> `/setup` asks 5 profile questions; no prepared CV needed.
- Clear the scrape cache without touching the profile: `/reset` with no arguments.
- Reset profile + cache: `/reset all`.
- Target a specific company: add its name to the `/scrape` query, e.g. `/scrape "Backend Kredivo" "Jakarta"`.
- 15 h/week and 2-3 weeks are the default constraint template; edit `.claude/skills/portfolio-architect/02-constraints-profile.md` any time.
- Token saving: run `/applyidea <id> --prompts` once, then work the milestones with another agent using `05_agent_prompts.md`. Use `/scaffold` only when you need a starter repo.
- Blueprints are intentionally conceptual. Need implementation detail? Have another agent execute the prompt pack instead of adding code sections to the blueprint.
- Language: instructions stay English; documents follow `.claude/config/lang.md`. Chat follows the language you write in.

## License & Sources

- Job scraping library: [python-jobspy](https://pypi.org/project/python-jobspy/) - use responsibly, respect robots and portal terms of service.
- System structure, skills, tools, and templates are local configuration in this repository, free to modify.
