# Blueprint Document Structure (`02_system_blueprint.md`)

Level: **low-level concept**. The reader must understand the problem, the design choices, the theory used, and the execution order - without reading code. **Max 1500 words.**

## Heading structure (required, fixed order)

1. `# [Project Title]` + one metadata line (job, stack, hour estimate, status)
2. `## 1. Problem & Relevance` - the real problem, who loses, why it is hard, link to the job posting. Max 200 words.
3. `## 2. Goals & Non-Goals` - 3-5 measurable goals; 2-4 explicit non-goals (scope fence).
4. `## 3. Design Alternatives & Decision` - 2-3 approaches. Table: Approach | Pros | Cons | When it fits. Then one decision paragraph + one line for the main reason.
5. `## 4. Architecture & Flow` - embed `![](diagrams/system_architecture.png)` and `![](diagrams/user_workflow.png)`. Component table: Component | Responsibility | Constraint. Max 8 components.
6. `## 5. Tech Stack & Skill Bridge` - Table: Layer | Technology | Already known / New | Reason.
7. `## 6. Key Theory & References` - 3-5 patterns/algorithms/concepts. Format: Name -> purpose (1-2 sentences) -> when it fails.
8. `## 7. Data & Interfaces (Concept)` - main entities and relations (prose/table), 3-5 interface operations (name, input, output, one line). No DDL, no full JSON.
9. `## 8. Technical Challenges & Solution Strategy` - 3-5 challenges (consistency, duplication, latency, evaluation, cost, safety). Format: Challenge -> Approach -> Theory -> How to prove it.
10. `## 9. Metrics & Validation` - table Metric | Target | Instrument | Baseline.
11. `## 10. Staged Execution Workflow` - table Phase | Input | Output | Definition of done. Include hour estimates.
12. `## 11. Risks & Mitigation` - 3-5 lines (free-tier quota, time, data, external dependencies).
13. `## 12. CV Bullet Draft` - 3 XYZ bullets (see `07-cv-bullet-generator.md`).

## Style fences
- Name the theory plus max 2 sentences (*idempotency key*, *recall@k*, *backpressure*). Not an academic explanation.
- Diagrams replace flow paragraphs. Never re-explain a diagram in prose.
- No code blocks, no DDL, no payloads, no folder trees, no install commands, no function names.
- Implementation detail does not belong here -> it appears as short instructions in `05_agent_prompts.md`.
- Every section is written once. No recap at the end of a section.
