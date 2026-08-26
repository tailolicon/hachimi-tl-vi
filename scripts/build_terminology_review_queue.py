from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANDIDATES = ROOT / "glossary/generated_candidates.json"
DEFAULT_OBSERVED = ROOT / "glossary/observed_terms.json"
DEFAULT_REGISTRY = ROOT / "glossary/term_registry.json"
DEFAULT_CHARACTERS = ROOT / "glossary/characters.json"
DEFAULT_REVIEWS = ROOT / "glossary/terminology_reviews.json"
DEFAULT_OUTPUT = ROOT / "glossary/terminology_review_queue.json"

KIND_PRIORITY = {
    "skill_name": 900,
    "race_name": 850,
    "race_display_name": 825,
    "scenario_name": 800,
    "support_unique_effect_name": 750,
    "support_card_title": 650,
    "trainee_card_title": 625,
    "support_card_full_name": 600,
    "trainee_card_full_name": 575,
    "support_display_name": 500,
    "character_name": 100,
    "character_display_name": 100,
    "character_name_alias": 100,
    "support_character_name": 100,
}
CHARACTER_KINDS = {
    "character_name",
    "character_display_name",
    "character_name_alias",
    "support_character_name",
}


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def aliases_from_term(term: dict[str, Any]) -> set[str]:
    aliases: set[str] = set()
    for field in ("zh_cn", "ja", "zh_tw", "source_aliases"):
        raw = term.get(field, [])
        if isinstance(raw, str):
            raw = [raw]
        if isinstance(raw, list):
            aliases.update(str(item).strip() for item in raw if str(item).strip())
    return aliases


def character_aliases(characters: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    records = characters.get("characters", {})
    if not isinstance(records, dict):
        return result
    for record in records.values():
        if not isinstance(record, dict):
            continue
        canonical = str(record.get("canonical") or "").strip()
        if canonical:
            result.add(canonical)
        for field in ("ja", "zh_cn", "zh_tw", "aliases"):
            raw = record.get(field, [])
            if isinstance(raw, str):
                raw = [raw]
            if isinstance(raw, list):
                result.update(str(item).strip() for item in raw if str(item).strip())
    return result


def review_decisions(reviews: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    raw = reviews.get("decisions", [])
    if not isinstance(raw, list):
        return result
    for decision in raw:
        if not isinstance(decision, dict):
            continue
        source = str(decision.get("source_zh_cn") or "").strip()
        action = str(decision.get("action") or "").strip().lower()
        if not source or action not in {"lock", "defer", "ignore"}:
            continue
        # A source should have one effective explicit review decision. If a later
        # decision supersedes an earlier one, the ledger order is authoritative.
        result[source] = decision
    return result


def best_kind(kinds: set[str]) -> str:
    if not kinds:
        return "unknown"
    return max(sorted(kinds), key=lambda kind: KIND_PRIORITY.get(kind, 300))


def build_queue(
    generated: dict[str, Any],
    observed: dict[str, Any],
    registry: dict[str, Any],
    characters: dict[str, Any],
    reviews: dict[str, Any] | None = None,
) -> dict[str, Any]:
    locked_aliases: dict[str, dict[str, Any]] = {}
    for term in registry.get("terms", []):
        if not isinstance(term, dict) or not term.get("locked"):
            continue
        for alias in aliases_from_term(term):
            locked_aliases[alias] = term

    observed_map: dict[str, dict[str, Any]] = {}
    for term in observed.get("terms", []):
        if not isinstance(term, dict):
            continue
        zh = term.get("zh_cn", [])
        if isinstance(zh, str):
            zh = [zh]
        if not isinstance(zh, list):
            continue
        for alias in zh:
            source = str(alias).strip()
            if source:
                observed_map[source] = term

    conflict_map: dict[str, dict[str, Any]] = {}
    for conflict in observed.get("conflicts", []):
        if not isinstance(conflict, dict):
            continue
        source = str(conflict.get("source_zh_cn") or "").strip()
        if source:
            conflict_map[source] = conflict

    decisions = review_decisions(reviews or {})
    char_aliases = character_aliases(characters)

    grouped: dict[str, dict[str, Any]] = {}
    candidates = generated.get("candidates", [])
    if not isinstance(candidates, list):
        candidates = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        source = str(candidate.get("source_text") or "").strip()
        if not source:
            continue
        row = grouped.setdefault(
            source,
            {
                "source_zh_cn": source,
                "kinds": set(),
                "locators": [],
                "candidate_ids": [],
            },
        )
        kind = str(candidate.get("kind") or "unknown")
        row["kinds"].add(kind)
        locator = {
            "category": str(candidate.get("source_category") or ""),
            "index": str(candidate.get("source_index") or ""),
        }
        if locator not in row["locators"] and len(row["locators"]) < 16:
            row["locators"].append(locator)
        candidate_id = str(candidate.get("id") or "")
        if candidate_id and candidate_id not in row["candidate_ids"]:
            row["candidate_ids"].append(candidate_id)

    queue: list[dict[str, Any]] = []
    status_counts: dict[str, int] = defaultdict(int)
    for source, grouped_row in grouped.items():
        kinds = set(grouped_row["kinds"])
        primary_kind = best_kind(kinds)
        base = KIND_PRIORITY.get(primary_kind, 300)
        locked = locked_aliases.get(source)
        conflict = conflict_map.get(source)
        memory = observed_map.get(source)
        decision = decisions.get(source)
        decision_action = str(decision.get("action") or "").strip().lower() if decision else None

        if locked:
            status = "canonical_locked"
            priority = 0
            reason = "Already covered by locked term_registry."
        elif decision_action == "defer":
            status = "reviewed_deferred"
            priority = 0
            reason = "Explicit review decision deferred canonical normalization."
        elif decision_action == "ignore":
            status = "reviewed_ignored"
            priority = 0
            reason = "Explicit review decision says this candidate should not become canonical terminology."
        elif decision_action == "lock":
            # Normally apply_terminology_reviews.py runs before this builder, so
            # an unapplied lock means something prevented registry promotion.
            status = "pending_lock_application"
            priority = 12000 + base
            reason = "Explicit lock decision exists but the canonical registry does not contain it yet."
        elif conflict:
            status = "conflict_review"
            priority = 10000 + base
            reason = "Merged translations disagree; resolve before promotion."
        elif kinds and kinds.issubset(CHARACTER_KINDS):
            if source in char_aliases:
                status = "handled_by_character_registry"
                priority = 0
                reason = "Proper-name identity is already handled by character registry."
            else:
                status = "character_identity_review"
                priority = 7000 + base
                reason = "Character-like proper name is not resolved by character registry."
        elif memory:
            status = "promotion_candidate"
            priority = 5000 + base
            reason = "A unique merged Vietnamese target exists; review and optionally lock it."
        elif source in char_aliases:
            status = "handled_by_character_registry"
            priority = 0
            reason = "Source matches a known character identity; do not semantic-calque it."
        else:
            status = "needs_translation_review"
            priority = 1000 + base
            reason = "No locked or observed Vietnamese mapping exists yet."

        output: dict[str, Any] = {
            "source_zh_cn": source,
            "kinds": sorted(kinds),
            "primary_kind": primary_kind,
            "status": status,
            "priority": priority,
            "reason": reason,
            "locators": grouped_row["locators"],
            "candidate_ids": grouped_row["candidate_ids"],
        }
        if locked:
            output["canonical_term_id"] = locked.get("id")
            output["canonical_target_vi"] = locked.get("target_vi")
        if memory:
            output["observed_target_vi"] = memory.get("target_vi")
            output["observed_term_id"] = memory.get("id")
        if conflict:
            output["conflicting_targets_vi"] = conflict.get("targets_vi", [])
        if decision:
            output["review_decision"] = {
                "decision_id": decision.get("decision_id"),
                "action": decision_action,
                "target_vi": decision.get("target_vi"),
            }
        queue.append(output)
        status_counts[status] += 1

    queue.sort(
        key=lambda row: (
            -int(row.get("priority", 0)),
            -KIND_PRIORITY.get(str(row.get("primary_kind")), 300),
            str(row.get("source_zh_cn", "")),
        )
    )

    actionable_statuses = {
        "pending_lock_application",
        "conflict_review",
        "character_identity_review",
        "promotion_candidate",
        "needs_translation_review",
    }
    actionable = [row for row in queue if row["status"] in actionable_statuses]
    return {
        "schema_version": 1,
        "source_repo": generated.get("source_repo"),
        "source_commit": generated.get("source_commit"),
        "policy": {
            "status": "review_only",
            "rule": "This queue ranks review work. It is never injected into translation prompts and never locks terms automatically.",
            "priority_order": "unapplied explicit locks > conflicts > unresolved character identities > observed promotion candidates > untranslated skill/race/scenario/support entities.",
            "character_rule": "Known character names are handled by characters.json and must not be semantic-calqued into Vietnamese.",
            "decision_rule": "Explicit defer/ignore decisions are removed from actionable work; explicit lock decisions remain actionable until the canonical registry contains them.",
        },
        "summary": {
            "unique_candidate_sources": len(queue),
            "actionable": len(actionable),
            "generated_candidate_records": int(generated.get("total", len(candidates)) or 0),
            "observed_unique_terms": int(observed.get("observed_count", len(observed_map)) or 0),
            "observed_conflicts": int(observed.get("conflict_count", len(conflict_map)) or 0),
            "explicit_review_decisions": len(decisions),
            "status_counts": dict(sorted(status_counts.items())),
        },
        "review_queue": actionable,
        "all_candidates": queue,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build prioritized review queue for terminology candidates.")
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--observed", type=Path, default=DEFAULT_OBSERVED)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--characters", type=Path, default=DEFAULT_CHARACTERS)
    parser.add_argument("--reviews", type=Path, default=DEFAULT_REVIEWS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    generated = read_json(args.candidates, {}) or {}
    observed = read_json(args.observed, {}) or {}
    registry = read_json(args.registry, {}) or {}
    characters = read_json(args.characters, {}) or {}
    reviews = read_json(args.reviews, {}) or {}
    if not all(isinstance(value, dict) for value in (generated, observed, registry, characters, reviews)):
        raise SystemExit("all terminology review inputs must be JSON objects")

    queue = build_queue(generated, observed, registry, characters, reviews)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = queue["summary"]
    print(
        f"candidate_records={summary['generated_candidate_records']} "
        f"unique_sources={summary['unique_candidate_sources']} "
        f"actionable={summary['actionable']} "
        f"conflicts={summary['observed_conflicts']} "
        f"decisions={summary['explicit_review_decisions']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
