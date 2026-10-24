# Agent Prompt Pack (`05_agent_prompts.md`)

Purpose: let another agent (Cursor, Claude Code, Codex, Gemini CLI, ChatGPT) execute the blueprint without re-explaining context. **Max 900 words.**

## File structure

```
# Agent Prompt Pack - <Project Name>
How to use (3 lines) + execution order.

## P0 - Context Prompt (use at the start of every session)
## P1 - <Milestone 1>
## P2 - <Milestone 2>
## P3 - <Milestone 3>
## P4 - <Milestone 4>
## P5 - Review & Benchmark
```

Milestone count follows the blueprint workflow. Max 6 prompts total.

## Format of each prompt (required, fixed order)

- **Goal** - one sentence describing the end result.
- **Context** - blueprint files/sections the agent must read (relative path), max 3.
- **Task** - 3-5 steps, imperative, one action per step.
- **Constraints** - language/framework, time limit, quota limits, code style, prohibitions.
- **Deliverable** - files/endpoints/tests that must exist.
- **Done when** - a **runnable command** plus the expected result. Not a description.
- **Out of scope** - what must not be touched in this milestone.

## Rule: "Done when" must be executable
Good: `Done when: python -m pytest tests/test_ingest.py passes and a duplicate submit returns the same job id.`
Bad: `Done when: ingestion works reliably.`

Every milestone needs at least one command the next agent can run without guessing. If the command does not exist yet, the milestone's Deliverable must include creating it.

## Rule: every prompt leaves a README trail
P0 requires the project `README.md` to keep three sections updated: what it does, how to run it (one command), and how to see the demo. Each milestone adds its command to that README. This is what makes the repo presentable on GitHub and in an interview.

## Rule: no hidden context
- Every prompt stands alone: a fresh agent can start with no chat history.
- Max 150 words per prompt. No long code; state the contract, not the implementation.
- Always include the non-goals and free-tier limits from `02-constraints-profile.md`.
- P0 carries: project goal, stack, expected folder shape (5 lines), conventions, prohibitions, and the README rule above.
- The review prompt carries the benchmark commands, the comparison method (baseline vs new, 3 runs, median), and the findings table format.
- Never include secrets, tokens, or internal URLs.
- Write prompts in the configured output language, but keep code identifiers, file paths, and commands in English so they can be pasted as-is.

## Optional variants
On request, add:
- `## P-Chat` - compact version for a chat assistant with no file access.
- `## P-Refactor` - repair instructions after a failed benchmark.

Filled example: `templates/agent_prompt_pack.example.md`.
Validate with: `python3 tools/check_portfolio.py <folder>`.
