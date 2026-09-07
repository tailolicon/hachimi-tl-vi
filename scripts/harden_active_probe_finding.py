from __future__ import annotations

import json

from canonical_findings import active_findings


def main() -> int:
    active = active_findings()
    payload = active[0] if active else None
    print("ACTIVE_FINDING_PROBE=" + json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
