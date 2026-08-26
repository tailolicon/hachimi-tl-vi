from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
WORK_ROOT = ROOT / "work/curation"


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def parse_time(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def reap(now: datetime | None = None) -> dict[str, int]:
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    claims = WORK_ROOT / "claims"
    stats = {"scanned": 0, "expired_removed": 0, "merged_removed": 0, "kept": 0}
    if not claims.exists():
        return stats

    for path in sorted(claims.glob("*.json")):
        stats["scanned"] += 1
        batch_id = path.stem
        doc = read_json(path, {}) or {}
        if not isinstance(doc, dict):
            path.unlink()
            stats["expired_removed"] += 1
            continue
        if (WORK_ROOT / "merged" / f"{batch_id}.json").exists():
            path.unlink()
            stats["merged_removed"] += 1
            continue
        claim_id = str(doc.get("claim_id") or "").strip()
        if claim_id and (WORK_ROOT / "completions" / batch_id / f"{claim_id}.json").exists():
            stats["kept"] += 1
            continue
        expires = parse_time(doc.get("expires_at"))
        if expires is None:
            heartbeat = parse_time(doc.get("heartbeat_at") or doc.get("claimed_at"))
            if heartbeat is None:
                path.unlink()
                stats["expired_removed"] += 1
                continue
            lease_minutes = int(doc.get("lease_minutes", 45) or 45)
            expires = heartbeat + __import__("datetime").timedelta(minutes=lease_minutes)
        if expires <= now:
            path.unlink()
            stats["expired_removed"] += 1
        else:
            stats["kept"] += 1
    return stats


def main() -> int:
    stats = reap()
    print(json.dumps(stats))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
