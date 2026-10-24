# Project Ideation

| Option | Idea | Problem absorbed | New technology | Est. hours | Risk |
|---|---|---|---|---|---|
| 1 (recommended) | Evidence-anchored document intake: an agent extracts six commercial fields from scanned invoices and must cite the page region for each value | Grounding, hallucination, auditability | Qdrant hybrid retrieval, bounded tool-calling agent, span verification | 34 | Medium: span alignment across OCR engines |
| 2 | Intake throughput service: queue-backed cascade that routes pages between a cheap text path and an expensive vision path under load | Latency, cost, backpressure | Async worker pool, queue with retry and dead-letter, load benchmarking | 36 | High: infra work crowds out AI depth |
| 3 | Layout-aware retrieval tuning: compare dense, sparse, and layout-hybrid indexes on field-evidence retrieval quality | Retrieval quality on tabular layouts | Qdrant named vectors, BM25 fusion, recall@k harness | 24 | Low: narrow, but reads as a tuning exercise, not a system |

## Choice

Option 1 wins. It absorbs the posting's three named responsibilities at once (LLM workflow agent, OCR/vision, retrieval with Qdrant) and keeps them in one coherent service rather than three demos. The hard mechanism is span verification: the model may not emit a value it cannot tie to a detected region, and the verifier is deterministic. That single constraint produces the interview story, the metrics, and the failure mode worth discussing.

Option 2 is a better infrastructure story but the candidate's gap is LLM and retrieval engineering, not queueing; 36 hours would mostly buy familiarity with tools already listed as medium weight. Option 3 is cheap but too close to a hyperparameter report, and it has no serving layer, which the posting names explicitly.

Scope fits the constraint profile: 34 estimated hours against a 30-60 hour ceiling, CPU-only inference on 16 GB RAM, free-tier LLM calls capped by a cache.

## Deliberately Excluded

- No custom OCR model training. PaddleOCR and Tesseract are used as-is; the contribution is the routing and verification around them.
- No fine-tuning of the language model. Prompt contracts, tool schemas, and the verifier carry the quality.
- No multi-tenant auth, billing, or admin UI. One API key, one demo client.
- No human-in-the-loop annotation tool. Low-confidence fields are flagged and returned, not reviewed in a UI.
