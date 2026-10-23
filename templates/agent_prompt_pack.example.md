# Agent Prompt Pack — <Nama Project>

Cara pakai: tempel `P0` di awal setiap sesi baru, lalu prompt milestone secara berurutan. Satu milestone = satu sesi. Jangan lompat.

Urutan: `P0` → `P1` → `P2` → `P3` → `P4` → `P5`.

---

## P0 — Context Prompt

**Goal**: Menyiapkan agent agar bekerja pada project ini tanpa perlu penjelasan ulang.

**Context**: `02_system_blueprint.md` bagian 2 (tujuan/non-goals), 4 (arsitektur), 5 (stack).

**Task**:
1. Baca tiga bagian blueprint tersebut.
2. Ringkas kembali stack, batasan, dan non-goals dalam 5 baris.
3. Tunggu prompt milestone berikutnya.

**Constraints**: Python 3.11, free-tier only, RAM 16GB, CPU-only inference, tanpa model besar lokal. Bahasa kode Inggris, komentar minimal.

**Deliverable**: ringkasan konteks 5 baris di awal sesi.

**Done when**: ringkasan menyebut stack, batas kuota, dan minimal 2 non-goals.

**Out of scope**: menulis fitur, mengubah blueprint.

---

## P1 — <Milestone 1: Fondasi>

**Goal**: <hasil akhir 1 kalimat>.

**Context**: `02_system_blueprint.md` bagian 7 (data & antarmuka), 10 (workflow fase 1).

**Task**:
1. <langkah imperatif>
2. <langkah imperatif>
3. <langkah imperatif>

**Constraints**: <bahasa, framework, batas waktu, larangan>.

**Deliverable**: <file/endpoint/test yang harus ada>.

**Done when**: <perintah verifikasi> lulus dan <metrik> tercapai.

**Out of scope**: <fitur yang tidak boleh disentuh di fase ini>.

---

## P2 — <Milestone 2>

(Format sama: Goal / Context / Task / Constraints / Deliverable / Done when / Out of scope.)

---

## P5 — Review & Benchmark

**Goal**: Membuktikan klaim performa dan menemukan regresi.

**Context**: `02_system_blueprint.md` bagian 9 (metrik & validasi).

**Task**:
1. Jalankan skenario benchmark pada baseline dan versi baru.
2. Bandingkan hasil dengan target di blueprint.
3. Laporkan temuan dalam tabel: Area | Masalah | Keparahan | Perbaikan.

**Constraints**: tanpa mengubah arsitektur saat mengukur. Ukur 3 kali, ambil median.

**Deliverable**: `benchmark_report.md` maks 1 halaman.

**Done when**: setiap metrik target punya angka aktual dan verdict lulus/tidak.

**Out of scope**: refactor besar, fitur baru.
