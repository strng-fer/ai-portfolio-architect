# Agent Prompt Pack - Grounded Intake

How to use: run P0 once at the start of every session, then one milestone per session in order.
Each prompt stands alone; a fresh agent needs no chat history.
Keep the README's three sections current after every milestone.

## P0 - Context Prompt

**Goal**: Establish shared context and project skeleton before any extraction code.

**Context**: `02_system_blueprint.md` sections 1, 4, 9; `01_project_ideation.md` Choice.

**Task**: 1. Read both files. 2. Create the README with What it does, How to run, How to see the demo. 3. Copy the six target metrics into `metrics.md` as empty rows. 4. Restate the four non-goals in one line.

**Constraints**: Python 3.11, FastAPI, PaddleOCR, Qdrant, Docker Compose. CPU only, 16 GB RAM, free-tier LLM quota. No training, no fine-tuning, no review UI. Code identifiers, paths, and commands stay English.

**Deliverable**: `README.md` with three sections, `metrics.md` with six rows, `Makefile` with a `check` target.

**Done when**: `make check` prints the three README section names and exits 0.

**Out of scope**: Dataset download, OCR, retrieval, HTTP endpoints.

## P1 - Data and Baseline

**Goal**: A reproducible evaluation split and a naive single-call baseline score.

**Context**: `02_system_blueprint.md` sections 7 and 9.

**Task**: 1. Fetch SROIE and FUNSD into `data/`. 2. Build a seeded held-out split. 3. Implement the single vision-language call baseline. 4. Score field-level exact match for six fields. 5. Record the baseline row in `metrics.md`.

**Constraints**: Cache every model response on disk keyed by document hash. No API key in source. Dataset under 500 MB. No prompt tuning between runs.

**Deliverable**: `data/fetch.py`, `benchmarks/field_accuracy.py`, baseline row filled.

**Done when**: `python benchmarks/field_accuracy.py --baseline` prints six per-field scores and exits 0.

**Out of scope**: Retrieval, verification, HTTP endpoints.

## P2 - Vision and Region Store

**Goal**: Pages become regions with text, geometry, engine tag, and quality score.

**Context**: `02_system_blueprint.md` sections 4 and 8.

**Task**: 1. Implement deskew and page quality scoring. 2. Run PaddleOCR with Tesseract fallback. 3. Detect layout regions with YOLO. 4. Persist regions with bounding boxes. 5. Report cross-engine text disagreement.

**Constraints**: No upscaling past the memory budget. Every region keeps its engine tag. CPU inference only. Derived artifacts are keyed by document hash.

**Deliverable**: Preprocessor module, region store, `benchmarks/alignment_report.py`.

**Done when**: `python benchmarks/alignment_report.py` prints disagreement counts for both engines and exits 0.

**Out of scope**: LLM calls, retrieval, escalation routing.

## P3 - Retrieval and Agent

**Goal**: The agent proposes six field values, each backed by retrieved regions.

**Context**: `02_system_blueprint.md` sections 6, 7, and 8.

**Task**: 1. Build the Qdrant collection with dense and sparse named vectors. 2. Implement reciprocal rank fusion. 3. Define the region-search tool contract. 4. Implement the bounded agent loop at six tool calls per field. 5. Emit proposals with region references.

**Constraints**: Tool budget fixed, not adaptive. No answer outside the schema. Embeddings cached by document hash. Every LLM response replayable from cache.

**Deliverable**: Retrieval module, agent module, `benchmarks/recall.py`.

**Done when**: `python benchmarks/recall.py` prints recall@5 and exits 0.

**Out of scope**: Verifier verdicts, HTTP endpoints, routing.

## P4 - Verifier and API

**Goal**: Only anchored values leave the service.

**Context**: `02_system_blueprint.md` sections 4, 8, and 9.

**Task**: 1. Implement span normalization and character-overlap matching. 2. Reject values without a supporting region and flag the field. 3. Expose submit, read, and explain endpoints. 4. Add idempotency on document hash. 5. Wire the demo command.

**Constraints**: The verifier calls no model. Unresolved fields return a flag, never a guess. Response shape stays stable. One API key, no multi-tenancy.

**Deliverable**: Verifier module, FastAPI app, `make demo`.

**Done when**: `make demo` prints six fields with citations and exits 0.

**Out of scope**: Benchmarking, routing tuning, deployment.

## P5 - Review and Benchmark

**Goal**: Six metrics measured against their baselines, three runs each, median reported.

**Context**: `02_system_blueprint.md` section 9; `metrics.md`.

**Task**: 1. Run each benchmark three times and take the median. 2. Compare every metric with its stated baseline. 3. Run the load script for p95 latency. 4. Write a findings table: metric, baseline, median, delta, verdict. 5. Update the README demo section.

**Constraints**: Report failures as failures. No prompt tuning between runs. Cap LLM spend at the free tier. No refactoring.

**Deliverable**: `benchmarks/report.md` with six rows, updated README.

**Done when**: `make bench` writes `benchmarks/report.md` with six metric rows and exits 0.

**Out of scope**: New features, refactors, extra datasets.
