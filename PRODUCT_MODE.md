# Product Mode

Default output used to end at a README and a metrics table. Product mode ends at **a live URL a stranger can use and real people did use**. Same mechanisms, same rigour, one more bar to clear.

## What changes

| Area | Demo mode (old default) | Product mode (now default) |
|---|---|---|
| Ideation | 3 mechanisms | 3 mechanisms, each with a named audience and what that audience does today |
| Blueprint | 12 sections, <=1500 words | 14 sections, <=1750 words: `Product Surface & UX` and `Go-Live Plan` added |
| Metrics | mechanism metrics only | mechanism metrics + up to two product metrics (time to first value, completion rate, users, retention) |
| Demo path | a command | a URL plus one click |
| Prompts | P1-P5 | P1-P8, where P6=UI, P7=Deploy, P8=Field use |
| Definition of done | `make eval` prints the table | `deploy_check.py` exits 0 and `usage_report.py` shows 5 users |

## The new files

| File | Role |
|---|---|
| `.claude/skills/portfolio-architect/01c-product-intent.md` | Your audience, shipping bar, refusals, hour split. Written by `/setup`. |
| `.claude/skills/portfolio-architect/13-product-mode.md` | The rules: shipping bar, required sections, milestones, product metrics. |
| `tools/product_fit.py` | Scores mechanisms against your intent profile and checks a blueprint for product evidence. |
| `tools/deploy_check.py` | Checks a live URL: HTTPS, reachability, cold start, content, health endpoint. |
| `tools/usage_report.py` | Turns the app's own usage log into the adoption table your README quotes. |

## The loop

```
/applyidea <job>         picks mechanisms, then filters them by product fit
                         (drops anything scoring below 60/100)
/prompt <slug>           adds P6 UI, P7 Deploy, P8 Field use
/scaffold <slug>         starter repo with tests for every milestone
```

After each milestone:

```
python tools/check_portfolio.py portfolios/<slug>     # budgets and metric provability
python tools/product_fit.py check portfolios/<slug>   # URL, first value, users, fallback
python tools/deploy_check.py portfolios/<slug>        # is it actually live
python tools/usage_report.py portfolios/<slug>        # did anyone use it
```

## Switching modes

Edit the `Mode` row in `01c-product-intent.md`:

- `product` — all six shipping-bar items enforced (default).
- `demo` — repo only; product sections become warnings instead of errors.
- `research` — measurements only; no UI, no deploy, no users.

`check_portfolio.py` reads this file, so the blueprint word budget follows the mode automatically.

## Why the score is not flat

`product_fit.py` scores each (mechanism, audience) pair on six criteria:

| Criterion | Weight | What it asks |
|---|---|---|
| affinity | 30 | Can this mechanism's domain serve this audience at all? |
| reach | 20 | Is the failure mode something a non-expert can see? |
| assets | 15 | Does it reuse a skill you already have? |
| surface | 15 | Does the pack supply a web-facing product shape? |
| hours | 10 | Is there room left for the mechanism after UI and deploy work? |
| refusal | 10 | Does it trip one of your stated refusals? |

Affinity uses the `AFFINITY` table in the tool, which maps your audience domain tags to pack domains. Edit it when you add an audience; keep it explicit so every score stays explainable.

## Example

For the Indocyber AI Engineer posting, the four candidate mechanisms scored:

| Mechanism | Audience | Score |
|---|---|---|
| `bounded-agent-loop` | SME bookkeepers | 96 |
| `eval-gate` | SME bookkeepers | 84 |
| `span-grounding` | SME bookkeepers | 84 |
| `retrieval-fusion` | SME bookkeepers | 84 |

The old picker gave `bounded-agent-loop` a score of 10 with no thought about who would use it. Now the winner is the one that produces a product a bookkeeper opens tomorrow.
