"""pvz_gw2_first_run — entry point.

Runs once on first launch (and manually if the user wants to retry).

Steps:
    1. Locate GW2 install via EA Desktop → Origin → Steam → user prompt
    2. If audio extraction is enabled & license-cleared: extract Frostbite audio
       into tf/custom/pvz_gw2_kit/sound/cache/ and map to TF2 sound slots
    3. Fallback mode: scan GW2 metadata/strings only, write a cache manifest
       so the mod boots with PvZ names + stock TF2 audio
    4. Write cache/manifest.json and scripts/vscripts/pvz_gw2_manifest.nut
       so the in-game VScript can show "Loaded N GW2 sounds" (or the fallback
       notice) on first spawn.

Design rules:
    - Idempotent: safe to re-run. Overwrites manifest, re-extracts missing files.
    - Pure stdlib + a small list of optional deps (see requirements.txt).
    - Exits 0 on success, 0 on soft-fail (fallback mode active), 2 on hard-fail
      (couldn't write cache folder at all).
    - No network calls. Never uploads anything.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from locator import GW2Locator
from extractor import FrostbiteExtractor, ExtractionDisabled
from mapper import SoundMapper
from manifest import write_manifest, write_vscript_stub

log = logging.getLogger("pvz_gw2_first_run")


def resolve_mod_root() -> Path:
    """Mod root is the folder containing this helper's parent (bin/..)."""
    here = Path(__file__).resolve().parent        # .../pvz_gw2_kit/bin/pvz_gw2_first_run/
    return here.parent.parent                     # .../pvz_gw2_kit/


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PvZ GW2 x TF2 - first-run helper")
    parser.add_argument("--mod-root", type=Path, default=None,
                        help="Override mod root (default: autodetect from this script's location).")
    parser.add_argument("--gw2-path", type=Path, default=None,
                        help="Skip auto-detect and point directly at a GW2 install folder.")
    parser.add_argument("--enable-extraction", action="store_true",
                        help="Enable Frostbite audio extraction. Requires a license-clean "
                             "extractor binary at bin/frostbite_dump.exe. See README.")
    parser.add_argument("--quiet", action="store_true", help="Only log warnings and errors.")
    parser.add_argument("--once", action="store_true",
                        help="Exit 0 immediately if cache/manifest.json already exists.")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.WARNING if args.quiet else logging.INFO,
        format="[%(levelname)s] %(message)s",
    )

    mod_root = args.mod_root or resolve_mod_root()
    cache_dir = mod_root / "sound" / "cache"
    manifest_path = cache_dir / "manifest.json"

    if args.once and manifest_path.exists():
        log.info("manifest already present, --once given, exiting")
        return 0

    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        log.error("cannot create cache dir %s: %s", cache_dir, e)
        return 2

    # --- Step 1: locate GW2 ---
    gw2 = GW2Locator(explicit_path=args.gw2_path).find()
    if gw2 is None:
        log.warning("GW2 install not found. Writing fallback manifest so the mod still boots.")
        return _write_fallback(mod_root, manifest_path, reason="not_found")

    log.info("GW2 install found at: %s", gw2)

    # --- Step 2: extraction (gated) ---
    extracted_count = 0
    extraction_mode = "disabled"
    if args.enable_extraction:
        try:
            extractor = FrostbiteExtractor(gw2_root=gw2, cache_dir=cache_dir)
            extracted_count = extractor.run()
            extraction_mode = "frostbite_dump"
        except ExtractionDisabled as e:
            log.warning("extraction disabled: %s", e)
            extraction_mode = "disabled_license"
        except Exception as e:  # pragma: no cover - defensive
            log.error("extractor crashed: %s", e)
            extraction_mode = "crashed"

    # --- Step 3: sound mapping (always runs; handles the strings-only case too) ---
    sounds_json = mod_root.parent / "sounds.json"
    chars_json  = mod_root.parent / "characters.json"
    if sounds_json.exists() and chars_json.exists():
        mapper = SoundMapper(sounds_json, chars_json, cache_dir)
        mapped_count = mapper.rebuild_game_sounds()
        log.info("mapped %d sound rules", mapped_count)
    else:
        log.warning("sounds.json/characters.json not next to mod root — skipping mapping")

    # --- Step 4: manifest ---
    write_manifest(manifest_path, {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "gw2_install_path": str(gw2),
        "extraction_mode": extraction_mode,
        "extracted_sound_count": extracted_count,
        "mode": "full" if extracted_count > 0 else "strings_only",
    })
    write_vscript_stub(mod_root / "scripts" / "vscripts" / "pvz_gw2_manifest.nut",
                       extracted_count)
    log.info("wrote manifest: %s (mode=%s, sounds=%d)",
             manifest_path, "full" if extracted_count > 0 else "strings_only", extracted_count)
    return 0


def _write_fallback(mod_root: Path, manifest_path: Path, reason: str) -> int:
    write_manifest(manifest_path, {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "gw2_install_path": None,
        "extraction_mode": "fallback",
        "extracted_sound_count": 0,
        "mode": "fallback_stock_tf2_audio",
        "reason": reason,
    })
    write_vscript_stub(mod_root / "scripts" / "vscripts" / "pvz_gw2_manifest.nut", 0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
