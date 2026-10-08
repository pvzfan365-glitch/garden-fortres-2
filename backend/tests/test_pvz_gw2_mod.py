"""Backend tests for PvZ GW2 x TF2 mod helper + preflight JSON sheets.

Covers:
- first_run main.py CLI flows (fallback / --once / vscript stub / extraction disabled)
- expand_sounds.py generator output
- JSON preflight sheets structural integrity
- SoundMapper._resolve_source() path matching
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

APP = Path("/app")
MOD = APP / "mod"
HELPER_DIR = MOD / "bin" / "pvz_gw2_first_run"
MAIN_PY = HELPER_DIR / "main.py"
EXPAND_PY = MOD / "tools" / "expand_sounds.py"

# ---------- utils ----------

def run_main(args: list[str], cwd: Path = APP) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(MAIN_PY), *args],
        capture_output=True, text=True, cwd=str(cwd), timeout=60,
    )


# ---------- first_run main.py ----------

class TestFirstRunMain:
    def test_fallback_manifest_when_no_gw2(self, tmp_path):
        mod_root = tmp_path / "pvz_test1"
        res = run_main(["--mod-root", str(mod_root), "--once"])
        assert res.returncode == 0, f"stderr={res.stderr}"
        manifest_path = mod_root / "sound" / "cache" / "manifest.json"
        assert manifest_path.exists()
        data = json.loads(manifest_path.read_text())
        assert data["mode"] == "fallback_stock_tf2_audio"
        assert data["extraction_mode"] == "fallback"
        assert data["extracted_sound_count"] == 0

    def test_once_short_circuits_on_second_run(self, tmp_path):
        mod_root = tmp_path / "pvz_test2"
        r1 = run_main(["--mod-root", str(mod_root), "--once"])
        assert r1.returncode == 0
        manifest_path = mod_root / "sound" / "cache" / "manifest.json"
        mtime1 = manifest_path.stat().st_mtime_ns
        r2 = run_main(["--mod-root", str(mod_root), "--once"])
        assert r2.returncode == 0
        mtime2 = manifest_path.stat().st_mtime_ns
        assert mtime1 == mtime2, "manifest should NOT be rewritten on --once rerun"
        assert "already present" in (r2.stderr + r2.stdout).lower() or mtime1 == mtime2

    def test_writes_vscript_stub_no_once(self, tmp_path):
        mod_root = tmp_path / "pvz_test3"
        res = run_main(["--mod-root", str(mod_root)])
        assert res.returncode == 0, f"stderr={res.stderr}"
        stub = mod_root / "scripts" / "vscripts" / "pvz_gw2_manifest.nut"
        assert stub.exists()
        content = stub.read_text()
        assert "::MANIFEST_COUNT <- 0;" in content

    def test_extraction_disabled_when_binary_missing(self, tmp_path):
        mod_root = tmp_path / "pvz_test4"
        fake_gw2 = tmp_path / "fake_gw2"
        fake_gw2.mkdir()
        (fake_gw2 / "pvzgw2.exe").write_bytes(b"\x00")
        # Also need a Data subpath to pass locator validation only (locator just
        # checks the exe), but extractor will fail on Data folder OR binary first.
        res = run_main([
            "--enable-extraction",
            "--mod-root", str(mod_root),
            "--gw2-path", str(fake_gw2),
        ])
        assert res.returncode == 0, f"stderr={res.stderr}"
        manifest_path = mod_root / "sound" / "cache" / "manifest.json"
        assert manifest_path.exists()
        data = json.loads(manifest_path.read_text())
        # Expect disabled_license because frostbite_dump.exe is missing
        assert data["extraction_mode"] in ("disabled_license", "disabled", "crashed")
        assert data["extracted_sound_count"] == 0


# ---------- expand_sounds.py ----------

class TestExpandSounds:
    def test_produces_full_sheet(self):
        # Run from /app so default paths mod/characters.json etc. resolve
        res = subprocess.run(
            [sys.executable, str(EXPAND_PY)],
            capture_output=True, text=True, cwd=str(APP), timeout=60,
        )
        assert res.returncode == 0, f"stderr={res.stderr}"
        out = MOD / "sounds.full.json"
        assert out.exists()
        data = json.loads(out.read_text())
        rules = data.get("rules", [])
        assert len(rules) >= 100, f"only {len(rules)} rules"
        # all 8 kits present
        chars = json.loads((MOD / "characters.json").read_text())
        kit_names = {k["gw2_character"] for k in chars["kits"]}
        rule_kits = {r.get("kit") for r in rules if r.get("kit")}
        missing = kit_names - rule_kits
        assert not missing, f"kits missing from rules: {missing}"


# ---------- JSON preflight sheets ----------

class TestPreflightSheets:
    @pytest.mark.parametrize("name", [
        "characters.json", "sounds.json", "sounds.full.json",
        "maps.json", "hooks.json", "melty.recipe.json",
    ])
    def test_valid_json(self, name):
        path = MOD / name
        assert path.exists(), f"{name} missing"
        data = json.loads(path.read_text())
        assert data is not None

    def test_characters_8_kits_split(self):
        chars = json.loads((MOD / "characters.json").read_text())
        kits = chars.get("kits", [])
        assert len(kits) == 8, f"expected 8 kits, got {len(kits)}"
        blu = [k for k in kits if k.get("team") == "BLU"]
        red = [k for k in kits if k.get("team") == "RED"]
        assert len(blu) == 4, f"BLU count {len(blu)}"
        assert len(red) == 4, f"RED count {len(red)}"

    def test_melty_recipe_has_5_phases(self):
        recipe = json.loads((MOD / "melty.recipe.json").read_text())
        phases = recipe.get("phases", [])
        assert len(phases) == 5, f"expected 5 phases, got {len(phases)}"

    def test_hooks_10_touchpoints_with_reversible(self):
        hooks = json.loads((MOD / "hooks.json").read_text())
        tps = hooks.get("touch_points", [])
        assert len(tps) == 10, f"expected 10 touch_points, got {len(tps)}"
        for tp in tps:
            assert "reversible" in tp, f"touch_point missing reversible: {tp}"


# ---------- SoundMapper._resolve_source ----------

class TestSoundMapperResolve:
    def test_resolve_source_matches_flat_raw_dir(self, tmp_path):
        sys.path.insert(0, str(HELPER_DIR))
        try:
            from mapper import SoundMapper  # type: ignore
        finally:
            pass
        cache_dir = tmp_path / "sound" / "cache"
        raw = cache_dir / "raw" / "plants" / "peashooter" / "vo" / "battlecry"
        raw.mkdir(parents=True)
        wav = raw / "pea_01.wav"
        wav.write_bytes(b"RIFF")

        mapper = SoundMapper(
            MOD / "sounds.json", MOD / "characters.json", cache_dir
        )
        resolved = mapper._resolve_source(
            "pvz_gw2/characters/plants/peashooter/vo/battlecry/*.sb"
        )
        assert resolved is not None, "expected to resolve to pea_01.wav"
        assert resolved.name == "pea_01.wav"
