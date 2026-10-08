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
- `/app/mod/characters.json` — 8 kits with team/class/sound-map/HUD-name/weapon-slot-map
- `/app/mod/sounds.json` — 25 sound rules (16 P0 required to boot v1), per-slot fallbacks
- `/app/mod/maps.json` — koth_harvest config, 11 cvars, 7 bot slots with class-forcing plan
- `/app/mod/hooks.json` — 10 TF2 touch-points, all reversible, Melty compliance declared
- `/app/mod/melty.recipe.json` — draft manifest with 5 phases + 4 risks logged
- Cross-sheet consistency checks pass (team split 4/4, bot math 7+1, every kit covered)

## Open blockers before Phase 2
- Real Frostbite bundle paths unknown — placeholders in `characters.json` and `sounds.json` must be reconciled after one successful extraction pass (Phase 3 output)
- `tf_bot_difficulty` needs playtest confirmation
- Frostbite extractor license-clean redistribution route — brief flagged this as the whole-project risk; strings-only fallback v1 documented

## Prioritized backlog
**P0 (next session):**
- Phase 2: Static VPK structure — write `tf_english.txt` strings, `scoreboard.res`, `classselection.res`, `autoexec.cfg`, pack with vpk.exe. Playable without GW2.

**P1:**
- Phase 3: GW2 locator (EA Desktop IS manifest → Origin registry → Steam → user prompt) + Frostbite extractor skeleton (gated on license decision)
- VScript `pvz_vo_gate.nut` for BLU-Scout vs RED-Scout team gating

**P2:**
- Phase 4: Full audio pass — remaining P1/P2 sound rules, taunt music, round-start stingers
- Phase 5: Melty `inspect_package` → `validate_recipe` → `one_click_check` → publish

## What I'll ask the user later
- Publish handle (at `create_mod` time)
- Yes/no on Frostbite extractor redistribution choice if Phase 3 needs it

## Files not touched (Melty rule)
Models, materials, animations, weapon stats, achievements, cosmetics — all stock TF2.
