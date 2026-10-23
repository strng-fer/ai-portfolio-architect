---
description: Ekstrak loker, riset GitHub & ArXiv, dan buat Blueprint + Diagram + PDF dengan alur Drafter-Reviewer
---

Target Loker (URL atau ID dari hasil scrape): $ARGUMENTS

Jalankan protokol **Drafter-Reviewer Loop** berikut secara berurutan:

### TAHAP 1: Akuisisi Data Loker & Riset Referensi
1. **Ambil Data Loker**:
   - Jika `$ARGUMENTS` adalah angka/ID, ambil detail loker dari `job_scraper/latest_scrape.json`.
   - Jika `$ARGUMENTS` adalah URL, jalankan `python3 tools/fetch_page.py "$ARGUMENTS" > job_scraper/current_job_raw.txt` lalu sanitasi dengan `python3 tools/posting_guard.py job_scraper/current_job_raw.txt > job_scraper/current_job_clean.md`.
2. **Analisis Kebutuhan & Profil**:
   - Baca `.claude/skills/portfolio-architect/01-candidate-profile.md`, `02-constraints-profile.md`, dan `03-architecture-style.md`.
   - Rumuskan kata kunci teknis utama dari loker tersebut (contoh: `"distributed task queue golang"`, `"multimodal RAG evaluation"`).
3. **Mining GitHub & Paper Ilmiah**:
   - Jalankan `python3 .agents/skills/github-repo-miner/mine_github.py --query "<kata_kunci_teknis>"`
   - Jalankan `python3 .agents/skills/arxiv-paper-miner/mine_arxiv.py --query "<kata_kunci_teknis>"`
   - Baca hasil di `job_scraper/github_refs.json` dan `job_scraper/arxiv_refs.json`.

### TAHAP 2: Penyusunan Draf (Peran: Drafter Agent)
Buat direktori `portfolios/<nama_perusahaan_slug>_<posisi_slug>/` beserta subfolder `diagrams/`, lalu buat file berikut:
1. `00_job_analysis.md`:
   - Bedah *Responsibilities*, *Requirements*, masalah bisnis perusahaan, serta tabel perbandingan *Skill Kandidat Saat Ini vs Kebutuhan Loker*.
2. `01_project_ideation.md`:
   - Berikan **3 opsi ide project portofolio** (Opsi 1: Rekomendasi Utama, Opsi 2: Fokus Infrastruktur/Skalabilitas, Opsi 3: Fokus Fitur/AI/Data).
   - Jelaskan alasan pemilihan Opsi 1 berdasarkan batasan waktu kandidat.
3. `02_system_blueprint.md` (Mengikuti aturan `05-blueprint-templates.md`):
   - **Executive Summary & Problem Statement** (masalah nyata yang diselesaikan).
   - **Tech Stack & Justifikasi Arsitektur** (kombinasi skill lama kandidat + skill baru dari loker).
   - **Desain Komponen, Skema Database, & Kontrak API/Event**.
   - **Skenario Pengujian & Target Metrik Performa** (misal: latensi < 100ms, akurasi retrieval > 85%).
   - **Roadmap Pengerjaan Mingguan** (Milestone 1 s/d selesai sesuai jam/minggu kandidat).
   - **Draf Resume Bullet Points** (menggunakan rumus Google XYZ dari `07-cv-bullet-generator.md`).
4. `03_references_study.md`:
   - Daftar minimal 5 repositori GitHub dan 3 paper ArXiv yang ditemukan, lengkap dengan penjelasan **bagian kode/algoritma mana yang harus dipelajari atau diadaptasi** ke dalam project ini.
5. `diagrams/system_architecture.mmd` & `diagrams/user_workflow.mmd`:
   - Buat diagram arsitektur sistem dan diagram alur kerja (*sequence/flowchart*) menggunakan sintaks Mermaid.js sesuai aturan `06-diagram-rules.md`.

### TAHAP 3: Kritik & Quality Gate (Peran: Reviewer Agent — Staff Engineer)
Evaluasi seluruh draf di Tahap 2 secara kritis:
1. **Anti-CRUD Check**: Apakah project ini terlihat seperti tugas kuliah biasa atau project CRUD generik? Jika ya, tulis ulang dengan menambahkan tantangan *production engineering* (caching, rate-limiting, evaluasi metrik, async worker, atau observability).
2. **Constraint Check**: Apakah project ini realistis diselesaikan dalam waktu dan spesifikasi perangkat yang tertulis di `02-constraints-profile.md`? Jika terlalu besar, pangkas fitur non-inti (*scope trimming*).
3. **Render & Verifikasi Diagram**:
   - Jalankan `python3 tools/compile_diagrams.py portfolios/<slug>/diagrams/`
   - Pastikan file `system_architecture.png` dan `user_workflow.png` berhasil terbentuk tanpa error sintaks. Jika gagal, perbaiki file `.mmd` dan ulangi sampai berhasil.

### TAHAP 4: Kompilasi Dokumen PDF & Pelacakan
1. Jalankan `python3 tools/compile_pdf.py portfolios/<slug>/` untuk menyatukan seluruh file Markdown dan gambar diagram `.png` menjadi `Blueprint_Final.pdf`.
2. Jalankan `python3 tools/verify_pdf.py portfolios/<slug>/Blueprint_Final.pdf` untuk memastikan PDF valid dan memiliki teks yang dapat diekstrak.
3. Tambahkan baris baru ke `portfolio_tracker.csv` berisi tanggal, perusahaan, posisi, judul ide project, lokasi folder output, dan status `BLUEPRINT_READY`.
