# Skill: Portfolio Architect

Skill berisi profil kandidat, standar kualitas, template dokumen, dan aturan hemat token untuk merancang project portofolio yang ditargetkan pada satu lowongan kerja.

## Daftar Modul

**Dasar (baca sesuai kebutuhan, jangan semua sekaligus)**
1. `01-candidate-profile.md` — kompetensi dan latar belakang kandidat.
2. `02-constraints-profile.md` — batas waktu, perangkat, dan kuota free-tier.
3. `03-architecture-style.md` — aturan kualitas ide (anti-CRUD, production-grade, terukur).

**Penilaian**
4. `04-gap-evaluation.md` — rubrik Portfolio Leverage Score.

**Output (low-level concept)**
5. `05-blueprint-templates.md` — struktur `02_system_blueprint.md` (konsep, alternatif desain, teori, workflow, ≤1500 kata).
6. `06-diagram-rules.md` — aturan Mermaid agar render bersih, maks 15 node.
7. `07-cv-bullet-generator.md` — rumus Google XYZ untuk bullet CV.
8. `09-lowlevel-output.md` — template ringkas `00`/`01`/`03`/`04` + quality gate.

**Hemat token & eksekusi**
9. `08-token-discipline.md` — kontrak output, batas baca, batas kata, larangan detail kode. **Wajib dibaca sebelum menjalankan command apa pun.**
10. `10-agent-prompt-pack.md` — struktur `05_agent_prompts.md` untuk dieksekusi agent lain. Contoh terisi: `templates/agent_prompt_pack.example.md`.

## Urutan baca standar `/applyidea`
`08` → `09` → `05` → `06` → `01` → `02` → `03`. Itu sudah cukup. Modul `04` hanya untuk `/scrape` dan `/rank`. Modul `10` hanya bila `--prompts`.
