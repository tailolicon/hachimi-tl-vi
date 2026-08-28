from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(name: str):
    return json.loads((ROOT / "work" / name).read_text(encoding="utf-8"))

def write(name: str, value):
    (ROOT / "work" / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    gaps = load("tmp_race_exact_gaps.json")
    mismatches = load("tmp_race_exact_mismatches.json")
    write("tmp_race_gap_names.json", [
        {"source": item["source"], "currents": item["currents"]} for item in gaps
    ])
    write("tmp_race_mismatch_names.json", [
        {"source": item["source"], "currents": item["currents"], "canonical_targets": item["canonical_targets"]}
        for item in mismatches
    ])
    write("tmp_race_compact.json", {
        "gaps": [{"source": item["source"], "currents": item["currents"], "locators": item["locators"]} for item in gaps],
        "mismatches": [{"source": item["source"], "currents": item["currents"], "canonical_ids": item["canonical_ids"], "canonical_targets": item["canonical_targets"], "locators": item["locators"]} for item in mismatches],
    })
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
