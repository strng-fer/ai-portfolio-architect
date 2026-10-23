# Template Output Ringkas (Ide, Analisis, Referensi, Review)

Semua file memakai tabel dan bullet. Tanpa prosa pembuka. Tanpa kesimpulan berulang.

## `00_job_analysis.md` — maks 450 kata
1. `## Ringkasan Loker` — perusahaan, posisi, level, 3 baris konteks bisnis.
2. `## Kebutuhan Inti` — tabel: Kebutuhan (dari jobdesk) | Bobot (tinggi/sedang) | Implikasi project. Maks 8 baris.
3. `## Gap Kandidat` — tabel: Area | Status (dikuasai / tipis / kosong) | Cara ditutup.
4. `## Masalah Bisnis yang Layak Diserang` — 1 paragraf + 1 bullet daftar masalah teknis spesifik.

## `01_project_ideation.md` — maks 550 kata
Tabel 3 opsi: Opsi | Ide (1 kalimat) | Masalah yang diserap | Teknologi baru | Est. jam | Risiko.
- Opsi 1 = rekomendasi utama, Opsi 2 = fokus infra/skalabilitas, Opsi 3 = fokus AI/data/fitur.
- `## Pilihan` — 1 paragraf: alasan Opsi 1 menang terhadap batasan waktu & gap.
- `## Yang Dibuang` — 3 bullet fitur yang sengaja tidak dibuat.

## `03_references_study.md` — maks 400 kata
Tabel Repo: Nama | Kenapa relevan | Bagian yang dipelajari (1 baris). Maks 3.
Tabel Paper: Judul | Gagasan yang dipakai | Bagian yang dipelajari. Maks 2.
URL wajib berasal dari `github_refs.json` / `arxiv_refs.json`. Tanpa URL karangan.

## `04_review_report.md` — maks 350 kata
Tabel temuan: # | Area | Masalah | Keparahan | Perbaikan. Maks 12 baris.
Quality gate (jawab ya/tidak, 1 baris masing-masing): anti-CRUD, realistis terhadap batasan, metrik terukur, diagram ter-render, non-goals jelas, batas kata terpenuhi.
`## Verdict` — 1 baris (LULUS / PATCH) + maks 3 bullet perubahan yang dilakukan.

## Aturan penerapan review
Patch beda minimal di bagian yang gagal saja. Jangan tulis ulang file yang sudah lolos.
