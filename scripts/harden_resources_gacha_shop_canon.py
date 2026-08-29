from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]


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


def _upsert(items: list[dict[str, Any]], record: dict[str, Any]) -> None:
    existing = _find(items, str(record["id"]))
    if existing is None:
        items.append(record)
    else:
        existing.clear()
        existing.update(record)


def harden(repo_root: Path = REPO_ROOT) -> None:
    """Harden high-frequency resource bridges without matching ordinary prose."""

    bridge_path = repo_root / "glossary/source_bridge_terms.json"
    payload = _load(bridge_path, {"schema_version": 1, "terms": []})
    terms = payload.setdefault("terms", [])

    monies = _find(terms, "currency.monies")
    if monies is not None:
        monies.update(
            {
                "source_paths": ["localize_dict.json"],
                "match_mode": "contains",
                "note": (
                    "金币 is the zh-CN localization bridge for the game's Monies currency. "
                    "Enforce it only in player-facing localize/UI data; ordinary story prose "
                    "about gold, coins, or money must not be canonicalized to Monies."
                ),
            }
        )

    cleat = _find(terms, "resource.cleat")
    if cleat is not None:
        cleat.update(
            {
                "source_paths": ["localize_dict.json"],
                "match_mode": "contains",
                "note": (
                    "蹄铁 is the zh-CN bridge for the player-facing Cleat/Cleats resource. "
                    "Enforce it only in player-facing localize/UI data; ordinary horse/hoof "
                    "prose must remain natural language."
                ),
            }
        )

    _upsert(
        terms,
        {
            "id": "currency.jewel.paid",
            "ja": ["有償ジュエル"],
            "zh_cn": ["付费宝石", "有偿宝石"],
            "preferred": "paid Jewels",
            "accepted": ["paid Jewel", "paid Jewels", "Jewel trả phí"],
            "forbidden": ["Jewel miễn phí", "free Jewel", "free Jewels"],
            "require_accepted": True,
            "source_paths": ["localize_dict.json"],
            "match_mode": "contains",
            "note": "Paid-Jewel wording is a fixed shop/account distinction. Scope to localize UI so generic paid/free prose is not captured.",
        },
    )
    _upsert(
        terms,
        {
            "id": "currency.jewel.free",
            "ja": ["無償ジュエル"],
            "zh_cn": ["免费宝石", "无偿宝石"],
            "preferred": "free Jewels",
            "accepted": ["free Jewel", "free Jewels", "Jewel miễn phí"],
            "forbidden": ["Jewel trả phí", "paid Jewel", "paid Jewels"],
            "require_accepted": True,
            "source_paths": ["localize_dict.json"],
            "match_mode": "contains",
            "note": "Free-Jewel wording is a fixed shop/account distinction. Scope to localize UI so generic paid/free prose is not captured.",
        },
    )
    _upsert(
        terms,
        {
            "id": "gacha.exchange_points",
            "ja": ["交換Pt", "交換ポイント"],
            "zh_cn": ["兑换点数", "交換點數"],
            "preferred": "Exchange Points",
            "accepted": ["Exchange Point", "Exchange Points"],
            "forbidden": ["Điểm đổi", "Điểm cần để đổi", "điểm đổi", "điểm cần để đổi"],
            "require_accepted": True,
            "source_paths": ["localize_dict.json"],
            "key_prefixes": ["Gacha"],
            "match_mode": "contains",
            "note": (
                "兑换点数 in Gacha UI is the banner pity currency shown as Exchange Points in "
                "Global usage. Restrict to Gacha localize keys so generic shop exchanges or story "
                "language do not become a pity-currency match."
            ),
        },
    )

    _write(bridge_path, payload)


if __name__ == "__main__":
    harden()
