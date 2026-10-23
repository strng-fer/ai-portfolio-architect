---
description: Onboarding profil kandidat dengan output ringkas
---

Jalankan `/setup`:

1. Cek `documents/cv/`, `documents/linkedin/`, `documents/transcripts/`, `documents/past_projects/`.
   - Ada file: baca, lalu ekstrak ke profil. Jangan mengutip isi dokumen di chat.
   - Kosong: ajukan 5 pertanyaan berikut **sekaligus dalam satu pesan**, bernomor, maksimal 1 baris per pertanyaan:
     1. Latar belakang + bahasa/framework paling dikuasai?
     2. Posisi yang diincar?
     3. Jam per minggu untuk project portofolio?
     4. Spesifikasi laptop/PC + hanya free-tier?
     5. Domain industri yang diminati?
2. Tulis `.claude/skills/portfolio-architect/01-candidate-profile.md` dan `02-constraints-profile.md` memakai tabel/bullet padat (maks 40 baris per file). Jangan menambah bab baru.
3. Output ke chat maksimal 6 baris: ringkasan 3 bullet + 1 baris next step. Tanpa paragraf pembuka.
