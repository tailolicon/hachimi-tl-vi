from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_narrative_stat_context_finding import harden
from scripts.resolve_context_guard_findings import resolve


CASES = (
    ("cf-cde74f30fa07e6a6", "获得相应的力量", "common.stat.power", "Power"),
    ("cf-2a3675dd079cad04", "坚定不移的力量", "common.stat.power", "Power"),
    ("cf-03be28442492e3b1", "力量感", "common.stat.power", "Power"),
    ("cf-daad507f1b0d4acc", "融会贯通的速度", "common.stat.speed", "Speed"),
    ("cf-9d903a48b310ef86", "提高跳过速度", "common.stat.speed", "Speed"),
    ("cf-b1060c0332f450d8", "成长速度", "common.stat.speed", "Speed"),
    ("cf-1daec5ebd9895c48", "充满毅力", "common.stat.guts", "Guts"),
)


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(
        json.dumps({
            "schema_version": 1,
            "terms": [
                {
                    "id": "common.stat.power",
                    "source_aliases": ["力量"],
                    "preferred": "Power",
                    "accepted": ["Power"],
                    "forbidden": ["Sức mạnh"],
                    "require_accepted": True,
                },
                {
                    "id": "common.stat.speed",
                    "source_aliases": ["速度"],
                    "preferred": "Speed",
                    "accepted": ["Speed"],
                    "forbidden": ["Tốc độ"],
                    "require_accepted": True,
                },
                {
                    "id": "common.stat.guts",
                    "source_aliases": ["毅力"],
                    "preferred": "Guts",
                    "accepted": ["Guts"],
                    "forbidden": ["Nghị lực"],
                    "require_accepted": True,
                },
            ],
        }, ensure_ascii=False),
        encoding="utf-8",
    )
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "canonical_findings.json").write_text(
        json.dumps({
            "schema_version": 1,
            "findings": [
                {
                    "finding_id": finding_id,
                    "status": "open",
                    "source_zh_cn": phrase,
                    "match_mode": "contains",
                    "source_paths": ["text_data_dict.json"],
                    "key_exact": [],
                    "json_path_prefixes": [],
                    "canonical_resolution": None,
                    "review_resolution": None,
                    "evidence": [{
                        "source_path": "text_data_dict.json",
                        "json_path": ["143", "1"],
                        "source_text": phrase,
                        "current_text": phrase,
                    }],
                }
                for finding_id, phrase, _, _ in CASES
            ],
        }, ensure_ascii=False),
        encoding="utf-8",
    )


def test_narrative_stat_exclusions_resolve_context_findings(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    assert resolve(tmp_path) is True
    assert resolve(tmp_path) is False
    payload = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    by_id = {item["finding_id"]: item for item in payload["findings"]}
    for finding_id, _, term_id, target in CASES:
        assert by_id[finding_id]["canonical_resolution"] == {
            "layer": "context_guard",
            "term_id": term_id,
            "target_vi": target,
        }
