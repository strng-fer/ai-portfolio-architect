---
description: Cari loker di portal kerja dan beri skor potensi project portofolio
---

Parameter pencarian: $ARGUMENTS

Lakukan langkah-langkah berikut:
1. Baca profil kandidat di `.claude/skills/portfolio-architect/01-candidate-profile.md` dan matriks evaluasi di `.claude/skills/portfolio-architect/04-gap-evaluation.md`.
2. Jalankan script scraper:
   `python3 .agents/skills/jobspy-search/search.py --query "$ARGUMENTS"`
3. Baca hasil di `job_scraper/latest_scrape.json`.
4. Evaluasi setiap lowongan dan hitung **Portfolio Leverage Score (0-100)**:
   - Skor tertinggi diberikan pada loker yang memiliki **60-70% irisan dengan skill kandidat saat ini** dan **30-40% teknologi/arsitektur baru** yang strategis untuk dipelajari lewat satu project portofolio.
   - Beri nilai tambah pada loker yang menuliskan masalah teknis secara spesifik di deskripsi pekerjaannya.
5. Simpan hasil yang sudah dinilai ke `job_scraper/ranked_jobs.json`.
6. Tampilkan tabel Markdown berisi 10 loker terbaik dengan kolom:
   `ID | Perusahaan | Posisi | Skill Match vs Gap | Ide Singkat Portofolio | Skor`
7. Berikan instruksi kepada user: *"Ketik `/applyidea <ID URL atau>` untuk membuat blueprint lengkap dari salah satu loker di atas."*
