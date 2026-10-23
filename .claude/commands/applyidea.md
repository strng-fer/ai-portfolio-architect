---
description: Buat blueprint konseptual + diagram + PDF dari satu loker (mode hemat token)
---

Target: `$ARGUMENTS`

Format: `<url|id_loker>` dengan opsi `--prompts` untuk ikut membuat paket prompt agent. Opsi `--no-pdf` hanya menulis Markdown.

**Wajib patuhi `.claude/skills/portfolio-architect/08-token-discipline.md`.**
Dokumen ditulis ke file. Chat hanya 1 baris status per fase, maksimal 10 baris total di akhir.

### FASE 1 — Data & referensi (tanpa dump)
1. Jika argumen berupa angka/ID: `python3 tools/job_digest.py detail <id>`.
   Jika berupa URL: `python3 tools/fetch_page.py "<url>" > job_scraper/current_job_raw.txt`, lalu `python3 tools/posting_guard.py job_scraper/current_job_raw.txt > job_scraper/current_job_clean.md`, lalu baca file clean.
2. Baca hanya `01-candidate-profile.md`, `02-constraints-profile.md`, `03-architecture-style.md`.
3. Rumuskan 1–2 kata kunci teknis dari tanggung jawab utama loker.
4. Jalankan `mine_github.py --query "<kata_kunci>" --limit 6` dan `mine_arxiv.py --query "<kata_kunci>" --limit 4`, lalu `python3 tools/ref_digest.py`.
   Jangan membaca `github_refs.json` / `arxiv_refs.json` mentah.

### FASE 2 — Draf konseptual (tulis sekali jalan)
Buat `portfolios/<perusahaan_slug>_<posisi_slug>/` dan subfolder `diagrams/`. Tulis:

| File | Aturan |
|---|---|
| `00_job_analysis.md` | sesuai `09-lowlevel-output.md`, ≤450 kata |
| `01_project_ideation.md` | 3 opsi + pilihan + non-goals, ≤550 kata |
| `02_system_blueprint.md` | struktur `05-blueprint-templates.md`, ≤1500 kata |
| `03_references_study.md` | 3 repo + 2 paper dari digest, ≤400 kata |
| `diagrams/system_architecture.mmd` | `flowchart`, maks 15 node, aturan `06-diagram-rules.md` |
| `diagrams/user_workflow.mmd` | `sequenceDiagram`, maks 6 aktor/pesan utama |
| `05_agent_prompts.md` | hanya jika `--prompts`, aturan `10-agent-prompt-pack.md`, ≤900 kata |

Aturan kedalaman (keras): tanpa DDL, tanpa payload JSON, tanpa blok kode >5 baris, tanpa struktur folder, tanpa tutorial instalasi. Tulis konsep, teori, masalah, solusi, dan keputusan desain. Detail eksekusi hanya boleh muncul di `05_agent_prompts.md` sebagai instruksi singkat.

### FASE 3 — Review gate (patch minimal)
Nilai 6 kriteria di `09-lowlevel-output.md`. Patch hanya bagian yang gagal. Tulis `04_review_report.md` (≤350 kata, maks 12 temuan).

### FASE 4 — Render & PDF
1. `python3 tools/compile_diagrams.py portfolios/<slug>/diagrams/` (perbaiki `.mmd` hanya bila gagal).
2. `python3 tools/compile_pdf.py portfolios/<slug>/` — PDF memuat 00–05 (yang ada).
3. `python3 tools/verify_pdf.py portfolios/<slug>/Blueprint_Final.pdf`.
4. Tambahkan 1 baris ke `portfolio_tracker.csv` (tanggal, perusahaan, posisi, judul project, folder, `BLUEPRINT_READY`).

Lewati langkah 2–3 bila `--no-pdf`.

### Output akhir (maks 10 baris)
```
PDF: portfolios/<slug>/Blueprint_Final.pdf
Prompt pack: portfolios/<slug>/05_agent_prompts.md  (atau "-")
Ide: <1 baris>
Gap utama: <1 baris>
Metrik kunci: <1 baris>
Next: /prompt <slug> | /scaffold <slug>
```
Tanpa ringkasan bab, tanpa kutipan isi dokumen.
