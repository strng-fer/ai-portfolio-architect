---
description: Onboarding profil peserta dari folder documents/ atau wawancara interaktif
---

Jalankan prosedur `/setup` berikut:

1. **Periksa Folder `documents/`**:
   Cek isi folder `documents/cv/`, `documents/linkedin/`, `documents/transcripts/`, dan `documents/past_projects/`.
   - **Jalur A (Jika ada file dokumen)**: Baca seluruh dokumen tersebut dan ekstrak latar belakang pendidikan, pengalaman kerja/organisasi, tech stack yang sudah dikuasai, project yang pernah dibuat, dan ketertarikan domain.
   - **Jalur B (Jika semua folder kosong)**: Lakukan wawancara interaktif dengan pengguna (tanyakan 5 poin ini secara ringkas):
     1. Latar belakang saat ini & bahasa pemrograman/framework yang paling dikuasai?
     2. Posisi pekerjaan utama yang sedang diincar (misal: Backend Engineer, AI Engineer, Data Scientist)?
     3. Berapa jam per minggu waktu luang untuk mengerjakan project portofolio?
     4. Spesifikasi laptop/PC saat ini dan apakah hanya ingin memakai layanan cloud *free-tier*?
     5. Domain industri yang diminati (misal: Fintech, Health/Fitness, EdTech, SaaS, E-Commerce)?

2. **Tulis ke File Profil Skill**:
   - Simpan profil kompetensi ke `.claude/skills/portfolio-architect/01-candidate-profile.md`.
   - Simpan batasan waktu dan spesifikasi perangkat ke `.claude/skills/portfolio-architect/02-constraints-profile.md`.

3. **Output Ringkasan**:
   Tampilkan ringkasan profil yang berhasil disimpan dan informasikan bahwa pengguna kini dapat menjalankan `/scrape "<posisi>" "<lokasi>"` atau `/applyidea <url_loker>`.
