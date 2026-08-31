from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_sore_loser_descriptor_context_finding import EXCLUSION, TERM_ID, harden
from scripts.resolve_context_guard_findings import resolve
from scripts.translation_review_common import load_locked_terms, locked_term_matches


def _seed(root: Path) -> None:
    glossary = root / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "term_registry.json").write_text(
        json.dumps({
            "terms": [{
                "id": TERM_ID,
                "locked": True,
                "zh_cn": ["不服输"],
                "target_vi": "Không chịu thua",
            }]
        }, ensure_ascii=False),
        encoding="utf-8",
    )
    (glossary / "ui_community_terms.json").write_text(
        json.dumps({"terms": []}, ensure_ascii=False),
        encoding="utf-8",
    )
    (glossary / "canonical_findings.json").write_text(
        json.dumps({
            "schema_version": 1,
            "findings": [{
                "finding_id": "cf-857f68c97ee8efed",
                "status": "open",
                "source_zh_cn": EXCLUSION,
                "kinds": ["context_rule"],
                "canonical_resolution": None,
                "evidence": [{
                    "source_path": "text_data_dict.json",
                    "json_path": ["144", "1009"],
                    "source_text": "唯我独尊！\\n不服输的傲娇少女",
                    "current_text": "Duy ngã độc tôn!\\nCô gái tsundere hiếu thắng",
                }],
            }],
        }, ensure_ascii=False),
        encoding="utf-8",
    )


def test_descriptor_is_excluded_but_skill_flavored_phrase_still_matches_and_finding_resolves(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    terms = load_locked_terms(tmp_path)
    descriptor = locked_term_matches(
        "唯我独尊！\\n不服输的傲娇少女",
        "Duy ngã độc tôn!\\nCô gái tsundere hiếu thắng",
        terms,
        source_path="text_data_dict.json",
        json_path=["144", "1009"],
    )
    assert not any(match["id"] == TERM_ID for match in descriptor)

    skill_flavored = locked_term_matches(
        "超×9不服输！\\n最强挑战者",
        "Siêu×9 không chịu thua!\\nKẻ thách thức mạnh nhất",
        terms,
        source_path="text_data_dict.json",
        json_path=["144", "1129"],
    )
    assert any(match["id"] == TERM_ID for match in skill_flavored)

    assert resolve(tmp_path) is True
    payload = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    assert payload["findings"][0]["canonical_resolution"] == {
        "layer": "context_guard",
        "term_id": TERM_ID,
        "target_vi": "Không chịu thua",
    }
