#!/usr/bin/env python3
"""Direct board scrapers for portals jobspy does not cover.

Each function returns a list of normalized records:
    {title, company, location, job_url, description, source}

Only boards with a verified public JSON endpoint live here. Boards that need a
logged-in session or defeat plain HTTP (Glints, Jobindo) are intentionally absent;
`search.py` reports them as unsupported instead of shipping a scraper that breaks.
"""
import re

import requests

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
HEADERS = {"User-Agent": UA, "Accept": "application/json"}
TIMEOUT = 25


def _clean(value) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    return "" if text.lower() == "nan" else text


def _record(title, company, location, url, description, source) -> dict | None:
    title = _clean(title)
    if not title:
        return None
    return {
        "title": title,
        "company": _clean(company),
        "location": _clean(location),
        "job_url": _clean(url),
        "description": _clean(description)[:4000],
        "source": source,
    }


STOPWORDS = {
    "the", "and", "for", "with", "job", "jobs", "kerja", "lowongan",
    "of", "in", "at", "to", "is", "or", "on", "by", "an", "as",
}


def query_tokens(query: str) -> list[str]:
    """Significant lowercase tokens from the search query.

    Two-letter tokens are kept because domain terms like `ai` and `ml` carry the
    whole meaning of a query such as "AI Engineer".
    """
    raw = re.findall(r"[a-z0-9]+", (query or "").lower())
    return [t for t in raw if len(t) >= 2 and t not in STOPWORDS]


def matches_query(record: dict, tokens: list[str]) -> bool:
    """True when the posting plausibly concerns the query.

    Needed because some boards fall back to their entire catalogue instead of
    returning zero results, which would poison the ranking with unrelated jobs.
    """
    if not tokens:
        return True
    haystack = f"{record.get('title', '')} {record.get('description', '')}".lower()
    return any(token in haystack for token in tokens)


def search_jobstreet(query: str, location: str, limit: int) -> list[dict]:
    """SEEK-powered JobStreet Indonesia. Public search endpoint, no auth."""
    params = {
        "siteKey": "ID-Main",
        "sourcesystem": "houston",
        "keywords": query,
        "pageSize": min(max(limit, 5), 100),
    }
    if location and location.lower() not in {"indonesia", "any"}:
        params["where"] = location
    resp = requests.get(
        "https://id.jobstreet.com/api/jobsearch/v5/search",
        params=params,
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    payload = resp.json()
    out = []
    for job in payload.get("data") or []:
        locs = job.get("locations") or []
        loc = ", ".join(_clean(l.get("label")) for l in locs if l.get("label"))
        tags = [_clean(t) for t in (job.get("classifications") or []) if _clean(t)]
        bullets = " ".join(_clean(b) for b in (job.get("bulletPoints") or []))
        desc = " ".join(x for x in [job.get("teaser"), " ".join(tags), bullets] if x)
        rec = _record(
            job.get("title"),
            job.get("companyName"),
            loc,
            f"https://id.jobstreet.com/job/{job.get('id')}",
            desc,
            "jobstreet",
        )
        if rec:
            out.append(rec)
    return out


def search_kalibrr(query: str, location: str, limit: int) -> list[dict]:
    """Kalibrr public job-board API.

    Kalibrr falls back to its full catalogue when the query has no matches, so
    every result is re-checked against the query before it is kept.
    """
    params = {"limit": min(max(limit, 5), 50), "offset": 0, "text": query}
    if "indonesia" in (location or "").lower() or not location:
        params["country"] = "Indonesia"
    resp = requests.get(
        "https://www.kalibrr.com/kjs/job_board/search",
        params=params,
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    payload = resp.json()
    tokens = query_tokens(query)
    out = []
    for job in payload.get("jobs") or []:
        gl = job.get("google_location") or {}
        loc = ", ".join(
            x for x in [_clean(gl.get("city")), _clean(gl.get("region")), _clean(gl.get("country"))] if x
        )
        company = job.get("company") or {}
        code = _clean(company.get("code")) or _clean(job.get("company_name")).lower().replace(" ", "-")
        slug = _clean(job.get("slug")) or _clean(job.get("name")).lower().replace(" ", "-")
        desc = " ".join(
            x
            for x in [
                _clean(job.get("description")),
                _clean(job.get("qualifications")),
                " ".join(_clean(p) for p in (job.get("perks") or [])),
            ]
            if x
        )
        rec = _record(
            job.get("name"),
            job.get("company_name") or company.get("name"),
            loc,
            f"https://www.kalibrr.com/c/{code}/jobs/{job.get('id')}/{slug}",
            desc,
            "kalibrr",
        )
        if rec and matches_query(rec, tokens):
            out.append(rec)
    return out


# Boards reached through a direct API, keyed by the name users pass to --sites.
DIRECT_BOARDS = {
    "jobstreet": search_jobstreet,
    "kalibrr": search_kalibrr,
}

# Known boards with no usable public endpoint. Reported, never faked.
UNSUPPORTED_BOARDS = {
    "jobindo": "no public search API; page is a JS app behind anti-bot",
    "glints": "search API requires a logged-in cookie token",
}
