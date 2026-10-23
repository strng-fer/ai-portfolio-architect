---
description: Cari loker dan beri skor potensi portofolio (output 10 baris, hemat token)
---

Parameter pencarian: `$ARGUMENTS`

1. Jalankan `python3 .agents/skills/jobspy-search/search.py --query "$ARGUMENTS" --location "<lokasi atau Indonesia>" --limit 15`.
2. Jalankan `python3 tools/job_digest.py list --top 15`. **Jangan** membaca `latest_scrape.json` mentah.
3. Baca hanya `.claude/skills/portfolio-architect/01-candidate-profile.md` dan `04-gap-evaluation.md`.
4. Beri Portfolio Leverage Score (0–100) pada tiap kandidat memakai rubrik 40/30/30. Nilai dari judul + stack + deskripsi singkat, jangan membuka `detail` untuk semua loker — maksimal 3 detail untuk kandidat teratas.
5. Tulis `job_scraper/ranked_jobs.json` (larik objek yang sama + field `score` + `ide_singkat` maks 12 kata).
6. Tampilkan **tabel 10 baris** saja: `ID | Perusahaan | Posisi | Skor | Ide singkat`. Tanpa paragraf penjelasan.
7. Tutup dengan 1 baris: `Lanjut: /applyidea <ID> --prompts`.
