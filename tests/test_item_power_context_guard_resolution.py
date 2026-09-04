from __future__ import annotations

import json
from pathlib import Path

from scripts.resolve_context_guard_findings import resolve
from scripts.translation_review_common import community_term_matches, load_community_terms


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _seed(tmp_path: Path) -> None:
    _write(tmp_path / "glossary" / "ui_community_terms.json", {"terms": [{
        "id": "common.stat.power",
        "source_aliases": ["力量"],
        "preferred": "Power",
        "accepted": ["Power"],
        "forbidden": ["Sức mạnh"],
        "require_accepted": True,
        "exclude_source_contains": [
            "商品的力量",
            "不可思议力量",
            "超越极限力量",
            "莱茵力量",
            "将情谊化为力量",
            "力量的传道者",
            "充满力量的乐曲",
            "将最大力量献给你",
            "宿敌赋予了我们力量",
            "依靠尾巴来支撑自己的力量",
        ],
    }]})
    _write(tmp_path / "glossary" / "term_registry.json", {"terms": []})
    _write(tmp_path / "glossary" / "canonical_findings.json", {"findings": [
        {
            "finding_id": "cf-5d23e532c5359881",
            "status": "open",
            "source_zh_cn": "力量",
            "canonical_resolution": None,
            "review_resolution": None,
            "evidence": [
                {"source_path": "text_data_dict.json", "json_path": ["130", "181"], "source_text": "商品的力量会让大家露出笑容。", "current_text": "Sức mạnh của sản phẩm sẽ khiến mọi người mỉm cười."},
                {"source_path": "text_data_dict.json", "json_path": ["128", "1104"], "source_text": "将情谊化为力量，超越无法估量的命运。", "current_text": "Biến tình cảm gắn bó thành sức mạnh, vượt qua số phận."},
            ],
        },
        {
            "finding_id": "cf-a4af27bf832dd765",
            "status": "open",
            "source_zh_cn": "力量",
            "canonical_resolution": None,
            "review_resolution": None,
            "evidence": [{"source_path": "text_data_dict.json", "json_path": ["130", "277"], "source_text": "力量的传道者", "current_text": "Người truyền bá sức mạnh"}],
        },
        {
            "finding_id": "cf-f6a4d26b3bc63f7c",
            "status": "open",
            "source_zh_cn": "力量",
            "canonical_resolution": None,
            "review_resolution": None,
            "evidence": [
                {"source_path": "text_data_dict.json", "json_path": ["128", "1187"], "source_text": "华丽、优雅、勇敢！点燃内心的充满力量的乐曲！", "current_text": "Rực rỡ, thanh lịch, dũng cảm! Một khúc nhạc tràn đầy sức mạnh thắp sáng trái tim!"},
                {"source_path": "text_data_dict.json", "json_path": ["128", "1190"], "source_text": "传递☆我们的全力应援！将最大力量献给你♪", "current_text": "Dành sức mạnh lớn nhất cho bạn♪"},
                {"source_path": "text_data_dict.json", "json_path": ["128", "1192"], "source_text": "因为宿敌赋予了我们力量——无论到哪里，都一起前行吧。", "current_text": "Bởi kình địch đã trao cho chúng ta sức mạnh—dù đi đâu, hãy cùng nhau tiến bước."},
            ],
        },
        {
            "finding_id": "cf-183dbea74ee91b48",
            "status": "open",
            "source_zh_cn": "华丽、优雅、勇敢！点燃内心的充满力量的乐曲！\\n无论遇到什么困难都不会屈服——这才是公主应有的姿态！",
            "canonical_resolution": None,
            "review_resolution": None,
            "evidence": [
                {"source_path": "text_data_dict.json", "json_path": ["128", "1187"], "source_text": "华丽、优雅、勇敢！点燃内心的充满力量的乐曲！\\n无论遇到什么困难都不会屈服——这才是公主应有的姿态！", "current_text": "Rực rỡ, thanh lịch, dũng cảm! Một khúc nhạc tràn đầy sức mạnh thắp sáng trái tim!\\nDù gặp bất cứ khó khăn nào cũng không khuất phục—đó mới là dáng vẻ của một công chúa!"},
            ],
        },
        {
            "finding_id": "cf-36e967229329369e",
            "status": "open",
            "source_zh_cn": "力量",
            "canonical_resolution": None,
            "review_resolution": None,
            "evidence": [
                {"source_path": "text_data_dict.json", "json_path": ["167", "1026"], "source_text": "有着能够依靠尾巴来支撑自己的力量……据说", "current_text": "Nghe nói có sức mạnh đủ để dùng đuôi chống đỡ cả cơ thể……"},
            ],
        },
        {
            "finding_id": "cf-ecde28dd625ae647",
            "status": "open",
            "source_zh_cn": "力量",
            "canonical_resolution": None,
            "review_resolution": None,
            "evidence": [
                {"source_path": "text_data_dict.json", "json_path": ["10", "110"], "source_text": "具有激发不可思议力量的能力。\\n可用于支援卡的强化。", "current_text": "Có khả năng khơi dậy sức mạnh kỳ diệu.\\nCó thể dùng để nâng cấp Support Card."},
                {"source_path": "text_data_dict.json", "json_path": ["10", "144"], "source_text": "据说是可以激发出超越极限力量的\\n彩虹色力量石。", "current_text": "Viên đá sức mạnh cầu vồng được cho là có thể khơi dậy sức mạnh vượt giới hạn."},
            ],
        },
        {
            "finding_id": "cf-5204eca8a2e00ad5",
            "status": "open",
            "source_zh_cn": "莱茵力量的特殊服装",
            "canonical_resolution": None,
            "review_resolution": None,
            "evidence": [
                {"source_path": "text_data_dict.json", "json_path": ["15", "110901"], "source_text": "莱茵力量的特殊服装", "current_text": "Trang phục đặc biệt (Rhein Kraft)"},
                {"source_path": "text_data_dict.json", "json_path": ["15", "110902"], "source_text": "莱茵力量的特殊服装", "current_text": "Trang phục đặc biệt (Rhein Kraft)"},
            ],
        },
    ]})


def test_narrative_and_proper_name_power_findings_resolve_without_disabling_power_stat(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert resolve(tmp_path) is True
    assert resolve(tmp_path) is False

    payload = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    for finding in payload["findings"]:
        assert finding["canonical_resolution"] == {
            "layer": "context_guard",
            "term_id": "common.stat.power",
            "target_vi": "Power",
        }

    terms = load_community_terms(tmp_path)
    for source, target, path in [
        ("将情谊化为力量，超越无法估量的命运。", "Biến tình cảm gắn bó thành sức mạnh, vượt qua số phận.", ["128", "1104"]),
        ("力量的传道者", "Người truyền bá sức mạnh", ["130", "277"]),
        ("华丽、优雅、勇敢！点燃内心的充满力量的乐曲！", "Một khúc nhạc tràn đầy sức mạnh", ["128", "1187"]),
        ("传递☆我们的全力应援！将最大力量献给你♪", "Dành sức mạnh lớn nhất cho bạn♪", ["128", "1190"]),
        ("因为宿敌赋予了我们力量——无论到哪里，都一起前行吧。", "Bởi kình địch đã trao cho chúng ta sức mạnh", ["128", "1192"]),
        ("有着能够依靠尾巴来支撑自己的力量……据说", "Nghe nói có sức mạnh đủ để dùng đuôi chống đỡ cả cơ thể……", ["167", "1026"]),
    ]:
        matches = community_term_matches(None, source, target, terms, source_path="text_data_dict.json", json_path=path)
        assert not any(match["id"] == "common.stat.power" for match in matches)

    proper_name = community_term_matches(None, "莱茵力量的特殊服装", "Trang phục đặc biệt (Rhein Kraft)", terms, source_path="text_data_dict.json", json_path=["15", "110901"])
    assert not any(match["id"] == "common.stat.power" for match in proper_name)

    stat = community_term_matches(None, "力量达到1200以上", "Power đạt từ 1200 trở lên", terms, source_path="text_data_dict.json", json_path=["131", "999"])
    power = next(match for match in stat if match["id"] == "common.stat.power")
    assert power["accepted_present"] is True
    assert power["forbidden_present"] is False
