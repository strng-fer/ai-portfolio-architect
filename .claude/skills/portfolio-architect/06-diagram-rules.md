# Mermaid Diagram Rules

Diagram adalah pengganti paragraf. Jaga kecil agar render cepat dan terbaca di PDF.

## Batas ukuran
- `system_architecture.mmd`: maks **15 node**, maks 2 tingkat kedalaman.
- `user_workflow.mmd`: maks **6 aktor/partisipan**, maks 12 pesan utama.
- Satu diagram = satu gagasan. Jika lebih, pecah jadi diagram baru, bukan menumpuk node.

## Sintaks
1. `flowchart TD` atau `flowchart LR` untuk arsitektur; `sequenceDiagram` untuk alur.
2. Bungkus label yang memuat tanda kurung, garis miring, titik dua, atau karakter khusus dengan tanda kutip ganda:
   - Benar: `A["FastAPI (API)"] --> B["PostgreSQL / pgvector"]`
   - Salah: `A[FastAPI (API)] --> B[PostgreSQL / pgvector]`
3. Tanpa tag HTML (`<br/>`, `<b>`) di dalam `sequenceDiagram`.
4. ID node pendek (`A`, `B`, `C`), label deskriptif. Tanpa emoji.

## Isi label
- Arsitektur: komponen + peran (`"Queue (buffer antrean)"`), bukan nama kelas.
- Alur: aktor manusia atau sistem (`User`, `API`, `Worker`), pesan berupa aksi.
- Jangan menaruh kode, path file, atau nama fungsi di diagram.

## Label perilaku wajib (murah, tapi penting)
- Tandai batas kepercayaan: `"LLM (tidak dipercaya)"` vs `"Verifier (deterministik)"`.
- Tandai titik gagal: `"Queue (retry + DLQ)"`.
- Tandai keputusan: `"Cache (hit/miss)"`.
Cukup 3 label tambahan. Jangan menghiasi semua node.
