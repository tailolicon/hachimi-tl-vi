import json
from pathlib import Path

from scripts.build_translation_review_plan import _prior_is_resolved
from scripts.merge_translation_review import _bridge_auto_defer_reasons
from scripts.translation_review_common import (
    load_source_bridge_config,
    semantic_guard_flags,
    source_bridge_policy_hash,
    source_bridge_risk_matches,
    source_bridge_term_matches,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _bridge_rules():
    config = load_source_bridge_config(REPO_ROOT)
    return config["terms"], config["untrusted_sources"]


def test_monies_rejects_literal_coin_translation() -> None:
    terms, _ = _bridge_rules()
    matches = source_bridge_term_matches("金币不足", "Không đủ xu", terms)
    assert len(matches) == 1
    assert matches[0]["id"] == "currency.monies"
    assert matches[0]["accepted_present"] is False
    assert matches[0]["forbidden_present"] is True


def test_monies_accepts_player_facing_term() -> None:
    terms, _ = _bridge_rules()
    matches = source_bridge_term_matches("素材和金币不足", "Không đủ nguyên liệu và Monies", terms)
    assert len(matches) == 1
    assert matches[0]["accepted_present"] is True
    assert matches[0]["forbidden_present"] is False


def test_cleat_rejects_horse_world_calque() -> None:
    terms, _ = _bridge_rules()
    matches = source_bridge_term_matches(
        "通过转换支援卡\n获得了以下的蹄铁",
        "Khi chuyển đổi Thẻ Hỗ trợ\nđã nhận được các Móng ngựa sau",
        terms,
    )
    assert len(matches) == 1
    assert matches[0]["id"] == "resource.cleat"
    assert matches[0]["accepted_present"] is False
    assert matches[0]["forbidden_present"] is True


def test_cleat_accepts_player_facing_term() -> None:
    terms, _ = _bridge_rules()
    matches = source_bridge_term_matches(
        "通过转换支援卡\n获得了以下的蹄铁",
        "Khi chuyển đổi Thẻ Hỗ trợ\nđã nhận được các Cleats sau",
        terms,
    )
    assert len(matches) == 1
    assert matches[0]["accepted_present"] is True


def test_known_lossy_zhcn_title_is_untrusted() -> None:
    _, risks = _bridge_rules()
    nail = source_bridge_risk_matches("凹凸马蹄", risks)
    front = source_bridge_risk_matches("前行", risks)
    unrelated = source_bridge_risk_matches("继续前行", risks)
    assert nail and nail[0]["mode"] == "defer_until_canonical"
    assert front and front[0]["mode"] == "defer_until_canonical"
    assert unrelated == []


def test_merge_auto_defers_literal_bridge_keep() -> None:
    terms, risks = _bridge_rules()
    item = {"source_text": "金币不足"}
    reasons, matched_terms, matched_risks = _bridge_auto_defer_reasons(
        item,
        "Không đủ xu",
        "keep",
        "high",
        terms,
        risks,
    )
    assert "source_bridge_forbidden_calque" in reasons
    assert "source_bridge_term_mismatch" in reasons
    assert matched_terms
    assert matched_risks == []


def test_merge_auto_defers_non_high_confidence_keep() -> None:
    terms, risks = _bridge_rules()
    reasons, _, _ = _bridge_auto_defer_reasons(
        {"source_text": "普通文本"},
        "Văn bản bình thường",
        "keep",
        "medium",
        terms,
        risks,
    )
    assert reasons == ["non_high_confidence_keep"]


def test_merge_auto_defers_known_lossy_source_even_if_translation_looks_fluent() -> None:
    terms, risks = _bridge_rules()
    reasons, _, matched_risks = _bridge_auto_defer_reasons(
        {"source_text": "前行"},
        "Tiến lên",
        "keep",
        "high",
        terms,
        risks,
    )
    assert "source_bridge_untrusted_source" in reasons
    assert matched_risks


def test_old_bridge_sensitive_review_is_reopened_selectively() -> None:
    bridge_hash = source_bridge_policy_hash(REPO_ROOT)
    prior = {
        "policy_version": 3,
        "context_snapshot_sha256": "ctx",
        "source_fingerprint": "source",
        "current_fingerprint": "target",
        "action": "keep",
        "confidence": "high",
    }
    assert not _prior_is_resolved(
        prior,
        context_hash="ctx",
        source_fp="source",
        current_fp="target",
        bridge_sensitive=True,
        bridge_hash=bridge_hash,
    )
    assert _prior_is_resolved(
        prior,
        context_hash="ctx",
        source_fp="source",
        current_fp="target",
        bridge_sensitive=False,
        bridge_hash=bridge_hash,
    )


def test_source_bridge_hash_ignores_generated_summary_and_evidence_churn(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "source_bridge_terms.json").write_text(
        json.dumps({"terms": [], "untrusted_sources": []}, ensure_ascii=False),
        encoding="utf-8",
    )
    generated_path = glossary / "source_bridge_risks.generated.json"
    generated = {
        "summary": {"scanned_decisions": 100},
        "untrusted_sources": [
            {
                "id": "curation.bridge.test",
                "zh_cn_exact": ["一线曙光"],
                "mode": "defer_until_canonical",
                "evidence": [{"note": "first evidence"}],
            }
        ],
    }
    generated_path.write_text(json.dumps(generated, ensure_ascii=False), encoding="utf-8")
    first = source_bridge_policy_hash(tmp_path)

    generated["summary"]["scanned_decisions"] = 999
    generated["untrusted_sources"][0]["evidence"] = [{"note": "new duplicate evidence"}]
    generated_path.write_text(json.dumps(generated, ensure_ascii=False), encoding="utf-8")
    second = source_bridge_policy_hash(tmp_path)
    assert second == first

    generated["untrusted_sources"].append(
        {
            "id": "curation.bridge.new",
            "zh_cn_exact": ["一跃而上"],
            "mode": "defer_until_canonical",
        }
    )
    generated_path.write_text(json.dumps(generated, ensure_ascii=False), encoding="utf-8")
    third = source_bridge_policy_hash(tmp_path)
    assert third != first


def test_semantic_guards_flag_numbers_and_direction() -> None:
    flags = semantic_guard_flags("最多60个，不能超过", "Tối đa 50, có thể tăng")
    assert "numeric_token_mismatch" in flags
    assert "negation_capability_risk" in flags
    assert "exceeds_risk" in flags
