from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def normalize(text: str) -> str:
    return " ".join(text.casefold().split())


def regression_id(uid: str, source: str) -> str:
    digest = hashlib.sha256(f"{uid}\0{source}".encode("utf-8")).hexdigest()[:16]
    return f"review.regression.{digest}"


def _batch_for_marker(
    repo_root: Path,
    review_name: str,
    marker: dict[str, Any],
) -> dict[str, Any] | None:
    plan_id = str(marker.get("plan_id", ""))
    batch_id = str(marker.get("batch_id", ""))
    if not plan_id or not batch_id:
        return None
    plan = load_json(repo_root / f"work/{review_name}/plans" / f"{plan_id}.json", {})
    if not isinstance(plan, dict):
        return None
    meta = next(
        (
            item
            for item in plan.get("batches", [])
            if isinstance(item, dict) and str(item.get("batch_id", "")) == batch_id
        ),
        None,
    )
    if meta is None:
        return None
    batch_path = str(meta.get("batch_path", ""))
    if not batch_path:
        return None
    batch = load_json(repo_root / batch_path, {})
    return batch if isinstance(batch, dict) else None


def _event_sort_key(event: dict[str, Any]) -> tuple[str, str, str, str, str]:
    return (
        str(event.get("merged_at", "")),
        str(event.get("origin", "")),
        str(event.get("plan_id", "")),
        str(event.get("batch_id", "")),
        str(event.get("claim_id", "")),
    )


def _collect_translation_events(repo_root: Path) -> tuple[list[dict[str, Any]], dict[str, int]]:
    review_root = repo_root / "work/translation_review"
    events: list[dict[str, Any]] = []
    stats = {"merged_markers": 0, "accepted_revisions": 0, "skipped_incomplete": 0}

    for marker_path in sorted((review_root / "merged").glob("*.json")):
        marker = load_json(marker_path, {})
        if not isinstance(marker, dict) or marker.get("status") != "merged":
            continue
        stats["merged_markers"] += 1
        batch_id = str(marker.get("batch_id", marker_path.stem))
        claim_id = str(marker.get("claim_id", ""))
        plan_id = str(marker.get("plan_id", ""))
        if not claim_id or not plan_id:
            stats["skipped_incomplete"] += 1
            continue

        batch = _batch_for_marker(repo_root, "translation_review", marker)
        result = load_json(review_root / "results" / batch_id / f"{claim_id}.json", {})
        if not isinstance(batch, dict) or not isinstance(result, dict):
            stats["skipped_incomplete"] += 1
            continue

        items = {
            str(item.get("uid", "")): item
            for item in batch.get("items", [])
            if isinstance(item, dict) and str(item.get("uid", ""))
        }
        decisions = {
            str(item.get("uid", "")): item
            for item in result.get("decisions", [])
            if isinstance(item, dict) and str(item.get("uid", ""))
        }
        auto_deferred = {
            str(item.get("uid", ""))
            for item in marker.get("auto_deferred", [])
            if isinstance(item, dict) and str(item.get("uid", ""))
        }

        for uid, decision in decisions.items():
            item = items.get(uid)
            if item is None or str(decision.get("action", "")) != "revise":
                continue
            if str(decision.get("confidence", "")) == "low" or uid in auto_deferred:
                continue
            old_text = item.get("current_text")
            new_text = decision.get("proposed_text")
            source = item.get("source_text")
            if not all(isinstance(value, str) and value.strip() for value in (old_text, new_text, source)):
                continue
            if normalize(old_text) == normalize(new_text):
                continue

            stats["accepted_revisions"] += 1
            events.append(
                {
                    "origin": "translation_review",
                    "uid": uid,
                    "source_text": source,
                    "source_fingerprint": item.get("source_fingerprint"),
                    "rejected_target": old_text,
                    "approved_target": new_text,
                    "merged_at": str(marker.get("merged_at", "")),
                    "plan_id": plan_id,
                    "batch_id": batch_id,
                    "claim_id": claim_id,
                    "reason": str(decision.get("reason", "")),
                }
            )
    return events, stats


def _collect_ui_events(repo_root: Path) -> tuple[list[dict[str, Any]], dict[str, int]]:
    review_root = repo_root / "work/ui_review"
    events: list[dict[str, Any]] = []
    stats = {"merged_markers": 0, "accepted_revisions": 0, "skipped_incomplete": 0}

    for marker_path in sorted((review_root / "merged").glob("*.json")):
        marker = load_json(marker_path, {})
        if not isinstance(marker, dict) or marker.get("status") != "merged":
            continue
        stats["merged_markers"] += 1
        batch_id = str(marker.get("batch_id", marker_path.stem))
        claim_id = str(marker.get("claim_id", ""))
        plan_id = str(marker.get("plan_id", ""))
        if not claim_id or not plan_id:
            stats["skipped_incomplete"] += 1
            continue

        batch = _batch_for_marker(repo_root, "ui_review", marker)
        result = load_json(review_root / "results" / batch_id / f"{claim_id}.json", {})
        if not isinstance(batch, dict) or not isinstance(result, dict):
            stats["skipped_incomplete"] += 1
            continue

        items = {
            str(item.get("key", "")): item
            for item in batch.get("items", [])
            if isinstance(item, dict) and str(item.get("key", ""))
        }
        decisions = {
            str(item.get("key", "")): item
            for item in result.get("decisions", [])
            if isinstance(item, dict) and str(item.get("key", ""))
        }

        for ui_key, decision in decisions.items():
            item = items.get(ui_key)
            if item is None or str(decision.get("action", "")) != "revise":
                continue
            # A merged UI revision has already passed merge_ui_review validation;
            # low-confidence revisions are rejected there and therefore must never
            # be promoted merely because an old result file exists.
            if str(decision.get("confidence", "")) == "low":
                continue
            uid = str(item.get("uid", ""))
            old_text = item.get("current_text")
            new_text = decision.get("proposed_text")
            source = item.get("source_text")
            if not uid:
                # Hard regression matching is identity-first. Do not turn an
                # incomplete UI record into a dangerous source-global rule.
                continue
            if not all(isinstance(value, str) and value.strip() for value in (old_text, new_text, source)):
                continue
            if normalize(old_text) == normalize(new_text):
                continue

            stats["accepted_revisions"] += 1
            events.append(
                {
                    "origin": "ui_review",
                    "uid": uid,
                    "source_text": source,
                    "source_fingerprint": item.get("source_fingerprint"),
                    "rejected_target": old_text,
                    "approved_target": new_text,
                    "merged_at": str(marker.get("merged_at", "")),
                    "plan_id": plan_id,
                    "batch_id": batch_id,
                    "claim_id": claim_id,
                    "reason": str(decision.get("reason", "")),
                    "ui_key": ui_key,
                    "control_type": str(decision.get("control_type", "unknown")),
                    "risk_flags": [str(value) for value in item.get("risk_flags", []) if str(value)],
                }
            )
    return events, stats


def build(repo_root: Path) -> dict[str, Any]:
    translation_events, translation_stats = _collect_translation_events(repo_root)
    ui_events, ui_stats = _collect_ui_events(repo_root)
    events = sorted(translation_events + ui_events, key=_event_sort_key)

    records: dict[tuple[str, str], dict[str, Any]] = {}
    for event in events:
        uid = str(event["uid"])
        source = str(event["source_text"])
        key = (uid, source)
        record = records.setdefault(
            key,
            {
                "id": regression_id(uid, source),
                "uid": uid,
                "scope": "uid",
                "source_text": source,
                "source_fingerprint": event.get("source_fingerprint"),
                "rejected_targets": [],
                "approved_target": str(event["approved_target"]),
                "origins": [],
                "ui_contexts": [],
                "evidence": [],
            },
        )
        rejected = record["rejected_targets"]
        old_text = str(event["rejected_target"])
        if old_text not in rejected:
            rejected.append(old_text)
        record["approved_target"] = str(event["approved_target"])
        if event["origin"] not in record["origins"]:
            record["origins"].append(event["origin"])

        if event["origin"] == "ui_review":
            ui_context = {
                "key": str(event.get("ui_key", "")),
                "control_type": str(event.get("control_type", "unknown")),
                "risk_flags": list(event.get("risk_flags", [])),
            }
            if ui_context not in record["ui_contexts"]:
                record["ui_contexts"].append(ui_context)

        evidence = {
            "origin": str(event["origin"]),
            "plan_id": str(event["plan_id"]),
            "batch_id": str(event["batch_id"]),
            "claim_id": str(event["claim_id"]),
            "merged_at": str(event.get("merged_at", "")),
            "reason": str(event.get("reason", "")),
        }
        if event["origin"] == "ui_review":
            evidence["ui_key"] = str(event.get("ui_key", ""))
            evidence["control_type"] = str(event.get("control_type", "unknown"))
        if evidence not in record["evidence"]:
            record["evidence"].append(evidence)

    entries = list(records.values())
    for entry in entries:
        # If a later accepted review intentionally returns to wording rejected by
        # an older review, the latest accepted state wins and must not hard-block
        # itself. All other historical bad forms remain regression targets.
        approved_norm = normalize(str(entry["approved_target"]))
        entry["rejected_targets"] = sorted(
            [value for value in entry["rejected_targets"] if normalize(value) != approved_norm],
            key=lambda value: (normalize(value), value),
        )
        entry["origins"] = sorted(entry["origins"])
        entry["ui_contexts"] = sorted(
            entry["ui_contexts"],
            key=lambda item: (item["key"], item["control_type"], tuple(item["risk_flags"])),
        )
        entry["evidence"] = sorted(
            entry["evidence"],
            key=lambda item: (
                item.get("merged_at", ""),
                item["origin"],
                item["plan_id"],
                item["batch_id"],
                item["claim_id"],
            ),
        )
    entries.sort(key=lambda item: (item["uid"], item["source_text"], item["id"]))

    total_markers = translation_stats["merged_markers"] + ui_stats["merged_markers"]
    total_revisions = translation_stats["accepted_revisions"] + ui_stats["accepted_revisions"]
    total_skipped = translation_stats["skipped_incomplete"] + ui_stats["skipped_incomplete"]
    payload = {
        "schema_version": 2,
        "policy_version": 2,
        "purpose": "Unified regression memory mined from accepted retrospective translation and UI revise decisions. Future translation must not reproduce a rejected target for the same source identity, including known-bad UI wording/layout choices.",
        "policy": {
            "hard_block": "Exact rejected target text is a merge-blocking regression for the same uid and source text.",
            "approved_target": "The latest reviewed replacement is prompt guidance, not an immutable global wording rule; higher-priority canonical/context rules may supersede it.",
            "ui_memory": "Accepted UI revisions preserve UI key/control/risk evidence so future workers can avoid wording that was semantically valid but rejected for player-facing layout or control constraints.",
            "growth": "Every accepted retrospective translation revise and accepted UI revise is folded into this file automatically by both review merge workflows.",
        },
        "summary": {
            "merged_markers_scanned": total_markers,
            "translation_merged_markers_scanned": translation_stats["merged_markers"],
            "ui_merged_markers_scanned": ui_stats["merged_markers"],
            "accepted_revision_events": total_revisions,
            "accepted_translation_revision_events": translation_stats["accepted_revisions"],
            "accepted_ui_revision_events": ui_stats["accepted_revisions"],
            "regression_identity_count": len(entries),
            "skipped_incomplete_markers": total_skipped,
            "translation_skipped_incomplete_markers": translation_stats["skipped_incomplete"],
            "ui_skipped_incomplete_markers": ui_stats["skipped_incomplete"],
        },
        "entries": entries,
    }
    write_json(repo_root / "glossary/translation_regressions.generated.json", payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build future-translation regression memory from accepted translation and UI review revisions."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()
    payload = build(args.repo_root.resolve())
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
