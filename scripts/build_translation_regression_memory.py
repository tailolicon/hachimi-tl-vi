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


def _batch_for_marker(repo_root: Path, marker: dict[str, Any]) -> dict[str, Any] | None:
    plan_id = str(marker.get("plan_id", ""))
    batch_id = str(marker.get("batch_id", ""))
    if not plan_id or not batch_id:
        return None
    plan = load_json(repo_root / "work/translation_review/plans" / f"{plan_id}.json", {})
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


def build(repo_root: Path) -> dict[str, Any]:
    review_root = repo_root / "work/translation_review"
    records: dict[tuple[str, str], dict[str, Any]] = {}
    scanned_markers = 0
    accepted_revisions = 0
    skipped_incomplete = 0

    for marker_path in sorted((review_root / "merged").glob("*.json")):
        marker = load_json(marker_path, {})
        if not isinstance(marker, dict) or marker.get("status") != "merged":
            continue
        scanned_markers += 1
        batch_id = str(marker.get("batch_id", marker_path.stem))
        claim_id = str(marker.get("claim_id", ""))
        plan_id = str(marker.get("plan_id", ""))
        if not claim_id or not plan_id:
            skipped_incomplete += 1
            continue

        batch = _batch_for_marker(repo_root, marker)
        result = load_json(
            review_root / "results" / batch_id / f"{claim_id}.json",
            {},
        )
        if not isinstance(batch, dict) or not isinstance(result, dict):
            skipped_incomplete += 1
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
            if item is None:
                continue
            if str(decision.get("action", "")) != "revise":
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

            accepted_revisions += 1
            key = (uid, source)
            record = records.setdefault(
                key,
                {
                    "id": regression_id(uid, source),
                    "uid": uid,
                    "scope": "uid",
                    "source_text": source,
                    "source_fingerprint": item.get("source_fingerprint"),
                    "rejected_targets": [],
                    "approved_target": new_text,
                    "evidence": [],
                },
            )
            rejected = record["rejected_targets"]
            if old_text not in rejected:
                rejected.append(old_text)
            # Markers are processed in filename order. The latest accepted review
            # encountered for an identity becomes the current approved reference;
            # every older form remains in rejected_targets.
            record["approved_target"] = new_text
            evidence = {
                "plan_id": plan_id,
                "batch_id": batch_id,
                "claim_id": claim_id,
                "reason": str(decision.get("reason", "")),
            }
            if evidence not in record["evidence"]:
                record["evidence"].append(evidence)

    entries = list(records.values())
    for entry in entries:
        entry["rejected_targets"] = sorted(entry["rejected_targets"], key=lambda value: (normalize(value), value))
        entry["evidence"] = sorted(
            entry["evidence"],
            key=lambda item: (item["plan_id"], item["batch_id"], item["claim_id"]),
        )
    entries.sort(key=lambda item: (item["uid"], item["source_text"], item["id"]))

    payload = {
        "schema_version": 1,
        "policy_version": 1,
        "purpose": "Regression memory mined from accepted retrospective revise decisions. Future translation must not reproduce a rejected target for the same source identity.",
        "policy": {
            "hard_block": "Exact rejected target text is a merge-blocking regression for the same uid and source text.",
            "approved_target": "Reviewed replacement is prompt guidance, not an immutable global wording rule; higher-priority canonical/context rules may supersede it.",
            "growth": "Every accepted retrospective revise decision is folded into this file automatically by the merge-review workflow.",
        },
        "summary": {
            "merged_markers_scanned": scanned_markers,
            "accepted_revision_events": accepted_revisions,
            "regression_identity_count": len(entries),
            "skipped_incomplete_markers": skipped_incomplete,
        },
        "entries": entries,
    }
    write_json(repo_root / "glossary/translation_regressions.generated.json", payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Build future-translation regression memory from accepted review revisions.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()
    payload = build(args.repo_root.resolve())
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
