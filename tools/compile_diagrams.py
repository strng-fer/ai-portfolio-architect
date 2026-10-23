#!/usr/bin/env python3
import base64
import json
import shutil
import subprocess
import sys
import urllib.request
import zlib
from pathlib import Path

CHROME_CANDIDATES = [
    "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
    "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
]

def make_puppeteer_config() -> Path:
    """Kroki mermaid 403 Cloudflare; 401 chromium cache perlu executablePath browser sistem."""
    cfg = {"args": ["--no-sandbox", "--disable-setuid-sandbox"]}
    for cand in CHROME_CANDIDATES:
        if Path(cand).exists():
            cfg["executablePath"] = cand
            break
    cfg_path = Path("tools/.puppeteer-config.json")
    cfg_path.write_text(json.dumps(cfg), encoding="utf-8")
    return cfg_path

def render_with_mmdc(mmd_path: Path, out_png: Path) -> bool:
    try:
        cfg_path = make_puppeteer_config() if not Path("tools/.puppeteer-config.json").exists() else Path("tools/.puppeteer-config.json")
        npx = shutil.which("npx") or shutil.which("npx.cmd") or "npx"
        cmd = [npx, "--yes", "@mermaid-js/mermaid-cli", "-i", str(mmd_path), "-o", str(out_png), "-b", "white", "-s", "2", "-p", str(cfg_path)]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return res.returncode == 0 and out_png.exists()
    except Exception:
        return False

def render_with_kroki(mmd_path: Path, out_png: Path) -> bool:
    try:
        code = mmd_path.read_text(encoding="utf-8")
        compressed = zlib.compress(code.encode("utf-8"), 9)
        payload = base64.urlsafe_b64encode(compressed).decode("ascii")
        url = f"https://kroki.io/mermaid/png/{payload}"
        req = urllib.request.Request(url, headers={"User-Agent": "AI-Portfolio-Architect/1.0"})
        with urllib.request.urlopen(req, timeout=20) as res:
            out_png.write_bytes(res.read())
        return out_png.exists() and out_png.stat().st_size > 100
    except Exception as e:
        print(f"[!] Kroki fallback gagal untuk {mmd_path.name}: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tools/compile_diagrams.py <diagrams_folder>")
        sys.exit(1)

    diag_dir = Path(sys.argv[1])
    mmd_files = list(diag_dir.glob("*.mmd"))
    if not mmd_files:
        print(f"[!] Tidak ada file .mmd di {diag_dir}")
        sys.exit(1)

    all_ok = True
    for mmd in mmd_files:
        out_png = mmd.with_suffix(".png")
        print(f"[*] Merender {mmd.name} -> {out_png.name}...")
        if not render_with_mmdc(mmd, out_png):
            print("[*] Mencoba fallback render via Kroki...")
            if not render_with_kroki(mmd, out_png):
                print(f"[X] Gagal merender {mmd.name}. Periksa sintaks Mermaid!")
                all_ok = False
                continue
        print(f"[+] Sukses membuat {out_png}")

    if not all_ok:
        sys.exit(1)

if __name__ == "__main__":
    main()
