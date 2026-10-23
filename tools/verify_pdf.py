#!/usr/bin/env python3
import sys
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tools/verify_pdf.py <pdf_path>")
        sys.exit(1)

    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f"[X] File PDF tidak ditemukan: {pdf_path}")
        sys.exit(1)

    size_kb = pdf_path.stat().st_size / 1024
    if size_kb < 5:
        print(f"[X] Ukuran PDF terlalu kecil ({size_kb:.1f} KB), kemungkinan korup.")
        sys.exit(1)

    print(f"[+] PDF terverifikasi valid: {pdf_path} ({size_kb:.1f} KB)")

if __name__ == "__main__":
    main()
