#!/usr/bin/env python3
import sys
import urllib.request
import re

# Force UTF-8 on Windows (cp1252 cannot encode unicode from web pages)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def fetch_url(url: str) -> str:
    # Try Jina Reader first, it returns clean Markdown
    jina_url = f"https://r.jina.ai/{url}"
    req = urllib.request.Request(
        jina_url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; AI-Portfolio-Architect/1.0)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            return res.read().decode("utf-8", errors="ignore")
    except Exception:
        pass

    # Fallback: Direct GET request
    req_direct = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}
    )
    with urllib.request.urlopen(req_direct, timeout=20) as res:
        html = res.read().decode("utf-8", errors="ignore")
        text = re.sub(r"<script.*?>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<style.*?>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        return re.sub(r"\s+", " ", text).strip()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tools/fetch_page.py <url>", file=sys.stderr)
        sys.exit(1)
    print(fetch_url(sys.argv[1]))
