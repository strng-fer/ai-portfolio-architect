# Skill: Portfolio Architect

Knowledge base for designing a portfolio project targeted at one real job posting. Contains the candidate profile, quality standards, document templates, and token-discipline rules.

## Modules (read only what the task needs)

**Language & foundations**
0. `00-language.md` - instruction vs output language policy.
1. `01-candidate-profile.md` - candidate background and competencies.
2. `02-constraints-profile.md` - time, hardware, and free-tier limits.
3. `03-architecture-style.md` - idea quality rules (anti-CRUD, production-grade, measurable).

**Scoring**
4. `04-gap-evaluation.md` - Portfolio Leverage Score rubric.

**Output (low-level concept)**
5. `05-blueprint-templates.md` - structure of `02_system_blueprint.md` (concept, design alternatives, theory, workflow, <=1500 words).
6. `06-diagram-rules.md` - Mermaid rules for clean renders, max 15 nodes.
7. `07-cv-bullet-generator.md` - Google XYZ formula for CV bullets.
8. `09-lowlevel-output.md` - compact templates for `00`/`01`/`03`/`04` plus the quality gate.

**Token economy & execution**
9. `08-token-discipline.md` - output contract, read limits, word budgets, no-code-detail rule. **Read before running any command.**
10. `10-agent-prompt-pack.md` - structure of `05_agent_prompts.md` for another agent to execute. Filled example: `templates/agent_prompt_pack.example.md`.

## Standard read order for `/applyidea`
`00` -> `08` -> `09` -> `05` -> `06` -> `01` -> `02` -> `03`. That is enough. Module `04` is only for `/scrape` and `/rank`. Module `10` only when `--prompts` is used.
