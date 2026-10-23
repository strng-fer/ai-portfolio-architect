# Architecture & Ideation Standards

## Core principle: "Built Like Production, Scoped Like a Sprint"
Every portfolio idea MUST satisfy:
1. **One narrow, deep problem**: one genuinely hard mechanism (consistency, evaluation, latency, duplication, compliance) beats a shallow full application.
2. **Quantitative metrics**: every blueprint states how it is measured (load benchmark, evaluation set, accuracy/latency metric) and a comparison baseline.
3. **Bridge the candidate's background**: use a familiar domain as context and the posting's new technology as the learning challenge.

## Document depth: concept, not code
A blueprint is a decision document. Required: problem, actors, flow, components + responsibilities, data concepts, interface concepts, key theory, metrics, risks, workflow.
Forbidden: implementation, DDL, full payloads, folder trees, tutorials. Technical detail goes to `05_agent_prompts.md`.

## Anti-overengineering fence
- Explain each concept once. Cross-reference instead of repeating.
- Theory gets a name plus one sentence of purpose. Not an academic essay.
- Tables replace repeated prose. Max 6 columns.
- Every section must be removable without breaking the others, except the problem section.

## Three-question idea test
1. Can the problem be stated in one sentence without naming technology?
2. Is there one hard part worth discussing in an interview?
3. Can the result be proven with numbers within the available time?
Any "no" -> revise the idea before writing the blueprint.
