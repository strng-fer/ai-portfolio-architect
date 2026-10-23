# Blueprint Document Structure (`02_system_blueprint.md`)

Level: **low-level concept**. Pembaca harus paham masalah, pilihan desain, teori yang dipakai, dan urutan eksekusi — tanpa membaca kode. **Batas 1500 kata.**

## Struktur heading (wajib, urutan tetap)

1. `# [Judul Project]` + 1 baris metadata (loker, stack, estimasi jam, status)
2. `## 1. Masalah & Relevansi` — masalah nyata, siapa yang dirugikan, kenapa sulit, kaitannya ke jobdesk. Maks 200 kata.
3. `## 2. Tujuan & Non-Goals` — 3–5 tujuan terukur; 2–4 non-goals eksplisit (pagar scope).
4. `## 3. Alternatif Desain & Keputusan` — 2–3 pendekatan. Tabel: Pendekatan | Kelebihan | Kekurangan | Kapan cocok. Lalu 1 paragraf keputusan + 1 baris alasan utama.
5. `## 4. Arsitektur & Alur` — embed `![](diagrams/system_architecture.png)` + `![](diagrams/user_workflow.png)`. Tabel komponen: Komponen | Tanggung Jawab | Batasan. Maks 8 komponen.
6. `## 5. Tech Stack & Jembatan Skill` — Tabel: Lapisan | Teknologi | Sudah dikuasai / Baru | Alasan.
7. `## 6. Teori & Rujukan Kunci` — 3–5 pattern/algoritma/teori. Format: Nama → kegunaan (1–2 kalimat) → kapan gagal.
8. `## 7. Data & Antarmuka (Konsep)` — entitas utama + relasi (prosa/tabel), 3–5 operasi antarmuka (nama, input, output, 1 baris). Tanpa DDL, tanpa JSON penuh.
9. `## 8. Masalah Teknis & Strategi Solusi` — 3–5 tantangan (konsistensi, duplikasi, latensi, evaluasi, biaya, keamanan). Format: Tantangan → Pendekatan → Teori → Cara membuktikan.
10. `## 9. Metrik & Validasi` — tabel Metrik | Target | Alat ukur | Baseline pembanding.
11. `## 10. Workflow Eksekusi Bertahap` — tabel Fase | Masukan | Keluaran | Definisi selesai. Sertakan estimasi jam per fase.
12. `## 11. Risiko & Mitigasi` — 3–5 baris (kuota free-tier, waktu, data, dependensi eksternal).
13. `## 12. Draf Bullet CV` — 3 bullet format XYZ (lihat `07-cv-bullet-generator.md`).

## Pagar gaya
- Teori disebut namanya + maks 2 kalimat (*idempotency key*, *recall@k*, *backpressure*). Bukan penjelasan akademik.
- Diagram menggantikan paragraf penjelas alur. Jangan jelaskan ulang isi diagram dengan prosa.
- Tanpa blok kode, tanpa DDL, tanpa payload, tanpa struktur folder, tanpa perintah instalasi, tanpa nama fungsi.
- Detail implementasi tidak masuk ke sini → muncul sebagai instruksi singkat di `05_agent_prompts.md`.
- Setiap bab ditulis sekali. Tanpa ringkasan ulang di akhir bab.
