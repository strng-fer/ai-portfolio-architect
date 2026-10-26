# Product Intent Profile

The blueprint answers "is this hard?". This file answers "would anyone use it?". Every idea is filtered through it before a document is written.

> Source: `/setup` product questions. Last updated: 2026-10-26.

## 1. Shipping Bar

| Field | Value |
|---|---|
| Mode | `product` (deployed and usable by a stranger) |
| Finished when | Public URL, first value under 60 s, no setup, real users |
| Surface | Web app with a real UI, one primary action |
| Hosting | Free tier only, $0, no credit card |
| Users | Real external users, 5 minimum, usage recorded by the app |
| Local fallback | Runnable offline on a 16 GB Windows laptop, CPU only |

Mode values: `product` (default, all six bar items enforced), `demo` (repo only, no deploy), `research` (measurement only, no UI).

## 2. Audience

Who the product is for, most specific first. An idea must name exactly one of these, or be dropped.

| Rank | Audience | Does today | Domain |
|---|---|---|---|
| 1 | Indonesian smallholder farmers and agri extension workers | Estimate crop problems from photos shared on WhatsApp; ask a human | agri |
| 2 | Indonesian SME back-office staff (invoicing, purchase orders) | Retype scanned documents into a spreadsheet | docops |
| 3 | Indonesian data/AI job seekers and junior engineers | Read blog posts; no working reference implementation | devtools |

An idea serves one row. "Everyone" is a rejected audience.

## 3. Distribution

| Field | Value |
|---|---|
| Channel | Public URL shared on LinkedIn and in Indonesian AI/agri communities |
| Landing need | One screenshot, one-line pitch, three-step how-it-works |
| Account required | No, for the core action |
| Language of UI | Indonesian first, English toggle if cheap |

## 4. Assets Already Held

Reuse these instead of inventing new data. An idea that needs none of them must justify why.

| Asset | Use |
|---|---|
| PyTorch + YOLO working experience | Detection and classification models |
| FastAPI working experience | API behind every UI |
| OpenCV | Preprocessing, image quality checks |
| AgriTech and industrial domain interest | Genuine audience knowledge |
| Indonesian language | Local-language UI and copy, a real differentiator |

## 5. Adoption Evidence

The app writes `usage.json`: anonymous session id, first-seen, action completed, duration, error seen. The README quotes a table generated from it.

| Metric | Minimum |
|---|---|
| External users who completed the primary action | 5 |
| Completed sessions | 20 |
| Documented user insight from a real conversation | 1 |

## 6. Refusals

Not building, regardless of how good the idea looks:

- Anything requiring a login before the core action.
- Anything that needs a paid API key to demo.
- Mobile-native apps (the laptop has no build chain for them).
- Products whose only user is a recruiter reading the repo.
- Products that need data I cannot legally obtain.

## 7. Hour Split

For a 30-60 h project: mechanism and evaluation 55%, UI 20%, deploy and field use 25%. Product work is never allowed to consume the mechanism's hours.
