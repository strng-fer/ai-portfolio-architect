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
- **Done when** - verifiable criteria (tests pass, metric reached, command succeeds).
- **Out of scope** - what must not be touched in this milestone.

## Writing language
Write prompts in the configured output language, but keep code identifiers, file paths, and shell commands in English so they can be pasted as-is.

## Content rules
- Every prompt stands alone: a fresh agent can start with no chat history.
- Max 150 words per prompt. No long code; state the contract, not the implementation.
- Always include the non-goals and free-tier limits from `02-constraints-profile.md`.
- P0 carries: project goal, stack, expected folder shape (5 lines), conventions, prohibitions.
- The review prompt carries the test/benchmark commands and the findings report format.
- Never include secrets, tokens, or internal URLs.
- Write prompts in the configured output language, but keep code identifiers and commands in English.

## Optional variants
On request, add:
- `## P-Chat` - compact version for a chat assistant with no file access.
- `## P-Refactor` - repair instructions after a failed benchmark.

Filled example: `templates/agent_prompt_pack.example.md`.
