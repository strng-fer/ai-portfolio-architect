# Token Discipline & Output Contract

Tujuan: hasil kerja tetap bermutu, tetapi token yang dibakar minimal. Dokumen adalah produk. Chat hanya status.

## 1. Aturan Chat (berlaku untuk semua command)

- **Dilarang** menampilkan draf, isi file, tabel panjang, atau proses berpikir di chat.
- Satu baris status per fase. Contoh: `[1/4] Data loker + referensi siap`.
- Output akhir maksimal **10 baris**: path PDF, path prompt pack (jika ada), 3 bullet temuan, 1 baris next step.
- Jangan mengulang instruksi user, jangan merangkum dokumen yang baru ditulis, jangan menawarkan bantuan tambahan.
- Jangan menyalin isi file ke chat "untuk konfirmasi". Tulis file, sebut path-nya.
- Tanpa emoji, tanpa banner, tanpa tabel hiasan.

## 2. Aturan Baca (input token)

- **Jangan** membaca `latest_scrape.json`, `github_refs.json`, `arxiv_refs.json` secara utuh. Ukurannya puluhan KB.
  Gunakan `python3 tools/job_digest.py` dan `python3 tools/ref_digest.py`.
- Baca file panjang dengan rentang baris (`offset`/`limit`) atau `grep`. Baca penuh hanya jika file < 150 baris.
- Jangan membaca ulang file yang baru saja ditulis sendiri.
- Jangan membaca seluruh `PLAN.md`/`README.md` untuk menjalankan tugas. Butuh aturan? Baca modul skill yang relevan saja.
- Satu file referensi dibaca sekali per sesi. Simpan ringkasan 1 baris di catatan kerja internal, bukan di chat.

## 3. Aturan Tulis (output token)

Batas kata per file. Ini batas keras, bukan saran.

| File | Maks kata | Isi |
|---|---|---|
| `00_job_analysis.md` | 450 | kebutuhan loker, gap, 1 paragraf masalah bisnis |
| `01_project_ideation.md` | 550 | 3 opsi ringkas + pilihan + alasan |
| `02_system_blueprint.md` | 1500 | konsep arsitektur, data, metrik, roadmap |
| `03_references_study.md` | 400 | 3 repo + 2 paper, masing-masing 1–2 baris |
| `04_review_report.md` | 350 | maks 12 temuan, format tabel |
| `05_agent_prompts.md` | 900 | 1 prompt konteks + 1 prompt per milestone + 1 prompt review |

Aturan tambahan:
- Tidak ada duplikasi antar file. Fakta ditulis sekali di tempat paling relevan.
- Tidak ada pengulangan kesimpulan di akhir setiap bab.
- Tanpa basa-basi pembuka ("Tentu", "Berikut adalah"). Langsung isi.
- Tabel lebih murah daripada prosa berulang. Pakai tabel untuk perbandingan.

## 4. Aturan Kedalaman (konsep, bukan kode)

Blueprint adalah **dokumen keputusan dan pemahaman**, bukan tutorial implementasi.

Dilarang di dalam blueprint:
- Blok kode lebih dari 5 baris, pseudocode panjang, DDL `CREATE TABLE`, payload JSON penuh.
- Struktur folder per-file, daftar dependency lengkap, konfigurasi Docker.
- Langkah instalasi, perintah shell, atau tutorial langkah-demi-langkah.
- Nama fungsi/kelas internal. Sebut tanggung jawab komponen, bukan simbol kode.

Wajib ada: masalah, aktor, alur, komponen + tanggung jawab, konsep data, konsep antarmuka, teori/algoritma kunci, metrik, risiko, non-goals, roadmap, bullet CV.

Kode detail diserahkan ke `05_agent_prompts.md` (prompt untuk agent lain) atau `/scaffold` (opsional).

## 5. Anggaran per Fase `/applyidea`

| Fase | Batas kerja |
|---|---|
| 1. Akuisisi + riset | 3 tool call digest, tanpa dump |
| 2. Draf | tulis 5 file sekali jalan, tanpa revisi gaya |
| 3. Review | patch beda minimal, bukan tulis ulang dokumen |
| 4. Render + PDF | jalankan tool, laporkan hasil 1 baris |

Reviewer hanya boleh mengubah bagian yang gagal quality gate. Dilarang menulis ulang file yang sudah lolos.

## 6. Eksekusi Tool
- Satu tool call per langkah, sekali per fase. Jangan mengulang tool hanya untuk menampilkan ulang output.
- Jangan membuka/membaca PDF atau PNG hasil jadi. Percayai `verify_pdf.py`.
- Kutip log error maksimal 5 baris terakhir.

## 7. Larangan Umum

- Jangan mengulang isi PDF di chat setelah kompilasi.
- Jangan membuat ringkasan eksekutif kedua di dalam dokumen.
- Jangan menambahkan bab baru di luar template.
- Jangan meminta konfirmasi di tengah alur kecuali ada data yang benar-benar hilang.
