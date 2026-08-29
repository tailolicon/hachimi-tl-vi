from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_resources_gacha_shop_canon import harden
from scripts.translation_review_common import source_bridge_term_matches


def _write_bridge(root: Path) -> None:
    path = root / "glossary" / "source_bridge_terms.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "terms": [
                    {
                        "id": "currency.monies",
                        "ja": ["マニー"],
                        "zh_cn": ["金币"],
                        "preferred": "Monies",
                        "accepted": ["Monies"],
                        "forbidden": ["xu", "tiền vàng", "đồng vàng"],
                        "require_accepted": True,
                    },
                    {
                        "id": "resource.cleat",
                        "ja": ["蹄鉄"],
                        "zh_cn": ["蹄铁"],
                        "preferred": "Cleat",
                        "accepted": ["Cleat", "Cleats"],
                        "forbidden": ["móng ngựa"],
                        "require_accepted": True,
                    },
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _terms(root: Path) -> list[dict]:
    return json.loads((root / "glossary" / "source_bridge_terms.json").read_text(encoding="utf-8"))["terms"]


def test_hardener_scopes_resource_bridges_to_localize_ui(tmp_path: Path) -> None:
    _write_bridge(tmp_path)
    harden(tmp_path)
    terms = {item["id"]: item for item in _terms(tmp_path)}

    assert terms["currency.monies"]["source_paths"] == ["localize_dict.json"]
    assert terms["resource.cleat"]["source_paths"] == ["localize_dict.json"]
    assert terms["currency.jewel.paid"]["source_paths"] == ["localize_dict.json"]
    assert terms["currency.jewel.free"]["source_paths"] == ["localize_dict.json"]
    assert terms["gacha.exchange_points"]["source_paths"] == ["localize_dict.json"]
    assert terms["gacha.exchange_points"]["key_prefixes"] == ["Gacha"]


def test_monies_matches_shop_ui_but_not_story_prose(tmp_path: Path) -> None:
    _write_bridge(tmp_path)
    harden(tmp_path)
    terms = _terms(tmp_path)

    ui = source_bridge_term_matches(
        "兑换所需的金币不足",
        "Không đủ Monies để đổi",
        terms,
        key="Shop137006",
        source_path="localize_dict.json",
        json_path=["Shop137006"],
    )
    story = source_bridge_term_matches(
        "桌上堆着闪闪发亮的金币。",
        "Trên bàn chất đầy những đồng tiền vàng lấp lánh.",
        terms,
        key=None,
        source_path="text_data_dict.json",
        json_path=["181", "999"],
    )

    assert [item["id"] for item in ui] == ["currency.monies"]
    assert ui[0]["accepted_present"] is True
    assert story == []


def test_cleat_matches_ui_but_not_hoof_prose(tmp_path: Path) -> None:
    _write_bridge(tmp_path)
    harden(tmp_path)
    terms = _terms(tmp_path)

    ui = source_bridge_term_matches(
        "用蹄铁兑换道具",
        "Đổi vật phẩm bằng Cleats",
        terms,
        key="Shop999001",
        source_path="localize_dict.json",
        json_path=["Shop999001"],
    )
    story = source_bridge_term_matches(
        "旧蹄铁上沾满了泥。",
        "Chiếc móng ngựa cũ dính đầy bùn.",
        terms,
        key=None,
        source_path="text_data_dict.json",
        json_path=["181", "1000"],
    )

    assert [item["id"] for item in ui] == ["resource.cleat"]
    assert ui[0]["accepted_present"] is True
    assert story == []


def test_paid_and_free_jewel_labels_are_distinct_and_ui_scoped(tmp_path: Path) -> None:
    _write_bridge(tmp_path)
    harden(tmp_path)
    terms = _terms(tmp_path)

    paid = source_bridge_term_matches(
        "付费宝石详情",
        "Chi tiết Jewel trả phí",
        terms,
        key="Shop626028",
        source_path="localize_dict.json",
        json_path=["Shop626028"],
    )
    free = source_bridge_term_matches(
        "免费宝石详情",
        "Chi tiết Jewel miễn phí",
        terms,
        key="Shop626029",
        source_path="localize_dict.json",
        json_path=["Shop626029"],
    )
    prose = source_bridge_term_matches(
        "这是免费获得的宝石般的礼物。",
        "Đây là món quà giống đá quý nhận miễn phí.",
        terms,
        key=None,
        source_path="text_data_dict.json",
        json_path=["181", "1001"],
    )

    assert [item["id"] for item in paid] == ["currency.jewel.paid"]
    assert paid[0]["accepted_present"] is True
    assert [item["id"] for item in free] == ["currency.jewel.free"]
    assert free[0]["accepted_present"] is True
    assert prose == []


def test_exchange_points_match_gacha_pity_but_not_generic_exchange(tmp_path: Path) -> None:
    _write_bridge(tmp_path)
    harden(tmp_path)
    terms = _terms(tmp_path)

    gacha = source_bridge_term_matches(
        "所需支援卡兑换点数",
        "Exchange Points cần để đổi Support Card",
        terms,
        key="Gacha0002",
        source_path="localize_dict.json",
        json_path=["Gacha0002"],
    )
    old_calque = source_bridge_term_matches(
        "所需育成赛马娘兑换点数",
        "Điểm cần để đổi Uma Musume",
        terms,
        key="Gacha0001",
        source_path="localize_dict.json",
        json_path=["Gacha0001"],
    )
    shop = source_bridge_term_matches(
        "兑换点数不足",
        "Không đủ điểm để đổi",
        terms,
        key="Shop999002",
        source_path="localize_dict.json",
        json_path=["Shop999002"],
    )
    story = source_bridge_term_matches(
        "把点数兑换成纪念品。",
        "Đổi điểm lấy quà lưu niệm.",
        terms,
        key=None,
        source_path="text_data_dict.json",
        json_path=["181", "1002"],
    )

    assert [item["id"] for item in gacha] == ["gacha.exchange_points"]
    assert gacha[0]["accepted_present"] is True
    assert [item["id"] for item in old_calque] == ["gacha.exchange_points"]
    assert old_calque[0]["accepted_present"] is False
    assert old_calque[0]["forbidden_present"] is True
    assert shop == []
    assert story == []


def test_hardener_is_idempotent(tmp_path: Path) -> None:
    _write_bridge(tmp_path)
    harden(tmp_path)
    first = (tmp_path / "glossary" / "source_bridge_terms.json").read_bytes()
    harden(tmp_path)
    second = (tmp_path / "glossary" / "source_bridge_terms.json").read_bytes()
    assert first == second
