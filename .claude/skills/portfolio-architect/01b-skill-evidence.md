# Skill Evidence Inventory

Claims are cheap. Evidence is not. Every row here must name an artifact that a reviewer could open: a repo, a commit range, a deployed endpoint, a report, a course certificate, or a shipped document.

This file is the **input** to gap scoring. `01-candidate-profile.md` is the narrative summary; this file is the ledger. When the two disagree, this file wins.

## How to fill a row

| Column | Rule |
|---|---|
| Skill | One concrete technology or capability. `PyTorch`, not `AI`. `Postgres indexing`, not `databases` |
| Level | `none` / `learning` / `working` / `strong`. No other value |
| Evidence | One artifact, or `-` when level is `none`. Never a vague phrase like "used before" |
| Last used | `YYYY-MM`, or `-` for `none` |
| Verified | `yes` (artifact public or checkable) / `no` (self-report only) / `stale` (older than 18 months) |

Level meaning:

- **none** - never used, no mental model. A gap that must be built from fundamentals.
- **learning** - followed a tutorial or course, no independent build. Thin.
- **working** - shipped something alone, would need a docs refresh. Extendable.
- **strong** - shipped repeatedly, can debug from first principles. Reusable as-is.

## Inventory

| Skill | Level | Evidence | Last used | Verified |
|---|---|---|---|---|
| Python | strong | - | - | no |
| PyTorch | working | - | - | no |
| YOLO (object detection) | working | - | - | no |
| OpenCV | working | - | - | no |
| FastAPI | working | - | - | no |
| Docker | learning | - | - | no |
| Git | working | - | - | no |
| Qdrant / vector DB | none | - | - | - |
| LLM application engineering | learning | - | - | no |
| RAG retrieval | learning | - | - | no |
| OCR pipelines | none | - | - | - |
| MLOps (registry, CI gates) | none | - | - | - |
| Model monitoring / drift | none | - | - | - |
| SQL / Postgres | learning | - | - | no |
| Evaluation harness design | none | - | - | - |
| Cloud deployment | none | - | - | - |

## Gap Rules

Gap status per posting requirement:

| Evidence found | Gap status | What the project must do |
|---|---|---|
| `strong` or `working`, `verified yes` | **solid** | Reuse as-is, do not re-teach |
| `working`, `verified no` or `stale` | **thin** | Prove it publicly once |
| `learning` | **thin** | Build one real mechanism with it |
| `none`, or skill absent from the table | **missing** | Make it the project's new-technology axis |

A project may carry **at most two missing skills**. Three or more means the posting is out of reach for the current budget: lower its score instead of pretending.

## Maintenance

- `/setup` writes this file and asks the candidate to confirm each level.
- `/expand` appends rows when new documents, repos, or endpoints are found. It never upgrades a level without an artifact.
- `/applyidea` reads this file during gap scoring and cites the exact row it used.
- `python tools/skill_evidence.py check` validates the table.
- `python tools/skill_evidence.py gap --needs "python,fastapi,qdrant"` prints the gap verdict for a posting.

Keep this file under 60 lines. One row per skill, no duplicates.
