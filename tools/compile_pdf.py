#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
from pathlib import Path

CHROME_CANDIDATES = [
    "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
    "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
]

def detect_system_browser() -> str:
    for cand in CHROME_CANDIDATES:
        if Path(cand).exists():
            return cand
    return ""

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tools/compile_pdf.py <portfolio_output_dir>")
        sys.exit(1)

    target_dir = Path(sys.argv[1])
    ordered_files = [
        "00_job_analysis.md",
        "01_project_ideation.md",
        "02_system_blueprint.md",
        "03_references_study.md",
        "04_review_report.md",
        "05_agent_prompts.md",
    ]

    combined_parts = []
    for fname in ordered_files:
        fpath = target_dir / fname
        if fpath.exists():
            combined_parts.append(fpath.read_text(encoding="utf-8"))

    if not combined_parts:
        print(f"[X] No blueprint markdown found in {target_dir} (expected 00_job_analysis.md ... 05_agent_prompts.md)")
        sys.exit(1)

    # Pastikan diagram terlampir jika belum di-embed di dalam 02_system_blueprint.md
    combined_text = "\n\n---\n\n".join(combined_parts)
    if "diagrams/system_architecture.png" not in combined_text and (target_dir / "diagrams/system_architecture.png").exists():
        combined_text += (
            "\n\n---\n\n## Lampiran Diagram Visual\n\n"
            "### System Architecture\n![](diagrams/system_architecture.png)\n\n"
            "### User & Data Workflow\n![](diagrams/user_workflow.png)\n"
        )

    full_md = target_dir / "Blueprint_Final.md"
    full_md.write_text(combined_text, encoding="utf-8")
    print(f"[+] Combined document written to {full_md}")

    out_pdf = target_dir / "Blueprint_Final.pdf"
    if out_pdf.exists():
        out_pdf.unlink()  # never let a stale PDF pass as the new render
    print("[*] Converting to PDF with md-to-pdf...")
    npx = shutil.which("npx") or shutil.which("npx.cmd") or "npx"
    cmd = [npx, "--yes", "md-to-pdf", str(full_md)]
    env = dict(os.environ)
    browser = detect_system_browser()
    if browser:
        env["PUPPETEER_EXECUTABLE_PATH"] = browser
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=90, env=env)
    if res.returncode == 0 and out_pdf.exists():
        print(f"[+] PDF created: {out_pdf}")
        sys.exit(0)
    else:
        print(f"[!] md-to-pdf output: {res.stderr}")

    print("[!] Make sure Node.js/npx is available for automatic PDF compilation.")
    sys.exit(1)

if __name__ == "__main__":
    main()
