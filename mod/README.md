# Garden Warfare: Mercenary Edition — Phase 1 Preflight Sheets

TF2 mod that reskins a 4v4 KOTH bot match into a Plants-vs-Zombies brawl, with GW2 audio streamed from the player's own install.

This folder is **Phase 1 only** — the design sheets. No code yet, per the brief: "No code until every cell is filled."

## Files

| File | Purpose | Rows / Entries |
|---|---|---|
| `characters.json` | 8 character kits — class × team × GW2 identity × sound-map × HUD name | 8 kits |
| `sounds.json` | GW2 source path → TF2 sound slot rules (VO, weapons, music) | 24 rules authored (16 P0 required for v1 boot) |
| `maps.json` | koth_harvest config, bot cvars, autoexec sequence | 1 map + 11 cvars + 7 bot slots |
| `hooks.json` | Every place the mod touches TF2 — surface area for Melty's `inspect_package` | 10 hooks |
| `melty.recipe.json` | Draft Melty manifest: primary=tf2, secondary=pvz_gw2, phases, risks | — |

## Open cells (blockers before Phase 2)

Each sheet declares its own `open_cells` section at the bottom. Highlights:

- **`characters.json#weapon_slot_map.*.gw2_fire`** — Real Frostbite bundle paths unknown until one successful extraction pass. Current values are placeholders the extractor must resolve 1:1.
- **`sounds.json#gw2_source`** — Same root cause.
- **`maps.json#bot_config.cvars.tf_bot_difficulty`** — Needs playtest.
- **`hooks.json#H-007.risks[Frostbite]`** — License-clean extraction route TBD. Fallback: strings-only v1.

## What's deliberately NOT in Phase 1

- No VPK packing yet (Phase 2).
- No Python extractor code (Phase 3).
- No models, materials, animations, or weapon-stat edits — ever (Melty rule: primary keeps its body).

## Next

Phase 2 — Static VPK (HUD names + scoreboard + bot cfg + autoexec), playable without GW2, verified in TF2.
