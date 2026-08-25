from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claims-root", type=Path, default=Path("work/claims"))
    parser.add_argument("--merged-root", type=Path, default=Path("work/merged"))
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    removed: list[str] = []
    if not args.claims_root.exists():
        print("No claims directory.")
        return 0

    for claim_path in sorted(args.claims_root.glob("batch-*.json")):
        try:
            payload = json.loads(claim_path.read_text(encoding="utf-8"))
            batch = int(payload["batch"])
            expires_at = parse_time(payload["expires_at"])
        except Exception:
            claim_path.unlink()
            removed.append(claim_path.as_posix())
            continue

        merged = args.merged_root / f"batch-{batch:05d}.json"
        if merged.exists() or expires_at <= now:
            claim_path.unlink()
            removed.append(claim_path.as_posix())

    print(json.dumps({"removed": removed, "count": len(removed)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
