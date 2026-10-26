# Invoice Reader

Turn a scanned invoice into the fields it can actually prove.

Paste an invoice, get four fields back. Every value links to the exact character span
it came from. A field the reader cannot find says **not found in this document** instead
of inventing a number.

**How it works, in three steps**

1. Paste text or open a sample invoice.
2. The reader spends at most 4 lookups and records what each one found.
3. You see the fields, their source spans, and the lookup trace.

**See the failure state:** open the `invoice missing total` sample. The total field
refuses, because the document does not contain it.

## Run locally

```
cd product && PORT=7860 python app.py
```

Then open <http://127.0.0.1:7860/>.

## Deploy

Free tier, Hugging Face Spaces (Docker SDK):

```
huggingface-cli upload <your-user>/invoice-reader . --repo-type space
```

The Space sleeps after 15 minutes idle on the free tier. When it is asleep the first
load takes up to 60 s; the samples still work.

## Endpoints

| Path | Purpose |
|---|---|
| `/` | Upload or pick a sample |
| `/healthz` | Liveness for `tools/deploy_check.py` |

## What this is not

A demo of the blueprint's mechanism, not the finished project. The blueprint
(`../02_system_blueprint.md`) specifies the planner, the Postgres budget ledger, the
stop rule, and the evaluation harness that turn this into a product for real invoices.
