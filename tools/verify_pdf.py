#!/usr/bin/env python3
import sys
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tools/verify_pdf.py <pdf_path>")
        sys.exit(1)

    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f"[X] PDF file not found: {pdf_path}")
        sys.exit(1)

    size_kb = pdf_path.stat().st_size / 1024
    if size_kb < 5:
        print(f"[X] PDF too small ({size_kb:.1f} KB), probably corrupt.")
        sys.exit(1)

    print(f"[+] PDF verified: {pdf_path} ({size_kb:.1f} KB)")

if __name__ == "__main__":
    main()
