# AI Portfolio Architect

Sistem berbasis AI agent ([CC] / OpenCode / AI CLI lain) yang menganalisis lowongan kerja nyata, memetakan *skill gap* kandidat, mencari referensi GitHub dan ArXiv, lalu merancang **Blueprint Project Portofolio berstandar produksi** - diagram arsitektur, dokumen Markdown konseptual, dan PDF.

**Bahasa:** [English](README.md) (default) | Bahasa Indonesia (file ini)
Ganti bahasa output dengan `/lang en` atau `/lang id`.

---

## Konsep Inti

| Komponen | Peran |
|---|---|
| **Portfolio Leverage Score** | Skor 0-100 kecocokan loker (bobot: Skill-Bridge 40, Problem Clarity 30, Reusability 30) |
| **Drafter-Reviewer Loop** | Draf dibuat, lalu dikritisi persona *Staff Engineer* sebelum finalisasi |
| **Anti-CRUD Rule** | Dilarang ide CRUD generik (To-Do, katalog e-commerce, kloning sosmed, wrapper API tipis). Ide wajib menyerang tantangan teknis spesifik dari loker |
| **Google XYZ Formula** | Rumus bullet CV: *"Achieved [X] as measured by [Y], by doing [Z]"* |
| **Konsep, Bukan Kode** | Blueprint memuat ide, desain, teori, masalah, solusi, metrik, workflow. Detail implementasi pindah ke `05_agent_prompts.md` atau `/scaffold` |
| **Hemat Token** | Chat hanya status, dokumen berbatas kata, input via digest script. Aturan: `.claude/skills/portfolio-architect/08-token-discipline.md` |
| **Agent Prompt Pack** | `05_agent_prompts.md` berisi P0 konteks + 1 prompt per milestone + prompt review, siap dieksekusi Cursor/[CC]/Codex |
| **Terbukti, Bukan Klaim** | Setiap baris metrik wajib punya Target angka, Instrument yang dinamai, dan Baseline. `tools/check_portfolio.py` memblokir PDF bila klaim tidak bisa dibuktikan |

## Arsitektur Alur Kerja

```
documents/ (CV, LinkedIn, transkrip)
        |
        v
     /setup -----------------> .claude/skills/portfolio-architect/
        |                        01-candidate-profile.md
        |                        02-constraints-profile.md
        v
   /scrape "<posisi>" "<lokasi>" --> .agents/skills/jobspy-search/search.py
        |                                   |
        v                                   v
  job_scraper/latest_scrape.json <---- JobStreet / Kalibrr / Indeed / LinkedIn
        |                              (+ glassdoor, zip_recruiter, bayt, naukri,
        |                               bdjobs, hellowork, google via --sites)
        |
        v
      /rank ----------------> job_scraper/ranked_jobs.json
        |
        v
  /applyidea <URL | ID> [--prompts] --> job_scraper/current_job_raw.txt
        |                                    | posting_guard.py (filter prompt injection)
        |                                    v
        |                             current_job_clean.md
        +--> .agents/skills/github-repo-miner/mine_github.py --> github_refs.json
        +--> .agents/skills/arxiv-paper-miner/mine_arxiv.py  --> arxiv_refs.json
        |                                    | tools/ref_digest.py (ringkasan padat)
        v                                    v
  portfolios/<perusahaan>_<posisi>/
        |-- 00_job_analysis.md
        |-- 01_project_ideation.md     (3 opsi ide)
        |-- 02_system_blueprint.md     (konsep arsitektur, data, teori, metrik, workflow, bullet CV)
        |-- 03_references_study.md     (3 repo GitHub, 2 paper ArXiv)
        |-- 04_review_report.md        (quality gate, maks 12 temuan)
        |-- 05_agent_prompts.md        (opsional --prompts: prompt siap eksekusi)
        `-- diagrams/
              |-- *.mmd                (Mermaid source)
              `-- *.png                (hasil compile_diagrams.py)
        |
        v
  tools/check_portfolio.py  <-- gerbang validasi: budget, bab wajib, metrik terbukti
        |
        v
  tools/compile_pdf.py --> Blueprint_Final.md --> Blueprint_Final.pdf
        |                        (verify_pdf.py)
        v
  portfolio_tracker.csv  (status: BLUEPRINT_READY)
        |
        v
   /prompt ------------> 05_agent_prompts.md   (untuk agent lain)
   /scaffold ----------> starter_repo/         (opsional, boilerplate)
```

## Struktur Direktori

```
ai-portfolio-architect/
|-- CLAUDE.md                          # Aturan sistem (dibaca AI agent)
|-- AGENTS.md                          # Salinan CLAUDE.md (standar OpenCode)
|-- README.md                          # Dokumentasi Inggris (default)
|-- README.id.md                       # Dokumentasi Indonesia
|-- setup_cli_links.sh                 # Script integrasi lintas AI CLI
|-- portfolio_tracker.csv              # Tracker semua blueprint
|-- .claude/
|   |-- settings.json                  # Whitelist permission Bash
|   |-- config/lang.md                 # Setelan bahasa output (satu-satunya sumber)
|   |-- commands/                      # 10 slash command
|   `-- skills/portfolio-architect/    # 13 modul pengetahuan (SKILL + 00-11)
|-- .agents/skills/                    # 3 CLI miner (data eksternal)
|   |-- jobspy-search/search.py        # Scraper lowongan (multi-board)
|   |-- jobspy-search/boards.py        # Scraper langsung: JobStreet (SEEK), Kalibrr
|   |-- github-repo-miner/mine_github.py   # Referensi repo GitHub
|   `-- arxiv-paper-miner/mine_arxiv.py    # Referensi paper ArXiv
|-- tools/
|   |-- fetch_page.py                  # Ambil halaman web (Jina Reader)
|   |-- posting_guard.py               # Filter prompt injection iklan lowongan
|   |-- job_digest.py                  # Ringkasan loker hemat token
|   |-- ref_digest.py                  # Ringkasan repo/paper hemat token (urut relevansi)
|   |-- check_portfolio.py             # Gerbang validasi: budget, bab, metrik terbukti
|   |-- prompt_contract.py             # Ekstrak kontrak eksekusi (perintah + metrik)
|   |-- scaffold_repo.py               # Buat starter repo sesuai kontrak itu
|   |-- portfolio_status.py            # Status semua portfolio dalam satu perintah
|   |-- compile_diagrams.py            # Render .mmd -> .png
|   |-- compile_pdf.py                 # Gabung Markdown -> PDF
|   |-- verify_pdf.py                  # Validasi PDF
|   `-- .puppeteer-config.json         # (auto-generate) path Chrome/Edge
|-- documents/                         # Dokumen kandidat
|-- job_scraper/                       # Cache scraping
|-- portfolios/                        # Output blueprint per loker
|-- templates/                         # Aset boilerplate + contoh prompt pack
`-- .opencode/command                   # Salinan agar command jalan di OpenCode
```

---

## Persyaratan

| Komponen | Kebutuhan | Keterangan |
|---|---|---|
| **Python** | >= 3.10 | Windows: buat shim `%APPDATA%\npm\python3.cmd` |
| **Node.js** | >= 18 (npx tersedia) | Render diagram Mermaid & konversi PDF |
| **Google Chrome / MS Edge** | Minimal 1 terinstal | Engine puppeteer |
| **Git Bash (Windows)** | Opsional | Untuk `setup_cli_links.sh` |
| **Internet** | Diperlukan | Scraping loker, GitHub API, ArXiv API |

## Langkah Setup

### 1. Dependensi Python

```bash
pip install python-jobspy requests
```

### 2. Paket Node global

```bash
npm install -g --allow-scripts=puppeteer @mermaid-js/mermaid-cli
npm install -g --allow-scripts=puppeteer md-to-pdf
```

> `--allow-scripts=puppeteer` penting agar postinstall Chromium berjalan.
> Jika Chromium gagal launch di Windows (`0xC000007B`), sistem otomatis memakai Chrome/Edge terinstal via `tools/.puppeteer-config.json`.

### 3. Script integrasi

```bash
bash setup_cli_links.sh
```

Windows (Git Bash):
```bash
"C:\Program Files\Git\bin\bash.exe" setup_cli_links.sh
```

Script melakukan empat hal: menyalin `CLAUDE.md` ke `AGENTS.md` (copy, bukan symlink, agar aman di semua sistem file), menyalin `.claude/commands/*.md` ke `.opencode/command/`, `chmod +x` semua script Python, dan membuat `.claude/config/lang.md` (English) bila belum ada. Jalankan ulang setiap kali `CLAUDE.md` diedit.

### 4. Verifikasi

```bash
python tools/fetch_page.py "https://example.com"
python .agents/skills/github-repo-miner/mine_github.py --query "python" --limit 2
python .agents/skills/arxiv-paper-miner/mine_arxiv.py --query "rag" --limit 2
python .agents/skills/jobspy-search/search.py --query "backend engineer jakarta" --limit 5
python .agents/skills/jobspy-search/search.py --query "AI Engineer" --location Indonesia --sites jobstreet,kalibrr --limit 5
```

---

## Cara Pakai

| Perintah | Fungsi |
|---|---|
| `/setup` | Onboarding: baca `documents/` atau 5 pertanyaan singkat |
| `/scrape "<posisi>" "<lokasi>"` | Scraping loker lintas board, hitung Portfolio Leverage Score, tabel 10 baris. Set board lewat `--sites`, proxy LinkedIn lewat `--proxies` |
| `/rank` | Urutkan ulang memakai rubrik `04-gap-evaluation.md` |
| `/applyidea <URL atau ID> [--prompts] [--no-pdf]` | Alur utama: analisis, riset, 3 opsi, blueprint konseptual, diagram, PDF, tracker |
| `/prompt <folder>` | Buat atau perbarui `05_agent_prompts.md` untuk agent lain |
| `/scaffold <portfolio_folder>` | Generate `starter_repo/`: failing test per milestone, benchmark script per metric, `Makefile`, `README` dengan tabel metrik, `TODO` |
| `/status [portfolio_folder]` | Laporkan status tiap portfolio (BLUEPRINT_READY / MARKDOWN_ONLY / INCOMPLETE / UNTRACKED) dan aksi berikutnya |
| `/lang <en\|id>` | Ganti bahasa output (default English) |
| `/expand` | Perkaya profil dari dokumen atau repo baru |
| `/reset` | Bersihkan cache (`all` juga reset profil) |

### Contoh Sesi End-to-End

```
1. /setup
   -> "Peran: Backend Engineer, 15 jam/minggu, RAM 16GB, minat fintech"

2. /scrape "Backend Engineer" "Jakarta"
   -> tabel 10 baris:
     ID | Perusahaan | Posisi              | Skor | Ide
     7  | Tokopedia  | Backend Eng (Golang)| 82   | Distributed rate-limiter

3. /applyidea 7 --prompts
   -> 4 fase, chat hanya status:
     [1/4] data loker + referensi siap
     [2/4] draf 00-03 + 05 + 2 diagram
     [3/4] review gate lulus
     [4/4] PDF + tracker

4. Kerjakan dengan agent lain memakai portfolios/<slug>/05_agent_prompts.md
```

> Yang dibaca agent: `job_digest.py` (10 baris) + `ref_digest.py` (5 baris) + 3 modul skill. Bukan JSON 96 KB.

---

## Spesifikasi Output Blueprint

| File | Isi wajib | Batas |
|---|---|---|
| `00_job_analysis.md` | Bedah responsibilities/requirements, masalah bisnis, tabel skill vs kebutuhan | 450 kata |
| `01_project_ideation.md` | 3 opsi + pilihan + non-goals | 550 kata |
| `02_system_blueprint.md` | Masalah, alternatif desain, konsep arsitektur (embed PNG), stack, konsep data & antarmuka, teori kunci, tantangan, metrik, workflow, bullet CV. **Tanpa detail implementasi** | 1500 kata |
| `03_references_study.md` | 3 repo GitHub + 2 paper ArXiv + bagian yang dipelajari | 400 kata |
| `04_review_report.md` | Quality gate: maks 12 temuan, tiap gate berisi bukti, hasil `check_portfolio.py` | 350 kata |
| `05_agent_prompts.md` | (opsional) P0 konteks + 1 prompt per milestone (dengan "Done when" yang bisa dijalankan) + prompt review | 900 kata |
| `diagrams/*.mmd` | `flowchart` arsitektur, `sequenceDiagram` workflow | maks 15 node |
| `diagrams/*.png` | Hasil render otomatis | - |
| `Blueprint_Final.md` / `.pdf` | Dokumen gabungan (00-05) | - |
| `starter_repo/` | (jika `/scaffold`) boilerplate ringkas | - |

**Yang di-commit:** sumber Markdown (`00`-`05`), sumber diagram `.mmd`, dan `portfolio_tracker.csv`.
**Yang dibuat ulang lokal (gitignored):** `Blueprint_Final.pdf`, `Blueprint_Final.md`, dan `diagrams/*.png`. Jalankan `tools/compile_diagrams.py` lalu `tools/compile_pdf.py` setelah clone.

**Dilarang dalam blueprint:** blok kode lebih dari 5 baris, DDL `CREATE TABLE`, payload JSON penuh, struktur folder per-file, tutorial instalasi, nama fungsi internal. Detail eksekusi pindah ke `05_agent_prompts.md` atau `/scaffold`.

## Aturan Mermaid

1. `system_architecture.mmd` -> `flowchart TD` / `flowchart LR`
2. `user_workflow.mmd` -> `sequenceDiagram`
3. Bungkus label dengan tanda kurung/karakter khusus memakai kutip ganda:
   - Benar: `A["FastAPI (Backend)"] --> B["PostgreSQL / pgvector"]`
   - Salah: `A[FastAPI (Backend)] --> B[PostgreSQL / pgvector]`
4. Tanpa tag HTML (`<br/>`) di `sequenceDiagram`

---

## Engine Detail

### Sumber Data

| Sumber | Endpoint / Library | Output |
|---|---|---|
| Lowongan (native) | `python-jobspy` - indeed, linkedin, glassdoor, zip_recruiter, bayt, naukri, bdjobs, hellowork, google | `job_scraper/latest_scrape.json` |
| Lowongan (API langsung) | JobStreet Indonesia (SEEK v5 JSON), API publik Kalibrr - lihat `boards.py` | `job_scraper/latest_scrape.json` |
| Repo GitHub | `api.github.com/search/repositories` | `job_scraper/github_refs.json` |
| Paper ilmiah | `export.arxiv.org/api/query` | `job_scraper/arxiv_refs.json` |
| Halaman web | Jina Reader `r.jina.ai/<url>` lalu fallback direct GET | stdout |

Setiap record membawa field `source`, jadi hasil ranking bisa dilacak ke board asalnya.

### Board Lowongan

Set default: `jobstreet,kalibrr,indeed,linkedin`. Ganti dengan `--sites`.

| Board | Akses | Status |
|---|---|---|
| `jobstreet` | API SEEK langsung (`id.jobstreet.com/api/jobsearch/v5`) | jalan, tanpa auth |
| `kalibrr` | API publik (`kalibrr.com/kjs/job_board/search`) | jalan, tanpa auth |
| `indeed`, `linkedin`, `glassdoor`, `zip_recruiter`, `bayt`, `naukri`, `bdjobs`, `hellowork` | `python-jobspy` | jalan; LinkedIn bisa balas HTTP 429 di IP rumahan |
| `google` | `python-jobspy` | saat ini kosong (scraper upstream rusak di 1.4.x) |
| `jobindo` | tidak ada | dilewati: aplikasi JS di balik anti-bot, tanpa API publik |
| `glints` | tidak ada | dilewati: API butuh cookie token login |

Poin desain:

- **Isolasi per board.** Tiap board punya try block sendiri, jadi satu 429 atau timeout tidak mematikan seluruh batch. Board yang gagal dilaporkan di akhir.
- **Batas round-robin.** Hasil diselang-seling antar board sebelum dipotong `--limit * 3`, sehingga board terakhir di daftar tidak pernah terpotong habis.
- **Gerbang relevansi.** Kalibrr mengembalikan seluruh katalognya saat query tidak cocok, jadi tiap hasil dicek ulang terhadap token query dan dibuang bila tidak relevan. Tanpa ini, query asal-asalan akan diam-diam mengembalikan ribuan lowongan tak terkait.
- **Deduplikasi.** Judul + perusahaan sama dari dua board disimpan sekali.

### Proxy (LinkedIn)

LinkedIn membatasi sebagian besar IP rumahan dan datacenter (HTTP 429). Pasang proxy:

```bash
python .agents/skills/jobspy-search/search.py --query "AI Engineer" --location Indonesia \
  --proxies "http://user:pass@host:port" --sites linkedin
```

Atau set `JOBSPY_PROXIES` sekali di environment. Board selain LinkedIn tidak memerlukannya.

### Exit Code

| Kode | Arti | Cache |
|---|---|---|
| 0 | minimal satu lowongan tersimpan | diganti |
| 1 | tidak ada lowongan | dipertahankan |
| 2 | `python-jobspy` tidak terpasang | dipertahankan |

### Anti Prompt Injection

```bash
python tools/posting_guard.py <file_raw> > <file_clean>
```

Baris berpola berikut dibuang: `ignore (all) previous/prior instructions`, `system prompt`, `you are now a ...`, `disregard above`.

### Digest Hemat Token

| Script | Fungsi | Keluaran |
|---|---|---|
| `tools/job_digest.py list --top 10` | 1 baris per loker: id, perusahaan, posisi, lokasi, skor, stack | sekitar 10 baris |
| `tools/job_digest.py detail <id>` | Detail 1 loker, deskripsi dipotong 1800 karakter (`--full` untuk utuh) | sekitar 15 baris |
| `tools/ref_digest.py --repo 3 --paper 2 --query "<kata kunci>"` | Repo urut relevansi lalu bintang + paper ArXiv | sekitar 12 baris |

Kedua digest gagal secara eksplisit: `job_digest` exit 1 bila cache hilang/korup, `ref_digest` exit 1 bila repo < `--min` atau paper < `--min-paper`, sehingga agent tidak bisa diam-diam mengutip kosong. Tanpa digest, agent membaca 20-100 KB JSON mentah per panggilan.

---

## Troubleshooting

| Gejala | Penyebab | Solusi |
|---|---|---|
| `python3: command not found` | Stub alias Windows | Buat shim `python3.cmd` di `%APPDATA%\npm`, atau hapus alias di `%LOCALAPPDATA%\Microsoft\WindowsApps\python3.exe` |
| `ModuleNotFoundError: jobspy` | Modul belum terinstal | `pip install python-jobspy` |
| `ModuleNotFoundError: requests` | Scraper board langsung membutuhkannya | `pip install requests` |
| `[!] linkedin: 429` | LinkedIn membatasi IP tersebut | Pakai `--proxies` atau set `JOBSPY_PROXIES`; board lain tetap jalan |
| `[i] jobindo: no public search API` | Board tanpa endpoint publik | Normal. Pakai `--sites jobstreet,kalibrr,indeed,linkedin` |
| `[i] glints: ... requires a logged-in cookie token` | Board mengunci API-nya | Normal. Tidak di-scrape |
| `[!] no postings returned. Keeping existing cache` | Query tidak cocok di semua board | Perlebar query; cache sebelumnya tetap utuh |
| Chromium fail `0xC000007B` | Chromium puppeteer tidak bisa jalan | Otomatis pakai Chrome/Edge via `tools/.puppeteer-config.json` |
| `npx` tidak terdeteksi (WinError 2) | Windows butuh `npx.cmd` | Ditangani, memakai `shutil.which("npx")` |
| `UnicodeEncodeError: cp1252` | Console bukan UTF-8 | Ditangani, `sys.stdout.reconfigure(encoding="utf-8")` |
| `HTTP Error 403` via Kroki | Cloudflare memblokir | Fallback otomatis ke mermaid-cli |
| ArXiv timeout | Relay lambat | Jalankan ulang |
| PDF gagal | Node/npx/Chromium bermasalah | `compile_pdf.py` exit 1, jalankan `verify_pdf.py` |
| Slash command tidak muncul | Salinan `.opencode/command` belum ada | `bash setup_cli_links.sh` |
| WSL error | bash mengarah ke WSL | Pakai Git Bash |

---

## View Layer Detail

- **Compile diagram:** `tools/compile_diagrams.py <folder_diagrams>` merender semua `.mmd` jadi `.png`, prioritas: (1) `npx mermaid-cli` + puppeteer config ke Chrome/Edge terinstal; (2) fallback Kroki API; (3) exit 1 bila keduanya gagal.
- **Compile PDF:** `tools/compile_pdf.py <folder_portofolio>` menggabungkan `00...05 .md`, menambah lampiran diagram bila blueprint belum menyisipkan gambar, lalu render via `md-to-pdf` (`PUPPETEER_EXECUTABLE_PATH` dideteksi otomatis).
- **Verify PDF:** `tools/verify_pdf.py <pdf> [--min-pages N]` memeriksa file ada, ukuran >= 5 KB, jumlah halaman, semua dokumen sumber masuk, dan tidak ada gambar yang rusak.
- **Check portfolio:** `tools/check_portfolio.py <folder> [--strict]` gerbang validasi: budget kata per file, bab wajib, larangan blok kode, baris metrik dengan target angka + instrument + baseline, gate review berbukti, dan perintah "Done when" yang bisa dijalankan. Exit 1 memblokir PDF.
- **Prompt contract:** `tools/prompt_contract.py <folder>` mengekstrak setiap perintah "Done when" dan setiap instrument metrik agar bisa diubah menjadi file nyata, bukan sekadar prosa.
- **Scaffold repo:** `tools/scaffold_repo.py <folder> [--dry-run] [--force]` menulis `starter_repo/` dengan satu test gagal per milestone (namanya menyebut requirement-nya), satu skrip benchmark per metrik, dan `Makefile` yang sudah memuat semua target yang dirujuk prompt. Test sengaja gagal sampai milestone dikerjakan.
- **Portfolio status:** `tools/portfolio_status.py [folder] [--json]` membaca tracker + artefak di disk dan melaporkan BLUEPRINT_READY, MARKDOWN_ONLY, INCOMPLETE, UNTRACKED, STALE_STATUS, atau NEEDS_REVIEW beserta aksi berikutnya.

## Tips Praktis

- `documents/` kosong, `/setup` menanyakan 5 poin profil.
- Hapus cache tanpa menghapus profil: `/reset`. Reset profil + cache: `/reset all`.
- Perusahaan spesifik: `/scrape "Backend Tokopedia" "Jakarta"`.
- Batasi board bila hanya percaya satu sumber: `--sites jobstreet,kalibrr` (default `jobstreet,kalibrr,indeed,linkedin`).
- Batas waktu default 15 jam/pekan, 2-3 minggu. Ubah di `02-constraints-profile.md`.
- Hemat token: jalankan `/applyidea <id> --prompts` sekali, lalu kerjakan milestone dengan agent lain memakai `05_agent_prompts.md`.
- Blueprint sengaja konseptual. Butuh detail implementasi? Minta agent lain mengeksekusi prompt pack.
- Bahasa: instruksi tetap Inggris, dokumen mengikuti `.claude/config/lang.md`, chat mengikuti bahasa yang kamu pakai.

## Lisensi & Sumber

- Library scraping: [python-jobspy](https://pypi.org/project/python-jobspy/). Gunakan bertanggung jawab, patuhi robots dan ToS portal.
- Struktur sistem, skill, tools, dan template adalah konfigurasi lokal repositori ini, bebas dimodifikasi.
