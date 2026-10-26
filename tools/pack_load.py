#!/usr/bin/env python3
"""Load and validate a role pack.

A pack carries the domain rules that differ per job family: which metric families
are legitimate, which idea shapes are banned, which mechanisms are native to the
domain, and whether ArXiv is a useful reference source. One codebase, one pack per
candidate, so the tool is not silently an AI-only tool.

Usage:
  python3 tools/pack_load.py --list
  python3 tools/pack_load.py --name llm
  python3 tools/pack_load.py --for-role "AI Engineer"
  python3 tools/pack_load.py --name llm --json

Exit codes:
  0 = pack found and valid
  1 = pack malformed, or no pack matched the role
  2 = packs directory missing
"""
import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PACK_DIR = Path(".claude/packs")

REQUIRED_KEYS = (
    "name",
    "label",
    "domain",
    "summary",
    "target_roles",
    "metric_families",
    "forbidden_ideas",
    "arxiv",
    "default_mechanisms",
    "demo_rule",
    "product_shape",
    "product_metric_families",
)

PRODUCT_KEYS = ("product_shape", "product_metric_families")


def load_yaml(path: Path) -> dict:
    try:
        import yaml
    except ImportError:
        print("[!] PyYAML is not installed. Run: pip install pyyaml")
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[X] ERROR {path.name}: {e}")
        return {}
    return data if isinstance(data, dict) else {}


def validate(pack: dict, path: Path) -> list[str]:
    errors = []
    for key in REQUIRED_KEYS:
        if key not in pack:
            errors.append(f"{path.name}: missing key '{key}'")
    if pack.get("name") and pack["name"] != path.stem:
        errors.append(f"{path.name}: name '{pack['name']}' does not match file name")
    for key in ("target_roles", "metric_families", "forbidden_ideas", "default_mechanisms", "product_metric_families"):
        value = pack.get(key)
        if value is not None and not isinstance(value, list):
            errors.append(f"{path.name}: '{key}' must be a list")
    if "arxiv" in pack and not isinstance(pack["arxiv"], bool):
        errors.append(f"{path.name}: 'arxiv' must be true or false")
    return errors


def all_packs(pack_dir: Path = PACK_DIR) -> tuple[list[dict], list[str]]:
    if not pack_dir.is_dir():
        return [], [f"packs directory not found: {pack_dir}"]
    packs, errors = [], []
    for path in sorted(pack_dir.glob("*.yaml")):
        pack = load_yaml(path)
        if not pack:
            errors.append(f"{path.name}: unreadable or empty")
            continue
        errors.extend(validate(pack, path))
        packs.append(pack)
    if not packs and not errors:
        errors.append("no *.yaml packs found")
    return packs, errors


def match_role(packs: list[dict], role: str) -> dict | None:
    role_l = role.lower().strip()
    if not role_l:
        return None
    best, best_len = None, 0
    for pack in packs:
        for target in pack.get("target_roles", []):
            target_l = target.lower()
            if target_l in role_l or role_l in target_l:
                if len(target_l) > best_len:
                    best, best_len = pack, len(target_l)
    return best


def print_pack(pack: dict) -> None:
    print(f"name: {pack['name']}")
    print(f"label: {pack['label']}")
    print(f"domain: {pack['domain']}")
    print(f"arxiv: {'yes' if pack['arxiv'] else 'no'}")
    print(f"summary: {pack['summary']}")
    print(f"metric_families: {', '.join(pack['metric_families'])}")
    print(f"default_mechanisms: {', '.join(pack['default_mechanisms'])}")
    print(f"forbidden_ideas: {', '.join(pack['forbidden_ideas'])}")
    print(f"demo_rule: {pack['demo_rule']}")
    print(f"product_shape: {pack['product_shape']}")
    print(f"product_metric_families: {', '.join(pack['product_metric_families'])}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Load a role pack")
    parser.add_argument("--name", help="Pack name, e.g. llm")
    parser.add_argument("--for-role", help="Match a pack to a target role string")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--dir", default=str(PACK_DIR))
    args = parser.parse_args()

    pack_dir = Path(args.dir)

    packs, errors = all_packs(pack_dir)
    if errors and not packs:
        for e in errors:
            print(f"[X] ERROR {e}")
        return 2
    for e in errors:
        print(f"[!] WARN {e}")

    if args.list:
        print("name | label | domain | arxiv | mechanisms")
        for pack in packs:
            print(
                f"{pack['name']} | {pack['label']} | {pack['domain']} | "
                f"{'yes' if pack['arxiv'] else 'no'} | {len(pack['default_mechanisms'])}"
            )
        print(f"[=] {len(packs)} pack(s)")
        return 0

    pack = None
    if args.name:
        pack = next((p for p in packs if p["name"] == args.name), None)
        if not pack:
            print(f"[X] ERROR no pack named '{args.name}'")
            print(f"[i] available: {', '.join(p['name'] for p in packs)}")
            return 1
    elif args.for_role:
        pack = match_role(packs, args.for_role)
        if not pack:
            print(f"[!] no pack matched role '{args.for_role}'")
            print(f"[i] available: {', '.join(p['name'] for p in packs)}")
            print("[i] pass --name to choose one explicitly")
            return 1
    else:
        parser.print_help()
        return 1

    if args.json:
        print(json.dumps(pack, indent=2, ensure_ascii=False))
    else:
        print_pack(pack)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
