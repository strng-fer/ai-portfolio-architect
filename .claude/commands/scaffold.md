---
description: Buat starter repo dari blueprint (opsional, tidak masuk alur utama)
---

Target: `$ARGUMENTS`

Jika `05_agent_prompts.md` ada, workstation utama sudah cukup dengan prompt pack itu — tanyakan 1 baris apakah tetap ingin scaffold.

Langkah:
1. Baca `02_system_blueprint.md` bagian 4 (stack), 5 (data & antarmuka), 8 (roadmap). Jangan baca bagian lain.
2. Buat `$ARGUMENTS/starter_repo/` berisi: struktur folder, `docker-compose.yml`/`Dockerfile`, file dependency, 2–3 file boilerplate inti, `README.md` ringkas (maks 40 baris), dan `TODO.md` per milestone.
3. Jangan menulis test atau logika bisnis penuh. Kode detail adalah tugas milestone di prompt pack.
4. Output maksimal 5 baris: path repo, jumlah file, 1 baris catatan.
