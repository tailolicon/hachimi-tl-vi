from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_character_training_ui_canon import harden


def test_hardener_persists_trainee_exclusions_in_player_facing_sync_source(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    scripts = tmp_path / "scripts"
    glossary.mkdir(parents=True)
    scripts.mkdir(parents=True)
    (glossary / "term_registry.json").write_text(
        json.dumps({"schema_version": 1, "terms": []}, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    sync_source = scripts / "enforce_player_facing_canon.py"
    sync_source.write_text(
        'BRAND_EXCLUSIONS = [\n'
        '    "ウマ娘 プリティーダービー",\n'
        '    "赛马娘Pretty Derby",\n'
        ']\n',
        encoding="utf-8",
    )

    harden(tmp_path)
    first = sync_source.read_text(encoding="utf-8")
    assert '    "育成赛马娘",\n' in first
    assert '    "育成\\n赛马娘",\n' in first

    harden(tmp_path)
    second = sync_source.read_text(encoding="utf-8")
    assert second == first
