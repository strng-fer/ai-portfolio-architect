# Agent Prompt Pack - Invoice Reader with a Call Budget

Run P0 first in every session, then one milestone per session. Stop when its `Done when` passes.

## P0 - Context Prompt (use at the start of every session)

**Goal** - Ship an invoice reader that SME bookkeepers use, with a hard tool-call cap.
**Context** - `02_system_blueprint.md` sections 2, 4, 9, 13, 14.
**Task** - Confirm the audience (SME back-office staff), the four-field output, the 4-call cap, and the free-tier ceiling.
**Constraints** - Python 3.12, FastAPI, Postgres with pgvector, CPU only, $0, no OCR training, no accounts.
**Deliverable** - `README.md` with what it does, one run command, and how to see the demo. Update it each milestone.
**Done when** - `python -m pytest -q` exits 0 and `README.md` names the audience and the refusal behaviour.
**Out of scope** - Auth, billing, batch upload, model choice UI.

## P1 - Corpus and eval set

**Goal** - A reproducible 60-item set from FUNSD.
**Context** - `02_system_blueprint.md` section 7.
**Task** - Take the 50-form test split. Build 44 answerable items and 16 with a field removed. Freeze a split hash.
**Constraints** - Ground truth from published annotations only, never hand-labelled. Seed fixed.
**Deliverable** - `data/build_eval_set.py`, `data/eval_set.jsonl`.
**Done when** - `python data/build_eval_set.py --verify` prints the same hash twice and reports 44 + 16 items.
**Out of scope** - OCR, augmentation, model training.

## P2 - Budget ledger and loop

**Goal** - A loop that cannot exceed 4 tool calls, priced per call.
**Context** - `02_system_blueprint.md` sections 4, 6, 8.
**Task** - Implement reserve-then-call. Key reservations by step id so retries reuse them. Add the trace store.
**Constraints** - The planner never writes to the ledger. One client wrapper is the only path to the model.
**Deliverable** - Ledger tables, `/extract` endpoint, `benchmarks/loop_trace.py`.
**Done when** - `python -m pytest tests/test_budget.py` exits 0 with a fault-injection case at 20% failure asserting p100 calls is 4.
**Out of scope** - UI, deploy, evaluation scoring.

## P3 - Stop rule and per-field verifier

**Goal** - Refuse a field instead of guessing.
**Context** - `02_system_blueprint.md` sections 6, 8.
**Task** - Add the no-new-span stop rule. Verify each value against a character span. Return a per-field refusal with a reason.
**Constraints** - Refusal is a response state, not an exception. Tune on the dev split, then freeze before the held-out run.
**Deliverable** - Span verifier, refusal path, `eval/verify_spans.py`.
**Done when** - `python eval/verify_spans.py --subset absent` reports per-field refusal accuracy >= 0.85 and exits 0.
**Out of scope** - Changing the cap, adding tools.

## P4 - Benchmarks

**Goal** - Every metric in section 9 measured against its baseline.
**Context** - `02_system_blueprint.md` section 9.
**Task** - Implement each instrument. Run baseline and new variant three times, report the median.
**Constraints** - Offline replay mode when the LLM quota is exhausted. Never invent a number.
**Deliverable** - Seven benchmark scripts, `benchmarks/eval.py` collecting them into one table.
**Done when** - `python benchmarks/eval.py` prints a table with target, baseline, and measured for all seven metrics and exits 0.
**Out of scope** - Tuning to beat the target; report honestly first.

## P5 - Review and report

**Goal** - A findings table a stranger can audit.
**Context** - `02_system_blueprint.md` sections 8-9.
**Task** - Compare baseline vs new, three runs each, median. List every metric that missed its target. Add one experiment where a weaker variant loses.
**Constraints** - No metric may be dropped to make the table green.
**Deliverable** - `REPORT.md` with the comparison table and the weaker-variant experiment.
**Done when** - `python benchmarks/eval.py --compare baseline` exits 0 and `REPORT.md` contains the weaker-variant section.
**Out of scope** - New features.

## P6 - UI

**Goal** - One page where a bookkeeper uploads an invoice and sees fields with sources.
**Context** - `02_system_blueprint.md` section 13.
**Task** - Build the drop zone, the field table with clickable spans, inline edit, CSV export. Add the empty, running, failure, and error states.
**Constraints** - No login. First value under 60 s. The failure state must show "not found in this document", never a stack trace.
**Deliverable** - UI routes, `static/`, `tests/test_ui.py`.
**Done when** - `python -m pytest tests/test_ui.py` exits 0 and posts a sample with a missing total, asserting the refusal text appears and no number is invented.
**Out of scope** - Accounts, history, batch upload.

## P7 - Deploy

**Goal** - A public URL on free tier with the quota fallback wired.
**Context** - `02_system_blueprint.md` section 14.
**Task** - Add the Dockerfile and space config. Deploy. Paste the returned URL into section 14. Wire the cached-result fallback.
**Constraints** - Free tier only. 512 MB image. No secrets in the repo.
**Deliverable** - Dockerfile, space config, `/healthz`, the URL in section 14.
**Done when** - `python tools/deploy_check.py portfolios/indocyber_global_teknologi_ai_engineer` exits 0.
**Out of scope** - Custom domain, paid tiers.

## P8 - Field use

**Goal** - Five real bookkeepers use it, and the log proves it.
**Context** - `02_system_blueprint.md` sections 13-14.
**Task** - Share the URL with five bookkeepers or SME owners. Watch one use it. Write one insight. Do not touch the log.
**Constraints** - Report the real number, even if it is 2. Never edit `usage.json`. Never fabricate a user.
**Deliverable** - `INSIGHTS.md` with one paragraph from a real conversation, and the usage table in `README.md`.
**Done when** - `python tools/usage_report.py portfolios/indocyber_global_teknologi_ai_engineer` exits 0.
**Out of scope** - Growth features, marketing pages.
