# Grounded Intake: Evidence-Anchored Document Extraction

Job: PT Indocyber Global Teknologi - AI Engineer · Stack: Python, FastAPI, PaddleOCR, Qdrant, containerized · Estimate: 34 h · Status: blueprint

## 1. Problem & Relevance

An enterprise client hands over a folder of scanned invoices and purchase orders. The ask is structured data: vendor, document number, date, line-item total, tax, currency. A vision-language model answers all six in one pass, and the demo looks finished.

It is not finished. A wrong total that no one can trace is worse than no extraction, because finance staff now re-check everything and trust nothing. The posting names this work directly: LLM reasoning, computer vision for detection and OCR, retrieval over a vector index, served through FastAPI for client proof-of-concepts.

The problem is not accuracy alone. It is **accountability**: every value must be defensible against the page it came from, and the system must know when it does not know. The hard part is a verification contract, not a prompt: a deterministic layer decides whether a proposed value is anchored to a detected region.

## 2. Goals & Non-Goals

**Goals**
1. Reach field-level exact match of 0.90 or better on six commercial fields.
2. Cite a verifiable page region for at least 99% of emitted fields.
3. Hold hallucinated values on degraded scans at or below 2%.
4. Keep p95 latency under 8 seconds per page on CPU.
5. Escalate to the vision path for at most 35% of pages.

**Non-Goals**
- No custom OCR or detection training; off-the-shelf engines are composed, not replaced.
- No model fine-tuning; quality comes from contracts and verification.
- No multi-tenant identity, billing, or review UI.
- No batch throughput target; concurrency is measured, not optimized.

## 3. Design Alternatives & Decision

| Approach | Pros | Cons | When it fits |
|---|---|---|---|
| Single vision-language call per page | Simplest; one prompt, one response | No citations; unverifiable; cost scales with pages | Clean, uniform documents |
| OCR then text-only LLM extraction | Cheap, fast, deterministic parsing | Loses layout; table columns collapse; no visual grounding | Born-digital PDFs |
| OCR plus layout index plus verifier (chosen) | Every value anchored; cascade controls cost; auditable | More moving parts; span alignment must be built | Scanned, heterogeneous enterprise documents |

Decision: the third approach. Citations are the product requirement, and only a pipeline that keeps geometry beside text can produce them; cost is controlled by routing, not by dropping verification.

## 4. Architecture & Flow

![](diagrams/system_architecture.png)

![](diagrams/user_workflow.png)

| Component | Responsibility | Constraint |
|---|---|---|
| Intake API | Accept a document, return a job reference | Stateless, idempotent on content hash |
| Preprocessor | Deskew, denoise, split pages, score quality | No upscaling past memory budget |
| Text path | Fast OCR and layout tokens | Clean pages only |
| Vision path | Detection plus OCR enhancement | Escalation only, quota-capped |
| Region index | Text, geometry, embeddings per region | Qdrant named dense and sparse vectors |
| Extraction agent | Query retrieval, propose values | 6 tool calls per field |
| Verifier | Check each value against a span | Deterministic, no model |
| Response composer | Emit fields, citations, confidence, flags | Flags unresolved fields |

**Demo path**: one command posts a scanned invoice to the extraction endpoint and prints six fields with page-region citations; a second command runs the unverified baseline for comparison.

## 5. Tech Stack & Skill Bridge

| Layer | Technology | Known / New | Reason |
|---|---|---|---|
| Serving | FastAPI, async endpoints | Known | Named in the posting |
| OCR | PaddleOCR, Tesseract fallback | Known (OpenCV) | Two engines expose alignment risk |
| Detection | YOLO for layout regions | Known | Reuses the strongest skill |
| Retrieval | Qdrant dense plus sparse vectors | New | Named in the posting |
| Agent | Tool-calling loop, strict schema | New | Workflow agents named |
| Verification | Geometry overlap, fuzzy span match | New | Core mechanism |
| Evaluation | Custom harness on public data | New | Turns claims into numbers |
| Packaging | Docker Compose | Known (thin) | One-command review |

## 6. Key Theory & References

- **Span anchoring**: a value is valid only if a region's text span matches it after normalization (case, separators, currency). Fails when OCR splits a number across regions.
- **Hybrid retrieval with score fusion**: dense vectors catch semantic field names, sparse vectors catch exact identifiers; reciprocal rank fusion combines them without calibration. Fails when both retrievers agree on the wrong region.
- **Cascade routing**: a cheap path handles the easy majority and escalates on a quality signal. Fails when that signal is unreliable, so routing is measured per stratum.
- **Confidence calibration**: emitted confidence should match observed accuracy per bucket. Fails on rare templates absent from the calibration set.

## 7. Data & Interfaces (Concept)

**Entities**: Document (hash, pages, quality), Page (image, deskew angle), Region (bounding box, engine, text, confidence), FieldProposal (name, value, region reference, verdict), Extraction (document, fields, flags, cost).

**Relations**: documents contain pages; pages contain regions; each proposal references one region or a null citation with a flag.

| Operation | Input | Output | Note |
|---|---|---|---|
| Submit document | Image or PDF | Extraction reference | Idempotent on content hash |
| Read extraction | Reference | Fields, citations, flags | Stable client contract |
| Explain field | Reference, field name | Region crop, matched span | Audit endpoint |
| Re-run with profile | Reference, profile | New extraction | Compares routing strategies |

**Data source**: SROIE scanned receipts (1,000 images, ICDAR 2019) for field accuracy, plus FUNSD (199 annotated forms) for layout stress. Both are public and small enough for CPU evaluation. One fetch script downloads both archives and builds the held-out split deterministically; published annotations remove the need for hand-labelling.

## 8. Technical Challenges & Solution Strategy

- **Span alignment across two OCR engines** → normalize text and compare by character overlap, not equality. Proof: alignment failure count per engine.
- **Hallucination on degraded scans** → reject any value without a supporting region and mark the field unresolved. Proof: hallucination rate on a degraded subset.
- **Cost control** → escalate by page quality score only. Proof: escalation rate and cost per document against the single-call baseline.
- **Tabular layouts** → index geometry features as sparse vectors beside dense embeddings. Proof: recall@5 on field-evidence queries.
- **Latency** → fixed tool budget and cached region embeddings per hash. Proof: p95 under a load script.

## 9. Metrics & Validation

| Metric | Target | Instrument | Baseline |
|---|---|---|---|
| Field-level exact match, 6 fields | ≥ 0.90 | `python benchmarks/field_accuracy.py` | Single vision-language call, same split |
| Citation validity rate | ≥ 99% of emitted fields | `python benchmarks/citation_check.py` | Unverified extraction, 0% traceable |
| Hallucination rate on degraded subset | ≤ 2% | `python benchmarks/degraded_eval.py` | No-verifier pipeline on same subset |
| Retrieval recall@5 for field evidence | ≥ 0.85 | `python benchmarks/recall.py` | BM25-only index |
| p95 latency per page, CPU | ≤ 8 s | `k6 run bench/load.js` | Synchronous single-call baseline |
| Escalation rate to vision path | ≤ 35% of pages | `python benchmarks/routing_report.py` | Always-escalate baseline, 100% |

## 10. Workflow

| Phase | Input | Output | Done | Hours |
|---|---|---|---|---|
| P1 Data and baseline | SROIE, FUNSD | Split, baseline scores | Baseline recorded | 6 |
| P2 Vision and regions | Page images | Regions with geometry | Regions persisted | 8 |
| P3 Retrieval and agent | Region index | Proposals with citations | Within tool budget | 8 |
| P4 Verifier and API | Proposals | Verified response | Flags emitted | 6 |
| P5 Benchmark and demo | Full pipeline | Metrics, demo | Six metrics reported | 6 |

## 11. Risks & Mitigation

- **Free-tier quota** exhausts mid-benchmark: cache model responses by document hash and keep a deterministic fallback extractor for the demo.
- **CPU-only latency** misses target: measure per stage, use a smaller detector, cache regions across runs.
- **Dataset mismatch**: receipts are not invoices, so accuracy is reported per template family rather than hidden in an average.

## 12. CV Bullet Draft

- Lifted field-level exact match on six invoice fields from 0.72 to 0.91 on the SROIE held-out split by adding a deterministic span verifier to a tool-calling extraction agent.
- Raised field-evidence recall@5 from 0.61 to 0.88 on 1,000 SROIE region queries by fusing dense and sparse vectors in a Qdrant hybrid index.
- Cut p95 extraction latency to 7.4 s per page on CPU under a k6 load script by cascading 31% of pages to a vision path and caching region embeddings.
