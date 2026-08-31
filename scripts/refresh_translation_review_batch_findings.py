from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

try:
    from scripts.translation_review_common import (
        canonical_finding_matches,
        item_scoped_context_hash,
        load_canonical_findings,
        load_community_terms,
        load_json,
        load_locked_terms,
        write_json,
    )
except ModuleNotFoundError:
    from translation_review_common import (  # type: ignore[no-redef]
        canonical_finding_matches,
        item_scoped_context_hash,
        load_canonical_findings,
        load_community_terms,
        load_json,
        load_locked_terms,
        write_json,
    )

ROOT = Path(__file__).resolve().parents[1]


def refresh_active_batches(repo_root: Path = ROOT) -> dict[str, Any]:
    review_root = repo_root / "work" / "translation_review"
    active = load_json(review_root / "active_plan.json", {}) or {}
    if active.get("status") != "active" or not active.get("plan_path"):
        return {"changed": False, "updated_batches": 0, "updated_items": 0}

    plan = load_json(repo_root / str(active["plan_path"]), {}) or {}
    findings = load_canonical_findings(repo_root)
    locked_terms = load_locked_terms(repo_root)
    community_terms = load_community_terms(repo_root)
    updated_batches = 0
    updated_items = 0

    for meta in plan.get("batches", []):
        if not isinstance(meta, dict) or not meta.get("batch_id") or not meta.get("batch_path"):
            continue
        batch_id = str(meta["batch_id"])
        if (review_root / "merged" / f"{batch_id}.json").exists():
            continue
        batch_path = repo_root / str(meta["batch_path"])
        batch = load_json(batch_path, {}) or {}
        batch_changed = False
        for item in batch.get("items", []):
            if not isinstance(item, dict):
                continue
            matches = canonical_finding_matches(
                item.get("key"),
                str(item.get("source_text", "")),
                findings,
                source_path=item.get("source_path"),
                json_path=item.get("json_path"),
            )
            old_matches = item.get("canonical_findings", [])
            new_context_hash = item_scoped_context_hash(
                key=item.get("key"),
                source=str(item.get("source_text", "")),
                source_path=item.get("source_path"),
                json_path=item.get("json_path"),
                locked_terms=locked_terms,
                community_terms=community_terms,
                canonical_findings=matches,
            )
            if old_matches != matches or item.get("item_context_sha256") != new_context_hash:
                item["canonical_findings"] = matches
                item["item_context_sha256"] = new_context_hash
                batch_changed = True
                updated_items += 1
        if batch_changed:
            write_json(batch_path, batch)
            updated_batches += 1

    return {
        "changed": bool(updated_batches),
        "updated_batches": updated_batches,
        "updated_items": updated_items,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Refresh live canonical-finding snapshots in unresolved translation-review batches.")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()
    print(refresh_active_batches(args.repo_root))


if __name__ == "__main__":
    main()
