# Candidate Constraints & Environment

> Sumber: Wawancara interaktif `/setup` (Jalur B). Terakhir diperbarui: 2026-02-13

## Waktu
- **Ketersediaan Waktu**: 5–8 jam / minggu (**sangat terbatas**).
- **Target Durasi Per Project**: 3–4 minggu (Total **20–32 jam kerja efektif**).
- **Implikasi Scope**: Wajib *Narrow & Deep* — maksimal **1 masalah inti** per project, maksimal 1 model/sistem utama, tanpa frontend berlebih. Blueprint harus memuat *milestone per minggu* dan daftar *explicit non-goals* (yang sengaja tidak dikerjakan).

## Perangkat Lokal
- **Spesifikasi**: RAM 16GB, laptop standar (CPU-only atau GPU terbatas).
- **Implikasi**: Dilarang mengandalkan training/fine-tuning model besar secara lokal. Gunakan model pra-terlatih kecil (mis. YOLO-n/s, MobileNet, atau `sentence-transformers` mini), inference CPU, dan dataset kecil yang sudah dikurasi.

## Anggaran Cloud / API
- **Anggaran**: **$0** — wajib *free-tier only*, tanpa kartu kredit bila memungkinkan.
- **Layanan yang Disarankan**: Hugging Face Spaces/Inference (free), Render/Railway free tier atau Fly.io, Supabase/Neon (Postgres free), Cloudflare R2/Pages, GitHub Actions (CI gratis untuk repo publik), Groq/Gemini free tier untuk LLM.
- **Aturan**: Setiap blueprint harus mencantumkan **batas kuota free-tier** dan **strategi fallback** (mis. *local inference*, caching, model quantization, atau mock mode) agar demo tetap hidup saat kuota habis.

## Batasan Tambahan
- **Tidak ada beban produksi nyata** — nilai jual dicapai lewat *benchmark terukur* (latency p95, throughput, akurasi pada evaluation set) yang bisa dijalankan di free-tier.
- **Portabilitas**: Semua project harus bisa dijalankan ulang dengan `docker compose up` atau satu perintah Makefile, agar reviewer bisa memverifikasi klaim di CV.
