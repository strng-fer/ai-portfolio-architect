#!/usr/bin/env python3
"""Ringkasan lowongan hemat token.

Jalankan sebelum membaca latest_scrape.json / ranked_jobs.json.
Agent cukup membaca keluaran ringkas ini, bukan file JSON penuh.

Usage:
  python3 tools/job_digest.py list                 # 10 loker teratas, 1 baris masing-masing
  python3 tools/job_digest.py detail <id>          # detail 1 loker, deskripsi dipotong
  python3 tools/job_digest.py detail <id> --full   # deskripsi utuh (hanya bila perlu)
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CANDIDATES = [
    ROOT / "job_scraper" / "ranked_jobs.json",
    ROOT / "job_scraper" / "latest_scrape.json",
]

TECH_HINTS = [
    "python", "go", "golang", "java", "typescript", "javascript", "rust", "sql",
    "fastapi", "django", "flask", "spring", "node", "react", "pytorch", "tensorflow",
    "sklearn", "postgres", "postgresql", "mysql", "mongo", "redis", "kafka", "rabbitmq",
    "docker", "kubernetes", "aws", "gcp", "azure", "airflow", "spark", "mlflow",
    "llm", "rag", "langchain", "vector", "pgvector", "qdrant", "opencv", "yolo",
]


def load():
    for path in CANDIDATES:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                data = data.get("jobs", data.get("results", []))
            if data:
                return data, path
    print("[!] Tidak ada job_scraper/*.json. Jalankan /scrape dulu.", file=sys.stderr)
    sys.exit(1)


def short(text, limit):
    text = re.sub(r"\s+", " ", (text or "")).strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def score(job):
    for key in ("score", "leverage_score", "portfolio_leverage_score"):
        if isinstance(job.get(key), (int, float)):
            return job[key]
    return None


def stack(text):
    low = (text or "").lower()
    found = [t for t in TECH_HINTS if re.search(rf"\b{re.escape(t)}\b", low)]
    return ", ".join(found[:6]) or "-"


def cmd_list(top):
    jobs, path = load()
    print(f"# sumber: {path.name} | total {len(jobs)} | tampil {min(top, len(jobs))}")
    for job in jobs[:top]:
        s = score(job)
        print(
            f"{job.get('id', '-')} | {short(job.get('company'), 24)} | "
            f"{short(job.get('title'), 40)} | {short(job.get('location'), 22)} | "
            f"skor={s if s is not None else '-'} | stack: {stack(job.get('description'))}"
        )


def cmd_detail(job_id, full):
    jobs, _ = load()
    for job in jobs:
        if str(job.get("id")) == str(job_id):
            desc = job.get("description") or ""
            print(f"id: {job.get('id')}")
            print(f"perusahaan: {job.get('company')}")
            print(f"posisi: {job.get('title')}")
            print(f"lokasi: {job.get('location')}")
            print(f"url: {job.get('job_url')}")
            print(f"stack terdeteksi: {stack(desc)}")
            print(f"panjang deskripsi: {len(desc)} karakter")
            print("--- deskripsi ---")
            print(desc if full else short(desc, 1800))
            if not full and len(desc) > 1800:
                print("--- terpotong: pakai --full bila benar-benar perlu ---")
            return
    print(f"[!] id {job_id} tidak ditemukan", file=sys.stderr)
    sys.exit(1)


def main():
    ap = argparse.ArgumentParser(add_help=True)
    sub = ap.add_subparsers(dest="cmd")
    p_list = sub.add_parser("list")
    p_list.add_argument("--top", type=int, default=10)
    p_detail = sub.add_parser("detail")
    p_detail.add_argument("id")
    p_detail.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.cmd == "detail":
        cmd_detail(args.id, args.full)
    else:
        cmd_list(getattr(args, "top", 10))


if __name__ == "__main__":
    main()
