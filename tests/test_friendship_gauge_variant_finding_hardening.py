from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_friendship_gauge_variant_finding import (
    COMMUNITY_TERM_ID,
    FINDING_ID,
    LOCKED_TERM_ID,
    SOURCE_ALIAS,
    harden,
)
from scripts.resolve_context_guard_findings import resolve
from scripts.translation_review_common import community_term_matches, load_community_terms


def _write(root: Path) -> None:
    glossary = root / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "term_registry.json").write_text(
        json.dumps({
            "terms": [{
                "id": LOCKED_TERM_ID,
                "zh_cn": ["羁绊值"],
                "target_vi": "Friendship Gauge",
                "locked": True,
                "source_paths": ["text_data_dict.json"],
                "json_path_prefixes": [["155"]],
                "match_mode": "contains",
                "invalidation_scope": "item",
            }]
        }, ensure_ascii=False),
        encoding="utf-8",
    )
    (glossary / "ui_community_terms.json").write_text(
        json.dumps({
            "terms": [{
                "id": COMMUNITY_TERM_ID,
                "source_aliases": ["羁绊值"],
                "preferred": "Friendship Gauge",
                "accepted": ["Friendship Gauge"],
                "compact": [],
                "forbidden": ["Gắn kết", "giá trị liên kết"],
                "require_accepted": True,
                "source_paths": ["text_data_dict.json"],
                "json_path_prefixes": [["155"]],
                "match_mode": "contains",
                "invalidation_scope": "item",
            }]
        }, ensure_ascii=False),
        encoding="utf-8",
    )
    (glossary / "canonical_findings.json").write_text(
        json.dumps({
            "schema_version": 1,
            "findings": [{
                "finding_id": FINDING_ID,
                "status": "open",
                "source_zh_cn": SOURCE_ALIAS,
                "suggested_targets_vi": ["Friendship Gauge"],
                "canonical_resolution": None,
                "evidence": [
                    {
                        "source_path": "text_data_dict.json",
                        "json_path": ["155", "30037"],
                        "source_text": "牵绊值达到80以上时，\\n速度加成",
                        "current_text": "Khi giá trị liên kết đạt từ 80 trở lên,\\nSpeed Bonus",
                    },
                    {
                        "source_path": "text_data_dict.json",
                        "json_path": ["155", "30082"],
                        "source_text": "牵绊值达到100以上时，\\n智力加成",
                        "current_text": "Khi điểm liên kết đạt 100 trở lên,\\nWit Bonus",
                    },
                ],
            }],
        }, ensure_ascii=False),
        encoding="utf-8",
    )


def test_variant_is_scoped_and_resolves_only_while_all_evidence_is_covered(tmp_path: Path) -> None:
    _write(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    terms = load_community_terms(tmp_path)
    matches = community_term_matches(
        None,
        "牵绊值达到100以上时，\\n友情加成",
        "Khi điểm liên kết đạt 100 trở lên,\\nFriendship Bonus",
        terms,
        source_path="text_data_dict.json",
        json_path=["155", "30183"],
    )
    gauge = next(match for match in matches if match["id"] == COMMUNITY_TERM_ID)
    assert gauge["accepted_present"] is False
    assert gauge["forbidden_present"] is True

    outside = community_term_matches(
        None,
        "牵绊值达到100以上时",
        "Friendship Gauge đạt ít nhất 100",
        terms,
        source_path="text_data_dict.json",
        json_path=["163", "999"],
    )
    assert not any(match["id"] == COMMUNITY_TERM_ID for match in outside)

    assert resolve(tmp_path) is True
    payload = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    finding = payload["findings"][0]
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": COMMUNITY_TERM_ID,
        "target_vi": "Friendship Gauge",
    }

    # Canonical refresh clears derived resolution before each production pass.
    # If later evidence escapes category 155, the positive evidence guard must
    # not close the source-path-wide finding again.
    finding["canonical_resolution"] = None
    finding["evidence"].append({
        "source_path": "text_data_dict.json",
        "json_path": ["163", "999"],
        "source_text": "牵绊值达到100以上时",
        "current_text": "Friendship Gauge đạt ít nhất 100",
    })
    (tmp_path / "glossary" / "canonical_findings.json").write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8"
    )
    assert resolve(tmp_path) is False
    reopened = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    assert reopened["findings"][0]["canonical_resolution"] is None
