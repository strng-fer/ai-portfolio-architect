# Agent Prompt Pack (`05_agent_prompts.md`)

Tujuan: blueprint bisa langsung dieksekusi oleh agent lain (Cursor, Claude Code, Codex, Gemini CLI, ChatGPT) tanpa perlu menjelaskan ulang konteks. **Batas 900 kata.**

## Struktur file

```
# Agent Prompt Pack — <Nama Project>
Cara pakai (3 baris) + urutan eksekusi.

## P0 — Context Prompt (pakai di awal setiap sesi)
## P1 — <Milestone 1>
## P2 — <Milestone 2>
## P3 — <Milestone 3>
## P4 — <Milestone 4>
## P5 — Review & Benchmark
```

Jumlah milestone mengikuti roadmap di blueprint. Maks 6 prompt total.

## Format tiap prompt (wajib, urutan tetap)

- **Goal** — 1 kalimat hasil akhir.
- **Context** — file/section blueprint yang perlu dibaca agent (path relatif), maks 3.
- **Task** — 3–5 langkah, imperatif, satu tindakan per langkah.
- **Constraints** — bahasa/framework, batas waktu, batas kuota, gaya kode, hal yang dilarang.
- **Deliverable** — file/endpoint/test yang harus ada.
- **Done when** — kriteria verifikasi yang bisa dijalankan (test lulus, metrik tercapai, perintah sukses).
- **Out of scope** — hal yang tidak boleh dikerjakan di milestone ini.

## Aturan isi
- Setiap prompt berdiri sendiri: agent baru bisa mulai tanpa riwayat chat.
- Maks 150 kata per prompt. Tanpa kode panjang; sebut kontrak, bukan implementasi.
- Selalu sertakan non-goals dan batas free-tier dari `02-constraints-profile.md`.
- P0 memuat: tujuan project, stack, struktur folder yang diharapkan (5 baris), konvensi, dan larangan.
- Prompt review memuat perintah menjalankan test/benchmark dan format laporan temuan.
- Jangan menyertakan rahasia, token, atau URL internal.

Contoh terisi: `templates/agent_prompt_pack.example.md`.

## Varian opsional
Jika user meminta, tambahkan:
- `## P-Chat` — versi ringkas untuk chat assistant (tanpa akses file).
- `## P-Refactor` — instruksi perbaikan setelah benchmark gagal.
