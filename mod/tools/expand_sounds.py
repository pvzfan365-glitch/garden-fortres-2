"""Phase 4 — expand sounds.json template into a full per-slot sheet.

Takes the 25 structural rules authored in Phase 1 and generates the remaining
~400 rows mechanically by iterating every TF2 VO category × every kit. The
output is written back to a new file so the hand-authored sheet isn't lost.

Run:
    python3 tools/expand_sounds.py --in mod/sounds.json --out mod/sounds.full.json

Idempotent. Safe to re-run.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


# TF2 VO slot filename patterns per category. {cls} = tf2 class, {n} = index.
CATEGORY_SLOTS = {
    "battlecry":   ["sound/vo/{cls}_battlecry{n:02d}.wav",      range(1, 4)],
    "pain":        ["sound/vo/{cls}_painseverehot{n:02d}.wav",  range(1, 5)],
    "death":       ["sound/vo/{cls}_painsharp{n:02d}.wav",      range(1, 4)],
    "taunt":       ["sound/vo/{cls}_taunts{n:02d}.wav",         range(1, 3)],
    "medic_call":  ["sound/vo/{cls}_medic{n:02d}.wav",          range(1, 3)],
    "thanks":      ["sound/vo/{cls}_thanks{n:02d}.wav",         range(1, 3)],
    "class_select":["sound/vo/{cls}_specialcompleted{n:02d}.wav", range(1, 3)],
}

# Categories that only apply to specific classes
CLASS_CATEGORY_FILTER = {
    "scout":    {"battlecry", "pain", "death", "taunt", "medic_call", "class_select"},
    "pyro":     {"battlecry", "pain", "death", "taunt", "medic_call", "class_select"},
    "medic":    {"battlecry", "pain", "death", "taunt", "medic_call", "thanks", "class_select"},
    "sniper":   {"battlecry", "pain", "death", "taunt", "medic_call", "class_select"},
    "engineer": {"battlecry", "pain", "death", "taunt", "medic_call", "class_select"},
    "heavy":    {"battlecry", "pain", "death", "taunt", "medic_call", "class_select"},
    "soldier":  {"battlecry", "pain", "death", "taunt", "medic_call", "class_select"},
}


def expand(sheet: dict) -> dict:
    # pull kit list from the companion characters.json next door
    chars_path = Path("mod/characters.json")
    chars = json.loads(chars_path.read_text(encoding="utf-8"))
    existing_ids = {r["rule_id"] for r in sheet["rules"]}
    existing_slots = {r["tf2_slot"] for r in sheet["rules"]}

    next_id = max(int(r["rule_id"].split("-")[1]) for r in sheet["rules"]
                  if r["rule_id"].startswith("VO-")) + 1

    for kit in chars["kits"]:
        tf2_class = kit["tf2_class"]
        team      = kit["team"]
        kit_name  = kit["gw2_character"]
        cats = CLASS_CATEGORY_FILTER.get(tf2_class, set())
        for cat, (pattern, idx_range) in CATEGORY_SLOTS.items():
            if cat not in cats:
                continue
            for n in idx_range:
                stock_slot = pattern.format(cls=tf2_class, n=n)
                new_slot   = stock_slot.replace(f"{tf2_class}_", f"{kit_name}_")
                if new_slot in existing_slots:
                    continue
                rule = {
                    "rule_id": f"VO-{next_id:03d}",
                    "class":   tf2_class,
                    "team":    team,
                    "kit":     kit_name,
                    "category": cat,
                    "tf2_slot": new_slot,
                    "replaces_tf2": stock_slot,
                    "gw2_source": f"pvz_gw2/characters/{_team_folder(team)}/{kit_name}/vo/{cat}/*.sb",
                    "fallback":  "stock",
                    "priority":  "P2",
                    "source":    "auto_expanded",
                }
                sheet["rules"].append(rule)
                existing_slots.add(new_slot)
                next_id += 1

    sheet["coverage_targets"]["total_rules_authored"] = len(sheet["rules"])
    sheet["coverage_targets"]["P2_rules_authored"] = sum(
        1 for r in sheet["rules"] if r.get("priority") == "P2"
    )
    sheet["schema_version"] = "0.2-expanded"
    return sheet


def _team_folder(team: str) -> str:
    return "plants" if team == "BLU" else "zombies"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in",  dest="src", type=Path, default=Path("mod/sounds.json"))
    ap.add_argument("--out", dest="dst", type=Path, default=Path("mod/sounds.full.json"))
    args = ap.parse_args()

    sheet = json.loads(args.src.read_text(encoding="utf-8"))
    out = expand(sheet)
    args.dst.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"wrote {args.dst} - {len(out['rules'])} rules total")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
