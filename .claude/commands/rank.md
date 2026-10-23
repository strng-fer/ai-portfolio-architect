---
description: Urutkan loker hasil scrape berdasarkan ROI belajar (tanpa narasi)
---

Baca hanya ringkasan: `python3 tools/job_digest.py list --top 20`.
Bila perlu, baca `.claude/skills/portfolio-architect/04-gap-evaluation.md` (rubrik skor) dan `01-candidate-profile.md`.

Hitung ulang skor, tulis `job_scraper/ranked_jobs.json` (field `score` + `ide_singkat` maks 12 kata per loker).
Tampilkan tabel 10 baris: `ID | Perusahaan | Posisi | Skor | Ide singkat`. Tanpa komentar tambahan selain 1 baris next step.
