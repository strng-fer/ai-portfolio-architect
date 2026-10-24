# Job Analysis - PT Indocyber Global Teknologi / AI Engineer

## Posting Summary
- **Company**: PT Indocyber Global Teknologi, Jakarta. IT system integrator serving enterprise and government clients.
- **Role**: AI Engineer, 1-2 years experience, S1/D4.
- **Business context**: The team runs R&D for internal products and custom client proof-of-concepts. Delivery pressure comes from short PoC cycles, not from long product roadmaps.

## Core Requirements
| Requirement (from posting) | Weight | Project implication |
|---|---|---|
| LLM text processing, reasoning, workflow agent | high | Agent calls tools, not just answers |
| Computer Vision: detection, OCR enhancement | high | Vision stage is first-class |
| Retrieval with Qdrant or Elasticsearch | high | Hybrid retrieval, measurable recall |
| FastAPI backend for model integration | high | Serving layer is a deliverable |
| Python, modular and readable | high | One service, clean seams |
| Docker and container deployment | medium | Reproducible demo |
| Vector database familiarity | medium | Qdrant as primary store |
| Prompt engineering, agentic AI, orchestration | medium | Bounded agent loop with verification |
| API design across microservices | medium | Clear request/response contract |

## Candidate Gap
| Area | Status | How this project closes it |
|---|---|---|
| Python, PyTorch, YOLO | solid | Used as the vision stage, no relearning |
| FastAPI serving | solid | Extended with async fan-out and streaming |
| LLM application engineering | thin | Bounded agent loop with tool calls and citations |
| Vector retrieval at scale | missing | Qdrant hybrid index with recall benchmarks |
| OCR-to-LLM handoff | thin | Span-anchored extraction contract |
| Evaluation discipline | missing | Field accuracy, citation validity, hallucination rate |
| Containerized delivery | thin | Docker Compose demo path |

## Business Problems Worth Attacking
Enterprise document intake is the recurring PoC request for an integrator: a client hands over scanned invoices and asks for structured data. The demo is easy; the handover is not. The model produces a plausible number that no one can trace to the page, so the client's finance team cannot audit it.

The hard parts are specific:

- **Grounding**: every value points to a page region, verifiable at a glance.
- **OCR degradation**: skew, stamps, and handwriting break token confidence; low-quality regions must be detected and routed.
- **Retrieval over layout**: field evidence is spatial, so text-only embeddings miss table structure.
- **Cost**: a full vision pass per page is expensive; a cascade decides when to escalate.
- **Evaluation**: accuracy hides hallucination, so citation validity is measured separately.
