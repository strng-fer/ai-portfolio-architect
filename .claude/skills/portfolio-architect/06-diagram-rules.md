# Mermaid Diagram Rules

Agar kompilasi `.mmd` ke `.png` selalu berhasil tanpa syntax error:
1. Gunakan `flowchart TD` atau `flowchart LR` untuk `system_architecture.mmd`.
2. Gunakan `sequenceDiagram` untuk `user_workflow.mmd`.
3. **PENTING**: Selalu bungkus label teks node yang mengandung tanda kurung, garis miring, atau karakter khusus dengan tanda kutip ganda.
   - Salah: `A[FastAPI (Backend)] --> B[PostgreSQL / pgvector]`
   - Benar: `A["FastAPI (Backend)"] --> B["PostgreSQL / pgvector"]`
4. Hindari penggunaan tag HTML (`<br/>`) di dalam `sequenceDiagram`.
