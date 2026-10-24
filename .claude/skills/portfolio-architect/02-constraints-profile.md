# Candidate Constraints & Environment

> Source: `/setup` (5-question intake). Last updated: 2026-10-24

## Time
- **Availability**: 10-15 hours / week (**limited**).
- **Target duration per project**: 3-4 weeks (total **30-60 effective hours**).
- **Scope implication**: *Narrow & Deep* - at most **one core problem** per project, at most one primary model/system, no heavy frontend. Blueprint must include per-week milestones and an explicit non-goals list.

## Local Hardware
- **Spec**: Windows laptop, 16 GB RAM, CPU-only or limited GPU.
- **Implication**: No local training or fine-tuning of large models. Use small pretrained models (YOLO-n/s, MobileNet, mini `sentence-transformers`), CPU inference, small curated datasets. Heavy training runs on Colab.

## Cloud / API Budget
- **Budget**: **$0** - free tier preferred, no credit card where possible.
- **GPU**: Google Colab free tier (T4, session-limited) for training; local CPU for inference demos.
- **Suggested services**: Hugging Face Spaces/Inference (free), Render/Railway free tier or Fly.io, Supabase/Neon (free Postgres), Cloudflare R2/Pages, GitHub Actions (free CI for public repos), Groq/Gemini free tier for LLMs.
- **Rule**: every blueprint must state **free-tier quota limits** and a **fallback strategy** (local inference, caching, quantization, or mock mode) so the demo survives exhausted quota.

## Additional Constraints
- **No real production load** - value is proven through *measurable benchmarks* (p95 latency, throughput, accuracy on an evaluation set) runnable on free tier.
- **Portability**: every project reproducible with `docker compose up` or a single Makefile command, so a reviewer can verify CV claims.
- **Colab risk**: training must checkpoint to Drive/HF Hub; no blueprint may assume a session survives past ~12 h or a GPU allocation.
