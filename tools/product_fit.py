#!/usr/bin/env python3
"""Filter and score portfolio ideas against the candidate's product intent.

The mechanism picker answers "is this hard enough?". This answers "would anyone
use it, and can this candidate actually ship it this month?".

Two jobs:
  pick    - score candidate ideas (mechanism x audience) and rank them
  check   - verify a finished blueprint carries the product-mode evidence

Usage:
  python3 tools/product_fit.py pick --mechanisms bounded-agent-loop,retrieval-fusion,eval-gate --audience "sme back-office staff"
  python3 tools/product_fit.py pick --mechanisms span-grounding --audience farmers --json
  python3 tools/product_fit.py check portfolios/<slug>
  python3 tools/product_fit.py audiences

Exit codes:
  0 = at least one idea is shippable / blueprint passes product mode
  1 = no shippable idea / blueprint fails product mode
  2 = intent file or pack missing
"""
import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

INTENT = Path(".claude/skills/portfolio-architect/01c-product-intent.md")
PACK_CONFIG = Path(".claude/config/pack.md")
PACK_DIR = Path(".claude/packs")

# Weights sum to 100. Fit dominates: an idea the named audience cannot use is not
# a product, it is a notebook with a UI bolted on.
W_AFFINITY = 30
W_REACH = 20
W_ASSET = 15
W_SURFACE = 15
W_HOURS = 10
W_REFUSAL = 10

MIN_SHIPPABLE = 60

# Which pack domains can serve which audience domain. Edit when the intent
# profile gains an audience; keep it explicit so the score stays explainable.
AFFINITY = {
    "agri": {"cv": 1.0, "ml": 0.9, "llm": 0.55, "data": 0.5, "mlops": 0.4, "backend": 0.35, "frontend": 0.2, "mobile": 0.3},
    "docops": {"llm": 1.0, "data": 0.9, "backend": 0.85, "ml": 0.7, "cv": 0.75, "mlops": 0.4, "frontend": 0.5, "mobile": 0.2},
    "devtools": {"backend": 1.0, "frontend": 1.0, "data": 0.95, "llm": 0.9, "mlops": 0.85, "ml": 0.7, "cv": 0.4, "mobile": 0.4},
}

# A failure mode the user can see is worth more than an internal one: it becomes
# the product's honest state instead of a silent wrong answer.
VISIBLE_FAILURE = ("refus", "needs more", "cannot", "unknown", "degrad", "wrong answer", "slow", "user-visible")


def read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def parse_intent(text):
    """Pull the fields that change the scoring decision out of the intent file."""
    mode = re.search(r"\|\s*Mode\s*\|\s*`([a-z]+)`", text)
    surface = re.search(r"\|\s*Surface\s*\|\s*(.+?)\s*\|", text)
    hosting = re.search(r"\|\s*Hosting\s*\|\s*(.+?)\s*\|", text)
    users = re.search(r"\|\s*Users\s*\|\s*(.+?)\s*\|", text)

    audiences = []
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 4 and cells[0].isdigit() and cells[0] in {"1", "2", "3", "4"}:
            audiences.append(
                {"rank": int(cells[0]), "name": cells[1], "today": cells[2], "domain": cells[3].lower()}
            )

    refusals = []
    in_block = False
    for line in text.splitlines():
        if line.strip().startswith("## ") and "Refusals" in line:
            in_block = True
            continue
        if in_block:
            if line.strip().startswith("## "):
                break
            if line.strip().startswith("- "):
                refusals.append(line.strip()[2:].strip().lower())

    assets = []
    in_block = False
    for line in text.splitlines():
        if line.strip().startswith("## ") and "Assets" in line:
            in_block = True
            continue
        if in_block:
            if line.strip().startswith("## "):
                break
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 2 and cells[0] and cells[0] != "Asset" and not set(cells[0]) <= set("-: "):
                assets.append(cells[0].lower())

    return {
        "mode": (mode.group(1) if mode else "product"),
        "surface": (surface.group(1) if surface else "web app"),
        "hosting": (hosting.group(1) if hosting else "free tier"),
        "users": (users.group(1) if users else "real external users"),
        "audiences": audiences,
        "refusals": refusals,
        "assets": assets,
    }


def active_pack():
    line = next((ln for ln in read_text(PACK_CONFIG).splitlines() if ln.lower().startswith("active pack:")), "")
    return line.split(":", 1)[1].strip() if ":" in line else "llm"


def load_pack(name):
    try:
        import yaml
    except ImportError:
        return {}
    path = PACK_DIR / f"{name}.yaml"
    if not path.is_file():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def load_catalogue():
    path = Path(".claude/skills/portfolio-architect/12-mechanism-catalogue.md")
    rows, header_seen = [], False
    for line in read_text(path).splitlines():
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|")):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) < 7 or all(set(c) <= set("-: ") for c in cells):
            continue
        if cells[0].lower() == "id":
            header_seen = True
            continue
        if not header_seen:
            continue
        mech_id = cells[0].strip("`")
        if re.fullmatch(r"[a-z0-9-]+", mech_id):
            rows.append(
                {
                    "id": mech_id,
                    "name": cells[1],
                    "domains": [d.strip() for d in cells[2].split(",") if d.strip()],
                    "fails": cells[6],
                    "metrics": cells[5],
                }
            )
    return rows


def score_idea(mech, audience, intent, pack, hours):
    """Return (score, criteria) where each criterion carries a reason."""
    criteria = []
    total = 0

    # 1. Audience affinity: can this mechanism's domain serve this audience at all?
    aud = next(
        (
            a
            for a in intent["audiences"]
            if audience.lower() in a["name"].lower() or a["name"].lower() in audience.lower()
        ),
        None,
    )
    domains = [d.lower() for d in mech["domains"]]
    if aud is None:
        criteria.append(("affinity", 0, W_AFFINITY, f"'{audience}' is not a named audience in the intent profile"))
    else:
        table = AFFINITY.get(aud["domain"], {})
        best = max((table.get(d, 0.0) for d in domains), default=0.0)
        # A lower-ranked audience is a weaker fit: less domain knowledge to draw
        # on, so the product needs more discovery work.
        rank_factor = {1: 1.0, 2: 0.85, 3: 0.7, 4: 0.6}.get(aud["rank"], 0.6)
        got = round(W_AFFINITY * best * rank_factor)
        if best >= 0.85:
            why = f"{'/'.join(domains)} directly serves a rank-{aud['rank']} {aud['domain']} audience"
        elif best >= 0.5:
            why = f"{'/'.join(domains)} serves {aud['domain']} only through a wrapper"
        else:
            why = f"{'/'.join(domains)} does not serve {aud['domain']} users; different audience wins"
        if rank_factor < 1.0:
            why += f" (rank {aud['rank']} penalty x{rank_factor})"
        criteria.append(("affinity", got, W_AFFINITY, why))
        total += got

    # 2. Reach: can the failure mode be shown to a non-expert?
    fails = mech["fails"].lower()
    visible = any(k in fails for k in VISIBLE_FAILURE)
    got = W_REACH if visible else round(W_REACH * 0.4)
    criteria.append(
        (
            "reach",
            got,
            W_REACH,
            "failure is user-visible and becomes an honest product state"
            if visible
            else "failure is internal; needs an explicit UI translation or the demo is theatre",
        )
    )
    total += got

    # 3. Asset reuse
    reuse = {"llm": "fastapi", "cv": "opencv", "ml": "pytorch", "backend": "fastapi", "data": "python"}
    hit = [d for d in domains if d in reuse]
    got = W_ASSET if hit else round(W_ASSET * 0.3)
    criteria.append(
        (
            "assets",
            got,
            W_ASSET,
            f"reuses {', '.join(reuse[d] for d in hit)}" if hit else "no existing asset reused",
        )
    )
    total += got

    # 4. Surface: does the pack's product shape land on the required surface?
    shape = str(pack.get("product_shape") or "")
    if intent["surface"].lower().startswith("web") and shape:
        got = W_SURFACE
        criteria.append(("surface", got, W_SURFACE, "pack supplies a web-facing product shape"))
    elif shape:
        got = round(W_SURFACE * 0.5)
        criteria.append(("surface", got, W_SURFACE, "pack shape exists but needs a surface translation"))
    else:
        got = 0
        criteria.append(("surface", 0, W_SURFACE, "pack has no product_shape"))
    total += got

    # 5. Hours: product work takes the last 25%, so the mechanism must leave room.
    room = hours * 0.75
    if room >= 18:
        got = W_HOURS
        criteria.append(("hours", got, W_HOURS, f"{room:.0f}h left for the mechanism after product work"))
    elif room >= 12:
        got = round(W_HOURS * 0.5)
        criteria.append(("hours", got, W_HOURS, f"tight: {room:.0f}h for the mechanism"))
    else:
        got = 0
        criteria.append(("hours", 0, W_HOURS, f"too tight: {room:.0f}h for the mechanism"))
    total += got

    # 6. Refusals: does the idea trip a stated refusal?
    idea_blob = f"{mech['name']} for {audience}".lower()
    tripped = [r for r in intent["refusals"] if any(w in idea_blob for w in r.split() if len(w) > 4)]
    if tripped:
        criteria.append(("refusal", 0, W_REFUSAL, f"trips refusal: {tripped[0][:60]}"))
    else:
        criteria.append(("refusal", W_REFUSAL, W_REFUSAL, "no stated refusal tripped"))
        total += W_REFUSAL

    return total, criteria


def cmd_pick(args):
    if not INTENT.is_file():
        print(f"[X] ERROR intent file missing: {INTENT}")
        print("[i] run /setup to create it")
        return 2

    intent = parse_intent(read_text(INTENT))
    if intent["mode"] != "product":
        print(f"[i] mode is '{intent['mode']}', not 'product'. Product checks are advisory only.")

    pack_name = args.pack or active_pack()
    pack = load_pack(pack_name)
    if not pack:
        print(f"[X] ERROR pack '{pack_name}' not loaded")
        return 2

    catalogue = {m["id"]: m for m in load_catalogue()}
    mechanisms = [m.strip() for m in args.mechanisms.split(",") if m.strip()]
    unknown = [m for m in mechanisms if m not in catalogue]
    if unknown:
        print(f"[!] unknown mechanism(s): {', '.join(unknown)}")
        mechanisms = [m for m in mechanisms if m in catalogue]
    if not mechanisms:
        print("[X] ERROR no known mechanism to score")
        return 1

    audiences = [args.audience] if args.audience else [a["name"] for a in intent["audiences"]]

    results = []
    for mech_id in mechanisms:
        mech = catalogue[mech_id]
        best = None
        for audience in audiences:
            total, criteria = score_idea(mech, audience, intent, pack, args.hours)
            if best is None or total > best[0]:
                best = (total, audience, criteria)
        total, audience, criteria = best
        results.append(
            {
                "mechanism": mech_id,
                "name": mech["name"],
                "audience": audience,
                "score": round(total, 1),
                "shippable": total >= MIN_SHIPPABLE,
                "criteria": [{"criterion": c, "got": g, "max": m, "why": w} for c, g, m, w in criteria],
            }
        )

    results.sort(key=lambda r: -r["score"])

    if args.json:
        print(json.dumps({"pack": pack_name, "mode": intent["mode"], "results": results}, indent=2, ensure_ascii=False))
        return 0 if any(r["shippable"] for r in results) else 1

    print(f"pack: {pack_name} | mode: {intent['mode']} | hours: {args.hours}")
    print("mechanism | audience | score | verdict")
    for r in results:
        verdict = "SHIPPABLE" if r["shippable"] else "not yet"
        print(f"{r['mechanism']} | {r['audience'][:34]} | {r['score']:.0f} | {verdict}")

    winner = results[0]
    print(f"\n[>] {winner['mechanism']}: {winner['score']:.0f}/100")
    for c in winner["criteria"]:
        print(f"    {c['criterion']:<9} {c['got']:>3}/{c['max']:<3} {c['why']}")

    blocked = [r for r in results if not r["shippable"]]
    if blocked:
        print(f"\n[!] {len(blocked)} idea(s) below the {MIN_SHIPPABLE} bar.")
        reasons = [c for c in blocked[0]["criteria"] if c["got"] < c["max"] // 2]
        for c in reasons[:3]:
            print(f"    fix {c['criterion']}: {c['why']}")

    return 0 if any(r["shippable"] for r in results) else 1


PRODUCT_SECTIONS = (
    "Product Surface",
    "Go-Live Plan",
)

EVIDENCE = {
    "url": re.compile(r"https?://[a-z0-9][a-z0-9.-]*\.[a-z]{2,}(?:/[^\s`|)]*)?", re.I),
    "first_value": re.compile(r"first value|60\s*s|60 seconds", re.I),
    "users": re.compile(r"\b(\d+)\s+(external )?users?\b", re.I),
    "fallback": re.compile(r"fallback|quota|free tier", re.I),
    "pending": re.compile(r"deploy(?:ment)?\s*(?:status)?\s*[:=-]\s*pending|url\s*[:=-]\s*pending", re.I),
}

# A placeholder URL passes a naive regex and proves nothing: the gate must not
# accept a link that cannot be opened.
PLACEHOLDER = re.compile(r"YOUR[-_]?(USER|NAME|APP|DOMAIN|SUBDOMAIN)|<[a-z-]+>|example\.(com|org)|TODO", re.I)

# Product mode has two honest states. `live` needs a real URL. `local` is a
# working product that runs, with the deploy still pending: allowed, but never
# reported as shippable.
DEPLOY_STATES = ("live", "local")


def cmd_check(args):
    folder = Path(args.folder)
    if not folder.is_dir():
        print(f"[X] ERROR folder not found: {folder}")
        return 1

    intent = parse_intent(read_text(INTENT)) if INTENT.is_file() else {"mode": "product"}
    product_mode = intent["mode"] == "product"
    blueprint = read_text(folder / "02_system_blueprint.md")
    prompts = read_text(folder / "05_agent_prompts.md")
    readme = read_text(folder / "README.md")

    errors, warnings = [], []

    if not blueprint:
        errors.append("02_system_blueprint.md missing")
    else:
        for section in PRODUCT_SECTIONS:
            if section.lower() not in blueprint.lower():
                msg = f"02_system_blueprint.md: missing section '{section}'"
                (errors if product_mode else warnings).append(msg)

    if product_mode:
        deploy_pending = bool(EVIDENCE["pending"].search(blueprint))
        url_match = EVIDENCE["url"].search(blueprint)
        if url_match and PLACEHOLDER.search(url_match.group(0)):
            errors.append(
                "02_system_blueprint.md: product URL is still a placeholder; deploy first, then paste the real link"
            )
        elif not url_match and deploy_pending:
            warnings.append(
                "02_system_blueprint.md: deploy pending - product ships locally; paste the Space URL at P7 to go live"
            )
        elif not url_match:
            errors.append("02_system_blueprint.md: no public URL for the deployed product")
        if not EVIDENCE["first_value"].search(blueprint):
            errors.append("02_system_blueprint.md: no first-value-under-60s path stated")
        if not EVIDENCE["fallback"].search(blueprint):
            errors.append("02_system_blueprint.md: no free-tier quota or fallback stated")
        if not EVIDENCE["users"].search(blueprint):
            errors.append("02_system_blueprint.md: no external-user target with a number")

        metric_block = re.search(r"##\s*9\.\s*Metrics.*?(?=\n## |\Z)", blueprint, re.S)
        if metric_block:
            blob = metric_block.group(0).lower()
            if not any(k in blob for k in ("time to first value", "completion rate", "external users", "retention")):
                errors.append("02_system_blueprint.md: section 9 has no product metric")
        else:
            errors.append("02_system_blueprint.md: section 9 missing")

        if prompts and "P6" not in prompts and "P7" not in prompts:
            warnings.append("05_agent_prompts.md: no UI/deploy milestone (P6+)")
        if not prompts:
            warnings.append("05_agent_prompts.md: absent, cannot check product milestones")
        if not readme:
            warnings.append("README.md: absent, cannot check pitch/screenshot/how-it-works")

    for w in warnings:
        print(f"[!] WARN {w}")
    for e in errors:
        print(f"[X] ERROR {e}")
    print(f"[=] {len(errors)} error(s), {len(warnings)} warning(s) | mode={intent['mode']} | {folder.name}")
    return 1 if errors else 0


def cmd_audiences(args):
    if not INTENT.is_file():
        print(f"[X] ERROR intent file missing: {INTENT}")
        return 2
    intent = parse_intent(read_text(INTENT))
    print(f"mode: {intent['mode']} | surface: {intent['surface']} | hosting: {intent['hosting']}")
    print("rank | audience | does today")
    for a in intent["audiences"]:
        print(f"{a['rank']} | {a['name']} | {a['today']}")
    if intent["refusals"]:
        print("refusals:")
        for r in intent["refusals"]:
            print(f"- {r}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Score portfolio ideas against product intent")
    sub = parser.add_subparsers(dest="command")

    pick = sub.add_parser("pick", help="Rank mechanisms by shippability")
    pick.add_argument("--mechanisms", required=True, help="Comma-separated mechanism ids")
    pick.add_argument("--audience", default=None, help="One audience; omit to try every named audience")
    pick.add_argument("--hours", type=int, default=34)
    pick.add_argument("--pack", default=None)
    pick.add_argument("--json", action="store_true")

    check = sub.add_parser("check", help="Verify a blueprint against product mode")
    check.add_argument("folder")

    sub.add_parser("audiences", help="List named audiences and refusals")

    argv = sys.argv[1:]
    if argv and not argv[0].startswith("-") and argv[0] not in {"pick", "check", "audiences"}:
        argv.insert(0, "check")

    args = parser.parse_args(argv)
    if args.command == "pick":
        return cmd_pick(args)
    if args.command == "check":
        return cmd_check(args)
    if args.command == "audiences":
        return cmd_audiences(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
