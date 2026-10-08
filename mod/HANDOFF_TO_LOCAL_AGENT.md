# HANDOFF TO LOCAL AGENT (Claude Code / Codex)

> You are reading this because Melty is driving the build from your Windows PC and asked you to paste its instructions into a local AI coding agent. **This file is the mod spec**. Everything you need is below. Keep Melty's "Copy instructions" output above this in your paste — those are your publish credentials; these are your build spec.

---

## What you're building

A TF2 mod that reskins a 4v4 KOTH bot match on `koth_harvest_final` into a Plants-vs-Zombies brawl using the player's own GW2 audio.

- Primary (Melty catalog): **TF2**
- Secondary (player install): **PvZ Garden Warfare 2** — audio & strings only, read live, never redistributed.

## Current state (what the Emergent agent produced for you)

All of this is already in the repo under `mod/`:

| Path | Status |
|---|---|
| `mod/characters.json` · `mod/sounds.json` · `mod/sounds.full.json` · `mod/maps.json` · `mod/hooks.json` · `mod/melty.recipe.json` | **Done** — the full design spec |
| `mod/pvz_gw2_kit/resource/tf_english.txt` · `scoreboard.res` · `classselection.res` | **Done** — HUD overrides |
| `mod/pvz_gw2_kit/scripts/game_sounds_vo.txt` | **Done** — new sound events |
| `mod/pvz_gw2_kit/scripts/vscripts/pvz_gw2_welcome.nut` · `pvz_gw2_cornertag.nut` · `pvz_vo_gate.nut` | **Done** — in-game VScript |
| `mod/pvz_gw2_kit/cfg/autoexec.cfg` · `cfg/mods/pvz_gw2_kit.cfg` | **Done** — bot & match cvars |
| `mod/bin/pvz_gw2_first_run/*.py` + `build.ps1` | **Done** — Python locator + extractor skeleton |
| `mod/build/pack_vpk.ps1` | **Done** — Windows VPK packer |
| `mod/tools/expand_sounds.py` | **Done** — generated `sounds.full.json` (140 rules) |

## What you need to do (3 steps)

### 1. Build the helper + pack the VPK

```powershell
cd mod\bin\pvz_gw2_first_run
.\build.ps1
# -> produces pvz_gw2_kit\bin\pvz_gw2_first_run.exe

cd ..\..\build
.\pack_vpk.ps1
# -> produces mod\dist\pvz_gw2_kit.vpk
```

### 2. Install locally and verify TF2 boots the match

```powershell
# Steam path auto-detected by pack_vpk.ps1; or do it manually:
Copy-Item -Force "mod\dist\pvz_gw2_kit.vpk" `
  "$env:ProgramFiles(x86)\Steam\steamapps\common\Team Fortress 2\tf\custom\pvz_gw2_kit.vpk"

# Also copy the helper so first-run can execute
New-Item -ItemType Directory -Force "$env:ProgramFiles(x86)\Steam\steamapps\common\Team Fortress 2\tf\custom\pvz_gw2_kit\bin"
Copy-Item "mod\pvz_gw2_kit\bin\pvz_gw2_first_run.exe" `
  "$env:ProgramFiles(x86)\Steam\steamapps\common\Team Fortress 2\tf\custom\pvz_gw2_kit\bin\"
```

Launch TF2. Expected:
- Loads straight into `koth_harvest_final`
- Scoreboard says "Plants" / "Zombies"
- Class pick strip tooltips say Peashooter / Chomper / etc.
- 7 bots are on the field, forced to the right classes
- One HUD line: `PvZ GW2 x TF2 v0.1 - GW2 install not found...` (if no GW2) or `Loaded N GW2 sounds...` (if GW2 extraction ran)

### 3. (Optional, risky) Enable full GW2 audio

The brief flags this as the project's legal risk. The helper **does not bundle** a Frostbite decoder — ship v1 strings-only unless you've obtained a license-clean `frostbite_dump.exe` to drop beside `main.py`. See `mod/bin/pvz_gw2_first_run/README.md` for candidate tools and licensing notes.

### 4. Publish to Melty

Use the Melty "Copy instructions" credentials to call `create_mod` with:
- Recipe: `mod/melty.recipe.json`
- VPK payload: `mod/dist/pvz_gw2_kit.vpk`
- Helper: `mod/pvz_gw2_kit/bin/pvz_gw2_first_run.exe`

Melty will run `inspect_package` → `validate_recipe` → `one_click_check`. All three should pass. If `one_click_check` complains about the unsigned .exe, code-sign on this machine or document the whitelist exception.

Take a real screenshot in-game (not faked — if extraction fell back, show fallback mode and say so in the description). Publish.

## Open decisions you (local agent) can make on behalf of the user

- **Strings-only vs full audio for v1**: default to strings-only. Zero legal exposure, mod still ships "GW2 really in it" via names + metadata. Upgrade to full in v1.1 if user supplies the extractor.
- **tf_bot_difficulty**: start at 2 (Hard). Tune after one playtest.
- **koth_harvest_final vs koth_viaduct fallback**: harvest_final ships with every TF2 install since 2012, use it.

## What to come back and ask the user

Only these (per the original brief):
1. **Publish handle** — needed for `melty.recipe.json#author_handle` when you call `create_mod`.
2. **If and only if the user wants full audio**: whether they'll obtain a Frostbite extractor themselves. Default to no.

That's it. Everything else is in the sheets. Build it.
