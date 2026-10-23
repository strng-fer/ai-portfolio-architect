---
description: Buat paket prompt/instruksi agent dari blueprint yang sudah ada
---

Target folder portofolio: `$ARGUMENTS`

Baca `02_system_blueprint.md` (bagian roadmap, stack, non-goals) dan `01_project_ideation.md` (bagian pilihan). Jangan baca file lain.

Tulis `$ARGUMENTS/05_agent_prompts.md` mengikuti `.claude/skills/portfolio-architect/10-agent-prompt-pack.md`:
- P0 context prompt (berdiri sendiri, memuat stack, batasan free-tier, konvensi, larangan).
- Satu prompt per milestone roadmap (maks 6).
- Satu prompt review/benchmark.
- Setiap prompt ≤150 kata, format Goal / Context / Task / Constraints / Deliverable / Done when / Out of scope.

Lalu jalankan `python3 tools/compile_pdf.py $ARGUMENTS` dan `python3 tools/verify_pdf.py $ARGUMENTS/Blueprint_Final.pdf`.

Output maksimal 5 baris: path prompt pack, jumlah prompt, path PDF, 1 baris catatan.
