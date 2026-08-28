from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS_ROOT = ROOT / "work/curation/results"
DEFAULT_REGISTRY = ROOT / "glossary/term_registry.json"
DEFAULT_SKILL_STYLE = ROOT / "glossary/skill_name_style.json"
DEFAULT_OUTPUT = ROOT / "glossary/source_bridge_risks.generated.json"

# Intentionally conservative. These patterns promote evidence where the curation
# note explicitly identifies semantic/image/voice loss or a source form that is
# unsafe to canonicalize without JP. Plain script conversion (e.g. katakana ->
# equivalent English spelling) is not enough on its own.
_STRONG_RISK_PATTERNS = (
    re.compile(r"\bzh-cn\b.*\bnot (?:a )?literal title match\b", re.I),
    re.compile(r"\bzh-cn\b.*\bnot title-equivalent\b", re.I),
    re.compile(r"\bzh-cn\b.*\b(?:changes?|reframes?|reshapes?|omits?|flattens?)\b", re.I),
    re.compile(r"\bzh-cn\b.*\breplaces?\b.*\b(?:image|meaning|nuance|wording|reference|gimmick|proper[- ]?name|styl(?:e|ization))\b", re.I),
    re.compile(r"\bzh-cn\b.*\b(?:interpretive|lossy)\b", re.I),
    re.compile(r"\bchinese bridge\b.*\b(?:interpretive|lossy|reshape|changes?|reframes?|omits?|flattens?)\b", re.I),
    re.compile(r"\bchinese bridge\b.*\bsemantically replaces?\b", re.I),
    re.compile(r"\binterpretive chinese rendering\b", re.I),
    re.compile(r"\bsource (?:shifts|reframes|changes|reshapes|omits|flattens)\b", re.I),
    re.compile(r"\bsource replaces?\b.*\b(?:image|meaning|nuance|wording|reference|gimmick|proper[- ]?name|styl(?:e|ization))\b", re.I),
    re.compile(r"\bnot title-equivalent\b", re.I),
    re.compile(r"\bdo not canonize a chinese-derived\b", re.I),
    re.compile(r"\bliteral vietnamese rendering would risk\b", re.I),
)


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    return []


def canonical_zh_sources(registry: dict[str, Any], skill_style: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for term in registry.get("terms", []):
        if not isinstance(term, dict) or not term.get("locked"):
            continue
        if not str(term.get("target_vi", "")).strip():
            continue
        result.update(value.strip() for value in _strings(term.get("zh_cn")) if value.strip())
    for item in skill_style.get("canonical_examples", []):
        if not isinstance(item, dict) or not str(item.get("target_vi", "")).strip():
            continue
        source = str(item.get("source_zh_cn", "")).strip()
        if source:
            result.add(source)
    return result


def is_confirmed_lossy_note(note: str) -> bool:
    return any(pattern.search(note) for pattern in _STRONG_RISK_PATTERNS)


def build_registry(
    results_root: Path,
    registry: dict[str, Any],
    skill_style: dict[str, Any],
) -> dict[str, Any]:
    canonical = canonical_zh_sources(registry, skill_style)
    grouped: dict[str, list[dict[str, str]]] = {}
    scanned_decisions = 0
    deferred_decisions = 0
    strong_evidence_decisions = 0
    skipped_canonical = 0

    if results_root.exists():
        for path in sorted(results_root.glob("term-*/*.json")):
            payload = read_json(path, {})
            if not isinstance(payload, dict):
                continue
            batch_id = str(payload.get("batch_id", ""))
            claim_id = str(payload.get("claim_id", ""))
            decisions = payload.get("decisions", [])
            if not isinstance(decisions, list):
                continue
            for decision in decisions:
                if not isinstance(decision, dict):
                    continue
                scanned_decisions += 1
                if str(decision.get("action", "")).strip().lower() != "defer":
                    continue
                deferred_decisions += 1
                source = str(decision.get("source_zh_cn", "")).strip()
                note = str(decision.get("note", "")).strip()
                if not source or not note or not is_confirmed_lossy_note(note):
                    continue
                strong_evidence_decisions += 1
                if source in canonical:
                    skipped_canonical += 1
                    continue
                rel = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()
                evidence = {
                    "path": rel,
                    "batch_id": batch_id,
                    "claim_id": claim_id,
                    "note": note,
                }
                rows = grouped.setdefault(source, [])
                if evidence not in rows:
                    rows.append(evidence)

    untrusted: list[dict[str, Any]] = []
    for source in sorted(grouped):
        digest = hashlib.sha256(source.encode("utf-8")).hexdigest()[:16]
        evidence = sorted(grouped[source], key=lambda row: (row["path"], row["claim_id"], row["note"]))
        untrusted.append({
            "id": f"curation.bridge.{digest}",
            "zh_cn_exact": [source],
            "mode": "defer_until_canonical",
            "evidence": evidence,
            "note": (
                "Curation evidence flags this zh-CN source as semantically lossy/interpretive or unsafe to "
                "canonicalize without JP-backed evidence. Do not preserve a literal zh-CN-derived Vietnamese "
                "title; use canonical JP-backed evidence or defer."
            ),
        })

    return {
        "schema_version": 1,
        "classification_version": 2,
        "generated_from": "work/curation/results/term-*/*.json",
        "policy": {
            "scope": "Strong zh-CN bridge-risk evidence only; script-only conversions are excluded.",
            "promotion_rule": (
                "Promote deferred curation decisions only when notes identify semantic/image/voice loss, "
                "non-equivalent/interpretive bridge wording, Chinese-derived proper-name/wordplay risk, or an "
                "explicit need for JP evidence. Equivalent script conversion alone is not promoted."
            ),
            "canonical_exclusion": (
                "Sources already covered by a locked term_registry target or exact skill_name_style canonical example "
                "are excluded because their canonical Vietnamese rendering is already enforceable elsewhere."
            ),
        },
        "summary": {
            "scanned_decisions": scanned_decisions,
            "deferred_decisions": deferred_decisions,
            "strong_evidence_decisions": strong_evidence_decisions,
            "skipped_already_canonical": skipped_canonical,
            "untrusted_source_count": len(untrusted),
        },
        "untrusted_sources": untrusted,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build item-scoped zh-CN source-bridge risk registry from curation evidence.")
    parser.add_argument("--results-root", type=Path, default=DEFAULT_RESULTS_ROOT)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--skill-style", type=Path, default=DEFAULT_SKILL_STYLE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    registry = read_json(args.registry, {}) or {}
    skill_style = read_json(args.skill_style, {}) or {}
    if not isinstance(registry, dict) or not isinstance(skill_style, dict):
        raise SystemExit("registry and skill-style inputs must be JSON objects")

    output = build_registry(args.results_root, registry, skill_style)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = output["summary"]
    print(
        f"scanned={summary['scanned_decisions']} deferred={summary['deferred_decisions']} "
        f"strong={summary['strong_evidence_decisions']} canonical_skip={summary['skipped_already_canonical']} "
        f"untrusted={summary['untrusted_source_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
