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


def test_hardener_is_idempotent(tmp_path: Path) -> None:
    _write_bridge(tmp_path)
    harden(tmp_path)
    first = (tmp_path / "glossary" / "source_bridge_terms.json").read_bytes()
    harden(tmp_path)
    second = (tmp_path / "glossary" / "source_bridge_terms.json").read_bytes()
    assert first == second
