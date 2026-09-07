from __future__ import annotations

import json
from pathlib import Path

from canonical_findings import active_findings

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    payload = json.loads((ROOT / "glossary/canonical_findings.json").read_text(encoding="utf-8"))
    active = active_findings(payload)
    first = active[0] if active else None
    print("ACTIVE_FINDING_PROBE=" + json.dumps(first, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
