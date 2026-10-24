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
| **Proven, Not Asserted** | Every metric row needs a numeric Target, a named Instrument, and a Baseline. `tools/check_portfolio.py` blocks the PDF when a claim cannot be proven |
| **Evidence, Not Claims** | `01b-skill-evidence.md` holds one row per skill with an artifact. Gaps are computed by `tools/skill_evidence.py`, not guessed from self-report |
| **Mechanism, Not Feature** | Ideas are selected from `12-mechanism-catalogue.md` (24 hard mechanisms) by posting signals, novelty against `_history.json`, and hour budget. The top 3 become the 3 ideation options |
| **Role Packs** | `.claude/packs/*.yaml` supply domain-specific metric families, banned idea shapes, and ArXiv policy. Same codebase, different job families (llm, cv, backend, data-eng, mlops, ml, frontend, mobile) |

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
  job_scraper/latest_scrape.json <---- JobStreet / Kalibrr / Indeed / LinkedIn
        |                              (+ glassdoor, zip_recruiter, bayt, naukri,
        |                               bdjobs, hellowork, google via --sites)
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
  tools/check_portfolio.py  <-- validation gate: budgets, sections, provable metrics
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
|   |-- commands/                      # 10 slash commands
|   `-- skills/portfolio-architect/    # 14 knowledge modules (SKILL + 00-12)
|-- .claude/packs/                     # Role packs (llm, cv, backend, data-eng, mlops, ml, frontend, mobile)
|-- .agents/skills/                    # 3 CLI miners (external data)
|   |-- jobspy-search/search.py        # Job scraper entry point (multi-board)
|   |-- jobspy-search/boards.py        # Direct scrapers: JobStreet (SEEK), Kalibrr
|   |-- github-repo-miner/mine_github.py   # GitHub repo references
|   `-- arxiv-paper-miner/mine_arxiv.py    # ArXiv paper references
|-- tools/
|   |-- fetch_page.py                  # Fetch a web page (via Jina Reader)
|   |-- posting_guard.py               # Prompt injection filter for job ads
|   |-- job_digest.py                  # Token-lean job summary (replaces raw JSON reads)
|   |-- ref_digest.py                  # Token-lean repo/paper summary (ranked by relevance)
|   |-- skill_evidence.py              # Validate the evidence ledger, compute gap vs a posting
|   |-- mechanism_pick.py              # Rank build mechanisms for posting signals + history
|   |-- pack_load.py                   # Load and validate a role pack
|   |-- check_portfolio.py             # Validation gate: budgets, sections, provable metrics
|   |-- prompt_contract.py             # Extract the executable contract (commands + metrics)
|   |-- scaffold_repo.py               # Generate a starter repo matching that contract
|   |-- portfolio_status.py            # One-command status across all portfolios
|   |-- compile_diagrams.py            # Render .mmd -> .png (mermaid-cli / Kroki fallback)
|   |-- compile_pdf.py                 # Merge Markdown + render PDF (md-to-pdf)
|   |-- verify_pdf.py                  # Validate PDF pages and document composition
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
pip install python-jobspy requests
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
python .agents/skills/jobspy-search/search.py --query "AI Engineer" --location Indonesia --sites jobstreet,kalibrr --limit 5
```

---

## Usage

All interaction goes through slash commands in [CC] / OpenCode:

| Command | Function |
|---|---|
| `/setup` | Onboarding: read `documents/` or ask 5 questions. Writes the competency and constraint profiles |
| `/scrape "<role>" "<location>"` | Scrape jobs across boards -> compute Portfolio Leverage Score -> compact top 10 table. Board set is configurable via `--sites`, LinkedIn proxies via `--proxies` |
| `/rank` | Re-rank using the `04-gap-evaluation.md` rubric |
| `/applyidea <URL or ID> [--prompts] [--no-pdf]` | Main flow: job analysis -> GitHub/ArXiv research -> 3 options -> conceptual blueprint -> diagrams -> PDF -> tracker. `--prompts` also writes the agent prompt pack |
| `/prompt <portfolio_folder>` | Create or refresh `05_agent_prompts.md`: executable instructions for another agent |
| `/scaffold <portfolio_folder>` | Generate `starter_repo/`: failing tests per milestone, benchmark scripts per metric, `Makefile`, `README` with metric table, `TODO` |
| `/status [portfolio_folder]` | Report every portfolio's state (BLUEPRINT_READY / MARKDOWN_ONLY / INCOMPLETE / UNTRACKED) and the next action |
| `/lang <en\|id>` | Switch output language (default English) |
| `/expand` | Scan new documents/repos to enrich the candidate profile |
| `/reset` | Clear the `job_scraper/` cache (`all` also resets the profile) |

### End-to-End Example

```
1. /setup
   -> "Role: Backend Engineer, 15 h/week, 16GB RAM, fintech interest"

2. /scrape "Backend Engineer" "Jakarta"
   -> 10-row table, for example:
     ID | Company   | Role                | Score | Idea
     7  | Tokopedia | Backend Eng (Golang)| 82    | Distributed rate-limiter

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
| `00_job_analysis.md` | Responsibilities/requirements breakdown, business problem, skill-vs-need table. Gap rows cite the evidence ledger | 450 words |
| `01_project_ideation.md` | 3 mechanisms from `mechanism_pick.py` ranked by signal fit, novelty, and budget, + choice + non-goals | 550 words |
| `02_system_blueprint.md` | Per `05-blueprint-templates.md`: problem, design alternatives, concept architecture (embedded PNG), stack, data & interface concepts, key theory, challenges, metrics, workflow, CV bullets. **No implementation detail** | 1500 words |
| `03_references_study.md` | 3 GitHub repos + 2 ArXiv papers with the part worth studying (1-2 lines each) | 400 words |
| `04_review_report.md` | Quality gate: max 12 findings table, evidence per gate line, `check_portfolio.py` result | 350 words |
| `05_agent_prompts.md` | (optional) Agent prompt pack: P0 context + one prompt per milestone (runnable "Done when") + review prompt | 900 words |
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

## Personalisation: three inputs

Two candidates scoring the same posting get different ideas only when these differ. The pipeline enforces all three.

| Input | File | Tool | What it decides |
|---|---|---|---|
| **Evidence** | `.claude/skills/portfolio-architect/01b-skill-evidence.md` | `tools/skill_evidence.py` | Which stack is reused, which is learned |
| **History** | `portfolios/_history.json` | `tools/mechanism_pick.py` | Which mechanism is novel, which deepens |
| **Pack** | `.claude/config/pack.md` + `.claude/packs/*.yaml` | `tools/pack_load.py` | Which metrics are legitimate, which ideas are banned |

### Evidence ledger

One row per skill. A level above `none` requires an artifact and a `last_used` month, otherwise the row is honest but unproven.

```bash
python tools/skill_evidence.py check              # validate the table
python tools/skill_evidence.py check --strict      # unproven rows block
python tools/skill_evidence.py gap --needs "python,fastapi,qdrant"
```

Gap verdicts: `solid` (reuse as-is), `thin` (prove it publicly), `missing` (new-technology axis). More than 2 `missing` skills means the posting is out of reach: the tool says so and the score should drop.

### Mechanism catalogue

24 hard mechanisms (`span-grounding`, `cascade-routing`, `idempotency`, `drift-detection`, ...) with posting signals, build cost (`S`/`M`/`L`), and metric family. Selection scores signal fit, penalises mechanisms already built, and rewards ones that fit the hour budget.

```bash
python tools/mechanism_pick.py list
python tools/mechanism_pick.py --signals "audit,extraction,ocr" --hours 34 --domain llm
python tools/mechanism_pick.py record --slug my_project --mechanism span-grounding --hours 34
```

### Role packs

Same codebase, different job families. A pack supplies metric families, `forbidden_ideas`, default mechanisms, and whether ArXiv is a useful reference source.

```bash
python tools/pack_load.py --list
python tools/pack_load.py --for-role "AI Engineer"
python tools/pack_load.py --name backend
```

Available: `llm`, `cv`, `backend`, `data-eng`, `mlops`, `ml`, `frontend`, `mobile`. `/setup` picks one from the target role; the `Active pack:` line in `.claude/config/pack.md` is the source of truth.

## Engine Details (Data, Scraper, Limits)

### Data Sources

| Source | Endpoint / Library | Output |
|---|---|---|
| Job postings (native) | `python-jobspy` - indeed, linkedin, glassdoor, zip_recruiter, bayt, naukri, bdjobs, hellowork, google | `job_scraper/latest_scrape.json` |
| Job postings (direct API) | JobStreet Indonesia (SEEK v5 JSON), Kalibrr public board API - see `boards.py` | `job_scraper/latest_scrape.json` |
| GitHub repositories | GitHub Search API `api.github.com/search/repositories` | `job_scraper/github_refs.json` |
| Scientific papers | ArXiv API `export.arxiv.org/api/query` | `job_scraper/arxiv_refs.json` |
| Web pages | Jina Reader `r.jina.ai/<url>` -> direct GET fallback | stdout |

Every record carries a `source` field, so a ranking can be traced back to the board it came from.

### Job Boards

Default set: `jobstreet,kalibrr,indeed,linkedin`. Override with `--sites`.

| Board | Access | Status |
|---|---|---|
| `jobstreet` | Direct SEEK API (`id.jobstreet.com/api/jobsearch/v5`) | works, no auth |
| `kalibrr` | Direct public API (`kalibrr.com/kjs/job_board/search`) | works, no auth |
| `indeed`, `linkedin`, `glassdoor`, `zip_recruiter`, `bayt`, `naukri`, `bdjobs`, `hellowork` | `python-jobspy` | works; LinkedIn may return HTTP 429 on consumer IPs |
| `google` | `python-jobspy` | currently returns no data (upstream scraper broken in 1.4.x) |
| `jobindo` | none | skipped: JS app behind anti-bot, no public search API |
| `glints` | none | skipped: search API requires a logged-in cookie token |

Design points:

- **Per-board isolation.** Each board runs in its own try block, so one 429 or timeout never kills the batch. Failures are listed at the end.
- **Round-robin cap.** Results are interleaved by board before the `--limit * 3` cap, so the last board in the list is never truncated away.
- **Relevance gate.** Kalibrr falls back to its full catalogue when a query matches nothing, so every result is re-checked against the query tokens and dropped if unrelated. Without this, a nonsense query would silently return thousands of unrelated jobs.
- **Deduplication.** Same title + company from two boards is kept once.

### Proxies (LinkedIn)

LinkedIn rate-limits most consumer and datacenter IPs (HTTP 429). Supply a proxy:

```bash
python .agents/skills/jobspy-search/search.py --query "AI Engineer" --location Indonesia \
  --proxies "http://user:pass@host:port" --sites linkedin
```

Or set `JOBSPY_PROXIES` once in the environment. Boards other than LinkedIn do not need it.

### Exit Codes

| Code | Meaning | Cache |
|---|---|---|
| 0 | saved at least one posting | replaced |
| 1 | no postings returned | preserved |
| 2 | `python-jobspy` missing | preserved |

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
| `tools/ref_digest.py --repo 3 --paper 2 --query "<keywords>"` | Repos ranked by query relevance then stars + ArXiv papers | ~12 lines |

Both digest tools fail loudly: `job_digest` exits 1 on a missing/corrupt cache, `ref_digest` exits 1 when there are fewer than `--min` repos or `--min-paper` papers, so the agent cannot silently cite nothing. Without the digests, the agent reads 20-100 KB of raw JSON per call. With them, a few KB.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `python3: command not found` / Windows Store opens | Windows stub alias intercepts | Create a `python3.cmd` shim in `%APPDATA%\npm` pointing at the real `python.exe`; or remove the alias in `%LOCALAPPDATA%\Microsoft\WindowsApps\python3.exe` |
| `ModuleNotFoundError: jobspy` | Module not installed | `pip install python-jobspy` |
| `ModuleNotFoundError: requests` | Direct board scrapers need it | `pip install requests` |
| `[!] linkedin: 429` | LinkedIn rate-limits the IP | Pass `--proxies` or set `JOBSPY_PROXIES`; other boards still work |
| `[i] jobindo: no public search API` | Board has no usable endpoint | Expected. Use `--sites jobstreet,kalibrr,indeed,linkedin` |
| `[i] glints: ... requires a logged-in cookie token` | Board gates its API | Expected. Not scraped |
| `[!] no postings returned. Keeping existing cache` | Query matched nothing on every board | Widen the query; the previous cache is intact |
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
- **Compile PDF:** `tools/compile_pdf.py <portfolio_folder>` - merges `00...05 .md` (fails if none exist), appends a visual diagram appendix when the blueprint does not embed images, then renders via `md-to-pdf` (`PUPPETEER_EXECUTABLE_PATH` auto-detected from Chrome/Edge). An old PDF is deleted first so a stale render can never pass.
- **Verify PDF:** `tools/verify_pdf.py <pdf> [--min-pages N]` - checks the file exists, is >= 5 KB, has the expected page count, contains every source document heading, and has no broken image reference.
- **Check portfolio:** `tools/check_portfolio.py <folder> [--strict]` - the validation gate. Enforces per-file word budgets, required blueprint sections, no code blocks over 5 lines, metric rows with a numeric target + named instrument + real baseline, evidence-bearing review gate lines, and runnable "Done when" commands. Exit 1 blocks the PDF.
- **Skill evidence:** `tools/skill_evidence.py check [--strict]` validates the ledger; `gap --needs "a,b,c"` prints a per-requirement verdict (`solid` / `thin` / `missing`) and exits 1 when more than 2 skills are missing.
- **Mechanism pick:** `tools/mechanism_pick.py --signals "..." --hours N [--domain X]` ranks catalogue mechanisms by signal fit, novelty against `_history.json`, and cost fit. `record` appends the chosen mechanism. `list` shows what is already built.
- **Role pack:** `tools/pack_load.py --list | --name X | --for-role "..."` loads the domain rules: metric families, `forbidden_ideas`, default mechanisms, and ArXiv policy.
- **Prompt contract:** `tools/prompt_contract.py <folder> [--json]` - extracts every `Done when` command and every metric instrument so they can be turned into real files instead of staying prose.
- **Scaffold repo:** `tools/scaffold_repo.py <folder> [--dry-run] [--force]` - writes `starter_repo/` where each milestone has a failing test that names its requirement, each metric has a benchmark script, and the `Makefile` already has every target the prompts reference. Tests fail on purpose until the milestone is implemented.
- **Portfolio status:** `tools/portfolio_status.py [folder] [--json]` - reads the tracker plus artifacts on disk and reports BLUEPRINT_READY, MARKDOWN_ONLY, INCOMPLETE, UNTRACKED, STALE_STATUS, or NEEDS_REVIEW with the next action. Exit 1 when any selected portfolio is not ready.

## Practical Tips

- Empty `documents/` -> `/setup` asks 5 profile questions; no prepared CV needed.
- Clear the scrape cache without touching the profile: `/reset` with no arguments.
- Reset profile + cache: `/reset all`.
- Target a specific company: add its name to the `/scrape` query, e.g. `/scrape "Backend Tokopedia" "Jakarta"`.
- Narrow the boards when you only trust one source: `--sites jobstreet,kalibrr` (default `jobstreet,kalibrr,indeed,linkedin`).
- 15 h/week and 2-3 weeks are the default constraint template; edit `.claude/skills/portfolio-architect/02-constraints-profile.md` any time.
- Token saving: run `/applyidea <id> --prompts` once, then work the milestones with another agent using `05_agent_prompts.md`. Use `/scaffold` only when you need a starter repo.
- Blueprints are intentionally conceptual. Need implementation detail? Have another agent execute the prompt pack instead of adding code sections to the blueprint.
- Language: instructions stay English; documents follow `.claude/config/lang.md`. Chat follows the language you write in.

## License & Sources

- Job scraping library: [python-jobspy](https://pypi.org/project/python-jobspy/) - use responsibly, respect robots and portal terms of service.
- System structure, skills, tools, and templates are local configuration in this repository, free to modify.
