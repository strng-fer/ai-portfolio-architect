#!/usr/bin/env python3
import re
import sys
from pathlib import Path

# Force UTF-8 di Windows (cp1252 menghambat karakter unicode dari halaman web)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SUSPICIOUS_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"system\s+prompt",
    r"you\s+are\s+now\s+a",
    r"disregard\s+above",
]

def sanitize_text(raw: str) -> str:
    clean_lines = []
    for line in raw.splitlines():
        flagged = False
        for pat in SUSPICIOUS_PATTERNS:
            if re.search(pat, line, flags=re.IGNORECASE):
                flagged = True
                break
        if not flagged:
            clean_lines.append(line)
    return "\n".join(clean_lines)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        content = sys.stdin.read()
    else:
        content = Path(sys.argv[1]).read_text(encoding="utf-8", errors="ignore")
    print(sanitize_text(content))
