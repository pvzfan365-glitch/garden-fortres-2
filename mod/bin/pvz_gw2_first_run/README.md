# pvz_gw2_first_run — notes for the local agent

Does three things on first launch:

1. Finds the player's GW2 install (EA Desktop → Origin registry → Steam → defaults).
2. Optionally extracts Frostbite audio by shelling out to `frostbite_dump.exe`
   placed beside this script — **not bundled, license-gated**.
3. Writes a manifest + a one-liner VScript stub the in-game HUD reads.

## Running it (dev)

```powershell
# strings-only mode (no extraction, always safe to ship)
python main.py

# with extraction enabled - requires frostbite_dump.exe next to main.py
python main.py --enable-extraction

# force a path
python main.py --gw2-path "D:\Games\Plants vs. Zombies Garden Warfare 2"

# skip if already run
python main.py --once --quiet
```

## Building the .exe

```powershell
.\build.ps1
```

Drops `pvz_gw2_first_run.exe` into `../../pvz_gw2_kit/bin/` ready to be VPK'd.

## The Frostbite extractor question (brief risk R-001)

This helper deliberately does **not** ship a Frostbite decoder. It shells out
to a `frostbite_dump.exe` that the user (or local build agent) must provide.
Candidates to evaluate for license-clean redistribution:

| Tool                | Redistributable? | Notes |
|---------------------|------------------|-------|
| Frosty Toolsuite CLI | **No** (closed-source, EULA restricts) | Rules out bundling. User can install it themselves. |
| DICE DUMP (hacky)    | Unclear          | Smaller, no official license statement. Avoid redistributing. |
| ChickenScratch (OSS) | **Yes** (MIT)    | WIP, incomplete GW2 bundle support — would need patches. |
| Strings-only (ours)  | **Yes**          | No extraction. HUD names + fallback audio. v1-safe. |

Recommendation if the local agent asks: ship **strings-only** as v1 (no .exe
needed), then let the user drop in `frostbite_dump.exe` themselves to unlock
full audio in v1.1.

## What this helper never does

- Download anything from the internet
- Modify files inside the GW2 install
- Upload or report any paths/data
- Run without the user triggering it (manifest-gated: `--once` + Melty `pre_launch`)
