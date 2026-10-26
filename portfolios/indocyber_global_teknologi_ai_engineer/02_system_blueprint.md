# Budgeted Evidence Agent

Job: AI Engineer, PT Indocyber Global Teknologi | Stack: Python, FastAPI, Postgres with pgvector, Docker | Estimate: 34 h | Status: blueprint

## 1. Problem & Relevance
A client PoC agent that answers document questions is easy to show and hard to price. Loop length is decided by the model, so one ambiguous question can consume twenty tool calls; cost and latency appear only on the invoice. When the agent finds no answer it still writes one, so a grounded answer looks like a guess.

The people who lose are the delivery engineer quoting a fixed price and the client accepting it. Both need spend per request and a latency ceiling before signing, plus a defined behaviour for "not in the documents", the case that destroys trust in a pilot.

This is hard because the natural fix, a shorter prompt asking the model to be efficient, is unenforceable. A guarantee needs an external counter, a stop rule that does not trust the model, and a refusal that is a first-class response. The posting asks for exactly this: LLM workflow agents, retrieval, served behind FastAPI for client prototypes.

## 2. Goals & Non-Goals
- Cap tool calls at 4 per request, enforced outside the model and recorded in the response.
- Hold p95 latency at or under 6 s on CPU-only inference over 50 forms.
- Price every request in the ledger, with unattributed spend at 0%.
- Answer only with spans a deterministic verifier accepts; refuse otherwise.
- Reach 0.85 exact-match field accuracy on 60 held-out items.

Non-goals: OCR training, multi-tenant isolation, UI beyond a trace viewer, streaming, fine-tuning.
## 3. Design Alternatives & Decision
| Approach | Pros | Cons | When it fits |
|---|---|---|---|
| Unbounded ReAct loop | Simplest, best raw accuracy | Cost and latency set by the model | Research notebooks |
| Framework runner with a turn limit | One configuration value; tracing for free | Counts turns, not spend; retries escape it | Teams already on a framework |
| Explicit budgeted loop with a stop rule | Cap, price, refusal are deterministic and testable | More request-path code; tuning needed | Client PoCs with a quoted price |

Decision: the explicit loop. The cap must survive retries, parallel tool calls, and model upgrades; only a counter the model cannot reach gives that, because a quoted price needs a worst case.

## 4. Architecture & Flow
![](diagrams/system_architecture.png)

![](diagrams/user_workflow.png)

| Component | Responsibility | Constraint |
|---|---|---|
| FastAPI edge | Validate request, attach budget, return trace id | Rejects undeclared budgets |
| Budget ledger | Reserve, decrement, price each call | Authoritative; planner cannot write |
| Planner (LLM) | Choose next tool, draft answer | Untrusted: proposes only |
| Tool registry | Three tools: retrieve, read page, compare fields | Fixed set, no dynamic tools |
| Retrieval | pgvector dense search plus lexical scoring | CPU embeddings, 50 forms |
| Stop controller | Stop on cap, on sufficiency, or on no gain | Deterministic, no model call |
| Verifier | Match each value to a span by offset | Deterministic check |
| Trace store | One JSONL row per step | Append-only |

## 5. Tech Stack & Skill Bridge
| Layer | Technology | Known / New | Reason |
|---|---|---|---|
| Language | Python | Known | Existing strength |
| API | FastAPI | Known, thin | Posting names it; needs a public artifact |
| Database | PostgreSQL with pgvector | New | Closes Postgres and vector-DB gaps together |
| Embeddings | Small sentence-transformer, CPU | New | Free tier, no GPU |
| LLM | Free-tier hosted model, local fallback | New | Quota risk forces a fallback |
| Packaging | Docker Compose | Thin | Posting lists container deployment |
| Evaluation | Python harness, fixed splits | New | Closes the evaluation-harness gap |

## 6. Key Theory & References
- **Budgeted agent loop**: each step reserves from a counter before acting, so worst-case cost follows the cap, not model behaviour. Fails when tools spawn sub-calls outside the reservation.
- **Diminishing-return stop rule**: stop when the last step added no new verified span. Fails when the gain signal is scored by the model that chose the step.
- **Evidence sufficiency**: an answer is admissible only if every claimed field maps to a verifiable span. Fails when the source splits a value across two regions.
- **Per-request cost attribution**: price each step from a token ledger at the call site. Fails when a call path bypasses the instrumented client.

## 7. Data & Interfaces (Concept)
Entities: document, page, chunk, item, run, step, span claim, budget entry.

| Operation | Input | Output |
|---|---|---|
| Ask | Item id, budget | Answer or refusal, spans, trace id |
| Trace lookup | Trace id | Ordered steps with cost |
| Evaluate | Split name | Accuracy, citation validity, refusal rate |
| Compare | Two run ids | Delta per metric |

Data source: FUNSD, a public set of 199 scanned forms with entity annotations. This project uses the 50-form test split, converted into 60 question items: 44 answerable, 16 unanswerable. Ground truth comes from the published annotations, not hand labelling. Reproduction: `python data/build_eval_set.py` rebuilds split and items from the raw archive with a fixed seed, so the split hash matches anywhere.

## 8. Technical Challenges & Solution Strategy
- **Termination guarantee**: the ledger reserves before the call and refuses after the cap, so a stuck planner ends in a refusal. Proof: replay 60 items, assert calls per request never exceed 4.
- **Budget accounting under retries**: reservation is keyed by step id, so a retried call reuses it instead of consuming a second one. Proof: fault-injection run failing 20% of tool calls.
- **Noisy retrieval on scanned text**: chunking respects layout blocks, and lexical scoring covers numeric fields embeddings blur. Proof: recall@5 against a chunk-by-character baseline.
- **Refusal calibration**: the sufficiency rule is tuned on a dev split, then frozen before the held-out run, so the 16 unanswerable items test it honestly. Proof: hallucination rate on that subset.
- **Attribution leakage**: one client wrapper is the only path to the model; a test asserts no direct call sites exist. Proof: unattributed share is 0%.

## 9. Metrics & Validation
| Metric | Target | Instrument | Baseline |
|---|---|---|---|
| Tool calls per request | <= 4 calls/req at p100 | `python benchmarks/loop_trace.py` | Unbounded ReAct loop, mean 11.4 calls/req on the same 60 items |
| p95 latency | <= 6 s | `python benchmarks/latency.py` | Unbounded loop, p95 21 s |
| Cost per request | <= $0.0009/req | `python benchmarks/cost.py` | Unbounded loop, $0.0031/req |
| Field accuracy | >= 0.85 exact match | `python eval/run_eval.py` | Single-shot extraction, 0.62 |
| Citation validity | >= 0.97 of claims verified | `python eval/verify_spans.py` | Unverified generation, 0.00 |
| Hallucination rate | <= 0.05 on unanswerable items | `python eval/run_eval.py --subset unanswerable` | Single-shot extraction, 0.41 |

## 10. Workflow
| Phase | Input | Output | Done | Hours |
|---|---|---|---|---|
| 1. Corpus and eval set | FUNSD archive | 50 forms, 60 items, split hash | Split rebuilds identical | 6 |
| 2. Ledger and loop | Phase 1 items | Budgeted loop, trace store | Cap holds under fault injection | 10 |
| 3. Stop rule and verifier | Phase 2 loop | Refusal path, span verifier | Unanswerable item refuses with trace | 8 |
| 4. Benchmarks | Phase 3 service | Six metric artifacts | All six instruments run twice | 6 |
| 5. Packaging and docs | Phase 4 artifacts | Compose file, README, viewer | Cold clone reproduces the table | 4 |

Demo path, the failure case the mechanism exists for: `curl -s -X POST localhost:8000/ask -H 'content-type: application/json' -d '{"item_id":"funsd_test_07","question":"total amount"}'` returns a refusal with the budget trace showing no admissible span.

## 11. Risks & Mitigation
- Free-tier LLM quota: cached planner decisions plus local fallback; benchmarks run in offline replay.
- Time: 34 h against a 40 h ceiling; only phase 3 may absorb slippage.
- Corpus and index limits: 50 forms is small, so every metric reports item count and a bootstrap interval; index the test split only.
- Stop-rule overfitting: dev split tunes, held-out split reports.

## 12. CV Bullet Draft
- Cut agent tool calls from a mean of 11.4 to a hard cap of 4 per request on 60 document QA items, making worst-case cost a function of the cap, not the model.
- Held p95 latency at 6 s and $0.0009 per request on CPU inference with a Postgres budget ledger that survives retries and fault injection.
- Reached 97% verifiable answers and 5% hallucination on unanswerable questions by making "insufficient evidence" a first-class response.
