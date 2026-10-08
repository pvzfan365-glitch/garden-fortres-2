"""Frostbite audio extractor — license-gated wrapper.

The brief flagged this as the whole-project legal risk. This module does NOT
include a Frostbite decoder itself. Instead it looks for a user-supplied
`frostbite_dump.exe` next to it and shells out to that, treating its output
as a flat `.wav` directory the mapper then renames into TF2's sound namespace.

If frostbite_dump.exe is missing, raises ExtractionDisabled so main.py can
fall back cleanly to strings-only mode. No bundled binary → no redistribution
question → ships safe.

Replace the stub binary with whatever license-clean tool you (the local
agent / user) decide on. Candidates documented in extractor_README.md.
"""
from __future__ import annotations

import logging
import os
import shutil
import subprocess
from pathlib import Path

log = logging.getLogger(__name__)


class ExtractionDisabled(RuntimeError):
    """Raised when the Frostbite extractor binary is missing or opted-out."""


class FrostbiteExtractor:
    #: logical subpaths under GW2 install that the extractor should walk
    DATA_SUBPATHS = ("Data", "Patch")

    def __init__(self, gw2_root: Path, cache_dir: Path):
        self.gw2_root = gw2_root
        self.cache_dir = cache_dir
        self.binary = Path(__file__).resolve().parent / "frostbite_dump.exe"

    def run(self) -> int:
        if not self.binary.exists():
            raise ExtractionDisabled(
                f"missing {self.binary.name} - ship a license-clean Frostbite "
                "dumper beside this helper or run with extraction disabled"
            )
        if not shutil.which(str(self.binary)) and not os.access(self.binary, os.X_OK):
            raise ExtractionDisabled(f"{self.binary} is not executable")

        data_dirs = [self.gw2_root / sub for sub in self.DATA_SUBPATHS
                     if (self.gw2_root / sub).exists()]
        if not data_dirs:
            raise ExtractionDisabled(
                f"no Data/Patch folders under {self.gw2_root} - unexpected install layout"
            )

        out_dir = self.cache_dir / "raw"
        out_dir.mkdir(parents=True, exist_ok=True)

        total = 0
        for d in data_dirs:
            try:
                proc = subprocess.run(
                    [str(self.binary),
                     "--input", str(d),
                     "--output", str(out_dir),
                     "--filter", "audio",
                     "--format", "wav"],
                    capture_output=True, text=True, timeout=600, check=False,
                )
            except (OSError, subprocess.TimeoutExpired) as e:
                log.warning("frostbite_dump failed on %s: %s", d, e)
                continue
            if proc.returncode != 0:
                log.warning("frostbite_dump exit=%d stderr=%s",
                            proc.returncode, proc.stderr[:400])
                continue
            total += _count_wavs(out_dir)

        return total


def _count_wavs(root: Path) -> int:
    return sum(1 for _ in root.rglob("*.wav"))
