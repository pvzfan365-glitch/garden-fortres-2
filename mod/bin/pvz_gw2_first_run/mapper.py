"""Map extracted raw .wav files → TF2 sound namespace.

Reads sounds.json (the Phase 1 preflight sheet) and copies/renames each
extracted file so it lives at the exact tf2_slot path the game expects.

If a rule's source wav is missing, the slot is left empty — Source will
fall back to the stock event (TF2 engine behaviour, confirmed in brief).
"""
from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path

log = logging.getLogger(__name__)


class SoundMapper:
    def __init__(self, sounds_json: Path, chars_json: Path, cache_dir: Path):
        self.sounds = json.loads(Path(sounds_json).read_text(encoding="utf-8"))
        self.chars  = json.loads(Path(chars_json).read_text(encoding="utf-8"))
        self.cache_dir = Path(cache_dir)
        self.raw_dir   = self.cache_dir / "raw"

    def rebuild_game_sounds(self) -> int:
        """Walk every sound rule, place the matching wav into the right slot.

        Returns the count of rules successfully mapped.
        """
        mapped = 0
        for rule in self.sounds.get("rules", []):
            tf2_slot_rel = rule.get("tf2_slot")
            source_hint  = rule.get("gw2_source")
            if not tf2_slot_rel or not source_hint:
                continue
            # tf2_slot comes in as e.g. "sound/vo/peashooter_battlecry01.wav".
            # We write under cache_dir but TF2 only reads from sound/, so strip
            # the leading "sound/" and anchor at cache_dir's parent.
            if tf2_slot_rel.startswith("sound/"):
                dest = self.cache_dir.parent / tf2_slot_rel
            else:
                dest = self.cache_dir / tf2_slot_rel

            src = self._resolve_source(source_hint)
            if src is None:
                log.debug("rule %s: source %s not extracted, skipping",
                          rule.get("rule_id"), source_hint)
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(src, dest)
                mapped += 1
            except OSError as e:
                log.warning("rule %s: copy failed: %s", rule.get("rule_id"), e)
        return mapped

    def _resolve_source(self, source_hint: str) -> Path | None:
        """Turn a logical gw2_source hint into an actual extracted wav path.

        gw2_source values look like
            'pvz_gw2/characters/plants/peashooter/vo/battlecry/*.sb'
        and the extractor writes files flat under cache/raw/ keyed on their
        bundle path. We match by substring of the stem.
        """
        if not self.raw_dir.exists():
            return None
        # Strip the leading top-level token (pvz_gw2/...) and any glob
        stem = source_hint.replace("pvz_gw2/", "").replace("*.sb", "").strip("/")
        # pick first file whose relative path contains the stem
        for wav in self.raw_dir.rglob("*.wav"):
            rel = str(wav.relative_to(self.raw_dir)).replace("\\", "/").lower()
            if stem.lower() in rel:
                return wav
        return None
