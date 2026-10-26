# Project Ideation - AI Engineer, Indocyber

The three options are the three ranked mechanisms from `mechanism_pick.py` (signals: agent, retrieval, workflow, ocr, citation; 40 hours; domain llm), filtered by `product_fit.py` (product mode).

| Option | Idea | User | Problem absorbed | New technology | Est. hours | Risk |
|---|---|---|---|---|---|---|
| 1 (recommended) `bounded-agent-loop` | An invoice reader for SME bookkeepers that caps its own tool calls, prices each request, and refuses instead of guessing | SME back-office staff, who retype scanned invoices into a spreadsheet | Unbounded loop cost; no refusal path | Agent loop state machine, Postgres ledger, pgvector | 34 | Stop rule mis-tuned, refusals too eager |
| 2 `retrieval-fusion` | A supplier-document search that survives OCR noise and shows why each result matched | SME back-office staff, who scroll old PDFs by hand | Weak recall on noisy scans | BM25 + pgvector rank fusion | 30 | Both retrievers agree on the wrong chunk |
| 3 `eval-gate` | A field-extraction release gate that blocks any model change that regresses on a client's own forms | SME ops leads, who discover regressions from angry customers | Silent quality regressions | Held-out set with fixed splits | 28 | Eval set leaks into prompting |

All three are new; `portfolios/_history.json` is empty, so no delta is required.

Product fit: option 1 scores 96/100, option 2 84, option 3 84. Option 1 wins because its failure mode is a state the user sees (a refusal with a reason), which is the only honest UI for a bookkeeper.

## Choice
Option 1 wins on three counts. It attacks the posting's first responsibility, the LLM workflow agent, instead of its nice-to-have list. At 34 hours it leaves 26 hours for the mechanism after the UI and deploy work, inside the 30-60 hour envelope in `02-constraints-profile.md`. And it produces the two numbers an SME actually cares about, cost per invoice and time to a reviewed result, which a bookkeeper can feel in the first minute.

The product is not a demo page: a bookkeeper uploads one invoice, sees the extracted fields with clickable source spans, fixes the doubtful ones, and exports. When the agent cannot ground a field it says so and asks for a clearer scan instead of inventing a number.

Option 2 is a stronger pure-retrieval story but its failure (silent miss) is harder to show honestly; option 3 is infrastructure a bookkeeper never sees, so it has no first-minute value.

Second mechanism on the same seam: `cost-attribution`. The ledger that enforces the cap is the one that prices the request.

## Deliberately Excluded
- OCR engine work: no PaddleOCR, Donut, or scan preprocessing. Pre-extracted page text is an input.
- Accounts, teams, and billing: one workspace, no auth, no admin UI.
- Framework adoption as a goal: LangGraph stays optional so the budget logic is inspectable and testable.
