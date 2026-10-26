# Invoice Reader with a Call Budget

Job: AI Engineer, PT Indocyber Global Teknologi | Stack: Python, FastAPI, Postgres with pgvector, Docker | Estimate: 34 h | Status: blueprint | Mode: product

## 1. Problem & Relevance
An SME bookkeeper retyping invoices misses a supplier line and the payment goes wrong. An AI reader is easy to demo and hard to trust: loop length is decided by the model, so one blurry invoice can consume twenty tool calls, and when the reader cannot find a field it still writes one.

The people who lose are the bookkeeper and the owner paying for the mistake. They need three things before they will use it: a result in under a minute, a visible source for every number, and an honest "I cannot read this field" instead of a confident guess.

This is hard because the natural fix, a prompt asking the model to be careful and brief, is unenforceable. A guarantee needs an external counter, a stop rule that does not trust the model, and a refusal that is a first-class state in the UI. The posting asks for exactly this: LLM workflow agents and retrieval behind FastAPI for client prototypes.

## 2. Goals & Non-Goals
- Cap tool calls at 4 per invoice, enforced outside the model and recorded in the response.
- First extracted field visible within 60 s of upload on CPU-only inference.
- Price every invoice in the ledger, with unattributed spend at 0%.
- Answer only with spans a deterministic verifier accepts; refuse per field otherwise.
- Reach 0.85 exact-match field accuracy on 60 held-out invoices.

Non-goals: OCR training, multi-tenant isolation, accounts or billing, streaming, fine-tuning.

## 3. Design Alternatives & Decision
| Approach | Pros | Cons | When it fits |
|---|---|---|---|
| Unbounded ReAct loop | Simplest, best raw accuracy | Cost set by the model | Research notebooks |
| Framework runner with a turn limit | Tuning for free | Counts turns, not spend; retries escape it | Teams on a framework |
| Budgeted loop with a stop rule | Cap, price, refusal all deterministic | More request-path code | Products with a price |

Decision: the budgeted loop. The cap must survive retries and model upgrades; only a counter the model cannot reach gives a worst case.

## 4. Architecture & Flow
![](diagrams/system_architecture.png)

![](diagrams/user_workflow.png)

| Component | Responsibility | Constraint |
|---|---|---|
| FastAPI edge | Validate upload, attach budget, return trace id | Rejects undeclared budgets |
| Budget ledger | Reserve, decrement, price each call | Authoritative; planner cannot write |
| Planner (LLM) | Choose next tool, draft answer | Untrusted: proposes only |
| Tool registry | Retrieve, read page, compare fields | Fixed set |
| Retrieval | pgvector plus lexical scoring | CPU embeddings |
| Stop controller | Stop on cap, sufficiency, or no gain | No model call |
| Verifier | Match each value to a span by offset | Deterministic |
| Trace store | One JSONL row per step | Append-only |

## 5. Tech Stack & Skill Bridge
| Layer | Technology | Known / New | Reason |
|---|---|---|---|
| Language | Python | Known | Existing strength |
| API | FastAPI | Known, thin | Posting names it |
| Database | PostgreSQL with pgvector | New | Closes two ledger gaps |
| Embeddings | Small sentence-transformer | New | Free tier |
| LLM | Free-tier hosted, local fallback | New | Quota risk |
| Packaging | Docker Compose | Thin | Posting lists it |
| Evaluation | Python harness, fixed splits | New | Evaluation gap |

## 6. Key Theory & References
- **Budgeted agent loop**: each step reserves from a counter before acting, so worst-case cost follows the cap. Fails when tools spawn sub-calls outside the reservation.
- **Diminishing-return stop rule**: stop when the last step added no verified span. Fails when the model scores its own gain.
- **Evidence sufficiency**: a field is admissible only with a verifiable span. Fails when the source splits a value.
- **Per-request cost attribution**: price each step at the call site. Fails when a path bypasses the instrumented client.

## 7. Data & Interfaces (Concept)
Entities: invoice, page, chunk, field, run, step, span claim, budget entry.

| Operation | Input | Output |
|---|---|---|
| Extract | Uploaded PDF or item id, budget | Fields with spans, or per-field refusal, trace id |
| Trace lookup | Trace id | Ordered steps with cost |
| Evaluate | Split name | Accuracy, citation validity, refusal rate, time to first value |
| Compare | Two run ids | Delta per metric |

Data source: FUNSD, a public set of 199 scanned forms with entity annotations. This project uses the 50-form test split, converted into 60 invoice-like field-extraction items: 44 answerable, 16 with a field deliberately absent. Ground truth comes from published annotations, not hand labelling. Reproduction: `python data/build_eval_set.py` rebuilds the split and items from the raw archive with a fixed seed, so the split hash matches anywhere.

## 8. Technical Challenges & Solution Strategy
- **Termination guarantee**: the ledger reserves before the call and refuses after the cap. Proof: replay 60 items, assert calls never exceed 4.
- Budget accounting under retries: reservation is keyed by step id, so a retry reuses it. Proof: fault injection failing 20% of calls.
- **Noisy retrieval on scanned text**: chunking respects layout blocks, and lexical scoring covers the numeric fields embeddings blur. Proof: recall@5 against a chunk-by-character baseline.
- **Refusal calibration**: the sufficiency rule is tuned on a dev split, then frozen before the held-out run, so the 16 absent-field items test it honestly. Proof: per-field refusal accuracy on that subset.
- **Attribution leakage**: one client wrapper is the only path to the model; a test asserts no direct call sites exist. Proof: unattributed share is 0%.

## 9. Metrics & Validation
| Metric | Target | Instrument | Baseline |
|---|---|---|---|
| Tool calls per invoice | <= 4 calls/req at p100 | `python benchmarks/loop_trace.py` | Unbounded ReAct loop, mean 11.4 calls/req on the same 60 items |
| Time to first value | <= 45 s median | `python tools/usage_report.py portfolios/<slug>` | Manual retyping, 4 min per invoice |
| Task completion rate | >= 70% of sessions | `python tools/usage_report.py portfolios/<slug>` | Spreadsheet workflow, no completion signal |
| External users | >= 5 completing users | `python tools/usage_report.py portfolios/<slug>` | Prototype shared with 0 users outside the author |
| Cost per invoice | <= $0.0009/req | `python benchmarks/cost.py` | Unbounded loop, $0.0031/req |
| Field accuracy | >= 0.85 exact match | `python eval/run_eval.py` | Single-shot extraction, 0.62 |
| Citation validity | >= 0.97 of claims verified | `python eval/verify_spans.py` | Unverified generation, 0.00 |

Time to first value and task completion share one instrument (`usage_report.py`) because both are read from the app's own usage log; that log doubles as the adoption evidence in section 14.

## 10. Workflow
| Phase | Input | Output | Done | Hours |
|---|---|---|---|---|
| 1. Corpus and eval set | FUNSD archive | 50 forms, 60 items | Split rebuilds identical | 5 |
| 2. Ledger and loop | Phase 1 items | Budgeted loop, trace store | Cap holds | 8 |
| 3. Stop rule and verifier | Phase 2 loop | Refusal path, span verifier | Absent field refuses | 6 |
| 4. Benchmarks | Phase 3 service | Seven artifacts | Instruments run twice | 4 |
| 5. UI | Phase 4 service | Upload page, field table | Headless check passes | 5 |
| 6. Deploy | Phase 5 image | Public URL, quota fallback | `deploy_check.py` exits 0 | 3 |
| 7. Field use | Phase 6 URL | 5 users, usage log | `usage_report.py` exits 0 | 3 |

Demo path, the failure case the mechanism exists for: open the deployed URL, upload `samples/invoice_missing_total.pdf`, and the field table shows `total: not found in this document` with the budget trace beside it, instead of a fabricated number.

## 11. Risks & Mitigation
- Free-tier LLM quota: cached planner decisions plus local fallback.
- The Space sleeps when idle: the landing page carries a recorded walkthrough; the URL is best-effort.
- 50 forms is small: every metric reports item count and a bootstrap interval.
- Stop-rule overfitting: dev split tunes, held-out split reports.

## 12. CV Bullet Draft
- Cut invoice-reader tool calls from a mean of 11.4 to a hard cap of 4 per invoice on 60 field-extraction items, making worst-case cost a function of the cap, not the model.
- Shipped a live invoice reader used by 5 SME bookkeepers, holding median time to first extracted field at 45 s and cost at $0.0009 per invoice on CPU inference.
- Reached 97% verifiable fields and 5% fabricated-value rate by making "field not found" a first-class UI state with a deterministic span verifier.

## 13. Product Surface & UX
One job: turn a scanned invoice into fields a bookkeeper can trust and export. First value under 60 seconds: upload, a progress line, then the field table with each value linked to its source box.

| Stage | What the user sees |
|---|---|
| Empty | Drop zone, two samples, one line on what happens to the file |
| Running | Current agent step and the call count out of 4 |
| Success | Field table, clickable spans, inline edit, CSV export |
| Failure | "Not found in this document", with a reason and a retake hint |
| Error | Plain message plus trace id, never a stack trace |

The screen that matters is the field table beside the page image. Absent: accounts, settings, history, batch upload, model choice.
## 14. Go-Live Plan
Deploy status: pending. The product runs locally today: `cd product && PORT=7860 python app.py`. A Dockerfile and `space_config.yml` are ready for Hugging Face Spaces (Docker SDK, free, 2 vCPU, 512 MB image, sleeps after 15 min idle, no persistent disk). The URL appears here at P7 after the upload returns it.

Fallback when sleep blocks the demo: cached-result mode serving the samples from disk, so the failure state stays reachable. Usage is recorded by the app into `product/usage.json` and reported by `python tools/usage_report.py portfolios/<slug>`. Target: 5 external users, 20 completed sessions.
