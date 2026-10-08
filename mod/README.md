# Garden Warfare: Mercenary Edition — Full Mod

TF2 mod that reskins a 4v4 KOTH bot match into Plants-vs-Zombies, with GW2 audio streamed from the player's own install.

**Status: Phases 1–4 complete. Phase 5 (VPK pack + Melty publish) runs on your Windows PC via Claude Code — see [`HANDOFF_TO_LOCAL_AGENT.md`](./HANDOFF_TO_LOCAL_AGENT.md).**

## Folder layout

```
mod/
├── characters.json          # 8 kits × class/team/sound-map/HUD-name
├── sounds.json              # 25 structural rules (hand-authored)
├── sounds.full.json         # 140 rules (expanded from above)
├── maps.json                # koth_harvest config + bot cvars
├── hooks.json               # Every place the mod touches TF2 (10 hooks)
├── melty.recipe.json        # Melty manifest, 5 phases, 4 risks
├── HANDOFF_TO_LOCAL_AGENT.md  # Paste-ready brief for Claude Code
├── README.md                # This file
│
├── pvz_gw2_kit/             # VPK source tree
│   ├── resource/
│   │   ├── tf_english.txt       # HUD class name overrides
│   │   └── ui/
│   │       ├── scoreboard.res
│   │       └── classselection.res
│   ├── scripts/
│   │   ├── game_sounds_vo.txt   # New sound events (Peashooter.BattleCry etc.)
│   │   └── vscripts/
│   │       ├── pvz_gw2_welcome.nut
│   │       ├── pvz_gw2_cornertag.nut
│   │       └── pvz_vo_gate.nut
│   ├── cfg/
│   │   ├── autoexec.cfg
│   │   └── mods/pvz_gw2_kit.cfg
│   ├── sound/cache/         # Populated by first-run helper
│   └── bin/                 # pvz_gw2_first_run.exe lands here after build
│
├── bin/pvz_gw2_first_run/   # Python locator + Frostbite extractor skeleton
│   ├── main.py
│   ├── locator.py           # EA Desktop → Origin → Steam → defaults
│   ├── extractor.py         # Shells out to user-supplied frostbite_dump.exe
│   ├── mapper.py            # Maps extracted .wav → TF2 sound slots
│   ├── manifest.py
│   ├── build.ps1            # PyInstaller build on Windows
│   ├── requirements.txt
│   └── README.md
│
├── tools/
│   └── expand_sounds.py     # Generates sounds.full.json from sounds.json
│
└── build/
    └── pack_vpk.ps1         # Windows VPK packer (uses TF2's vpk.exe)
```

## Phase status

| Phase | Deliverable | Status |
|---|---|---|
| 1 | Preflight sheets | ✅ done |
| 2 | Static VPK sources | ✅ sources done, pack on Windows |
| 3 | GW2 locator + extractor | ✅ code done, strings-only by default |
| 4 | Full audio pass | ✅ 140-rule template generated |
| 5 | Melty package + publish | ⏳ on local Claude Code |

## How to actually run it

See `HANDOFF_TO_LOCAL_AGENT.md`. Three commands on a Windows machine with TF2 installed:

```powershell
cd mod\bin\pvz_gw2_first_run; .\build.ps1
cd ..\..\build;                .\pack_vpk.ps1
# then copy mod\dist\pvz_gw2_kit.vpk into tf\custom\
```

## Design rules that never got broken

- No TF2 models, materials, animations, or weapon stats touched (Melty rule).
- GW2 audio never bundled with the mod — read live from the player's install.
- Graceful fallback to stock TF2 audio if GW2 isn't found; mod still boots and shows PvZ names.
- Every touch point is reversible by deleting one file.
