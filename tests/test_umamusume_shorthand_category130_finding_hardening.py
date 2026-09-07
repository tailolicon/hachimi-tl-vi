from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_umamusume_shorthand_category130_finding import TERM, TERM_ID, harden


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_category130_umamusume_shorthand_is_scoped_and_idempotent(tmp_path: Path) -> None:
    _write(tmp_path / "glossary" / "ui_community_terms.json", {"schema_version": 1, "terms": []})

    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    term = next(item for item in community["terms"] if item["id"] == TERM_ID)
    assert term["source_aliases"] == ["马娘"]
    assert term["preferred"] == "Mã Nương"
    assert term["accepted"] == ["Mã Nương"]
    assert term["source_paths"] == ["text_data_dict.json"]
    assert term["json_path_prefixes"] == [["130"]]
    assert term["match_mode"] == "contains"
    assert term["invalidation_scope"] == "item"


def test_category130_umamusume_shorthand_does_not_globalize_short_alias() -> None:
    assert TERM["json_path_prefixes"] == [["130"]]
    assert ["144"] not in TERM["json_path_prefixes"]
    assert TERM["source_paths"] == ["text_data_dict.json"]
    assert TERM["source_aliases"] == ["马娘"]
    assert TERM["match_mode"] == "contains"
