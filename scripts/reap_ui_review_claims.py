from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from ui_review_common import load_json, parse_utc


def reap(repo_root: Path) -> dict[str, object]:
    claims_root = repo_root / "work" / "ui_review" / "claims"
    removed: list[str] = []
    now = datetime.now(timezone.utc)
    if claims_root.exists():
        for path in sorted(claims_root.glob("*.json")):
            try:
                claim = load_json(path)
                expires = parse_utc(str(claim["expires_at"]))
            except Exception:
                continue
            if expires <= now:
                path.unlink()
                removed.append(path.name)
    return {"removed": removed, "removed_count": len(removed)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Remove expired UI review claims.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()
    report = reap(args.repo_root.resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
