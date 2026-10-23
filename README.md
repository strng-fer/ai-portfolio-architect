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
| **Konseptual, Bukan Kode** | Blueprint hanya memuat ide, desain, teori, masalah, solusi, metrik, roadmap. Kode detail diserahkan ke `05_agent_prompts.md` atau `/scaffold` |
| **Hemat Token** | Chat = status saja, dokumen berbatas kata, input via digest script. Aturan: `.claude/skills/portfolio-architect/08-token-discipline.md` |
| **Agent Prompt Pack** | `05_agent_prompts.md` berisi P0 konteks + 1 prompt per milestone + prompt review, siap dieksekusi Cursor/Claude Code/Codex |

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
        ├── 02_system_blueprint.md     (konsep arsitektur, data, metrik, roadmap, bullet CV)
        ├── 03_references_study.md     (3 repo GitHub, 2 paper ArXiv)
        ├── 04_review_report.md        (quality gate, maks 12 temuan)
        ├── 05_agent_prompts.md        (opsional --prompts: prompt siap eksekusi)
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
   /prompt ────────────► 05_agent_prompts.md   (untuk agent lain)
   /scaffold ──────────► starter_repo/         (opsional, boilerplate)
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
│   ├── commands/                      # 8 slash command
│   └── skills/portfolio-architect/    # 10 file knowledge base (SKILL + 9 modul)
├── .agents/skills/                    # 3 CLI miner (scraper data eksternal)
│   ├── jobspy-search/search.py        # Scraper lowongan (indeed/LinkedIn/glassdoor)
│   ├── github-repo-miner/mine_github.py   # Cari repo referensi GitHub
│   └── arxiv-paper-miner/mine_arxiv.py    # Cari paper ilmiah ArXiv
├── tools/
│   ├── fetch_page.py                  # Ambil isi halaman web (via Jina Reader)
│   ├── posting_guard.py               # Filter prompt injection dari iklan lowongan
│   ├── job_digest.py                  # Ringkasan loker hemat token (ganti baca JSON mentah)
│   ├── ref_digest.py                  # Ringkasan repo/paper hemat token
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
| `/scrape "<posisi>" "<lokasi>"` | Scraping loker → hitung Portfolio Leverage Score → tabel top 10 (ringkas) |
| `/rank` | Urutkan ulang berdasarkan rubrik `04-gap-evaluation.md` |
| `/applyidea <URL atau ID> [--prompts]` | Alur utama: analisis loker → riset GitHub/ArXiv → 3 ide → blueprint konseptual → diagram → PDF → tracker. `--prompts` ikut membuat paket prompt agent |
| `/prompt <folder_portofolio>` | Buat/perbarui `05_agent_prompts.md`: instruksi siap eksekusi untuk agent lain |
| `/scaffold <folder_portofolio>` | Opsional. Starter repo ringkas (struktur, docker, TODO) |
| `/expand` | Pindai dokumen/repo baru untuk memperbarui profil kandidat |
| `/reset` | Bersihkan cache `job_scraper/` (dengan `all` juga reset profil) |

### Contoh Sesi End-to-End

```
1. /setup
   → "Peran: Backend Engineer, 15 jam/minggu, RAM 16GB, minat Fintech"

2. /scrape "Backend Engineer" "Jakarta"
   → Tabel 10 baris, contoh:
     ID | Perusahaan | Posisi              | Skor | Ide
     7  | Kredivo    | Backend Eng (Golang)| 82   | Distributed rate-limiter

3. /applyidea 7 --prompts
   → 4 fase, chat hanya status:
     [1/4] data loker + referensi siap
     [2/4] draf 00-03 + 05 + 2 diagram
     [3/4] review gate lulus
     [4/4] PDF + tracker

4. Kerjakan dengan agent lain memakai portfolios/<slug>/05_agent_prompts.md
   → /scaffold portfolios/<slug> hanya bila butuh starter repo
```

> Token yang dibaca agent: `job_digest.py` (10 baris) + `ref_digest.py` (5 baris) + 3 modul skill. Bukan JSON 96 KB.

---

## Spesifikasi File Output (Blueprint)

Setiap folder `portfolios/<perusahaan>_<posisi>/` berisi:

| File | Isi Wajib | Batas |
|---|---|---|
| `00_job_analysis.md` | Bedah Responsibilities/Requirements, masalah bisnis, tabel skill vs kebutuhan | 450 kata |
| `01_project_ideation.md` | 3 opsi ide: (1) Rekomendasi utama, (2) Fokus Infrastruktur, (3) Fokus AI/Data + non-goals | 550 kata |
| `02_system_blueprint.md` | Struktur sesuai `05-blueprint-templates.md`: masalah, konsep arsitektur (embed PNG), tech stack, konsep data & antarmuka, teori kunci, metrik, roadmap, bullet CV. **Tanpa kode detail** | 1500 kata |
| `03_references_study.md` | 3 repo GitHub + 2 paper ArXiv + bagian yang dipelajari (1–2 baris masing-masing) | 400 kata |
| `04_review_report.md` | Quality gate: tabel maks 12 temuan + verdict | 350 kata |
| `05_agent_prompts.md` | (opsional) Paket prompt agent: P0 konteks + 1 prompt per milestone + prompt review | 900 kata |
| `diagrams/*.mmd` | Sumber Mermaid (flowchart `system_architecture`, sequenceDiagram `user_workflow`) | maks 15 node |
| `diagrams/*.png` | Hasil render otomatis dari `.mmd` | — |
| `Blueprint_Final.md` | Dokumen gabungan (auto-generate, termasuk 04 & 05) | — |
| `Blueprint_Final.pdf` | PDF final | — |
| `starter_repo/` | (jika `/scaffold` dijalankan) boilerplate ringkas | — |

**Larangan isi blueprint:** blok kode > 5 baris, DDL `CREATE TABLE`, payload JSON penuh, struktur folder per-file, tutorial instalasi, nama fungsi internal. Detail eksekusi pindah ke `05_agent_prompts.md` atau `/scaffold`.

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

### Digest Hemat Token

| Script | Fungsi | Keluaran |
|---|---|---|
| `tools/job_digest.py list --top 10` | 1 baris per loker: id, perusahaan, posisi, lokasi, skor, stack terdeteksi | ~10 baris |
| `tools/job_digest.py detail <id>` | Detail 1 loker, deskripsi dipotong 1800 karakter (`--full` untuk utuh) | ~15 baris |
| `tools/ref_digest.py --repo 3 --paper 2` | Repo urut bintang + paper ArXiv | ~12 baris |

Tanpa digest, agent membaca JSON mentah 20–100 KB per panggilan. Dengan digest, cukup beberapa KB.

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
- **Compile PDF:** `tools/compile_pdf.py <folder_portofolio>` — gabungan `00...05 .md`, tambah `Lampiran Diagram Visual` bila blueprint belum menyisipkan gambar, lalu render ke PDF via `md-to-pdf` (env `PUPPETEER_EXECUTABLE_PATH` di-detect otomatis dari Chrome/Edge).
- **Verify PDF:** `tools/verify_pdf.py <pdf>` — cek file ada + ukuran ≥ 5 KB.

## Tips Praktis

- Folder `documents/` kosong → `/setup` akan otomatis bertanya 5 poin profil; tak perlu CV siap.
- Waktu kosongkan `job_scraper/` cache tanpa menghapus profil: `/reset` tanpa argumen.
- Reset profil + cache: `/reset all`.
- Untuk perusahaan spesifik: tambahkan nama perusahaan ke query `/scrape`, misal `/scrape "Backend Kredivo" "Jakarta"`.
- 15 jam/pekan, 2–3 minggu adalah default template batasan; ubah di `.claude/skills/portfolio-architect/02-constraints-profile.md` kapan pun.
- Hemat token: jalankan `/applyidea <id> --prompts` sekali, lalu kerjakan milestone dengan agent lain memakai `05_agent_prompts.md`. `/scaffold` hanya bila perlu.
- Blueprint sengaja konseptual. Bila butuh detail implementasi, minta agent lain mengeksekusi prompt pack, bukan menambah bab kode ke blueprint.

## Catatan Lisensi & Sumber

- Library scraping lowongan: [python-jobspy](https://pypi.org/project/python-jobspy/) — gunakan bertanggung jawab, mematuhi robots & terms of service portal.
- Struktur sistem, skill, tools, dan template adalah konfigurasi lokal milik repositori ini, bebas dimodifikasi.
