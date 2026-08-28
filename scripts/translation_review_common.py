from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any

# Letters/ideographs only; do not classify JP punctuation such as U+30FB middle dot as leakage.
_CJK_RE = re.compile(r"[\u3041-\u3096\u30a1-\u30fa\u3400-\u4dbf\u4e00-\u9fff]")
_NUMBER_RE = re.compile(r"(?<![\w{])\d+(?:\.\d+)?%?")

# Only files that deterministically define the normal review policy belong in the
# global plan snapshot. Character/speech evidence is intentionally lazy and
# targeted per item; changing one profile must not invalidate 19k unrelated
# system/UI/skill review decisions.
#
# Source-bridge files are deliberately NOT included here. They are versioned by
# source_bridge_policy_hash() and applied item-by-item so a new bridge safeguard
# reopens only entries that actually match it instead of invalidating all 19k.
CONTEXT_PATHS = (
    "TRANSLATION_REVIEW.md",
    "GAME_CONTEXT.md",
    "glossary/term_registry.json",
    "glossary/ui_community_terms.json",
    "glossary/skill_name_style.json",
    "glossary/style_rules.json",
)
SOURCE_BRIDGE_PATH = "glossary/source_bridge_terms.json"
SOURCE_BRIDGE_GENERATED_PATH = "glossary/source_bridge_risks.generated.json"
SOURCE_BRIDGE_PATHS = (SOURCE_BRIDGE_PATH, SOURCE_BRIDGE_GENERATED_PATH)


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


def source_bridge_policy_hash(repo_root: Path) -> str:
    """Hash only effective bridge enforcement, not generated audit bookkeeping.

    The generated registry's summary/evidence can grow when curation workers add
    duplicate or unrelated notes. Those changes should not invalidate active
    review plans. A hash change is reserved for an actual manual rule change or
    for adding/removing/changing an automatically enforced untrusted source.
    """
    manual = load_json(repo_root / SOURCE_BRIDGE_PATH, {}) or {}
    generated = load_json(repo_root / SOURCE_BRIDGE_GENERATED_PATH, {}) or {}
    if not isinstance(manual, dict):
        manual = {}
    if not isinstance(generated, dict):
        generated = {}

    generated_untrusted: list[dict[str, Any]] = []
    for risk in generated.get("untrusted_sources", []):
        if not isinstance(risk, dict):
            continue
        aliases = sorted(str(value).strip() for value in risk.get("zh_cn_exact", []) if str(value).strip())
        if not aliases:
            continue
        generated_untrusted.append({
            "id": str(risk.get("id", "")),
            "zh_cn_exact": aliases,
            "mode": str(risk.get("mode", "defer_until_canonical")),
        })
    generated_untrusted.sort(key=lambda item: (tuple(item["zh_cn_exact"]), item["id"], item["mode"]))

    semantic = {
        "manual_terms": [item for item in manual.get("terms", []) if isinstance(item, dict)],
        "manual_untrusted_sources": [
            item for item in manual.get("untrusted_sources", []) if isinstance(item, dict)
        ],
        "generated_untrusted_sources": generated_untrusted,
    }
    encoded = json.dumps(
        semantic,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


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


def load_source_bridge_config(repo_root: Path) -> dict[str, Any]:
    manual = load_json(repo_root / SOURCE_BRIDGE_PATH, {"terms": [], "untrusted_sources": []})
    generated = load_json(repo_root / SOURCE_BRIDGE_GENERATED_PATH, {"untrusted_sources": []})
    if not isinstance(manual, dict):
        manual = {"terms": [], "untrusted_sources": []}
    if not isinstance(generated, dict):
        generated = {"untrusted_sources": []}

    untrusted: list[dict[str, Any]] = []
    seen_alias_sets: set[tuple[str, ...]] = set()
    for payload in (manual, generated):
        for risk in payload.get("untrusted_sources", []):
            if not isinstance(risk, dict):
                continue
            aliases = tuple(sorted(str(v).strip() for v in risk.get("zh_cn_exact", []) if str(v).strip()))
            if not aliases or aliases in seen_alias_sets:
                continue
            seen_alias_sets.add(aliases)
            untrusted.append(risk)

    return {
        "schema_version": manual.get("schema_version", 1),
        "policy": manual.get("policy", {}),
        "terms": [item for item in manual.get("terms", []) if isinstance(item, dict)],
        "untrusted_sources": untrusted,
        "generated_summary": generated.get("summary", {}),
    }


def source_bridge_term_matches(
    source: str,
    target: str,
    terms: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for term in terms:
        if not isinstance(term, dict):
            continue
        aliases = [str(v) for v in term.get("zh_cn", []) if str(v)]
        matched_aliases = [alias for alias in aliases if _alias_matches(source, alias)]
        if not matched_aliases:
            continue
        accepted = [str(v) for v in term.get("accepted", []) if str(v)]
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
            "ja": [str(v) for v in term.get("ja", []) if str(v)],
            "note": str(term.get("note", "")),
        })
    return result


def source_bridge_risk_matches(source: str, risks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    stripped = source.strip()
    result: list[dict[str, Any]] = []
    for risk in risks:
        if not isinstance(risk, dict):
            continue
        aliases = [str(v).strip() for v in risk.get("zh_cn_exact", []) if str(v).strip()]
        matched_aliases = [alias for alias in aliases if stripped == alias]
        if not matched_aliases:
            continue
        result.append({
            "id": str(risk.get("id", "")),
            "matched_aliases": matched_aliases,
            "ja": [str(v) for v in risk.get("ja", []) if str(v)],
            "mode": str(risk.get("mode", "defer_until_canonical")),
            "note": str(risk.get("note", "")),
            "evidence": [item for item in risk.get("evidence", []) if isinstance(item, dict)],
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


def semantic_guard_flags(source: str, target: str) -> list[str]:
    """Conservative semantic tripwires that only prioritize review; they never auto-rewrite text."""
    flags: list[str] = []
    source_numbers = Counter(_NUMBER_RE.findall(source))
    target_numbers = Counter(_NUMBER_RE.findall(target))
    if source_numbers != target_numbers:
        flags.append("numeric_token_mismatch")

    normalized_target = normalize(target)
    semantic_pairs = (
        (("不能", "无法", "不可", "不可以"), ("không thể", "không được"), "negation_capability_risk"),
        (("还未", "尚未", "未"), ("chưa",), "not_yet_risk"),
        (("没有", "无"), ("không có", "không còn"), "absence_risk"),
        (("以上",), ("trở lên", "ít nhất", "từ"), "lower_bound_risk"),
        (("以下",), ("trở xuống", "không quá", "tối đa"), "upper_bound_risk"),
        (("以内",), ("trong vòng", "không quá", "tối đa"), "within_limit_risk"),
        (("超过",), ("vượt", "hơn"), "exceeds_risk"),
        (("增加", "提升", "提高"), ("tăng",), "increase_direction_risk"),
        (("减少", "降低", "下降"), ("giảm",), "decrease_direction_risk"),
    )
    for source_markers, target_markers, flag in semantic_pairs:
        if any(marker in source for marker in source_markers) and not any(marker in normalized_target for marker in target_markers):
            flags.append(flag)
    return flags


def risk_metadata(
    source: str,
    target: str,
    locked_terms: list[dict[str, Any]],
    community_terms: list[dict[str, Any]],
    skill_example: dict[str, Any] | None,
    source_bridge_terms: list[dict[str, Any]] | None = None,
    source_bridge_risks: list[dict[str, Any]] | None = None,
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

    bridge_terms = source_bridge_terms or []
    bridge_risks = source_bridge_risks or []
    if bridge_terms:
        flags.append("source_bridge_term")
        score += 3
    if any(item.get("forbidden_present") for item in bridge_terms):
        flags.append("source_bridge_calque_risk")
        score += 12
    if any(item.get("require_accepted", True) and item.get("accepted") and not item.get("accepted_present") for item in bridge_terms):
        flags.append("source_bridge_term_mismatch")
        score += 10
    if bridge_risks:
        flags.append("source_bridge_untrusted")
        score += 14

    semantic_flags = semantic_guard_flags(source, target)
    flags.extend(flag for flag in semantic_flags if flag not in flags)
    score += 5 * len(semantic_flags)
    return flags, score
