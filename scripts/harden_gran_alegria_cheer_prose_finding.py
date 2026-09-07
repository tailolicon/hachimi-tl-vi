from __future__ import annotations

"""Prevent the Gran Alegria zh-CN alias from overmatching ordinary cheer prose."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TERM_ID = "character.gran_alegria"
SOURCE = "向在这个时代出生的所有人宣告——\\n来吧，放声欢呼吧。你也将成为『传奇』的暴风眼！"
DECISION = {
    "decision_id": "audit.finding.gran-alegria-cheer-prose-overmatch",
    "source_zh_cn": SOURCE,
    "action": "ignore",
    "target_vi": "",
    "kind": "context_rule",
    "category": "character",
    "note": (
        "In this exact profile/prose sentence, 放声欢呼 is the ordinary verb phrase 'cheer loudly', "
        "not the character identity Gran Alegria. The canonical character alias remains valid elsewhere; "
        "the locked term is hardened with an exact-source exclusion so this false positive no longer blocks review."
    ),
}


def _load(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return dict(default or {})
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def harden(repo_root: Path = ROOT) -> bool:
    registry_path = repo_root / "glossary" / "term_registry.json"
    registry = _load(registry_path)
    terms = registry.get("terms", [])
    if not isinstance(terms, list):
        raise ValueError("glossary/term_registry.json terms must be a list")

    before_registry = json.dumps(registry, ensure_ascii=False, sort_keys=True)
    matched = False
    for term in terms:
        if not isinstance(term, dict) or term.get("id") != TERM_ID:
            continue
        matched = True
        exclusions = [str(value) for value in term.get("exclude_source_contains", []) if str(value)]
        term["exclude_source_contains"] = list(dict.fromkeys([*exclusions, SOURCE]))
        term["context_note"] = (
            "放声欢呼 is Gran Alegria only as the verified character identity. Do not match it inside the "
            "excluded ordinary-prose sentence where the words mean 'cheer loudly'."
        )
        break
    if not matched:
        raise ValueError(f"missing canonical term {TERM_ID}")

    registry_changed = before_registry != json.dumps(registry, ensure_ascii=False, sort_keys=True)
    if registry_changed:
        _write(registry_path, registry)

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before_reviews = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    for index, item in enumerate(decisions):
        if isinstance(item, dict) and item.get("decision_id") == DECISION["decision_id"]:
            merged = dict(item)
            merged.update(DECISION)
            decisions[index] = merged
            break
    else:
        decisions.append(dict(DECISION))
    reviews_changed = before_reviews != json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    if reviews_changed:
        _write(reviews_path, reviews)

    return registry_changed or reviews_changed


def main() -> int:
    changed = harden(ROOT)
    print(f"gran_alegria_cheer_prose_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
