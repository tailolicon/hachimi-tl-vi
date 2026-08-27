from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
WORK_ROOT = ROOT / "work/curation"
ACTIVE_PATH = WORK_ROOT / "active_plan.json"


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def active_plan() -> tuple[str, set[str]]:
    active = read_json(ACTIVE_PATH, {}) or {}
    if not isinstance(active, dict):
        raise ValueError("active curation plan must be an object")
    plan_id = str(active.get("plan_id") or "").strip()
    plan_rel = str(active.get("plan_path") or "").strip()
    if not plan_id or not plan_rel:
        raise ValueError("active curation plan is missing plan_id/plan_path")
    plan = read_json(ROOT / plan_rel, {}) or {}
    if not isinstance(plan, dict) or str(plan.get("plan_id") or "") != plan_id:
        raise ValueError("active curation plan pointer does not match plan contents")
    batches: set[str] = set()
    for field in ("speech_batches", "terminology_batches"):
        for batch in plan.get(field, []):
            if isinstance(batch, dict):
                batch_id = str(batch.get("batch_id") or "").strip()
                if batch_id:
                    batches.add(batch_id)
    return plan_id, batches


def valid_completion(path: Path, *, plan_id: str, batch_id: str) -> tuple[dict[str, Any], Path] | None:
    completion = read_json(path, {}) or {}
    if not isinstance(completion, dict):
        return None
    claim_id = str(completion.get("claim_id") or "").strip()
    if not claim_id:
        return None
    if str(completion.get("plan_id") or "") != plan_id or str(completion.get("batch_id") or "") != batch_id:
        return None
    result_path = WORK_ROOT / "results" / batch_id / f"{claim_id}.json"
    result = read_json(result_path, {}) or {}
    if not isinstance(result, dict):
        return None
    for doc in (completion, result):
        if str(doc.get("plan_id") or "") != plan_id:
            return None
        if str(doc.get("batch_id") or "") != batch_id:
            return None
        if str(doc.get("claim_id") or "") != claim_id:
            return None
    return completion, result_path


def historical_claim(batch_id: str, claim_ids: set[str], *, plan_id: str) -> dict[str, Any] | None:
    if not claim_ids:
        return None
    rel = f"work/curation/claims/{batch_id}.json"
    log = subprocess.run(
        ["git", "log", "--format=%H", "--all", "--", rel],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    for commit in (line.strip() for line in log.stdout.splitlines() if line.strip()):
        shown = subprocess.run(
            ["git", "show", f"{commit}:{rel}"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if shown.returncode != 0 or not shown.stdout.strip():
            continue
        try:
            claim = json.loads(shown.stdout)
        except json.JSONDecodeError:
            continue
        if not isinstance(claim, dict):
            continue
        if str(claim.get("plan_id") or "") != plan_id:
            continue
        if str(claim.get("batch_id") or "") != batch_id:
            continue
        if str(claim.get("claim_id") or "") in claim_ids:
            return claim
    return None


def prepare() -> dict[str, int]:
    plan_id, batches = active_plan()
    stats = {
        "batches_scanned": 0,
        "ready": 0,
        "claims_recovered": 0,
        "stale_completions_removed": 0,
        "no_valid_completion": 0,
        "no_claim_history": 0,
    }

    for batch_id in sorted(batches):
        if (WORK_ROOT / "merged" / f"{batch_id}.json").exists():
            continue
        completion_dir = WORK_ROOT / "completions" / batch_id
        if not completion_dir.exists():
            continue
        stats["batches_scanned"] += 1

        candidates: dict[str, Path] = {}
        for path in sorted(completion_dir.glob("*.json")):
            valid = valid_completion(path, plan_id=plan_id, batch_id=batch_id)
            if valid is None:
                continue
            completion, _ = valid
            claim_id = str(completion["claim_id"])
            candidates[claim_id] = path

        if not candidates:
            stats["no_valid_completion"] += 1
            continue

        claim_path = WORK_ROOT / "claims" / f"{batch_id}.json"
        current = read_json(claim_path, {}) or {}
        current_id = ""
        if isinstance(current, dict):
            if str(current.get("plan_id") or "") == plan_id and str(current.get("batch_id") or "") == batch_id:
                current_id = str(current.get("claim_id") or "").strip()

        if current_id not in candidates:
            recovered = historical_claim(batch_id, set(candidates), plan_id=plan_id)
            if recovered is None:
                stats["no_claim_history"] += 1
                continue
            write_json(claim_path, recovered)
            current_id = str(recovered.get("claim_id") or "").strip()
            stats["claims_recovered"] += 1

        for claim_id, path in candidates.items():
            if claim_id != current_id:
                path.unlink()
                stats["stale_completions_removed"] += 1

        if current_id and (completion_dir / f"{current_id}.json").exists():
            stats["ready"] += 1
        elif current_id in candidates:
            # Some legacy completion filenames are not exactly <claim_id>.json.
            stats["ready"] += 1

    return stats


def main() -> int:
    try:
        stats = prepare()
    except (ValueError, subprocess.CalledProcessError) as exc:
        raise SystemExit(str(exc)) from exc
    print(json.dumps(stats, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
