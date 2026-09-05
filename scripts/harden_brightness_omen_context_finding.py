from __future__ import annotations

"""Prevent standalone Skill alias 光明 from overmatching longer proper-name compounds."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-36f01160a6498749"
TERM_ID = "reviewed.skill_name.6b9641d2417b"
EXCLUSIONS = ["光明的征兆", "目白光明"]
DECISION = {
    "decision_id": "audit.finding-brightness-omen-overmatch-ignore",
    "source_zh_cn": "光明的征兆",
    "action": "ignore",
    "target_vi": "",
    "kind": "context_rule",
    "category": "skill_name",
    "note": (
        "The finding reports a false substring match from standalone Skill 光明. The live term is "
        "hardened to exclude the distinct compound 光明的征兆, so this context finding should no "
        "longer block review. This decision does not canonize a Vietnamese title for 光明的征兆."
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

    registry_before = json.dumps(registry, ensure_ascii=False, sort_keys=True)
    matched = False
    for term in terms:
        if not isinstance(term, dict) or term.get("id") != TERM_ID:
            continue
        matched = True
        exclusions = [str(value) for value in term.get("exclude_source_contains", []) if str(value)]
        term["exclude_source_contains"] = list(dict.fromkeys([*exclusions, *EXCLUSIONS]))
        term["context_note"] = (
            "Standalone Skill 光明 maps to Ánh sáng only as that Skill identity. Do not match the alias "
            "inside the distinct longer Skill title 光明的征兆 or the verified character name 目白光明 "
            "(Mejiro Bright)."
        )
        break

    if not matched:
        raise ValueError(f"missing canonical term {TERM_ID}")

    changed = registry_before != json.dumps(registry, ensure_ascii=False, sort_keys=True)
    if changed:
        _write(registry_path, registry)

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    reviews_before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    for index, item in enumerate(decisions):
        if isinstance(item, dict) and item.get("decision_id") == DECISION["decision_id"]:
            merged = dict(item)
            merged.update(DECISION)
            decisions[index] = merged
            break
    else:
        decisions.append(dict(DECISION))
    reviews_changed = reviews_before != json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    if reviews_changed:
        _write(reviews_path, reviews)

    return changed or reviews_changed


def main() -> int:
    changed = harden(ROOT)
    print(f"brightness_omen_context_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
