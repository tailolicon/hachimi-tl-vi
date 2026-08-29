from __future__ import annotations

import argparse
import hashlib
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REVIEWS = ROOT / "glossary/terminology_reviews.json"
DEFAULT_REGISTRY = ROOT / "glossary/term_registry.json"
ALLOWED_ACTIONS = {"lock", "defer", "ignore"}


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def clean_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        raise ValueError("alias fields must be strings or arrays of strings")
    out: list[str] = []
    for item in value:
        text = str(item).strip()
        if text and text not in out:
            out.append(text)
    return out


def stable_term_id(decision: dict[str, Any]) -> str:
    explicit = str(decision.get("term_id") or "").strip()
    if explicit:
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", explicit):
            raise ValueError(f"invalid term_id: {explicit!r}")
        return explicit
    source = str(decision.get("source_zh_cn") or "").strip()
    kind = str(decision.get("kind") or "term").strip().lower()
    safe_kind = re.sub(r"[^a-z0-9_.-]+", "_", kind).strip("_") or "term"
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()[:12]
    return f"reviewed.{safe_kind}.{digest}"


def aliases_for_term(term: dict[str, Any]) -> dict[str, list[str]]:
    return {
        "ja": clean_list(term.get("ja")),
        "zh_cn": clean_list(term.get("zh_cn")),
        "zh_tw": clean_list(term.get("zh_tw")),
        "source_aliases": clean_list(term.get("source_aliases")),
    }


def _path_prefixes(term: dict[str, Any]) -> list[tuple[str, ...]]:
    raw = term.get("json_path_prefixes") or []
    out: list[tuple[str, ...]] = []
    if not isinstance(raw, list):
        return out
    for prefix in raw:
        if isinstance(prefix, list) and prefix:
            out.append(tuple(str(part) for part in prefix))
    return out


def _prefixes_overlap(left: tuple[str, ...], right: tuple[str, ...]) -> bool:
    width = min(len(left), len(right))
    return left[:width] == right[:width]


def scopes_provably_disjoint(left: dict[str, Any], right: dict[str, Any]) -> bool:
    left_paths = set(clean_list(left.get("source_paths")))
    right_paths = set(clean_list(right.get("source_paths")))
    if left_paths and right_paths and left_paths.isdisjoint(right_paths):
        return True

    left_keys = set(clean_list(left.get("key_exact")))
    right_keys = set(clean_list(right.get("key_exact")))
    if left_keys and right_keys and left_keys.isdisjoint(right_keys):
        return True

    left_prefixes = _path_prefixes(left)
    right_prefixes = _path_prefixes(right)
    if left_prefixes and right_prefixes:
        return not any(
            _prefixes_overlap(left_prefix, right_prefix)
            for left_prefix in left_prefixes
            for right_prefix in right_prefixes
        )
    return False


def locked_alias_index(terms: list[dict[str, Any]]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    index: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for term in terms:
        if not isinstance(term, dict) or not term.get("locked"):
            continue
        for field, aliases in aliases_for_term(term).items():
            for alias in aliases:
                key = (field, alias)
                existing_terms = index.setdefault(key, [])
                for existing in existing_terms:
                    if existing.get("target_vi") == term.get("target_vi"):
                        continue
                    if scopes_provably_disjoint(existing, term):
                        continue
                    raise ValueError(
                        f"existing locked registry is internally conflicting for {field}:{alias!r}"
                    )
                existing_terms.append(term)
    return index

def normalize_decision(decision: dict[str, Any], ordinal: int) -> dict[str, Any]:
    action = str(decision.get("action") or "").strip().lower()
    if action not in ALLOWED_ACTIONS:
        raise ValueError(f"decision #{ordinal}: unsupported action {action!r}")
    decision_id = str(decision.get("decision_id") or f"decision-{ordinal:04d}").strip()
    source = str(decision.get("source_zh_cn") or "").strip()
    if not source:
        raise ValueError(f"decision {decision_id}: source_zh_cn is required")
    result = dict(decision)
    result["action"] = action
    result["decision_id"] = decision_id
    result["source_zh_cn"] = source
    if action == "lock":
        target = str(decision.get("target_vi") or "").strip()
        if not target:
            raise ValueError(f"decision {decision_id}: target_vi is required for lock")
        result["target_vi"] = target
        result["term_id"] = stable_term_id(result)
    return result


def build_locked_term(decision: dict[str, Any]) -> dict[str, Any]:
    category = str(decision.get("category") or decision.get("kind") or "reviewed").strip()
    term: dict[str, Any] = {
        "id": decision["term_id"],
        "category": category,
        "zh_cn": clean_list([decision["source_zh_cn"], *clean_list(decision.get("zh_cn_aliases"))]),
        "target_vi": decision["target_vi"],
        "locked": True,
        "review": {
            "decision_id": decision["decision_id"],
            "source": "glossary/terminology_reviews.json",
        },
    }
    for field in ("ja", "zh_tw", "source_aliases"):
        aliases = clean_list(decision.get(field))
        if aliases:
            term[field] = aliases
    note = str(decision.get("note") or "").strip()
    if note:
        term["note"] = note
    return term


def apply_reviews(registry: dict[str, Any], reviews: dict[str, Any]) -> tuple[dict[str, Any], dict[str, int]]:
    result = deepcopy(registry)
    terms = result.setdefault("terms", [])
    if not isinstance(terms, list):
        raise ValueError("term_registry.terms must be an array")
    if not all(isinstance(term, dict) for term in terms):
        raise ValueError("term_registry.terms must contain only objects")

    raw_decisions = reviews.get("decisions", [])
    if not isinstance(raw_decisions, list):
        raise ValueError("terminology_reviews.decisions must be an array")

    normalized: list[dict[str, Any]] = []
    seen_decision_ids: set[str] = set()
    for ordinal, raw in enumerate(raw_decisions, start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"decision #{ordinal} must be an object")
        decision = normalize_decision(raw, ordinal)
        decision_id = decision["decision_id"]
        if decision_id in seen_decision_ids:
            raise ValueError(f"duplicate decision_id: {decision_id}")
        seen_decision_ids.add(decision_id)
        normalized.append(decision)

    stats = {"decisions": len(normalized), "locked_added": 0, "locked_existing": 0, "deferred": 0, "ignored": 0}
    term_by_id = {str(term.get("id")): term for term in terms if term.get("id")}
    alias_index = locked_alias_index(terms)

    for decision in normalized:
        action = decision["action"]
        if action == "defer":
            stats["deferred"] += 1
            continue
        if action == "ignore":
            stats["ignored"] += 1
            continue

        candidate = build_locked_term(decision)
        target = candidate["target_vi"]
        term_id = candidate["id"]

        existing_id = term_by_id.get(term_id)
        if existing_id is not None:
            if not existing_id.get("locked"):
                raise ValueError(f"decision {decision['decision_id']}: term_id {term_id!r} already exists but is not locked")
            if str(existing_id.get("target_vi") or "") != target:
                raise ValueError(
                    f"decision {decision['decision_id']}: term_id {term_id!r} already maps to "
                    f"{existing_id.get('target_vi')!r}, not {target!r}"
                )

        matched_existing: dict[str, Any] | None = None
        scope_term = existing_id or candidate
        for field, aliases in aliases_for_term(candidate).items():
            for alias in aliases:
                previous_terms = alias_index.get((field, alias), [])
                for previous in previous_terms:
                    if previous is existing_id:
                        if matched_existing is None:
                            matched_existing = previous
                        continue
                    previous_target = str(previous.get("target_vi") or "")
                    if previous_target != target:
                        if scopes_provably_disjoint(previous, scope_term):
                            continue
                        raise ValueError(
                            f"decision {decision['decision_id']}: locked alias {field}:{alias!r} already maps "
                            f"to {previous_target!r}, not {target!r}"
                        )
                    if matched_existing is None:
                        matched_existing = previous
                    elif matched_existing is not previous and existing_id is None:
                        raise ValueError(
                            f"decision {decision['decision_id']}: aliases span multiple existing locked concepts; review manually"
                        )

        if existing_id is not None and matched_existing is not None and existing_id is not matched_existing:
            if str(matched_existing.get("target_vi") or "") != target:
                raise ValueError(
                    f"decision {decision['decision_id']}: term_id and aliases point to different existing concepts"
                )

        existing = existing_id or matched_existing
        if existing is not None:
            # Idempotent application. We deliberately do not silently mutate an
            # existing canonical concept with extra aliases; that needs its own
            # explicit registry edit/review.
            stats["locked_existing"] += 1
            continue

        terms.append(candidate)
        term_by_id[term_id] = candidate
        for field, aliases in aliases_for_term(candidate).items():
            for alias in aliases:
                alias_index.setdefault((field, alias), []).append(candidate)
        stats["locked_added"] += 1

    return result, stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply explicit reviewed terminology locks safely.")
    parser.add_argument("--reviews", type=Path, default=DEFAULT_REVIEWS)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--check", action="store_true", help="Validate decisions without writing term_registry.json")
    args = parser.parse_args()

    reviews = read_json(args.reviews, {}) or {}
    registry = read_json(args.registry, {}) or {}
    if not isinstance(reviews, dict) or not isinstance(registry, dict):
        raise SystemExit("reviews and registry must be JSON objects")

    try:
        updated, stats = apply_reviews(registry, reviews)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    if not args.check:
        args.registry.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        "decisions={decisions} added={locked_added} existing={locked_existing} "
        "deferred={deferred} ignored={ignored}".format(**stats)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
