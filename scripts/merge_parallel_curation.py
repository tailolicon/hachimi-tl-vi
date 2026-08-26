from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ACTIVE = ROOT / "work/curation/active_plan.json"
DEFAULT_SPEECH_BIBLE = ROOT / "glossary/speech_bible.json"
DEFAULT_TERM_REVIEWS = ROOT / "glossary/terminology_reviews.json"
WORK_ROOT = ROOT / "work/curation"
ALLOWED_TERM_ACTIONS = {"lock", "defer", "ignore"}


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_active_plan(active_path: Path) -> tuple[dict[str, Any], dict[str, Any], Path]:
    active = read_json(active_path, {}) or {}
    if not isinstance(active, dict):
        raise ValueError("active curation plan must be an object")
    plan_id = str(active.get("plan_id") or "").strip()
    rel = str(active.get("plan_path") or "").strip()
    if not plan_id or not rel:
        raise ValueError("active curation plan is missing plan_id/plan_path")
    plan_path = ROOT / rel
    plan = read_json(plan_path, {}) or {}
    if not isinstance(plan, dict) or plan.get("plan_id") != plan_id:
        raise ValueError("active curation plan pointer does not match plan contents")
    return active, plan, plan_path


def batch_index(plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for field in ("speech_batches", "terminology_batches"):
        for batch in plan.get(field, []):
            if not isinstance(batch, dict):
                continue
            batch_id = str(batch.get("batch_id") or "").strip()
            if not batch_id:
                continue
            if batch_id in index:
                raise ValueError(f"duplicate batch_id in plan: {batch_id}")
            index[batch_id] = batch
    return index


def clean_string_list(value: Any, *, max_items: int = 16, max_len: int = 500) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        raise ValueError("expected string or array of strings")
    out: list[str] = []
    for item in value:
        text = str(item).strip()
        if not text:
            continue
        if len(text) > max_len:
            raise ValueError("curation field is too long; store compact guidance, not copied prose")
        if text not in out:
            out.append(text)
        if len(out) > max_items:
            raise ValueError("too many items in compact curation field")
    return out


def validate_envelope(
    result: dict[str, Any],
    completion: dict[str, Any],
    claim: dict[str, Any],
    *,
    plan_id: str,
    batch_id: str,
) -> str:
    claim_id = str(completion.get("claim_id") or "").strip()
    if not claim_id:
        raise ValueError(f"{batch_id}: completion is missing claim_id")
    for label, doc in (("completion", completion), ("claim", claim), ("result", result)):
        if str(doc.get("plan_id") or "") != plan_id:
            raise ValueError(f"{batch_id}: {label} plan_id does not match active plan")
        if str(doc.get("batch_id") or "") != batch_id:
            raise ValueError(f"{batch_id}: {label} batch_id mismatch")
        if str(doc.get("claim_id") or "") != claim_id:
            raise ValueError(f"{batch_id}: {label} claim_id mismatch")
    return claim_id


def merge_speech_batch(
    batch: dict[str, Any],
    result: dict[str, Any],
    speech_bible: dict[str, Any],
    *,
    plan_id: str,
    batch_id: str,
    claim_id: str,
    worker_id: str,
) -> int:
    raw_profiles = result.get("profiles")
    if not isinstance(raw_profiles, list):
        raise ValueError(f"{batch_id}: speech result must contain profiles[]")
    expected = {str(item.get("character_key")): item for item in batch.get("items", []) if isinstance(item, dict)}
    received: dict[str, dict[str, Any]] = {}
    for raw in raw_profiles:
        if not isinstance(raw, dict):
            raise ValueError(f"{batch_id}: each profile must be an object")
        key = str(raw.get("character_key") or "").strip()
        if not key or key in received:
            raise ValueError(f"{batch_id}: duplicate/missing character_key in speech result")
        received[key] = raw
    if set(received) != set(expected):
        missing = sorted(set(expected) - set(received))
        extra = sorted(set(received) - set(expected))
        raise ValueError(f"{batch_id}: speech result coverage mismatch missing={missing} extra={extra}")

    profiles = speech_bible.setdefault("profiles", {})
    if not isinstance(profiles, dict):
        raise ValueError("speech_bible.profiles must be an object")
    added = 0
    for key, raw in received.items():
        task = expected[key]
        canonical = str(raw.get("canonical") or "").strip()
        if canonical != str(task.get("canonical") or "").strip():
            raise ValueError(f"{batch_id}: canonical name mismatch for {key}")
        existing = profiles.get(key)
        if isinstance(existing, dict):
            curation = existing.get("curation", {})
            if isinstance(curation, dict) and curation.get("batch_id") == batch_id and curation.get("claim_id") == claim_id:
                continue
            raise ValueError(f"{batch_id}: {canonical} already has a curated profile; refusing silent overwrite")

        register = clean_string_list(raw.get("register"), max_items=10, max_len=120)
        rules = clean_string_list(raw.get("translation_rules"), max_items=10, max_len=500)
        anti_rules = clean_string_list(raw.get("anti_rules"), max_items=8, max_len=500)
        source_urls = clean_string_list(raw.get("source_urls"), max_items=8, max_len=500)
        if not register:
            raise ValueError(f"{batch_id}: {canonical} requires non-empty register")
        if len(rules) < 2:
            raise ValueError(f"{batch_id}: {canonical} requires at least two translation_rules")
        tempo = str(raw.get("tempo") or "").strip()
        politeness = str(raw.get("politeness") or "").strip()
        if not tempo or not politeness or len(tempo) > 500 or len(politeness) > 500:
            raise ValueError(f"{batch_id}: {canonical} requires compact tempo/politeness")
        confidence = str(raw.get("confidence") or "medium").strip().lower()
        if confidence not in {"high", "medium", "low"}:
            raise ValueError(f"{batch_id}: invalid confidence for {canonical}")
        self_reference = str(raw.get("self_reference") or "").strip()
        if len(self_reference) > 500:
            raise ValueError(f"{batch_id}: self_reference too long for {canonical}")
        evidence_note = str(raw.get("evidence_note") or "").strip()
        if len(evidence_note) > 800:
            raise ValueError(f"{batch_id}: evidence_note too long for {canonical}")

        profile: dict[str, Any] = {
            "canonical": canonical,
            "status": "parallel_curated_review",
            "register": register,
            "tempo": tempo,
            "politeness": politeness,
            "translation_rules": rules,
            "confidence": confidence,
            "curation": {
                "plan_id": plan_id,
                "batch_id": batch_id,
                "claim_id": claim_id,
                "worker_id": worker_id,
                "merged_at": utc_now(),
            },
        }
        if self_reference:
            profile["self_reference"] = self_reference
        if anti_rules:
            profile["anti_rules"] = anti_rules
        if source_urls:
            profile["source_urls"] = source_urls
        if evidence_note:
            profile["evidence_note"] = evidence_note
        profiles[key] = profile
        added += 1
    return added


def merge_term_batch(
    batch: dict[str, Any],
    result: dict[str, Any],
    reviews: dict[str, Any],
    *,
    plan_id: str,
    batch_id: str,
    claim_id: str,
    worker_id: str,
) -> int:
    raw_decisions = result.get("decisions")
    if not isinstance(raw_decisions, list):
        raise ValueError(f"{batch_id}: terminology result must contain decisions[]")
    expected = {str(item.get("source_zh_cn")): item for item in batch.get("items", []) if isinstance(item, dict)}
    received: dict[str, dict[str, Any]] = {}
    for raw in raw_decisions:
        if not isinstance(raw, dict):
            raise ValueError(f"{batch_id}: each terminology decision must be an object")
        source = str(raw.get("source_zh_cn") or "").strip()
        if not source or source in received:
            raise ValueError(f"{batch_id}: duplicate/missing source_zh_cn in terminology result")
        received[source] = raw
    if set(received) != set(expected):
        missing = sorted(set(expected) - set(received))
        extra = sorted(set(received) - set(expected))
        raise ValueError(f"{batch_id}: terminology result coverage mismatch missing={missing} extra={extra}")

    ledger = reviews.setdefault("decisions", [])
    if not isinstance(ledger, list):
        raise ValueError("terminology_reviews.decisions must be an array")
    existing_by_source = {
        str(item.get("source_zh_cn") or "").strip(): item
        for item in ledger
        if isinstance(item, dict) and str(item.get("source_zh_cn") or "").strip()
    }
    added = 0
    for ordinal, (source, raw) in enumerate(received.items(), start=1):
        action = str(raw.get("action") or "").strip().lower()
        if action not in ALLOWED_TERM_ACTIONS:
            raise ValueError(f"{batch_id}: {source!r} has unsupported action {action!r}")
        target = str(raw.get("target_vi") or "").strip()
        if action == "lock" and not target:
            raise ValueError(f"{batch_id}: lock requires target_vi for {source!r}")
        if len(target) > 500:
            raise ValueError(f"{batch_id}: target_vi too long for {source!r}")

        previous = existing_by_source.get(source)
        if previous is not None:
            same = str(previous.get("action") or "") == action and str(previous.get("target_vi") or "") == target
            if same:
                continue
            raise ValueError(f"{batch_id}: {source!r} already has a different review decision")

        task = expected[source]
        decision: dict[str, Any] = {
            "decision_id": f"parallel.{plan_id}.{batch_id}.{ordinal:02d}",
            "action": action,
            "source_zh_cn": source,
            "kind": str(raw.get("kind") or task.get("primary_kind") or "reviewed"),
            "note": str(raw.get("note") or "").strip()[:1000],
            "parallel_curation": {
                "plan_id": plan_id,
                "batch_id": batch_id,
                "claim_id": claim_id,
                "worker_id": worker_id,
                "merged_at": utc_now(),
            },
        }
        if action == "lock":
            decision["target_vi"] = target
            for field in ("term_id", "category"):
                value = str(raw.get(field) or "").strip()
                if value:
                    decision[field] = value
            for field in ("ja", "zh_tw", "source_aliases", "zh_cn_aliases"):
                values = clean_string_list(raw.get(field), max_items=12, max_len=300)
                if values:
                    decision[field] = values
        ledger.append(decision)
        existing_by_source[source] = decision
        added += 1
    return added


def merge_ready(*, active_path: Path = DEFAULT_ACTIVE, max_batches: int | None = None) -> dict[str, int]:
    active, plan, _ = load_active_plan(active_path)
    plan_id = str(active["plan_id"])
    batches = batch_index(plan)
    speech_bible = read_json(DEFAULT_SPEECH_BIBLE, {}) or {}
    reviews = read_json(DEFAULT_TERM_REVIEWS, {}) or {}
    if not isinstance(speech_bible, dict) or not isinstance(reviews, dict):
        raise ValueError("canonical curation files must be JSON objects")

    stats = {"batches": 0, "speech_profiles": 0, "terminology_decisions": 0}
    completion_root = WORK_ROOT / "completions"
    if not completion_root.exists():
        return stats

    for completion_path in sorted(completion_root.glob("*/*.json")):
        batch_id = completion_path.parent.name
        if batch_id not in batches:
            continue
        merged_path = WORK_ROOT / "merged" / f"{batch_id}.json"
        if merged_path.exists():
            continue
        completion = read_json(completion_path, {}) or {}
        if not isinstance(completion, dict) or completion.get("plan_id") != plan_id:
            continue
        claim_path = WORK_ROOT / "claims" / f"{batch_id}.json"
        claim = read_json(claim_path, {}) or {}
        if not isinstance(claim, dict):
            continue
        claim_id = str(completion.get("claim_id") or "").strip()
        result_path = WORK_ROOT / "results" / batch_id / f"{claim_id}.json"
        result = read_json(result_path, {}) or {}
        if not isinstance(result, dict):
            raise ValueError(f"{batch_id}: missing result for completion {completion_path}")
        validate_envelope(result, completion, claim, plan_id=plan_id, batch_id=batch_id)
        worker_id = str(claim.get("worker_id") or result.get("worker_id") or "unknown")
        batch = batches[batch_id]
        kind = str(batch.get("kind") or "")
        if kind == "speech":
            stats["speech_profiles"] += merge_speech_batch(
                batch,
                result,
                speech_bible,
                plan_id=plan_id,
                batch_id=batch_id,
                claim_id=claim_id,
                worker_id=worker_id,
            )
        elif kind == "terminology":
            stats["terminology_decisions"] += merge_term_batch(
                batch,
                result,
                reviews,
                plan_id=plan_id,
                batch_id=batch_id,
                claim_id=claim_id,
                worker_id=worker_id,
            )
        else:
            raise ValueError(f"{batch_id}: unsupported curation batch kind {kind!r}")
        write_json(
            merged_path,
            {
                "schema_version": 1,
                "plan_id": plan_id,
                "batch_id": batch_id,
                "claim_id": claim_id,
                "worker_id": worker_id,
                "merged_at": utc_now(),
                "result_path": result_path.relative_to(ROOT).as_posix(),
            },
        )
        stats["batches"] += 1
        if max_batches is not None and stats["batches"] >= max_batches:
            break

    if stats["batches"]:
        write_json(DEFAULT_SPEECH_BIBLE, speech_bible)
        write_json(DEFAULT_TERM_REVIEWS, reviews)
    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and merge completed parallel curation batches.")
    parser.add_argument("--active", type=Path, default=DEFAULT_ACTIVE)
    parser.add_argument("--max-batches", type=int)
    args = parser.parse_args()
    try:
        stats = merge_ready(active_path=args.active, max_batches=args.max_batches)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    print(json.dumps(stats, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
