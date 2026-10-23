# Candidate Constraints & Environment

> Source: `/setup` (initial template). Last updated: -

## Time
- **Availability**: 5-8 hours / week (**very limited**).
- **Target duration per project**: 3-4 weeks (total **20-32 effective hours**).
- **Scope implication**: *Narrow & Deep* - at most **one core problem** per project, at most one primary model/system, no heavy frontend. The blueprint must include per-week milestones and an explicit non-goals list.

## Local Hardware
- **Spec**: 16 GB RAM, standard laptop (CPU-only or limited GPU).
- **Implication**: No local training or fine-tuning of large models. Use small pretrained models (e.g. YOLO-n/s, MobileNet, mini `sentence-transformers`), CPU inference, and small curated datasets.

## Cloud / API Budget
- **Budget**: **$0** - free tier only, no credit card where possible.
- **Suggested services**: Hugging Face Spaces/Inference (free), Render/Railway free tier or Fly.io, Supabase/Neon (free Postgres), Cloudflare R2/Pages, GitHub Actions (free CI for public repos), Groq/Gemini free tier for LLMs.
- **Rule**: every blueprint must state **free-tier quota limits** and a **fallback strategy** (local inference, caching, quantization, or mock mode) so the demo survives exhausted quota.

## Additional Constraints
- **No real production load** - value is proven through *measurable benchmarks* (p95 latency, throughput, accuracy on an evaluation set) runnable on free tier.
- **Portability**: every project must be reproducible with `docker compose up` or a single Makefile command, so a reviewer can verify CV claims.
