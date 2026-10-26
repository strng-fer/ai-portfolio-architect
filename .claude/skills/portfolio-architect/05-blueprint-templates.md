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
8. `## 7. Data & Interfaces (Concept)` - main entities and relations (prose/table), 3-5 interface operations (name, input, output, one line). No DDL, no full JSON. Include one line on data source and reproducibility (see rule below).
9. `## 8. Technical Challenges & Solution Strategy` - 3-5 challenges (consistency, duplication, latency, evaluation, cost, safety). Format: Challenge -> Approach -> Theory -> How to prove it.
10. `## 9. Metrics & Validation` - table Metric | Target | Instrument | Baseline. Hard rule below.
11. `## 10. Workflow` - table Phase | Input | Output | Done, plus hour estimate per phase.
12. `## 11. Risks & Mitigation` - 3-5 lines (free-tier quota, time, data, external dependencies).
13. `## 12. CV Bullet Draft` - 3 XYZ bullets (see `07-cv-bullet-generator.md`).
14. `## 13. Product Surface & UX` - **product mode only** (`13-product-mode.md`): the one job the user hires it for, the 5-step first-run path, empty state, error state, the single screen that matters, what is absent from the UI. Max 150 words.
15. `## 14. Go-Live Plan` - **product mode only**: host, free-tier limits, deploy command, quota fallback, seed data on first load, how usage is recorded. Max 150 words.

In product mode the word budget for `02` is **1750**, not 1500. Run `python3 tools/product_fit.py check portfolios/<slug>` after `check_portfolio.py`.

## Rule: every metric must be provable
A metric row is only valid when all four cells are real:

| Cell | Requirement |
|---|---|
| Target | contains a number and a unit (`< 4 s`, `> 95%`, `<= $0.002/req`) |
| Instrument | names the concrete tool or artifact that produces the number (`python benchmarks/recall.py`, `k6 load.js`, `pytest -m perf`) |
| Baseline | a comparison you can actually build (naive single call, no cache, manual sample). `N/A` is forbidden |
| Proof | the same instrument runs before and after the change |

If a number cannot be measured within the free tier, replace the metric - do not invent a tool you will not run.

## Rule: data must be obtainable
Section 7 names the dataset or source and answers three things in one line each:
1. Where does the data come from (public dataset, synthetic generator, small hand-labelled set)?
2. How large (rows, documents, calls)?
3. How is it reproduced by someone else (script name or a single command description)?

## Rule: one demo path
Section 4 or 10 states the single command or endpoint a reviewer uses to see the project work. "Run the app" is not a demo path.

## Style fences
- Name the theory plus max 2 sentences (*idempotency key*, *recall@k*, *backpressure*). Not an academic explanation.
- Diagrams replace flow paragraphs. Never re-explain a diagram in prose.
- No code blocks, no DDL, no payloads, no folder trees, no install commands, no function names.
- Implementation detail does not belong here -> it appears as short instructions in `05_agent_prompts.md`.
- Every section is written once. No recap at the end of a section.
- Validate before compiling: `python3 tools/check_portfolio.py <folder>` must exit 0.
