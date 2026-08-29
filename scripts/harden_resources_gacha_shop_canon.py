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


def harden(repo_root: Path = REPO_ROOT) -> None:
    """Harden high-frequency resource bridges without matching ordinary prose.

    zh-CN uses semantic substitutions for some Uma Musume resource identities.
    Those aliases are useful in player-facing resource/UI strings, but they are
    unsafe as global prose aliases.  Resource bridge rules are therefore kept
    on UI localization data until narrower text-data contexts are proven.
    """

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

    _write(bridge_path, payload)


if __name__ == "__main__":
    harden()
