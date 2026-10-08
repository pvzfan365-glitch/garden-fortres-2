# PRD — PvZ GW2 × TF2: Garden Warfare: Mercenary Edition

**Type:** TF2 game mod (Melty mashup) — not a web app.
**Primary:** TF2 (host). **Secondary:** PvZ GW2 (audio/strings from player's install, never redistributed).

## User persona
Solo TF2 player who owns GW2 and wants a quick PvZ-flavored 4v4 KOTH bot match. No friends, no servers, no setup beyond pressing Play in Melty.

## Core requirements
- 8 character kits: 4 BLU Plants (Peashooter/Chomper/Sunflower/Cactus) + 4 RED Zombies (Imp/Scientist/All-Star/Foot Soldier)
- GW2 content loaded at runtime: VO, weapon sounds, taunt music, HUD names
- Solo KOTH on `koth_harvest_final`: 1 human + 3 BLU bots vs 4 RED bots
- Graceful fallback to stock TF2 audio if GW2 install not found
- Visible HUD attribution line on first run

## What's been implemented (2026-01)

**Phase 1 — Preflight sheets (DONE):**
- `/app/mod/characters.json`, `sounds.json`, `maps.json`, `hooks.json`, `melty.recipe.json`

**Phase 2 — Static VPK sources (DONE, awaiting Windows pack):**
- `/app/mod/pvz_gw2_kit/resource/tf_english.txt` — HUD name overrides
- `/app/mod/pvz_gw2_kit/resource/ui/scoreboard.res` — "Plants" / "Zombies" labels
- `/app/mod/pvz_gw2_kit/resource/ui/classselection.res` — PvZ tooltip blurbs
- `/app/mod/pvz_gw2_kit/scripts/game_sounds_vo.txt` — new sound events
- `/app/mod/pvz_gw2_kit/scripts/vscripts/pvz_gw2_welcome.nut` — HUD welcome
- `/app/mod/pvz_gw2_kit/scripts/vscripts/pvz_gw2_cornertag.nut` — persistent tag
- `/app/mod/pvz_gw2_kit/scripts/vscripts/pvz_vo_gate.nut` — Scout BLU/RED VO gating
- `/app/mod/pvz_gw2_kit/cfg/autoexec.cfg` + `cfg/mods/pvz_gw2_kit.cfg` — bot & match cvars

**Phase 3 — GW2 locator + extractor (DONE, strings-only by default):**
- `/app/mod/bin/pvz_gw2_first_run/{main,locator,extractor,mapper,manifest}.py`
- Locator: EA Desktop IS → Origin registry → Steam libraryfolders → defaults → user prompt
- Extractor: license-gated — shells out to user-supplied `frostbite_dump.exe`, else falls back cleanly
- Verified end-to-end: fallback mode writes manifest + VScript stub, exits 0

**Phase 4 — Full audio pass template (DONE):**
- `/app/mod/tools/expand_sounds.py` → generated `/app/mod/sounds.full.json` with 140 rules across all 8 kits × 6-9 categories each

**Phase 5 — Melty package + publish (awaiting local Claude Code):**
- `/app/mod/build/pack_vpk.ps1` — Windows VPK packer (uses TF2's vpk.exe)
- `/app/mod/bin/pvz_gw2_first_run/build.ps1` — PyInstaller build
- `/app/mod/melty.recipe.json` — updated with concrete payload paths + risks
- `/app/mod/HANDOFF_TO_LOCAL_AGENT.md` — paste-ready brief for Claude Code

## Testing
- iteration_2.json: 14/15 tests passed, 1 HIGH bug (SoundMapper stem construction)
- iteration_3.json: **15/15 tests passed** after fix; HIGH bug resolved
- `/app/backend/tests/test_pvz_gw2_mod.py` is the reusable regression suite

## Open blockers before Melty publish
- Must run `pack_vpk.ps1` + `build.ps1` on a Windows machine with TF2 installed — can't run from Linux pod
- Publish handle still TBD (ask user at `create_mod` time)
- Frostbite extractor decision: strings-only (default, zero legal risk) vs user supplies `frostbite_dump.exe`
- `tf_bot_difficulty` awaits one playtest confirmation

## Backlog (post-v1)
- v1.1: full audio once `frostbite_dump.exe` route is settled
- v1.2: more TF2 maps beyond koth_harvest (koth_viaduct, koth_lakeside)
- v1.3: swap TF2's Demoman/Spy for PvZ Z7-Imp and Rose if balance holds

## Files not touched (Melty rule, never changes)
Models, materials, animations, weapon stats, achievements, cosmetics — all stock TF2.
