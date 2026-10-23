# Agent Prompt Pack - <Project Name>

How to use: paste `P0` at the start of every new session, then run milestone prompts in order. One milestone = one session. Do not skip.

Order: `P0` -> `P1` -> `P2` -> `P3` -> `P4` -> `P5`.

---

## P0 - Context Prompt

**Goal**: Prepare the agent to work on this project with no further explanation.

**Context**: `02_system_blueprint.md` sections 2 (goals/non-goals), 4 (architecture), 5 (stack).

**Task**:
1. Read those three blueprint sections.
2. Restate the stack, constraints, and non-goals in 5 lines.
3. Wait for the next milestone prompt.

**Constraints**: Python 3.11, free tier only, 16 GB RAM, CPU-only inference, no large local models. Code in English, minimal comments.

**Deliverable**: a 5-line context summary at the start of the session.

**Done when**: the summary names the stack, quota limits, and at least 2 non-goals.

**Out of scope**: writing features, editing the blueprint.

---

## P1 - <Milestone 1: Foundation>

**Goal**: <one-sentence end result>.

**Context**: `02_system_blueprint.md` sections 7 (data & interfaces), 10 (workflow phase 1).

**Task**:
1. <imperative step>
2. <imperative step>
3. <imperative step>

**Constraints**: <language, framework, time limit, prohibitions>.

**Deliverable**: <files/endpoints/tests that must exist>.

**Done when**: <verification command> passes and <metric> is reached.

**Out of scope**: <features that must not be touched in this phase>.

---

## P2 - <Milestone 2>

(Same format: Goal / Context / Task / Constraints / Deliverable / Done when / Out of scope.)

---

## P5 - Review & Benchmark

**Goal**: Prove the performance claims and catch regressions.

**Context**: `02_system_blueprint.md` section 9 (metrics & validation).

**Task**:
1. Run the benchmark scenario against baseline and the new version.
2. Compare results with the blueprint targets.
3. Report findings in a table: Area | Problem | Severity | Fix.

**Constraints**: do not change the architecture while measuring. Measure 3 times, take the median.

**Deliverable**: `benchmark_report.md`, max 1 page.

**Done when**: every target metric has an actual number and a pass/fail verdict.

**Out of scope**: large refactors, new features.
