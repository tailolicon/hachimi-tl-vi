from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "scripts/harden_race_canon.py"


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    old = '''def _is_proper_race(term: dict[str, Any]) -> bool:\n    tid = str(term.get("id", ""))\n    if str(term.get("category", "")) == "race_name":\n        return True\n    if not tid.startswith("race."):\n        return False\n    return tid not in {\n        "race.generic", "race.surface.turf", "race.surface.dirt",\n        "race.distance.sprint", "race.distance.mile", "race.distance.medium", "race.distance.long",\n        "race.strategy.style", "race.strategy.front_runner", "race.strategy.pace_chaser",\n        "race.strategy.late_surger", "race.strategy.end_closer", "race.strategy.runaway",\n    }\n'''
    new = '''def _is_proper_race(term: dict[str, Any]) -> bool:\n    # Only structured proper-race records may receive the default named-race\n    # guards. Prefix-based detection is unsafe because system records such as\n    # race.class.*, race.grade.*, race.ui.*, and race.track_condition.* also\n    # intentionally use the race.* namespace. RACES upserts normalize verified\n    # legacy named races to category=race_name before persistence.\n    return str(term.get("category", "")) == "race_name"\n'''
    if new in text:
        return 0
    if old not in text:
        raise RuntimeError("expected _is_proper_race block not found")
    PATH.write_text(text.replace(old, new, 1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
