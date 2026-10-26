# Product Mode: From Blueprint to Shippable Product

The default blueprint ends at a repo that proves its metrics. Product mode ends at a product a stranger can use without reading anything.

This module turns every project into a **shippable artifact**: a deployed web app on free tier, with a first-run path a non-technical user completes unaided, and usage evidence from real people.

## 1. What "user-ready" means (the bar)

A project is user-ready only when all six hold:

| # | Requirement | Verifiable by |
|---|---|---|
| 1 | Live public URL, HTTPS, no login wall for the core action | open the link in a fresh browser |
| 2 | First value under 60 seconds, zero setup, zero docs | a stranger handed only the URL |
| 3 | Failure path visible to the user, not a stack trace | trigger the mechanism's failure mode in the UI |
| 4 | Free-tier quota stated, with a fallback that keeps the demo alive | `02_system_blueprint.md` section 11 |
| 5 | Real usage evidence: >= 5 external users, >= 20 sessions | `usage.json` written by the app itself |
| 6 | Product copy: one-line pitch, one screenshot, 3-step how-it-works | `README.md` top section |

Requirement 5 is measured, not claimed. The app records anonymous sessions; the README quotes the numbers.

## 2. Required new blueprint sections

Product mode adds two sections to `02_system_blueprint.md` (template: `05-blueprint-templates.md`):

- **`## 13. Product Surface & UX`** — the one job the user hires the product for, the first-run path as 5 numbered steps, the empty state, the error state, the one screen that matters, and what is deliberately absent from the UI.
- **`## 14. Go-Live Plan`** — host, free-tier limits, the deploy command, the quota fallback, the seed data a stranger sees on first load, and how usage is recorded.

Word budget for `02` rises from 1500 to 1750 in product mode. Nothing else changes.

## 3. Ideation rule: ideas must survive the "usable tomorrow" test

Add to every ideation option row a **User** column: who the product is for, in one clause, and what they do today instead. An option whose user is "recruiters looking at my repo" is not a product — drop it.

The three ranked mechanisms still decide the three options. Product mode changes **how** each is expressed, not which ones are offered:

- the mechanism becomes the product's differentiating behaviour, not an internal article,
- the failure mode becomes a user-visible state (a refusal, a warning, a "needs a human" flag),
- the metric becomes something the user feels (time-to-first-answer, cost the user saves).

## 4. Demo path becomes a URL

`05-blueprint-templates.md` rule "one demo path" is superseded: the demo path is now **a URL plus one action**. The blueprint states the URL, what to click, what the user sees, and what they see when the mechanism fails. Screenshots are taken at milestone close, not at design time.

## 5. Milestone shape in product mode

Product work adds three milestones to the standard contract (`11-execution-handoff.md`):

| Milestone | Deliverable | Done when |
|---|---|---|
| UI | One page, one primary action, empty + error states | `curl -s <url>/healthz` and a headless check that the primary action works end to end |
| Deploy | Public URL on free tier, env config, quota fallback | `python tools/deploy_check.py <url>` exits 0 |
| Field use | 5 external users, usage log, one written user insight | `python tools/usage_report.py <slug>` shows >= 5 users and >= 20 sessions |

`tools/deploy_check.py` checks reachability, HTTPS, cold-start time, and that the failure state renders. `tools/usage_report.py` reads the app's own `usage.json` (or a hosted equivalent) and prints the evidence table the README quotes.

## 6. Metrics in product mode

The mechanism metric stays (it is what makes the project worth reading). Add up to two product metrics from the pack's `product_metric_families`:

- **time to first value** — seconds from first load to the user's first useful output,
- **task completion rate** — share of sessions that reach the primary action's success state,
- **external users** — distinct people who completed the primary action,
- **retention** — share of users who return within 7 days.

Every product metric needs the same four cells as any other metric: target with a number, instrument naming the tool, a baseline you can actually build, and a proof run. An unmeasurable product metric is worse than no product metric.

## 7. What product mode does NOT change

- The mechanism is still chosen by `mechanism_pick.py`, not by product taste.
- Banned idea shapes still apply. "A nicer UI over the same RAG demo" is still banned.
- Word budgets, token discipline, and the validation gate still apply.
- Scope still fits the hour budget in `02-constraints-profile.md`. Product work is the last 25% of hours, never the first.

## 8. Failure handling in product mode

- If the free tier cannot keep the app warm, ship a recorded 60-second walkthrough on the landing page and keep the URL as best-effort. Say so in section 11; never claim always-on.
- If five external users cannot be found, report the actual number. A product with 2 users and honest numbers beats a product with invented ones.
- If the UI milestone exceeds its estimate by more than 50%, cut UI surface, not the mechanism or the deploy.
