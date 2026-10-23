# AI Portfolio Architect

Sistem berbasis AI agent (Claude Code / OpenCode / AI CLI lain) yang membantu kandidat menganalisis lowongan kerja nyata, memetakan *skill gap*, mencari referensi kode GitHub dan paper ArXiv, lalu merancang **Blueprint Project Portofolio berstandar produksi** — lengkap dengan diagram arsitektur, dokumen Markdown, dan PDF.

---

## Konsep Inti

| Komponen | Peran |
|---|---|
| **Portfolio Leverage Score** | Skor 0–100 untuk menilai kecocokan loker dengan profil kandidat (bobot: Skill-Bridge 40, Problem Clarity 30, Reusability 30) |
| **Drafter-Reviewer Loop** | Draf dibuat oleh "Drafter Agent", lalu dikritisi "Reviewer Agent" (persona Staff Engineer) sebelum difinalisasi |
| **Anti-CRUD Rule** | Ide project dilarang berupa aplikasi CRUD generik (To-Do, katalog e-commerce, kloning sosial media). Wajib menyelesaikan masalah teknis spesifik dari loker (high-concurrency booking, hybrid RAG, distributed rate-limiter, dst.) |
| **Google XYZ Formula** | Rumus bullet CV: *"Achieved [X] as measured by [Y], by doing [Z]"* |

## Arsitektur Alur Kerja

```
documents/ (CV, LinkedIn, transkrip)
        │
        ▼
     /setup ──────────────► .claude/skills/portfolio-architect/
        │                    01-candidate-profile.md
        │                    02-constraints-profile.md
        ▼
   /scrape "<posisi>" "<lokasi>" ──► .agents/skills/jobspy-search/search.py
        │                                   │
        ▼                                   ▼
  job_scraper/latest_scrape.json ◄──── Indeed / LinkedIn / Glassdoor
        │
        ▼
      /rank ───────────────► job_scraper/ranked_jobs.json
        │
        ▼
  /applyidea <URL | ID> ──► job_scraper/current_job_raw.txt
        │                          │ posting_guard.py (filter prompt injection)
        │                          ▼
        │                   current_job_clean.md
        ├──► .agents/skills/github-repo-miner/mine_github.py ──► github_refs.json
        ├──► .agents/skills/arxiv-paper-miner/mine_arxiv.py  ──► arxiv_refs.json
        │
        ▼
  portfolios/<perusahaan>_<posisi>/
        ├── 00_job_analysis.md
        ├── 01_project_ideation.md     (3 opsi ide)
        ├── 02_system_blueprint.md     (arsitektur, skema DB, API, roadmap, bullet CV)
        ├── 03_references_study.md     (≥5 repo GitHub, ≥3 paper ArXiv)
        └── diagrams/
              ├── *.mmd                (Mermaid source)
              └── *.png                (hasil compile_diagrams.py)
        │
        ▼
  tools/compile_pdf.py ──► Blueprint_Final.md ──► Blueprint_Final.pdf
        │                        (verify_pdf.py)
        ▼
  portfolio_tracker.csv  (status: BLUEPRINT_READY)
        │
        ▼
     /scaffold ──────────► portfolios/<slug>/starter_repo/  (boilerplate siap coding)
```

## Struktur Direktori

```
ai-portfolio-architect/
├── CLAUDE.md                          # Aturan sistem (dibaca AI agent)
├── AGENTS.md                          # Symbolic link → CLAUDE.md (standar OpenCode)
├── PLAN.md                            # Spesifikasi rancangan sistem
├── setup_cli_links.sh                 # Script integrasi lintas AI CLI
├── portfolio_tracker.csv              # Tracker semua blueprint yang dibuat
├── .claude/
│   ├── settings.json                  # Whitelist permission Bash
│   ├── commands/                      # 7 slash commands
│   └── skills/portfolio-architect/    # 8 file knowledge base (SKILL + 7 modul)
├── .agents/skills/                    # 3 CLI miner (scraper data eksternal)
│   ├── jobspy-search/search.py        # Scraper lowongan (indeed/LinkedIn/glassdoor)
│   ├── github-repo-miner/mine_github.py   # Cari repo referensi GitHub
│   └── arxiv-paper-miner/mine_arxiv.py    # Cari paper ilmiah ArXiv
├── tools/
│   ├── fetch_page.py                  # Ambil isi halaman web (via Jina Reader)
│   ├── posting_guard.py               # Filter prompt injection dari iklan lowongan
│   ├── compile_diagrams.py            # Render .mmd → .png (mermaid-cli / Kroki fallback)
│   ├── compile_pdf.py                 # Gabung Markdown + render PDF (md-to-pdf)
│   ├── verify_pdf.py                  # Validasi ukuran & keberadaan PDF
│   └── .puppeteer-config.json         # (auto-generate) executablePath Chrome/Edge
├── documents/                         # Dokumen kandidat (cv/, linkedin/, transcripts/, past_projects/)
├── job_scraper/                       # Cache hasil scraping (latest_scrape.json, ranked_jobs.json, *_refs.json)
├── portfolios/                        # Output blueprint per loker
├── templates/                         # Khusus untuk boilerplate (dipakai /scaffold)
└── .opencode/command → .claude/commands   # Symbolic link (agar slash command jalan di OpenCode)
```

---

## Persyaratan (Prerequisites)

| Komponen | Kebutuhan | Keterangan |
|---|---|---|
| **Python** | ≥ 3.10 | Windows harap set `%APPDATA%\npm\python3.cmd` shim (lihat Troubleshooting) |
| **Node.js** | ≥ 18 (npx tersedia) | Untuk merender diagram Mermaid & konversi PDF |
| **Google Chrome / MS Edge** | Terinstal minimal 1 | Dimerlukan sebagai engine puppeteer (mermaid-cli & md-to-pdf) |
| **Git Bash (Windows)** | Opsional | Untuk menjalankan `setup_cli_links.sh` |
| **Jaringan internet** | Diperlukan | Untuk scraping lowongan, GitHub API, dan ArXiv API |

## Langkah Setup

### 1. Install Dependensi Python

```bash
pip install python-jobspy
```

### 2. Install Node global packages (merender diagram + PDF)

```bash
npm install -g --allow-scripts=puppeteer @mermaid-js/mermaid-cli
npm install -g --allow-scripts=puppeteer md-to-pdf
```

> `--allow-scripts=puppeteer` penting agar postinstall Chromium diunduh.
> Jika Chromium gagal launch di Windows (code `0xC000007B`), sistem akan otomatis fallback ke Chrome/Edge yang terinstal via `tools/.puppeteer-config.json`.

### 3. Jalankan Script Integrasi (Linkiage CLI)

**Linux / macOS:**
```bash
bash setup_cli_links.sh
```

**Windows (pakai Git Bash):**
```bash
"C:\Program Files\Git\bin\bash.exe" setup_cli_links.sh
```

Script ini melakukan 3 hal:
1. `ln -sf CLAUDE.md AGENTS.md` → AI CLI modern membaca konfigurasi agent dari `AGENTS.md`.
2. `ln -sf ../.claude/commands .opencode/command` → slash command aktif di OpenCode.
3. `chmod +x tools/*.py .agents/skills/*/*.py` → daftar script python siap dieksekusi.

### 4. Verifikasi Instalasi

```bash
python tools/fetch_page.py "https://example.com"              # harus exit 0
python .agents/skills/github-repo-miner/mine_github.py --query "python" --limit 2
python .agents/skills/arxiv-paper-miner/mine_arxiv.py --query "rag" --limit 2
python .agents/skills/jobspy-search/search.py --query "backend engineer jakarta" --limit 5
```

---

## Cara Pakai (Alur Pengguna)

Semua interaksi lewat slash command di Claude Code / OpenCode:

| Perintah | Fungsi |
|---|---|
| `/setup` | Onboarding: baca dokumen `documents/` atau wawancara 5 poin. Membuat profil kompetensi dan batasan (waktu, RAM, anggaran) |
| `/scrape "<posisi>" "<lokasi>"` | Scraping loker → hitung Portfolio Leverage Score → tabel top 10 |
| `/rank` | Re-purpose ranking berdasarkan rubrik `04-gap-evaluation.md` |
| `/applyidea <URL atau ID>` | Menjalankan **Drafter-Reviewer Loop** end-to-end: analisis loker → riset GitHub/ArXiv → 3 ide project → blueprint → diagram → PDF → update tracker |
| `/scaffold <folder_portofolio>` | Buat starter boilerplate repo (tech stack, docker, README, TODO checklist) |
| `/expand` | Pindai dokumen/repo baru untuk memperbarui profil kandidat |
| `/reset` | Bersihkan cache `job_scraper/` (dengan `all` juga reset profil) |

### Contoh Sesi End-to-End

```
1. /setup
   → "Peran: Backend Engineer, 15 jam/minggu, RAM 16GB, minat Fintech"

2. /scrape "Backend Engineer" "Jakarta"
   → Tabel 10 loker terbaik beserta skor kecocokan, contoh:
     ID | Perusahaan  | Posisi              | Match vs Gap | Ide                    | Skor
     7  | Kredivo     | Backend Eng (Golang)| Go baru, SQL kuat | Distributed rate-limiter | 82

3. /applyidea 7
   → Loop berjalan otomatis:
     TAHAP 1: baca loker #7 → mine 5 repo GitHub + 3 paper ArXiv
     TAHAP 2: draf 00-03 + diagram .mmd
     TAHAP 3: reviewer kritik (anti-CRUD + scope check) + render PNG
     TAHAP 4: Blueprint_Final.pdf + tracker CSV

4. /scaffold portfolios/kredivo_backend-engineer-golang
   → started_repo/ siap dikerjakan
```

---

## Spesifikasi File Output (Blueprint)

Setiap folder `portfolios/<perusahaan>_<posisi>/` berisi:

| File | Isi Wajib |
|---|---|
| `00_job_analysis.md` | Bedah Responsibilities/Requirements, masalah bisnis, tabel skill vs kebutuhan |
| `01_project_ideation.md` | 3 opsi ide: (1) Rekomendasi utama, (2) Fokus Infrastruktur, (3) Fokus AI/Data |
| `02_system_blueprint.md` | Struktur sesuai `05-blueprint-templates.md`: masalah, arsitektur (embed PNG), tech stack, skema DB, contract API, benchmark, sprint plan, bullet CV |
| `03_references_study.md` | ≥5 repo GitHub + ≥3 paper ArXiv + penjelasan bagian mana yang diadaptasi |
| `diagrams/*.mmd` | Sumber Mermaid (flowchart `system_architecture`, sequenceDiagram `user_workflow`) |
| `diagrams/*.png` | Hasil render otomatis dari `.mmd` |
| `Blueprint_Final.md` | Dokumen gabungan (auto-generate) |
| `Blueprint_Final.pdf` | PDF final |
| `starter_repo/` | (jika `/scaffold` dijalankan) boilerplate kode produksi |

## Aturan Mermaid (Wajib untuk render PNG sukses)

1. `system_architecture.mmd` → gunakan `flowchart TD` atau `flowchart LR`
2. `user_workflow.mmd` → gunakan `sequenceDiagram`
3. **Bungkus label mengandung tanda kurung/karakter khusus dengan kutip ganda:**
   - Benar: `A["FastAPI (Backend)"] --> B["PostgreSQL / pgvector"]`
   - Salah: `A[FastAPI (Backend)] --> B[PostgreSQL / pgvector]`
4. Hindari tag HTML `<br/>` di dalam `sequenceDiagram`

---

## Engine Detail (Data, Scraper, dan Limitasi)

### Data Source Portfolio

| Sumber | Endpoint / Library | Output Folder |
|---|---|---|
| Lowongan kerja | `python-jobspy` (indeed, LinkedIn, glassdoor*; jobstreet otomatis kalau tersedia di versi library) | `job_scraper/latest_scrape.json` |
| Repository GitHub | GitHub Search API `api.github.com/search/repositories` | `job_scraper/github_refs.json` |
| Paper ilmiah | ArXiv API `export.arxiv.org/api/query` | `job_scraper/arxiv_refs.json` |
| Halaman web | Jina Reader `r.jina.ai/<url>` → fallback direct GET | stdout |

> \* Glassdoor **di-drop otomatis** jika lokasi mengandung "indonesia"/"jakarta", karena country tidak didukung.

### Batasan `python-jobspy` versi 1.4.0 (terbaru saat ini)

- `jobstreet` **belum didukung** PyPI (site valid: linkedin, indeed, zip_recruiter, glassdoor, google, bayt, naukri, bdjobs, hellowork).
- Script otomatis mencatat versi baru apabila `python-jobspy` update dan menambah dukungan jobstreet — tidak perlu edit kode.
- Untuk opsi JobStreet custom scraper manual, pantau repositori upstream: https://github.com/cullenwatson/jobs-scraper

### Anti Prompt Injection

Semua teks lowongan dari internet **wajib** melewati:

```bash
python tools/posting_guard.py <file_raw> > <file_clean>
```

Baris berpola berikut dibuang otomatis:
- `ignore (all) previous/prior instructions`
- `system prompt`
- `you are now a ...`
- `disregard above`

---

## Troubleshooting

| Gejala | Penyebab | Solusi |
|---|---|---|
| `python3: command not found` / tampil Windows Store | Windows stub alias menghalangi | Buat shim `python3.cmd` di `%APPDATA%\npm` yang memanggil `python.exe` asli; atau hapus alias di `%LOCALAPPDATA%\Microsoft\WindowsApps\python3.exe` |
| `ModuleNotFoundError: jobspy` | Modul tidak terinstal | `pip install python-jobspy` |
| `Invalid site_name: 'jobstreet'` (versi lama jobspy) | library belum mendukung | Sudah ditangani otomatis — site tidak valid dilewati (`[i] Site tidak didukung ... dilewati`) |
| Chromium launch fail `0xC000007B` / `2147483651` | Chromium hasil unduhan puppeteer gagal dijalankan di mesin ini | Sistem sudah otomatis: pakai `tools/.puppeteer-config.json` + `PUPPETEER_EXECUTABLE_PATH` mengacu ke Chrome/Edge yang terinstal |
| `npx` tidak terdeteksi di Python (WinError 2) | `subprocess` di Windows sedan `.cmd`; `npx` adalah `npx.cmd` | Sudah ditangani — script memakai `shutil.which("npx")` |
| `UnicodeEncodeError: cp1252` saat print teks web | Windows console default bukan UTF-8 | Sudah ditangani di `fetch_page.py`, `posting_guard.py` — `sys.stdout.reconfigure(encoding="utf-8")` |
| `HTTP Error 403` saat render via Kroki | Cloudflare memblokir jaringan/IP | Fallback otomatis ke mermaid-cli (npx) |
| ArXiv timeout pada percobaan pertama | Jaringan/relay lambat; timeout set ke 30s | Jalankan ulang command — retry manual |
| PDF gagal / tidak ada | Node/npx tidak berjalan, atau Chromium gagal launch | compile_pdf.py exit 1 — jalankan verify_pdf.py untuk diagnosis |
| Slash command tidak muncul di OpenCode | symlink `.opencode/command` belum ada | Jalankan `bash setup_cli_links.sh` (atau shortcut Windows) |
| WSL error `Windows Subsystem for Linux has no installed distributions` | bash bawaan mengarah ke WSL | Pakai Git Bash: `"C:\Program Files\Git\bin\bash.exe" setup_cli_links.sh` |

---

## View Layer Detail

- **Compile Diagram:** `tools/compile_diagrams.py <folder_diagrams>` — render semua `.mmd` jadi `.png` dengan prioritas: (1) `npx mermaid-cli` + puppeteer config ke Chrome/Edge yang terinstal; (2) fallback Kroki API; (3) exit 1 jika keduanya gagal.
- **Compile PDF:** `tools/compile_pdf.py <folder_portofolio>` — gabungan `00...03 .md`, tambah `Lampiran Diagram Visual` versi blueprint belum menyisipkan gambar, lalu render ke PDF via `md-to-pdf` (env `PUPPETEER_EXECUTABLE_PATH` di-detect otomatis dari Chrome/Edge).
- **Verify PDF:** `tools/verify_pdf.py <pdf>` — cek file ada + ukuran ≥ 5 KB.

## Tips Praktis

- Folder `documents/` kosong → `/setup` akan otomatis bertanya 5 poin profil; tak perlu CV siap.
- Waktu kosongkan `job_scraper/` cache tanpa menghapus profil: `/reset` tanpa argumen.
- Reset profil + cache: `/reset all`.
- Untuk perusahaan spesifik: tambahkan nama perusahaan ke query `/scrape`, misal `/scrape "Backend Kredivo" "Jakarta"`.
- 15 jam/pekan, 2–3 minggu adalah default template batasan; ubah di `.claude/skills/portfolio-architect/02-constraints-profile.md` kapan pun.

## Catatan Lisensi & Sumber

- Library scraping lowongan: [python-jobspy](https://pypi.org/project/python-jobspy/) — gunakan bertanggung jawab, mematuhi robots & terms of service portal.
- Struktur sistem, skill, tools, dan template adalah konfigurasi lokal milik repositori ini, bebas dimodifikasi.
