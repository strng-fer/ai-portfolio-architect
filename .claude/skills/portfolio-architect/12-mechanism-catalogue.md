# Mechanism Catalogue

A **mechanism** is the hard thing a project is actually about: a consistency guarantee, an evaluation loop, a cost control, a failure mode handled properly. It is not a feature and not a stack.

Ideation must select a mechanism, not invent one. That is what stops every blueprint from becoming "a RAG chatbot with citations".

## How selection works

`/applyidea` runs `tools/mechanism_pick.py` with three inputs:

1. **Signals** extracted from the posting's responsibilities (`audit`, `latency`, `duplicate`, `ocr`, ...).
2. **History** from `portfolios/_history.json`: mechanisms already used, so the next project deepens the portfolio instead of repeating it.
3. **Hour budget** from `02-constraints-profile.md`, which filters by build cost.

Output: three ranked candidates. Each becomes one option in `01_project_ideation.md`.

## Build cost

| Tag | Hours | Meaning |
|---|---|---|
| `S` | 6-12 | One mechanism, one seam, provable in a week |
| `M` | 12-24 | One mechanism plus a serving path and an evaluation harness |
| `L` | 24-40 | Mechanism plus a system around it; needs the full budget |

## Catalogue

| ID | Mechanism | Domains | Posting signals | Cost | Metric family | When it fails |
|---|---|---|---|---|---|---|
| `span-grounding` | Every generated value cites a source span, verified deterministically | llm, cv | audit, compliance, extraction, citation, traceable | M | citation validity, hallucination rate | OCR splits the value across two regions |
| `retrieval-fusion` | Dense + sparse retrieval combined by rank fusion | llm, search | search, retrieval, rag, recall, knowledge | M | recall@k, nDCG | Both retrievers agree on the wrong chunk |
| `cascade-routing` | Cheap path first, escalate on a quality signal | llm, cv, mlops | cost, quota, latency, budget, escalation | M | escalation rate, cost/req, p95 | The quality signal itself is unreliable |
| `eval-gate` | A held-out set blocks any change that regresses quality | llm, mlops, cv | evaluation, regression, quality, release | M | pass rate, delta vs baseline | The eval set leaks into training or prompting |
| `idempotency` | Duplicate submissions collapse to one effect | backend, data | duplicate, retry, payment, webhook, exactly-once | S | duplicate rate, replay safety | The key is derived from mutable input |
| `backpressure` | Bounded queues shed or delay load instead of collapsing | backend, data | traffic, throughput, spike, reliability, sla | M | p95, drop rate, queue depth | The producer has no way to slow down |
| `exactly-once-sink` | Write-once semantics across retries and restarts | data, backend | pipeline, etl, restart, dedupe, streaming | M | duplicate rows, lost records | The sink cannot express a unique constraint |
| `cache-invalidation` | Cached answers are provably fresh after a write | backend, llm | cache, freshness, stale, realtime | S | staleness window, hit rate | Invalidation events are dropped |
| `schema-drift` | Upstream shape changes are detected before they break parsing | data, backend | integration, upstream, api, schema, breaking | S | detection latency, breakage rate | Drift is silent but valid |
| `drift-detection` | Input or output distribution shift raises an alert | mlops, ml | monitoring, production, drift, alert, degradation | M | PSI, alert precision/recall | The reference window is already contaminated |
| `calibration` | Emitted confidence matches observed accuracy per bucket | ml, llm | confidence, threshold, risk, decision | S | ECE, bucket accuracy | Rare classes are absent from calibration |
| `active-learning` | Uncertain samples are selected for labelling | ml, cv | labelling, annotation, budget, human-in-loop | M | labels per accuracy point | Uncertainty is miscalibrated |
| `edge-quantization` | Model runs within a latency and memory envelope on device | cv, mobile | edge, device, on-device, latency, memory | M | p95 ms, model size, accuracy delta | The envelope is dominated by I/O, not inference |
| `class-imbalance` | Rare-class recall is held without wrecking precision | ml, cv | imbalance, rare, defect, fraud, detection | S | per-class recall, PR-AUC | The rare class is unlabelled, not just rare |
| `multi-tenant-isolation` | One tenant's data or load cannot leak into another's | backend, saas | multi-tenant, isolation, permissions, enterprise | M | cross-tenant leak count, noisy-neighbour p95 | Isolation is enforced only in the query layer |
| `audit-trail` | Every state change is reconstructable after the fact | backend, compliance | audit, compliance, history, who-changed | S | reconstruction completeness | Events are written after the mutation commits |
| `rate-limit-fairness` | Limits hold per identity, not globally | backend | rate, quota, abuse, fairness, throttling | S | false-reject rate, fairness index | Identity is spoofable |
| `conflict-resolution` | Concurrent edits converge to one state | mobile, backend | offline, sync, concurrent, conflict, collaborative | M | conflict rate, convergence time | Clocks are unsynchronised and trusted |
| `cold-start` | New users or items get useful output with no history | ml, search | recommendation, personalisation, new-user | M | cold-start recall, time-to-useful | Content features are missing too |
| `cost-attribution` | Spend is attributed per workflow, not per app | llm, mlops | cost, budget, spend, billing, quota | S | cost/request, unattributed share | Calls bypass the instrumented path |
| `prompt-injection-guard` | Untrusted text cannot redirect the agent | llm, security | untrusted, user-content, agent, tool-calling | S | attack success rate | The guard is a model, not a rule |
| `bounded-agent-loop` | Tool-call budget caps cost and latency per request | llm | agent, tool, orchestration, workflow, autonomy | S | calls/request, p99 latency | The task genuinely needs more evidence |
| `partial-failure` | One downstream failure degrades output instead of failing it | backend, data | dependency, resilience, degradation, fallback | S | success rate under fault, degraded share | The fallback is untested |
| `reproducible-split` | Evaluation is identical across machines and runs | ml, data | reproducibility, benchmark, comparison | S | split hash equality | The source data changes underneath |

## Rules for using the catalogue

1. **One primary mechanism per project.** A second mechanism is allowed only if it is the same seam (`cascade-routing` + `cost-attribution` is fine; `span-grounding` + `edge-quantization` is two projects).
2. **Prefer an unused mechanism.** After three projects, novelty matters more than raw fit: a portfolio of five retrieval demos reads worse than one retrieval, one serving, one evaluation.
3. **Reuse is allowed when deepening.** If the history has `retrieval-fusion` at `M`, choosing it again at `L` with a different constraint (multilingual, streaming, on-device) is a progression, not a repeat. State the delta in `01_project_ideation.md`.
4. **The mechanism decides the metrics.** Section 9 of the blueprint takes its metric family from this table. Do not invent metrics outside the family without justification.
5. **The mechanism decides the demo.** The demo path must exercise the mechanism's failure mode, not the happy path.

## Extending the catalogue

Add a row when a posting names a challenge no row covers. Keep the columns identical. Signals are lowercase, comma-free keywords that actually appear in postings; they are what the picker matches on.
