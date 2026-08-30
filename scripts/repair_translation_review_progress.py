from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
MARKER = ROOT / "work/translation_review/context_hash_semantics_v2.json"


def _replace_once(path: Path, old: str, new: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return False
    if old not in text:
        raise RuntimeError(f"expected migration anchor missing in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")
    return True


def migrate(repo_root: Path = ROOT) -> dict[str, object]:
    common = repo_root / "scripts/translation_review_common.py"
    source_changed = False

    source_changed |= _replace_once(
        common,
        '''CONTEXT_PATHS = (
    "TRANSLATION_REVIEW.md",
    "GAME_CONTEXT.md",
    "glossary/term_registry.json",
    "glossary/ui_community_terms.json",
    "glossary/translation_audit_policy.json",
    "glossary/skill_name_style.json",
    "glossary/style_rules.json",
)''',
        '''CONTEXT_PATHS = (
    "GAME_CONTEXT.md",
    "glossary/translation_audit_policy.json",
    "glossary/skill_name_style.json",
    "glossary/style_rules.json",
)''',
    )

    source_changed |= _replace_once(
        common,
        '''def item_scoped_policy_hash(repo_root: Path) -> str:
    semantic: dict[str, list[dict[str, Any]]] = {}
    for rel in ("glossary/term_registry.json", "glossary/ui_community_terms.json"):
        payload = load_json(repo_root / rel, {}) or {}
        terms = payload.get("terms", []) if isinstance(payload, dict) else []
        semantic[rel] = sorted(
            [
                term for term in terms
                if isinstance(term, dict) and str(term.get("invalidation_scope", "")) == "item"
            ],
            key=lambda term: str(term.get("id", "")),
        )
    finding_payload = load_json(repo_root / CANONICAL_FINDINGS_PATH, {}) or {}
    semantic[CANONICAL_FINDINGS_PATH] = sorted(
        [finding_semantic_view(finding) for finding in active_findings(finding_payload)],
        key=lambda finding: str(finding.get("finding_id", "")),
    )
    encoded = json.dumps(semantic, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
''',
        '''def item_scoped_policy_hash(repo_root: Path) -> str:
    """Hash terminology policy that can reopen only matching review items.

    Canonical findings are intentionally excluded from plan identity: the merger
    applies active findings dynamically item-by-item. Evidence growth or a newly
    reported finding therefore cannot churn the entire active plan.
    """
    semantic: dict[str, list[dict[str, Any]]] = {}
    for rel in ("glossary/term_registry.json", "glossary/ui_community_terms.json"):
        payload = load_json(repo_root / rel, {}) or {}
        terms = payload.get("terms", []) if isinstance(payload, dict) else []
        semantic[rel] = sorted(
            [term for term in terms if isinstance(term, dict)],
            key=lambda term: str(term.get("id", "")),
        )
    encoded = json.dumps(semantic, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
''',
    )

    source_changed |= _replace_once(
        common,
        '''        for term in terms:
            if str(term.get("invalidation_scope", "")) != "item":
                continue
            if not _context_matches(term, key=key, source_path=source_path, json_path=json_path):''',
        '''        for term in terms:
            if not _context_matches(term, key=key, source_path=source_path, json_path=json_path):''',
    )

    # Import after source migration so the hash is calculated with v2 semantics.
    from scripts.translation_review_common import context_snapshot_hash, load_json, write_json

    current_hash = context_snapshot_hash(repo_root)
    reviewed_path = repo_root / "work/translation_review/reviewed_index.json"
    reviewed = load_json(
        reviewed_path,
        {"schema_version": 1, "policy_version": 3, "entries": {}},
    )
    entries = reviewed.setdefault("entries", {})
    migrated = 0

    if not MARKER.exists():
        for row in entries.values():
            if not isinstance(row, dict):
                continue
            if int(row.get("policy_version", 0)) != 3:
                continue
            if str(row.get("action", "")) not in {"keep", "revise"}:
                continue
            row["context_snapshot_sha256"] = current_hash
            migrated += 1
        write_json(reviewed_path, reviewed)
        write_json(MARKER, {
            "schema_version": 1,
            "migration": "global-context-v2-item-effective-terminology",
            "context_snapshot_sha256": current_hash,
            "migrated_resolved_entries": migrated,
        })

    result = {
        "source_changed": source_changed,
        "context_snapshot_sha256": current_hash,
        "migrated_resolved_entries": migrated,
        "marker_exists": MARKER.exists(),
    }
    print(result)
    return result


if __name__ == "__main__":
    migrate()
