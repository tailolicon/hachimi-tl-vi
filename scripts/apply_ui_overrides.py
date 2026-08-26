from __future__ import annotations

import argparse
import json
from pathlib import Path

from hachimi_tl_vi.ui_policy import apply_ui_overrides


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply canonical compact-UI overrides.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--check",
        action="store_true",
        help="Do not write; exit 1 when checked-out localized_data still needs overrides.",
    )
    parser.add_argument(
        "--strict-missing",
        action="store_true",
        help="Exit 2 when a reviewed key is not present in the checked-out data.",
    )
    args = parser.parse_args()

    report = apply_ui_overrides(args.repo_root, write=not args.check)
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if args.strict_missing and report["missing_keys"]:
        return 2
    if args.check and report["total_changes"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
