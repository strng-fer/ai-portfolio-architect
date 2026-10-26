# Job Analysis - PT Indocyber Global Teknologi, AI Engineer

## Posting Summary
- Company: PT Indocyber Global Teknologi, Jakarta IT services and product house.
- Role: AI Engineer, 1-2 years, S1/D4.
- Context: R&D team for internal products plus client proof-of-concept work, spanning LLM agents, computer vision, and retrieval behind FastAPI.

## Core Requirements
| Requirement | Weight | Project implication |
|---|---|---|
| LLM workflow agents (reasoning, text processing) | high | The agent loop is the core mechanism |
| Retrieval and indexing (Qdrant, Elasticsearch, other vector DB) | high | pgvector stands in for Qdrant |
| FastAPI backend for model integration | high | One HTTP agent endpoint |
| Custom client PoC delivery | high | Demoable in one command |
| Python, modular and readable | high | Reuse existing strength |
| Database knowledge | medium | New axis: schema, index, ledger |
| Docker deployment | medium | Compose reproducibility |
| Technical documentation | medium | Trace format doubles as docs |

## Candidate Gap
| Area | Status | How this project closes it |
|---|---|---|
| LLM application engineering | thin (row "LLM application engineering", level learning) | Real agent loop with budget accounting |
| Agent orchestration (LangGraph) | missing (absent from ledger) | Explicit loop state machine, no framework lock-in |
| Qdrant / vector DB | missing (row "Qdrant / vector DB", level none) | pgvector retrieval with measured recall |
| PostgreSQL | missing (absent from ledger) | Ledger, traces, index in one schema |
| OCR pipelines | missing (row "OCR pipelines", level none) | Excluded: corpus ships pre-extracted text |
| Docker | thin (row "Docker", level learning) | Compose file with API and Postgres |
| Evaluation harness design | missing (row, level none) | 60-item held-out set, fixed split |

Gap verdict: the detected stack (`python,fastapi,flask,postgresql,docker`) scores 2 missing, exactly at the ceiling. Adding the nice-to-have stack (qdrant, elasticsearch, ocr, langgraph) scores 5 missing and out of reach, so those stay out of scope.

## Business Problems Worth Attacking
Client PoCs die between the demo and the quotation. An agent that answers well on ten hand-picked documents still gives no cost per request, no latency bound, and no stopping rule. On a real corpus it either loops until the token budget dies or answers without evidence. The buyer asks "how much per request, how fast", then "what happens when it does not know".
- No termination guarantee: loop length is chosen by the model.
- No cost attribution: spend is reported per application, not per request.
- No refusal path: unanswerable questions still produce confident text.
