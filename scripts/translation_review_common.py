from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any

# Letters/ideographs only; do not classify JP punctuation such as U+30FB middle dot as leakage.
_CJK_RE = re.compile(r"[\u3041-\u3096\u30a1-\u30fa\u3400-\u4dbf\u4e00-\u9fff]")

# Only files that deterministically define the normal review policy belong in the
# global plan snapshot. Character/speech evidence is intentionally lazy and
# targeted per item; changing one profile must not invalidate 19k unrelated
# system/UI/skill review decisions.
CONTEXT_PATHS = (
    "TRANSLATION_REVIEW.md",
    "GAME_CONTEXT.md",
    "glossary/term_registry.json",
    "glossary/ui_community_terms.json",
    "glossary/skill_name_style.json",
    "glossary/style_rules.json",
)


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


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def text_fingerprint(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def context_snapshot_hash(repo_root: Path) -> str:
    digest = hashlib.sha256()
    for rel in CONTEXT_PATHS:
        digest.update(rel.encode("utf-8") + b"\0")
        path = repo_root / rel
        if path.exists():
            digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def get_json_path(document: Any, path: list[Any]) -> Any:
    node = document
    for segment in path:
        if isinstance(node, dict):
            node = node[str(segment)]
        elif isinstance(node, list):
            if not isinstance(segment, int):
                raise TypeError(f"list path segment must be int, got {segment!r}")
            node = node[segment]
        else:
            raise TypeError(f"cannot traverse through {type(node).__name__}")
    return node


def normalize(text: str) -> str:
    return " ".join(text.casefold().split())


def contains_any(text: str, values: list[str]) -> bool:
    normalized = normalize(text)
    return any(normalize(value) in normalized for value in values if value)


def _alias_matches(source: str, alias: str) -> bool:
    if not alias:
        return False
    if source == alias:
        return True
    return len(alias) >= 2 and alias in source


def load_locked_terms(repo_root: Path) -> list[dict[str, Any]]:
    payload = load_json(repo_root / "glossary/term_registry.json", {"terms": []})
    return [
        term for term in payload.get("terms", [])
        if isinstance(term, dict) and bool(term.get("locked")) and str(term.get("target_vi", "")).strip()
    ]


def locked_term_matches(source: str, target: str, terms: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for term in terms:
        aliases = [str(v) for v in term.get("zh_cn", []) if str(v)]
        matched_aliases = [alias for alias in aliases if _alias_matches(source, alias)]
        if not matched_aliases:
            continue
        expected = str(term["target_vi"])
        result.append({
            "id": str(term.get("id", "")),
            "target_vi": expected,
            "matched_aliases": matched_aliases,
            "present": contains_any(target, [expected]),
        })
    return result


def load_community_terms(repo_root: Path) -> list[dict[str, Any]]:
    payload = load_json(repo_root / "glossary/ui_community_terms.json", {"terms": []})
    return [term for term in payload.get("terms", []) if isinstance(term, dict)]


def community_term_matches(
    key: str | None,
    source: str,
    target: str,
    terms: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for term in terms:
        prefixes = [str(v) for v in term.get("key_prefixes", []) if str(v)]
        if prefixes and (key is None or not any(key.startswith(prefix) for prefix in prefixes)):
            continue
        aliases = [str(v) for v in term.get("source_aliases", []) if str(v)]
        matched_aliases = [alias for alias in aliases if _alias_matches(source, alias)]
        if not matched_aliases:
            continue
        accepted = list(dict.fromkeys(
            [str(v) for v in term.get("accepted", []) if str(v)]
            + [str(v) for v in term.get("compact", []) if str(v)]
        ))
        forbidden = [str(v) for v in term.get("forbidden", []) if str(v)]
        result.append({
            "id": str(term.get("id", "")),
            "preferred": str(term.get("preferred", "")),
            "accepted": accepted,
            "forbidden": forbidden,
            "matched_aliases": matched_aliases,
            "accepted_present": contains_any(target, accepted),
            "forbidden_present": contains_any(target, forbidden),
            "require_accepted": bool(term.get("require_accepted", True)),
            "basis": str(term.get("basis", "")),
        })
    return result


def suppress_overridden_locked_terms(
    locked_terms: list[dict[str, Any]],
    community_terms: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Apply documented precedence: player-facing community terms override older locked mappings.

    We only suppress a locked match when both layers matched at least one identical source alias,
    so unrelated concepts appearing in the same sentence remain independently enforced.
    """
    community_aliases = {
        str(alias)
        for term in community_terms
        for alias in term.get("matched_aliases", [])
        if str(alias)
    }
    if not community_aliases:
        return locked_terms
    return [
        term for term in locked_terms
        if community_aliases.isdisjoint({str(alias) for alias in term.get("matched_aliases", []) if str(alias)})
    ]


def load_skill_examples(repo_root: Path) -> dict[str, dict[str, Any]]:
    payload = load_json(repo_root / "glossary/skill_name_style.json", {"canonical_examples": []})
    result: dict[str, dict[str, Any]] = {}
    for item in payload.get("canonical_examples", []):
        if not isinstance(item, dict):
            continue
        source = str(item.get("source_zh_cn", "")).strip()
        target = str(item.get("target_vi", "")).strip()
        if source and target:
            result[source] = {
                "source_zh_cn": source,
                "target_vi": target,
                "ja": item.get("ja", []),
                "note": str(item.get("note", "")),
            }
    return result


def risk_metadata(
    source: str,
    target: str,
    locked_terms: list[dict[str, Any]],
    community_terms: list[dict[str, Any]],
    skill_example: dict[str, Any] | None,
) -> tuple[list[str], int]:
    flags: list[str] = []
    score = 0
    if source.strip() == target.strip():
        flags.append("source_equal_target")
        score += 10
    if _CJK_RE.search(target):
        flags.append("cjk_in_target")
        score += 8
    if source.strip() and target.strip():
        ratio = len(target) / max(1, len(source))
        if ratio > 3.0:
            flags.append("very_long_target")
            score += 3
        elif ratio < 0.25:
            flags.append("very_short_target")
            score += 3
    if any(not item["present"] for item in locked_terms):
        flags.append("locked_term_mismatch")
        score += 8
    if community_terms:
        flags.append("community_term")
        score += 2
    if any(item["forbidden_present"] for item in community_terms):
        flags.append("community_calque_risk")
        score += 8
    if any(item["require_accepted"] and item["accepted"] and not item["accepted_present"] for item in community_terms):
        flags.append("community_term_mismatch")
        score += 6
    if skill_example is not None and normalize(target) != normalize(str(skill_example["target_vi"])):
        flags.append("canonical_skill_name_mismatch")
        score += 10
    return flags, score
