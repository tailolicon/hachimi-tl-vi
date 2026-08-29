from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

JRA_COURSES = {
    "tokyo": ("东京", "東京", "Tokyo"),
    "nakayama": ("中山", "中山", "Nakayama"),
    "kyoto": ("京都", "京都", "Kyoto"),
    "hanshin": ("阪神", "阪神", "Hanshin"),
    "chukyo": ("中京", "中京", "Chukyo"),
    "sapporo": ("札幌", "札幌", "Sapporo"),
    "hakodate": ("函馆", "函館", "Hakodate"),
    "niigata": ("新潟", "新潟", "Niigata"),
    "fukushima": ("福岛", "福島", "Fukushima"),
    "kokura": ("小仓", "小倉", "Kokura"),
}
LOCAL_COURSES = {
    "kawasaki": ("川崎", "川崎", "Kawasaki"),
    "funabashi": ("船桥", "船橋", "Funabashi"),
}

RACES: dict[str, dict[str, Any]] = {
    "race.tokyo_yushun": {
        "zh_cn": ["东京优骏（日本德比）", "日本德比"],
        "ja": ["東京優駿", "日本ダービー"],
        "target_vi": "Japanese Derby",
        "note": "Canonical player-facing form is Japanese Derby; JP identity is 東京優駿 / Tokyo Yushun. One target prevents legacy Japan Derby/Japanese Derby/Tokyo Yushun split-brain.",
    },
    "race.japanese_oaks": {
        "zh_cn": ["优骏牝马（日本橡树大赛）"],
        "ja": ["優駿牝馬", "オークス"],
        "target_vi": "Japanese Oaks",
        "note": "Global game-facing race label is Japanese Oaks; JRA identifies the same race as Yushun Himba (Japanese Oaks).",
    },
    "race.japan_cup": {"zh_cn": ["日本杯"], "ja": ["ジャパンカップ"], "target_vi": "Japan Cup"},
    "race.japan_dirt_derby": {"zh_cn": ["日本沙土德比"], "ja": ["ジャパンダートダービー"], "target_vi": "Japan Dirt Derby", "note": "Historical game identity; preserve the historical NAR English proper name rather than applying the later real-race rename."},
    "race.arima_kinen": {"zh_cn": ["有马纪念"], "ja": ["有馬記念"], "target_vi": "Arima Kinen"},
    "race.asahi_hai_futurity_stakes": {"zh_cn": ["朝日杯未来锦标", "朝日杯FS"], "ja": ["朝日杯フューチュリティステークス", "朝日杯FS"], "target_vi": "Asahi Hai Futurity Stakes"},
    "race.satsuki_sho": {"zh_cn": ["皋月赏"], "ja": ["皐月賞"], "target_vi": "Satsuki Sho"},
    "race.kikuka_sho": {"zh_cn": ["菊花赏"], "ja": ["菊花賞"], "target_vi": "Kikuka Sho"},
    "race.oka_sho": {"zh_cn": ["樱花赏"], "ja": ["桜花賞"], "target_vi": "Oka Sho"},
    "race.tenno_sho_spring": {"zh_cn": ["天皇赏（春）"], "ja": ["天皇賞（春）"], "target_vi": "Tenno Sho (Spring)"},
    "race.tenno_sho_autumn": {"zh_cn": ["天皇赏（秋）"], "ja": ["天皇賞（秋）"], "target_vi": "Tenno Sho (Autumn)"},
    "race.takarazuka_kinen": {"zh_cn": ["宝冢纪念"], "ja": ["宝塚記念"], "target_vi": "Takarazuka Kinen"},
    "race.yasuda_kinen": {"zh_cn": ["安田纪念"], "ja": ["安田記念"], "target_vi": "Yasuda Kinen"},
    "race.mile_championship": {"zh_cn": ["英里冠军赛"], "ja": ["マイルチャンピオンシップ"], "target_vi": "Mile Championship"},
    "race.sprinters_stakes": {"zh_cn": ["短途马锦标"], "ja": ["スプリンターズステークス"], "target_vi": "Sprinters Stakes"},
    "race.nhk_mile_cup": {"zh_cn": ["NHK英里杯"], "ja": ["NHKマイルカップ"], "target_vi": "NHK Mile Cup"},
    "race.osaka_hai": {"zh_cn": ["大阪杯"], "ja": ["大阪杯"], "target_vi": "Osaka Hai"},
    "race.hopeful_stakes": {"zh_cn": ["希望锦标"], "ja": ["ホープフルステークス", "ホープフルS"], "target_vi": "Hopeful Stakes"},
    "race.february_stakes": {"zh_cn": ["二月锦标"], "ja": ["フェブラリーステークス", "フェブラリーS"], "target_vi": "February Stakes"},
    "race.champions_cup": {"zh_cn": ["冠军杯"], "ja": ["チャンピオンズカップ"], "target_vi": "Champions Cup"},
    "race.victoria_mile": {"zh_cn": ["维多利亚英里赛"], "ja": ["ヴィクトリアマイル"], "target_vi": "Victoria Mile"},
    "race.queen_elizabeth_ii_cup": {"zh_cn": ["伊丽莎白女王杯"], "ja": ["エリザベス女王杯"], "target_vi": "Queen Elizabeth II Cup"},
    "race.nikkei_sho": {"zh_cn": ["日经赏"], "ja": ["日経賞"], "target_vi": "Nikkei Sho"},
    "race.nikkei_shinshun_hai": {"zh_cn": ["日经新春杯"], "ja": ["日経新春杯"], "target_vi": "Nikkei Shinshun Hai"},
    "race.radio_nikkei_sho": {"zh_cn": ["日经广播赏"], "ja": ["ラジオNIKKEI賞"], "target_vi": "Radio Nikkei Sho"},
    "race.cluster_cup": {"zh_cn": ["星团杯"], "ja": ["クラスターカップ"], "target_vi": "Cluster Cup"},
    "race.sparking_lady_cup": {"zh_cn": ["星火雌马杯"], "ja": ["スパーキングレディーカップ"], "target_vi": "Sparking Lady Cup"},
    "race.hanshin_juvenile_fillies": {"zh_cn": ["阪神两岁雌马大赛"], "ja": ["阪神ジュベナイルフィリーズ"], "target_vi": "Hanshin Juvenile Fillies"},
    "race.kanto_oaks": {"zh_cn": ["关东橡树大赛"], "ja": ["関東オークス"], "target_vi": "Kanto Oaks"},
    "race.zen_nippon_nisai_yushun": {"zh_cn": ["全日本新马优骏"], "ja": ["全日本2歳優駿"], "target_vi": "Zen-Nippon Nisai Yushun"},
    "race.kyodo_news_hai": {"zh_cn": ["共同通信杯"], "ja": ["共同通信杯"], "target_vi": "Kyodo News Hai"},
    "race.sekiya_kinen": {"zh_cn": ["关屋纪念"], "ja": ["関屋記念"], "target_vi": "Sekiya Kinen"},
    "race.hakodate_sprint_stakes": {"zh_cn": ["函馆短途锦标"], "ja": ["函館スプリントステークス"], "target_vi": "Hakodate Sprint Stakes"},
    "race.hakodate_kinen": {"zh_cn": ["函馆纪念"], "ja": ["函館記念"], "target_vi": "Hakodate Kinen"},
    "race.antares_stakes": {"zh_cn": ["天蝎锦标"], "ja": ["アンタレスステークス"], "target_vi": "Antares Stakes"},
    "race.sapporo_kinen": {"zh_cn": ["札幌纪念"], "ja": ["札幌記念"], "target_vi": "Sapporo Kinen"},
    "race.ibis_summer_dash": {"zh_cn": ["朱鹮夏季短跑赛"], "ja": ["アイビスサマーダッシュ"], "target_vi": "Ibis Summer Dash"},
    "race.kashiwa_kinen": {"zh_cn": ["柏纪念"], "ja": ["かしわ記念"], "target_vi": "Kashiwa Kinen"},
    "race.negishi_stakes": {"zh_cn": ["根岸锦标"], "ja": ["根岸ステークス"], "target_vi": "Negishi Stakes"},
    "race.elm_stakes": {"zh_cn": ["榆树锦标"], "ja": ["エルムステークス"], "target_vi": "Elm Stakes"},
    "race.tulip_sho": {"zh_cn": ["郁金香赏"], "ja": ["チューリップ賞"], "target_vi": "Tulip Sho"},
    "race.kinko_sho": {"zh_cn": ["金鯱赏"], "ja": ["金鯱賞"], "target_vi": "Kinko Sho"},
    "race.diamond_stakes": {"zh_cn": ["钻石锦标"], "ja": ["ダイヤモンドステークス"], "target_vi": "Diamond Stakes"},
    "race.stayers_stakes": {"zh_cn": ["长途锦标"], "ja": ["ステイヤーズステークス"], "target_vi": "Stayers Stakes"},
    "race.diolite_kinen": {"zh_cn": ["闪长岩纪念"], "ja": ["ダイオライト記念"], "target_vi": "Diolite Kinen"},
    "race.hankyu_hai": {"zh_cn": ["阪急杯"], "ja": ["阪急杯"], "target_vi": "Hankyu Hai"},
    "race.ladies_prelude": {"zh_cn": ["雌马预赛"], "ja": ["レディスプレリュード"], "target_vi": "Ladies Prelude"},
    "race.prix_arc_de_triomphe": {"zh_cn": ["凯旋门赏"], "ja": ["凱旋門賞"], "target_vi": "Prix de l'Arc de Triomphe"},
    "race.tokyo_sports_hai_nisai_stakes": {"zh_cn": ["东京体育杯新马锦标"], "ja": ["東京スポーツ杯2歳ステークス"], "target_vi": "Tokyo Sports Hai Nisai Stakes", "note": "Verified JRA/in-game identity; preserve Nisai instead of semantic-calquing the zh-CN title."},
    "race.keio_hai_nisai_stakes": {"zh_cn": ["京王杯新马锦标"], "ja": ["京王杯2歳ステークス"], "target_vi": "Keio Hai Nisai Stakes", "note": "Verified JRA/in-game identity; lossy zh-CN 京城锦标 is handled separately by an exact retrospective slot rule."},
    "race.hakodate_nisai_stakes": {"zh_cn": ["函馆新马锦标"], "ja": ["函館2歳ステークス"], "target_vi": "Hakodate Nisai Stakes", "note": "Verified JRA/in-game identity."},
    "race.sapporo_nisai_stakes": {"zh_cn": ["札幌新马锦标"], "ja": ["札幌2歳ステークス"], "target_vi": "Sapporo Nisai Stakes", "note": "Verified JRA/in-game identity."},
    "race.nakayama_himba_stakes": {"zh_cn": ["中山赛马娘锦标"], "ja": ["中山牝馬ステークス"], "target_vi": "Nakayama Himba Stakes", "note": "Verified JRA/in-game identity; zh-CN semantic wording is not spelling authority."},
    "race.kyoto_himba_stakes": {"zh_cn": ["京都赛马娘锦标"], "ja": ["京都牝馬ステークス"], "target_vi": "Kyoto Himba Stakes", "note": "Verified historical JRA/in-game identity."},
    "race.hanshin_himba_stakes": {"zh_cn": ["阪神赛马娘锦标"], "ja": ["阪神牝馬ステークス"], "target_vi": "Hanshin Himba Stakes", "note": "Verified JRA/in-game identity."},
}

BRIDGE_RACES = {
    "race.bridge.capella_stakes": ("五车二锦标", "Capella Stakes", "カペラステークス"),
    "race.bridge.stayers_stakes": ("长途锦标", "Stayers Stakes", "ステイヤーズステークス"),
    "race.bridge.diolite_kinen": ("闪长岩纪念", "Diolite Kinen", "ダイオライト記念"),
    "race.bridge.cluster_cup": ("星团杯", "Cluster Cup", "クラスターカップ"),
    "race.bridge.sparking_lady_cup": ("星火雌马杯", "Sparking Lady Cup", "スパーキングレディーカップ"),
}


def _load(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _find(items: list[dict[str, Any]], record_id: str) -> dict[str, Any] | None:
    for item in items:
        if isinstance(item, dict) and str(item.get("id", "")) == record_id:
            return item
    return None


def _upsert(items: list[dict[str, Any]], record: dict[str, Any]) -> dict[str, Any]:
    found = _find(items, str(record["id"]))
    if found is not None:
        found.update(record)
        return found
    items.append(dict(record))
    return items[-1]


def _is_proper_race(term: dict[str, Any]) -> bool:
    # Only structured proper-race records may receive the default named-race
    # guards. Prefix-based detection is unsafe because system records such as
    # race.class.*, race.grade.*, race.ui.*, and race.track_condition.* also
    # intentionally use the race.* namespace. RACES upserts normalize verified
    # legacy named races to category=race_name before persistence.
    return str(term.get("category", "")) == "race_name"


def _harden_registry(repo_root: Path) -> None:
    path = repo_root / "glossary/term_registry.json"
    payload = _load(path, {"terms": []})
    terms = payload.setdefault("terms", [])

    # Proper names are an expandable registry. Their semantic changes must only
    # invalidate entries that actually contain the identity.
    for term in terms:
        if isinstance(term, dict) and bool(term.get("locked")) and _is_proper_race(term):
            term["source_paths"] = ["text_data_dict.json"]
            term["json_path_prefixes"] = [["32"], ["33"], ["111"]]
            term["match_mode"] = "contains"
            term["invalidation_scope"] = "item"

    # Remove old competing Derby/Japanese-Oaks aliases so one identity has one
    # player-facing target. The records remain as history only.
    for obsolete_id in ("reviewed.race_name.867d16270a74",):
        obsolete = _find(terms, obsolete_id)
        if obsolete is not None:
            obsolete["locked"] = False
            obsolete["zh_cn"] = []
            obsolete["note"] = "Superseded by race.tokyo_yushun; kept only as registry history to prevent competing Derby targets."

    for race_id, spec in RACES.items():
        record = {
            "id": race_id,
            "category": "race_name",
            "ja": list(spec.get("ja", [])),
            "zh_cn": list(spec.get("zh_cn", [])),
            "target_vi": spec["target_vi"],
            "locked": True,
            "source_paths": ["text_data_dict.json"],
            "json_path_prefixes": [["32"], ["33"], ["111"]],
            "match_mode": "contains",
            "invalidation_scope": "item",
            "note": spec.get("note", "Verified player-facing/JRA/NAR/international proper-race identity; do not semantic-calque the zh-CN title."),
        }
        _upsert(terms, record)

    # zh-CN 京城锦标 is a demonstrated identity collision: category 32/33 slot
    # 3061 is Miyako Stakes, while retrospective category 111/134 is a different
    # race. Never allow the Miyako identity to leak outside its pinned identity slots.
    miyako = _find(terms, "race.miyako_stakes")
    if miyako is not None:
        miyako.update({
            "category": "race_name",
            "zh_cn": ["京城锦标"],
            "source_paths": ["text_data_dict.json"],
            "json_path_prefixes": [["32", "3061"], ["33", "3061"]],
            "match_mode": "exact",
            "invalidation_scope": "item",
            "note": "Pinned 32/3061 and 33/3061 are Miyako Stakes. zh-CN 京城锦标 collides with a different retrospective identity at 111/134, so this rule is intentionally slot-scoped.",
        })

    _upsert(terms, {
        "id": "race.keio_hai_nisai_stakes.zhcollapse_111_134",
        "category": "race_name",
        "ja": ["京王杯2歳ステークス"],
        "zh_cn": ["京城锦标"],
        "target_vi": "Keio Hai Nisai Stakes",
        "locked": True,
        "source_paths": ["text_data_dict.json"],
        "json_path_prefixes": [["111", "134"]],
        "match_mode": "exact",
        "invalidation_scope": "item",
        "note": "At retrospective identity 111/134, lossy zh-CN 京城锦标 is Keio Hai Nisai Stakes. Keep it structurally distinct from Miyako Stakes at 32/3061 and 33/3061.",
    })

    # Race classes: exact primary UI labels plus explicitly race-oriented text
    # tables. Story prose (e.g. category 128) is intentionally outside these guards.
    class_specs = (
        ("race.class.junior", "新马级", "ジュニア級", "Junior Class", ["Outgame619034", "SingleMode0017"]),
        ("race.class.classic", "经典级", "クラシック級", "Classic Class", ["Outgame619035", "SingleMode0018"]),
        ("race.class.senior", "古马级", "シニア級", "Senior Class", ["Outgame619036", "SingleMode0019"]),
    )
    for rid, zh, ja, target, keys in class_specs:
        _upsert(terms, {
            "id": rid + ".ui",
            "category": "race_class",
            "ja": [ja], "zh_cn": [zh], "target_vi": target, "locked": True,
            "source_paths": ["localize_dict.json"], "key_exact": keys,
            "match_mode": "exact", "invalidation_scope": "item",
            "note": "Exact Career class labels; do not promote the bare year/class word in generic prose.",
        })
        _upsert(terms, {
            "id": rid + ".race_text",
            "category": "race_class",
            "ja": [ja], "zh_cn": [zh], "target_vi": target, "locked": True,
            "source_paths": ["text_data_dict.json"], "json_path_prefixes": [["10"], ["111"], ["131"]],
            "match_mode": "contains", "invalidation_scope": "item",
            "note": "Race/reward/requirement-table use of the Career class label; narrative prose categories are excluded.",
        })

    for rid, zh, target in (("race.grade.g1", "GⅠ", "G1"), ("race.grade.g2", "GⅡ", "G2"), ("race.grade.g3", "GⅢ", "G3")):
        _upsert(terms, {
            "id": rid, "category": "race_grade", "ja": [zh], "zh_cn": [zh], "target_vi": target,
            "locked": True, "match_mode": "contains", "invalidation_scope": "global",
            "note": "Conventional player-facing race-grade formatting uses ASCII G1/G2/G3; the source numeral is an unambiguous race grade marker.",
        })
    for rid, aliases, target in (
        ("race.grade.open", ["OP", "OP比赛"], "OP"),
        ("race.grade.pre_open", ["Pre-OP", "Pre-OP比赛"], "Pre-OP"),
    ):
        _upsert(terms, {
            "id": rid, "category": "race_grade", "ja": [target], "zh_cn": aliases, "target_vi": target,
            "locked": True, "match_mode": "exact", "invalidation_scope": "item",
            "source_paths": ["localize_dict.json"],
            "note": "Observed race-grade UI label. Exact matching prevents short OP text from leaking into unrelated prose.",
        })

    _upsert(terms, {
        "id": "race.ui.make_debut", "category": "race_ui", "ja": ["メイクデビュー"], "zh_cn": ["出道战"],
        "target_vi": "Make Debut", "locked": True, "source_paths": ["localize_dict.json", "text_data_dict.json"],
        "json_path_prefixes": [["TrainingChallenge4180924"], ["121"], ["130"]],
        "match_mode": "exact", "invalidation_scope": "item",
        "note": "Career debut-race system label. Guarded to observed race UI/requirement slots; generic debut prose is not matched.",
    })
    _upsert(terms, {
        "id": "race.ui.maiden", "category": "race_ui", "ja": ["未勝利戦"], "zh_cn": ["未冠赛"],
        "target_vi": "Maiden Race", "locked": True, "match_mode": "exact", "invalidation_scope": "item",
        "note": "Observed no-win/maiden race system label; use the established racing/game label instead of a literal Vietnamese calque.",
    })

    # Track/course-condition UI: one-character Chinese values are dangerous in
    # prose, so they are locked only to the exact Race UI keys.
    for rid, key, zh, ja, target in (
        ("race.track_condition.firm", "Race0186", "良", "良", "Firm"),
        ("race.track_condition.good", "Race0187", "稍重", "稍重", "Good"),
        ("race.track_condition.soft", "Race0188", "重", "重", "Soft"),
        ("race.track_condition.heavy", "Race0189", "不良", "不良", "Heavy"),
        ("race.course.inner", "Race0190", "内圈", "内回り", "Inner"),
        ("race.course.outer", "Race0191", "外圈", "外回り", "Outer"),
        ("race.course.left", "Race0192", "逆时针", "左", "Left"),
        ("race.course.right", "Race0193", "顺时针", "右", "Right"),
    ):
        _upsert(terms, {
            "id": rid, "category": "race_ui", "ja": [ja], "zh_cn": [zh], "target_vi": target,
            "locked": True, "source_paths": ["localize_dict.json"], "key_exact": [key],
            "match_mode": "exact", "invalidation_scope": "item",
            "note": "Exact Race UI slot; narrow key guard prevents generic Chinese/Japanese prose from receiving track/course labels.",
        })
    _upsert(terms, {
        "id": "race.track_condition.label", "category": "race_ui", "ja": ["バ場状態"], "zh_cn": ["马场状态"],
        "target_vi": "Track Condition", "locked": True, "source_paths": ["localize_dict.json"],
        "key_exact": ["RoomMatch0028", "RoomMatch0037", "RoomMatch0153", "RoomMatch0171"],
        "match_mode": "contains", "invalidation_scope": "item",
        "note": "Player-facing room/race setup label. Other prose containing 马场状态 is intentionally not forced to this English UI label.",
    })

    # Official JRA racecourse spellings. Category 35/456/426 are pinned course
    # identity tables; category 131 contains race requirements explicitly naming
    # racecourses. Story/prose categories are excluded.
    for slug, (zh, ja, target) in {**JRA_COURSES, **LOCAL_COURSES}.items():
        _upsert(terms, {
            "id": f"racecourse.{slug}", "category": "racecourse", "ja": [ja], "zh_cn": [zh], "target_vi": target,
            "locked": True, "source_paths": ["text_data_dict.json"],
            "json_path_prefixes": [["35"], ["456"], ["426"], ["131"]],
            "match_mode": "contains", "invalidation_scope": "item",
            "note": "Official/international racecourse spelling. Context is restricted to pinned racecourse identity and race-requirement tables, not ordinary place-name prose.",
        })

    _write(path, payload)


def _harden_community(repo_root: Path) -> None:
    path = repo_root / "glossary/ui_community_terms.json"
    payload = _load(path, {"terms": []})
    terms = payload.setdefault("terms", [])
    for rid, source, preferred, forbidden in (
        ("common.race_grade.g1", "GⅠ", "G1", ["GⅠ"]),
        ("common.race_grade.g2", "GⅡ", "G2", ["GⅡ"]),
        ("common.race_grade.g3", "GⅢ", "G3", ["GⅢ"]),
    ):
        _upsert(terms, {
            "id": rid, "category": "race_grade", "source_aliases": [source], "preferred": preferred,
            "accepted": [preferred], "compact": [], "forbidden": forbidden, "require_accepted": True,
            "match_mode": "contains", "invalidation_scope": "global",
            "basis": "Conventional player-facing race-grade formatting; source marker is unambiguous and applies globally.",
        })
    _write(path, payload)


def _harden_bridge(repo_root: Path) -> None:
    path = repo_root / "glossary/source_bridge_terms.json"
    payload = _load(path, {"schema_version": 1, "policy": {}, "terms": [], "untrusted_sources": []})
    policy = payload.setdefault("policy", {})
    policy["race_hardening"] = (
        "zh-CN race titles are identity-risk data, not authority for proper-name form. Resolve JP identity first; proper race names and racecourses are item-scoped. Never add broad aliases for generic 比赛/杯/锦标/德比/冠军/最终. Game-specific 新马/赛马娘 substitutions and scenario/event race labels stay deferred unless a verified player-facing identity exists."
    )
    terms = payload.setdefault("terms", [])
    for rid, (zh, target, ja) in BRIDGE_RACES.items():
        _upsert(terms, {
            "id": rid, "category": "race_name", "ja": [ja], "zh_cn": [zh],
            "preferred": target, "accepted": [target], "forbidden": [], "require_accepted": True,
            "source_paths": ["text_data_dict.json"], "json_path_prefixes": [["111"], ["147"]],
            "match_mode": "contains", "invalidation_scope": "item",
            "note": "Verified semantic zh-CN proper-race bridge; preserve the canonical international/Japanese race name rather than translating the Chinese meaning.",
        })
    _write(path, payload)


def harden(repo_root: Path = REPO_ROOT) -> None:
    _harden_registry(repo_root)
    _harden_community(repo_root)
    _harden_bridge(repo_root)


if __name__ == "__main__":
    harden()
