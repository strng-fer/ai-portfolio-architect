# Project Ideation - AI Engineer, Indocyber

The three options are the three ranked mechanisms from `mechanism_pick.py` (signals: agent, retrieval, workflow, ocr, citation; 40 hours; domain llm).

| Option | Idea | Problem absorbed | New technology | Est. hours | Risk |
|---|---|---|---|---|---|
| 1 (recommended) `bounded-agent-loop` | A document agent whose tool calls are capped per request, whose stop rule is driven by marginal evidence gain, and which returns an explicit refusal when the cap is reached | Unbounded loop cost and latency; missing refusal path | Agent loop state machine, Postgres budget ledger, pgvector retrieval | 34 | Stop rule mis-tuned, refusals too eager |
| 2 `prompt-injection-guard` | Untrusted document text is quarantined so it can never add a tool or rewrite the task | Client documents as an attack surface | Rule-based tool allowlist, instruction/data separation | 22 | Guard blocks only known patterns |
| 3 `retrieval-fusion` | Dense and lexical retrieval fused by reciprocal rank to lift recall on OCR-noisy text | Weak retrieval on noisy scans | BM25 plus pgvector, rank fusion | 26 | Both retrievers agree on the wrong chunk |

History: `portfolios/_history.json` contains no projects, so all three mechanisms are new. No delta required.

## Choice
Option 1 wins on three counts. It attacks the posting's first responsibility, the LLM workflow agent, instead of its nice-to-have list. Its cost tag is `S` with an `M`-grade harness, so 34 hours fits the 30-60 hour envelope in `02-constraints-profile.md`. It also produces the two numbers a client PoC is judged on, cost per request and p95 latency, which the candidate cannot currently show.

Option 2 is a component, not a project: without an agent to protect it has no failure mode to demonstrate, and its single metric (attack success rate) sits outside the pack's families. Option 3 is the strongest pure-retrieval option, but recall@k on 50 forms is a thin story at 26 hours and repeats the most common portfolio shape.

Second mechanism on the same seam: `cost-attribution`. It shares the budget seam, because the ledger that enforces the cap is the same ledger that prices the request. No second seam is opened.

## Deliberately Excluded
- OCR engine work: no PaddleOCR, Donut, or scan preprocessing. Pre-extracted page text is an input, not a deliverable.
- Multi-tenant surface: one workspace, no auth, no billing, no admin UI.
- Framework adoption as a goal: LangGraph stays optional. The loop is written explicitly so the budget logic is inspectable and testable.
