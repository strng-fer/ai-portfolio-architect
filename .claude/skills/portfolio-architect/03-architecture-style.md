# Architecture & Ideation Standards

## Prinsip Utama: "Built Like Production, Scoped Like a Sprint"
Setiap ide project portofolio WAJIB memenuhi:
1. **Satu Masalah Inti yang Dalam (Narrow & Deep)**: satu mekanisme yang benar-benar sulit (konsistensi, evaluasi, latensi, duplikasi, kepatuhan) lebih bernilai daripada aplikasi utuh yang dangkal.
2. **Metrik Kuantitatif**: setiap blueprint menyebut cara mengukur (benchmark beban, evaluation set, metrik akurasi/latensi) dan baseline pembanding.
3. **Menjembatani Background Peserta**: domain yang sudah akrab dipakai sebagai konteks, teknologi baru dari loker dipakai sebagai tantangan belajar.

## Kedalaman Dokumen: Konsep, Bukan Kode
Blueprint adalah dokumen keputusan. Yang wajib ada: masalah, aktor, alur, komponen + tanggung jawab, konsep data, konsep antarmuka, teori kunci, metrik, risiko, roadmap.
Yang dilarang: implementasi, DDL, payload penuh, struktur folder, tutorial. Detail teknis diserahkan ke `05_agent_prompts.md`.

## Pagar Anti-Overengineering Dokumen
- Satu konsep dijelaskan sekali. Rujuk silang, jangan ulang.
- Teori cukup nama + 1 kalimat kegunaan. Bukan penjelasan akademik.
- Tabel menggantikan prosa berulang. Maks 6 kolom.
- Setiap bab harus bisa dihapus tanpa merusak bab lain, kecuali bagian masalah.

## Kualitas Ide: Uji Tiga Pertanyaan
1. Apakah masalahnya bisa dijelaskan dalam 1 kalimat tanpa menyebut teknologi?
2. Apakah ada satu bagian yang sulit dan layak dibahas di interview?
3. Apakah hasilnya bisa dibuktikan dengan angka dalam waktu yang tersedia?
Jika ada jawaban "tidak", revisi ide sebelum menulis blueprint.
