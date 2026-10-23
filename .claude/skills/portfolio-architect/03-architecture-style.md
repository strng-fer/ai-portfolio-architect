# Architecture & Ideation Standards

## Prinsip Utama: "Built Like Production, Scoped Like a Sprint"
Setiap ide project portofolio yang dirancang WAJIB memenuhi kriteria berikut:
1. **Satu Masalah Inti yang Dalam (Narrow & Deep)**:
   Lebih baik membuat satu fitur *payment reconciliation engine* yang menangani *race condition* dan *idempotency* dengan sempurna daripada membuat aplikasi kloningan *e-commerce* utuh tapi dangkal.
2. **Memiliki Metrik Kuantitatif (Measurable Benchmark)**:
   Setiap blueprint wajib menyertakan cara menguji performa sistem (misal: menggunakan `k6`/`locust` untuk beban trafik, atau *evaluation dataset* untuk sistem AI/ML).
3. **Menjembatani Background Peserta**:
   Gunakan domain yang sudah akrab bagi peserta (dari `01-candidate-profile.md`) sebagai konteks kasus, lalu terapkan teknologi yang diminta oleh perusahaan target.
