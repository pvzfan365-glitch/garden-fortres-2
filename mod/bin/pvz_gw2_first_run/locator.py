"""GW2 install locator.

Strategy order (first hit wins):
    1. --gw2-path CLI arg (explicit user override)
    2. EA Desktop IS manifests
         %LOCALAPPDATA%\\Electronic Arts\\EA Desktop\\InstallManager\\IS\\*.json
         (post-2022 format; the "installInfo" node holds installPath)
    3. Origin legacy registry
         HKLM\\SOFTWARE\\WOW6432Node\\Origin Games\\Plants vs Zombies Garden Warfare 2
         value "InstallDir"
    4. Steam libraryfolders.vdf
         %ProgramFiles(x86)%\\Steam\\steamapps\\libraryfolders.vdf
         (rare but exists)
    5. Known default paths

A match must contain pvzgw2.exe (or PVZGW2.exe) at the root for us to accept it.
"""
from __future__ import annotations

import glob
import json
import logging
import os
import re
from pathlib import Path
from typing import Iterable

log = logging.getLogger(__name__)

_EXE_NAMES = ("pvzgw2.exe", "PVZGW2.exe", "PvZGW2.exe")


class GW2Locator:
    def __init__(self, explicit_path: Path | None = None):
        self.explicit_path = explicit_path

    def find(self) -> Path | None:
        for name, fn in (
            ("explicit",         self._from_explicit),
            ("ea_desktop",       self._from_ea_desktop),
            ("origin_registry",  self._from_origin_registry),
            ("steam",            self._from_steam),
            ("defaults",         self._from_defaults),
        ):
            try:
                p = fn()
            except Exception as e:
                log.debug("locator strategy %s failed: %s", name, e)
                continue
            if p and self._valid_install(p):
                log.info("locator strategy %s hit: %s", name, p)
                return p
        return None

    # ----- strategies -----

    def _from_explicit(self) -> Path | None:
        return self.explicit_path

    def _from_ea_desktop(self) -> Path | None:
        local = os.environ.get("LOCALAPPDATA")
        if not local:
            return None
        pattern = str(Path(local) / "Electronic Arts" / "EA Desktop" / "InstallManager" / "IS" / "*.json")
        for jf in glob.glob(pattern):
            try:
                with open(jf, encoding="utf-8") as f:
                    data = json.load(f)
            except (OSError, json.JSONDecodeError):
                continue
            # Format drift tolerance: try several shapes
            candidates: list[str] = []
            info = data.get("installInfo") or data.get("InstallInfo") or {}
            if isinstance(info, dict):
                for key in ("installPath", "InstallPath", "installLocation", "InstallLocation"):
                    v = info.get(key)
                    if isinstance(v, str):
                        candidates.append(v)
            # Also look at the top level
            for key in ("installPath", "InstallPath", "baseInstallPath"):
                v = data.get(key)
                if isinstance(v, str):
                    candidates.append(v)
            # Match by title id or display name
            title = (data.get("displayName") or data.get("DisplayName") or "").lower()
            if "garden warfare 2" not in title and "pvzgw2" not in title:
                # Some IS files are gameless shells; still consider them if
                # their path contains the game folder
                candidates = [c for c in candidates if "garden warfare 2" in c.lower()]
            for c in candidates:
                p = Path(c)
                if self._valid_install(p):
                    return p
        return None

    def _from_origin_registry(self) -> Path | None:
        if os.name != "nt":
            return None
        try:
            import winreg  # type: ignore
        except ImportError:
            return None
        for hive, path in (
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Origin Games\Plants vs Zombies Garden Warfare 2"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Origin Games\Plants vs Zombies Garden Warfare 2"),
            (winreg.HKEY_CURRENT_USER,  r"SOFTWARE\Origin Games\Plants vs Zombies Garden Warfare 2"),
        ):
            try:
                with winreg.OpenKey(hive, path) as k:
                    v, _ = winreg.QueryValueEx(k, "InstallDir")
                    p = Path(v)
                    if self._valid_install(p):
                        return p
            except OSError:
                continue
        return None

    def _from_steam(self) -> Path | None:
        pf86 = os.environ.get("ProgramFiles(x86)")
        if not pf86:
            return None
        vdf_path = Path(pf86) / "Steam" / "steamapps" / "libraryfolders.vdf"
        if not vdf_path.exists():
            return None
        try:
            text = vdf_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return None
        # minimal VDF parse: grab every "path" value
        for match in re.finditer(r'"path"\s+"([^"]+)"', text):
            lib = Path(match.group(1).replace("\\\\", "\\"))
            candidate = lib / "steamapps" / "common" / "Plants vs. Zombies Garden Warfare 2"
            if self._valid_install(candidate):
                return candidate
        return None

    def _from_defaults(self) -> Path | None:
        defaults: Iterable[str] = (
            r"C:\Program Files\EA Games\Plants vs. Zombies Garden Warfare 2",
            r"C:\Program Files (x86)\EA Games\Plants vs. Zombies Garden Warfare 2",
            r"C:\Program Files (x86)\Origin Games\Plants vs. Zombies Garden Warfare 2",
            r"D:\Program Files\EA Games\Plants vs. Zombies Garden Warfare 2",
            r"D:\Program Files (x86)\EA Games\Plants vs. Zombies Garden Warfare 2",
        )
        for d in defaults:
            p = Path(d)
            if self._valid_install(p):
                return p
        return None

    # ----- validation -----

    @staticmethod
    def _valid_install(p: Path) -> bool:
        if not p or not p.exists() or not p.is_dir():
            return False
        for exe in _EXE_NAMES:
            if (p / exe).exists():
                return True
        return False
