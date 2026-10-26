#!/usr/bin/env python3
"""Prove a portfolio product is actually live and usable.

Product mode ends with a URL, not a repo. This checks the URL the way a stranger
would: reachable, HTTPS, fast enough, healthy, and honest about failure.

Usage:
  python3 tools/deploy_check.py https://my-app.hf.space
  python3 tools/deploy_check.py https://my-app.hf.space --max-cold 45
  python3 tools/deploy_check.py portfolios/<slug>        # reads the URL from the blueprint

Exit codes:
  0 = the product passes the shipping bar
  1 = a blocking problem (unreachable, no HTTPS, health failing)
  2 = no URL found
"""
import argparse
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

URL_RE = re.compile(r"https?://[a-z0-9][a-z0-9.-]*\.[a-z]{2,}(?::\d+)?(?:/[^\s)\]|,]*)?", re.I)
HEALTH_PATHS = ("/healthz", "/health", "/api/health", "/status")


def find_url(target):
    if target.startswith(("http://", "https://")):
        return target.rstrip(".,;")
    folder = Path(target)
    for name in ("02_system_blueprint.md", "README.md", "01_project_ideation.md"):
        path = folder / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for match in URL_RE.finditer(text):
            url = match.group(0)
            if any(bad in url for bad in ("github.com", "arxiv.org", "localhost", "127.0.0.1")):
                continue
            return url
    return None


def fetch(url, timeout):
    started = time.perf_counter()
    req = urllib.request.Request(url, headers={"User-Agent": "portfolio-deploy-check/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            body = res.read(200_000).decode("utf-8", errors="replace")
            return res.status, time.perf_counter() - started, body, None
    except urllib.error.HTTPError as exc:
        return exc.code, time.perf_counter() - started, "", f"HTTP {exc.code}"
    except urllib.error.URLError as exc:
        return None, time.perf_counter() - started, "", str(exc.reason)
    except (ssl.SSLError, OSError) as exc:
        return None, time.perf_counter() - started, "", str(exc)


def check(base, max_cold):
    """Return (findings, blocking_count, health_path, elapsed).

    Each finding is (name, ok, detail, blocking). A non-blocking failure is a
    warning the owner should fix, not a reason to call the product unshippable.
    """
    findings, blocking = [], 0

    if not base.startswith("https://"):
        findings.append(("https", False, "URL is not HTTPS; a stranger sees a browser warning", True))
        blocking += 1
    else:
        findings.append(("https", True, "HTTPS", False))

    status, elapsed, body, err = fetch(base, timeout=max_cold)
    if err or status is None:
        findings.append(("reachable", False, f"cannot load the page: {err}", True))
        return findings, blocking + 1, None, elapsed

    findings.append(("reachable", True, f"HTTP {status} in {elapsed:.1f}s", False))
    if elapsed > max_cold:
        findings.append(("cold_start", False, f"{elapsed:.0f}s exceeds the {max_cold}s first-value budget", True))
        blocking += 1
    else:
        findings.append(("cold_start", True, f"{elapsed:.1f}s within the {max_cold}s budget", False))

    lowered = body.lower()
    if len(body) < 400:
        findings.append(("content", False, f"only {len(body)} bytes of HTML; likely a placeholder page", True))
        blocking += 1
    elif "application error" in lowered or "internal server error" in lowered:
        findings.append(("content", False, "page renders a server-error screen", True))
        blocking += 1
    else:
        findings.append(("content", True, f"{len(body)} bytes of HTML, no error screen", False))

    health = None
    missing_health = []
    for path in HEALTH_PATHS:
        h_status, h_elapsed, _, h_err = fetch(base.rstrip("/") + path, timeout=max_cold)
        if h_status == 200 and not h_err:
            health = path
            findings.append(("health", True, f"{path} returns 200 in {h_elapsed:.1f}s", False))
            break
        if h_status is None:
            missing_health.append(path)
    if health is None:
        detail = (
            "connection failed on every health path"
            if len(missing_health) == len(HEALTH_PATHS)
            else "no health endpoint answered 200; add /healthz so uptime is observable"
        )
        findings.append(("health", False, detail, False))

    return findings, blocking, health, elapsed


def main():
    parser = argparse.ArgumentParser(description="Check a deployed portfolio product")
    parser.add_argument("target", help="URL or portfolio folder")
    parser.add_argument("--max-cold", type=float, default=60.0, help="first-load budget in seconds")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    url = find_url(args.target)
    if not url:
        print(f"[X] ERROR no product URL found in {args.target}")
        print("[i] put the deployed URL in section 14 of 02_system_blueprint.md")
        return 2

    findings, blocking, health, elapsed = check(url, args.max_cold)

    if args.json:
        print(json.dumps({"url": url, "blocking": blocking, "health": health,
                          "findings": [{"check": c, "ok": ok, "detail": d, "blocking": b}
                                       for c, ok, d, b in findings]},
                         indent=2, ensure_ascii=False))
        return 0 if blocking == 0 else 1

    print(f"url: {url}")
    warnings = 0
    for name, ok, detail, is_blocking in findings:
        if ok:
            mark = "ok  "
        elif is_blocking:
            mark = "FAIL"
        else:
            mark = "warn"
            warnings += 1
        print(f"  {mark} {name:<10} {detail}")
    print(f"[=] {blocking} blocking issue(s), {warnings} warning(s) | "
          f"first load {elapsed:.1f}s | health {health or 'none'}")
    return 0 if blocking == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
