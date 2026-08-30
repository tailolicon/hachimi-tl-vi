import json

from scripts.canonical_findings import refresh_canonical_resolutions


def test_skill_name_canonical_example_resolves_matching_finding(tmp_path):
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "term_registry.json").write_text('{"terms": []}', encoding="utf-8")
    (glossary / "ui_community_terms.json").write_text('{"terms": []}', encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text('{"terms": []}', encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({
        "decisions": [{
            "decision_id": "test.corner-adept",
            "source_zh_cn": "弯道巧者○",
            "action": "lock",
            "target_vi": "Thành thạo khúc cua○"
        }]
    }, ensure_ascii=False), encoding="utf-8")
    (glossary / "skill_name_style.json").write_text(json.dumps({
        "canonical_examples": [{
            "source_zh_cn": "弯道巧者○",
            "target_vi": "Thành thạo khúc cua○"
        }]
    }, ensure_ascii=False), encoding="utf-8")
    ledger = {
        "findings": [{
            "finding_id": "cf-test",
            "status": "open",
            "source_zh_cn": "弯道巧者○",
            "match_mode": "exact",
            "source_paths": ["text_data_dict.json"],
            "key_exact": [],
            "json_path_prefixes": [["147"]],
            "suggested_targets_vi": [],
            "review_resolution": None,
            "canonical_resolution": None
        }]
    }

    refreshed = refresh_canonical_resolutions(tmp_path, ledger)

    resolution = refreshed["findings"][0]["canonical_resolution"]
    assert resolution is not None
    assert resolution["layer"] == "skill_name"
    assert resolution["target_vi"] == "Thành thạo khúc cua○"
