# Getting Started

This guide is for someone who has just cloned the repository and wants a finished portfolio project blueprint. It assumes no prior knowledge of the system.

If you want the design rationale instead, read [README.md](README.md). If you want the Indonesian version, read [README.id.md](README.id.md).

---

## 1. What you get

You give it a job posting. You get back a folder containing:

| Output | What it is |
|---|---|
| `00_job_analysis.md` | What the posting actually asks for, and where your evidence does not yet reach |
| `01_project_ideation.md` | Three candidate projects, ranked, with the reasoning |
| `02_system_blueprint.md` | The design: problem, alternatives, architecture, theory, metrics, workflow |
| `03_references_study.md` | Three real repositories and two papers worth reading, with the specific part to study |
| `04_review_report.md` | A quality gate that proves the blueprint meets its own rules |
| `05_agent_prompts.md` | Ready-to-paste prompts that let another agent build the project |
| `Blueprint_Final.pdf` | Everything above, as one document you can send to a recruiter |
| `diagrams/*.png` | Architecture and workflow diagrams |

The blueprint is deliberately **conceptual**. It contains no code, no schema, no tutorial. It is the document you would write before building, and the one you defend in an interview.

---

## 2. Install

Requirements: Python 3.10+, Node 18+, and Chrome or Edge installed.

```bash
git clone <this-repo>
cd ai-portfolio-architect

pip install python-jobspy requests pyyaml

npm install -g --allow-scripts=puppeteer @mermaid-js/mermaid-cli
npm install -g --allow-scripts=puppeteer md-to-pdf

bash setup_cli_links.sh
```

On Windows, run the last line as:

```bash
"C:\Program Files\Git\bin\bash.exe" setup_cli_links.sh
```

Verify the install:

```bash
python tools/pack_load.py --list          # should list 8 role packs
python tools/mechanism_pick.py list       # should list 24 mechanisms
python tools/skill_evidence.py check      # warnings are fine at this stage
```

If a command fails, see Troubleshooting in [README.md](README.md).

---

## 3. Onboarding: three things must be true

The system only produces personal output if it knows three things about you. Skipping any one of them degrades the result to generic advice.

### 3.1 Tell it who you are

Put your CV, LinkedIn export, or transcripts into `documents/cv/`, `documents/linkedin/`, `documents/transcripts/`, or `documents/past_projects/`. Then run:

```
/setup
```

With documents present it reads them. With the folders empty it asks five short questions instead. Either way it writes:

- `01-candidate-profile.md` — the narrative summary
- `02-constraints-profile.md` — your hours, hardware, and budget
- `01b-skill-evidence.md` — the ledger (see below)

It also picks a **role pack** from your target role.

### 3.2 Fill the evidence ledger

This is the single highest-leverage file in the repository. Open `.claude/skills/portfolio-architect/01b-skill-evidence.md`.

Every row is one skill, and every level above `none` needs an artifact:

| Skill | Level | Evidence | Last used | Verified |
|---|---|---|---|---|
| Python | strong | `github.com/you/scraper` | 2026-08 | yes |
| FastAPI | working | `github.com/you/api-demo` | 2026-05 | yes |
| Kubernetes | none | - | - | - |

Levels mean:

- `none` — never used. This is what a project should teach you.
- `learning` — followed a tutorial, no independent build.
- `working` — shipped something alone, would need a docs refresh.
- `strong` — shipped repeatedly, can debug from first principles.

`verified: yes` means a reviewer could open the artifact. If you cannot link it, use `verified: no` and the tool treats the row as thin.

The fastest way to fill this in bulk is `/expand <your-github-url>`, which reads your repos and appends rows.

Check your work:

```bash
python tools/skill_evidence.py check
```

Warnings mean a level is claimed without proof. They are acceptable while you are still assembling artifacts, and they disappear as you add them.

### 3.3 Confirm your role pack

```bash
python tools/pack_load.py --for-role "Backend Engineer"
```

The `Active pack:` line in `.claude/config/pack.md` decides which metrics are legitimate and which idea shapes are banned. Available packs:

| Pack | For |
|---|---|
| `llm` | AI engineer, LLM engineer, applied scientist |
| `cv` | computer vision, perception |
| `ml` | data scientist, ML engineer, research engineer |
| `mlops` | ML platform, MLOps |
| `backend` | backend, platform, SRE |
| `data-eng` | data engineer, analytics engineer |
| `frontend` | frontend, full stack |
| `mobile` | Android, iOS, Flutter |

If your role has no pack, see section 8.

---

## 4. Your first project, end to end

```
/setup
/scrape "Backend Engineer" "Jakarta"
/applyidea 3 --prompts
```

That is the whole loop. What happens inside:

**`/scrape`** searches JobStreet, Kalibrr, Indeed, and LinkedIn, then scores every posting 0–100 using your evidence ledger:

- 40 points — how much of the stack you already cover, computed from the ledger
- 30 points — how clearly the posting names a technical challenge
- 30 points — how reusable the resulting stack is across companies

You get a ten-row table. The `Score` column is personal: the same posting scores differently for you than for someone else.

**`/applyidea 3`** takes the posting and does five things in order:

1. Scores your gap against the posting stack. If three or more skills are missing, it says the posting is out of reach and lowers the score instead of inventing a project you cannot finish.
2. Ranks mechanisms from the catalogue against the posting's signals, penalising anything already in your history.
3. Uses the top three mechanisms as the three project options.
4. Writes the blueprint, the diagrams, and the review gate.
5. Renders the PDF and records the chosen mechanism so your next project favours something new.

Add `--prompts` to also get the agent prompt pack. Add `--no-pdf` if you only want Markdown.

---

## 5. Worked example: a backend engineer

Same tool, different pack. Suppose the ledger says:

| Skill | Level | Verified |
|---|---|---|
| Go | working | yes |
| PostgreSQL | working | yes |
| Docker | working | yes |
| Kubernetes | none | - |
| Kafka | learning | no |

And the posting is a payments backend role naming "idempotent payment processing, high throughput, exactly-once delivery."

```
/scrape "Backend Engineer" "Jakarta"
```

Suppose the posting scores 78. Then:

```bash
python tools/skill_evidence.py gap --needs "go,postgresql,kafka,kubernetes"
```

Output: `go` solid, `postgresql` solid, `kafka` thin, `kubernetes` missing. One missing skill — workable, and Kubernetes is the new axis.

```bash
python tools/mechanism_pick.py --signals "idempotent,payment,throughput,exactly-once" --hours 30 --domain backend
```

Output ranks `idempotency` (S, 6–12 h) and `exactly-once-sink` (M) above `backpressure`. Because `idempotency` is cheap and fits your budget, it becomes option 1: a payment intake service where duplicate submissions collapse to one effect, proven by a duplicate-rate benchmark against a naive insert.

That is a project you can finish in two weekends, and it answers a named requirement in the posting. Notice the pack is what made it a backend project: the `backend` pack forbids "to-do app" and requires a fault-injection run, and its metric families are p95, throughput, and duplicate rate rather than citation validity.

---

## 6. The daily loop

Once the blueprint exists, building is a separate job. The blueprint's job is to stop you from wandering.

```
/status                                  # where is everything?
/prompt portfolios/<slug>                # refresh the agent prompt pack
/scaffold portfolios/<slug>              # generate a starter repo
```

`/scaffold` writes a repo where each milestone has a failing test that names its requirement, each metric has a benchmark script, and the `Makefile` already has every target the prompts reference. The tests fail on purpose until you implement the milestone.

Then hand `05_agent_prompts.md` to Cursor, Claude Code, Codex, or any agent. Each prompt is self-contained: goal, context, task, constraints, deliverable, a runnable "Done when", and an out-of-scope list.

---

## 7. What good output looks like

A blueprint is finished when:

- Every metric row has a number, a named instrument, and a baseline you can actually build.
- The data source is named with its size and a way to reproduce it.
- One demo path exists that a reviewer can run.
- `python tools/check_portfolio.py portfolios/<slug>` exits 0.
- The PDF exists and `tools/verify_pdf.py` confirms every source document reached it.

The tool refuses to render a PDF when those are not true. If it blocks you, it is doing its job.

---

## 8. Customising for your own domain

### Add a role pack

Create `.claude/packs/<name>.yaml`:

```yaml
name: security
label: Application Security
domain: security
summary: Systems where the hard part is proving an attack fails.
target_roles:
  - security engineer
  - appsec engineer
metric_families:
  - attack success rate
  - false positive rate
  - detection latency
forbidden_ideas:
  - vulnerability scanner wrapper
  - CTF writeup collection
arxiv: false
default_mechanisms:
  - prompt-injection-guard
  - audit-trail
  - rate-limit-fairness
demo_rule: The demo must run a real attack that fails against the new control.
```

Then validate:

```bash
python tools/pack_load.py --name security
python tools/pack_load.py --for-role "Security Engineer"
```

Set `Active pack: security` in `.claude/config/pack.md`.

### Add a mechanism

Add one row to the table in `.claude/skills/portfolio-architect/12-mechanism-catalogue.md`. Keep the seven columns identical. The `Posting signals` cell is what the picker matches on, so use words that actually appear in postings.

Validate that your pack references still resolve:

```bash
python tools/mechanism_pick.py list
```

### Change the output language

```
/lang id
```

Documents follow `.claude/config/lang.md`. File names, folder slugs, and CSV headers stay English so the tool keeps working across languages.

---

## 9. Common questions

**Why did it tell me my posting is out of reach?**
Your ledger shows three or more `missing` skills for that stack. That is a real signal, not a bug. Either pick a closer posting or accept a longer build.

**Why do I get warnings from `skill_evidence.py check`?**
A level is claimed with no artifact. Add a repo link and set `verified: yes`, or lower the level to `none`.

**Why did it choose a mechanism I did not expect?**
Because it already appears in `portfolios/_history.json`. The tool penalises repetition so your portfolio shows range. Delete the entry if you genuinely want to build it again.

**Can I use this for a non-technical role?**
Partly. The scrapers, blueprints, and metrics work for any role that names technical challenges. Roles whose work is not measurable by a benchmark (pure design, pure management) fit poorly, because every blueprint must carry provable numbers.

**Can two people use one clone?**
No. The ledger, constraints, pack, and history are all personal. Give each person their own clone. The tool is one codebase per person by design; sharing a clone would mean sharing a candidate.

**Where does it store my data?**
Everything is local. `documents/` is gitignored, `job_scraper/` is gitignored, and `portfolios/_history.json` is gitignored. Nothing is uploaded except the job queries sent to the job boards and the keyword queries sent to GitHub and ArXiv.

---

## 10. Where to read next

| You want | Read |
|---|---|
| Why the design works this way | [README.md](README.md) |
| Every command in detail | `.claude/commands/*.md` |
| The rules the agent follows | `CLAUDE.md` |
| How scoring works | `.claude/skills/portfolio-architect/04-gap-evaluation.md` |
| The mechanism list | `.claude/skills/portfolio-architect/12-mechanism-catalogue.md` |
| Output depth rules | `.claude/skills/portfolio-architect/08-token-discipline.md` |
