from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from scripts.translation_review_common import (
        community_term_matches,
        load_community_terms,
        load_locked_terms,
        locked_term_matches,
    )
except ModuleNotFoundError:
    from translation_review_common import (  # type: ignore[no-redef]
        community_term_matches,
        load_community_terms,
        load_locked_terms,
        locked_term_matches,
    )


ROOT = Path(__file__).resolve().parents[1]
POWER_CONTEXT_GUARD_IDS = {
    "cf-14defc3b38d1efcd",
    "cf-1606ab03065110f0",
    "cf-2549c5753263451d",
    "cf-40320a059fe422c5",
    "cf-418e723cca9d411b",
    "cf-53deea84a131c5c1",
    "cf-9acf7ae6c0c968ce",
    "cf-9e20bab99a663608",
    "cf-a6c1bdfd933a9e86",
    "cf-a8c99a7184b30629",
    "cf-c2b4254feb56171f",
    "cf-d7f5148da47b8e7f",
    "cf-df66d1828a60839c",
}


GUARDS = {
    "cf-0477e3b1d68a9798": {
        "layer": "locked",
        "term_id": "reviewed.skill_name.0be1f248cf96",
        "target_vi": "Nở rộ",
    },
    "cf-04aeb4f2712eb3c6": {
        "layer": "locked",
        "term_id": "reviewed.skill_name.5907479481a9",
        "target_vi": "Dốc hết sức",
    },
    "cf-05ee17c3f625371f": {
        "layer": "community",
        "term_id": "race_state.rushed.text131",
        "target_vi": "Rushed",
    },
    "cf-15798cd76b70746c": {
        "layer": "locked",
        "term_id": "reviewed.race_name.b4e4d79a5f98",
        "target_vi": "Queen Cup",
    },
    "cf-2b8709d527abc360": {
        "layer": "locked",
        "term_id": "race.generic",
        "target_vi": "Cuộc đua",
    },
    "cf-552896cb4b769204": {
        "layer": "locked",
        "term_id": "race.generic",
        "target_vi": "Cuộc đua",
    },
    "cf-5d23e532c5359881": {
        "layer": "community",
        "term_id": "common.stat.power",
        "target_vi": "Power",
    },
    "cf-a4af27bf832dd765": {
        "layer": "community",
        "term_id": "common.stat.power",
        "target_vi": "Power",
    },
    "cf-f6a4d26b3bc63f7c": {
        "layer": "community",
        "term_id": "common.stat.power",
        "target_vi": "Power",
    },
    "cf-ecde28dd625ae647": {
        "layer": "community",
        "term_id": "common.stat.power",
        "target_vi": "Power",
    },
    "cf-5204eca8a2e00ad5": {
        "layer": "community",
        "term_id": "common.stat.power",
        "target_vi": "Power",
    },
    "cf-cde74f30fa07e6a6": {
        "layer": "community",
        "term_id": "common.stat.power",
        "target_vi": "Power",
    },
    "cf-2a3675dd079cad04": {
        "layer": "community",
        "term_id": "common.stat.power",
        "target_vi": "Power",
    },
    "cf-03be28442492e3b1": {
        "layer": "community",
        "term_id": "common.stat.power",
        "target_vi": "Power",
    },
    "cf-daad507f1b0d4acc": {
        "layer": "community",
        "term_id": "common.stat.speed",
        "target_vi": "Speed",
    },
    "cf-f6302c57277dc9bc": {
        "layer": "community",
        "term_id": "common.world.umamusume",
        "target_vi": "Mã Nương",
    },
    "cf-d1bcaa0ab582cbdf": {
        "layer": "locked",
        "term_id": "currency.jewel",
        "target_vi": "Jewel",
    },
    "cf-97e98b6571188de5": {
        "layer": "locked",
        "term_id": "reviewed.condition.97c2a1f26a21",
        "target_vi": "Recovery Spirit",
    },
    "cf-4247246a96780f8b": {
        "layer": "locked",
        "term_id": "reviewed.skill_name.5dffb471df59",
        "target_vi": "Đổi mới",
    },
    "cf-b4ddf0728febc08f": {
        "layer": "locked",
        "term_id": "reviewed.skill_name.e778cffef185",
        "target_vi": "Một bước vượt lên",
    },
    "cf-a54e17e1f89443be": {
        "layer": "locked",
        "term_id": "reviewed.skill_name.1c68057834c9",
        "target_vi": "Khải hoàn",
    },
    "cf-857f68c97ee8efed": {
        "layer": "locked",
        "term_id": "skill.201072",
        "target_vi": "Không chịu thua",
    },
    "cf-1db30364f26517a5": {
        "layer": "community",
        "term_id": "common.distance.long",
        "target_vi": "Long",
    },
    # Regenerated review findings may key the same overmatch by the excluded
    # compound (超长距离) rather than by the nested generic alias (长距离). Keep
    # both semantic incarnations tied to the same proven context guard.
    "cf-072fd00f345e81cb": {
        "layer": "community",
        "term_id": "common.distance.long",
        "target_vi": "Long",
    },
    "cf-fbbcf5f4a79f6cf8": {
        "layer": "community",
        "term_id": "common.stat.wit",
        "target_vi": "Wit",
    },
    # Regenerated equivalent of the 智力扣 puzzle overmatch guard.
    "cf-9758a6327ee17eae": {
        "layer": "community",
        "term_id": "common.stat.wit",
        "target_vi": "Wit",
    },
}

for _finding_id in POWER_CONTEXT_GUARD_IDS:
    # These regenerated findings all report the same Power-stat overmatch. The
    # resolver still verifies every evidence row against the live rule, so merely
    # registering an ID never closes a finding whose Power matcher is still active.
    GUARDS.setdefault(_finding_id, {
        "layer": "community",
        "term_id": "common.stat.power",
        "target_vi": "Power",
    })

GUARDS.update({
    "cf-1daec5ebd9895c48": {
        "layer": "community",
        "term_id": "common.stat.guts",
        "target_vi": "Guts",
    },
    "cf-9d903a48b310ef86": {
        "layer": "community",
        "term_id": "common.stat.speed",
        "target_vi": "Speed",
    },
    "cf-9844f9093f379eac": {
        "layer": "community",
        "term_id": "common.world.umamusume",
        "target_vi": "Mã Nương",
    },
    "cf-187d58b59b5dc9be": {
        "layer": "locked",
        "term_id": "race.generic",
        "target_vi": "Cuộc đua",
    },
})

# Some worker findings were reported with source_path-wide scope even though all
# durable evidence belongs to a narrower canonical UI category. Positive evidence
# guards resolve such a finding only when every evidence row is currently covered
# by the named live term. Canonical refresh resets resolutions before this pass,
# so any future evidence outside the proven scope automatically reopens the finding.
POSITIVE_EVIDENCE_GUARDS = {
    "cf-55673a272df0aaae": {
        "layer": "community",
        "term_id": "common.friendship_gauge.support_effects",
        "target_vi": "Friendship Gauge",
    },
}


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def _key(item: dict[str, Any]) -> str | None:
    raw_path = item.get("json_path")
    if item.get("source_path") == "localize_dict.json" and isinstance(raw_path, list) and raw_path:
        return str(raw_path[-1])
    return None


def _guard_matches_item(
    item: dict[str, Any],
    guard: dict[str, str],
    community_terms: list[dict[str, Any]],
    locked_terms: list[dict[str, Any]],
) -> bool:
    source = str(item.get("source_text") or "")
    target = str(item.get("current_text") or "")
    source_path = str(item.get("source_path") or "") or None
    json_path = item.get("json_path") if isinstance(item.get("json_path"), list) else None
    if guard["layer"] == "community":
        matches = community_term_matches(
            _key(item), source, target, community_terms,
            source_path=source_path, json_path=json_path,
        )
    else:
        matches = locked_term_matches(
            source, target, locked_terms,
            key=_key(item), source_path=source_path, json_path=json_path,
        )
    term_id = str(guard["term_id"])
    return any(str(match.get("id") or "") == term_id for match in matches)


def resolve(repo_root: Path = ROOT) -> bool:
    path = repo_root / "glossary" / "canonical_findings.json"
    payload = _load(path)
    community_terms = load_community_terms(repo_root)
    locked_terms = load_locked_terms(repo_root)
    before = json.dumps(payload, ensure_ascii=False, sort_keys=True)

    for finding in payload.get("findings", []):
        if not isinstance(finding, dict):
            continue
        if isinstance(finding.get("canonical_resolution"), dict):
            continue

        finding_id = str(finding.get("finding_id") or "")
        evidence = [item for item in finding.get("evidence", []) if isinstance(item, dict)]

        positive_guard = POSITIVE_EVIDENCE_GUARDS.get(finding_id)
        if positive_guard is not None:
            if not evidence:
                continue
            suggested = {
                str(value).strip().casefold()
                for value in finding.get("suggested_targets_vi", [])
                if str(value).strip()
            }
            expected = str(positive_guard["target_vi"]).strip().casefold()
            if suggested and expected not in suggested:
                continue
            if not all(
                _guard_matches_item(item, positive_guard, community_terms, locked_terms)
                for item in evidence
            ):
                continue
            finding["canonical_resolution"] = {
                "layer": str(positive_guard["layer"]),
                "term_id": str(positive_guard["term_id"]),
                "target_vi": str(positive_guard["target_vi"]),
            }
            continue

        guard = GUARDS.get(finding_id)
        if guard is None:
            continue
        # Context guards are fallback evidence that an old overmatching rule has
        # been neutralized. Never replace a positive canonical resolution that
        # already matches the reviewed target; canonical refresh owns that result.
        if not evidence:
            continue
        still_overmatches = any(
            _guard_matches_item(item, guard, community_terms, locked_terms)
            for item in evidence
        )
        if still_overmatches:
            continue
        finding["canonical_resolution"] = {
            "layer": "context_guard",
            "term_id": str(guard["term_id"]),
            "target_vi": str(guard["target_vi"]),
        }

    changed = before != json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if changed:
        _write(path, payload)
    return changed


def main() -> int:
    changed = resolve(ROOT)
    print(f"context_guard_resolutions_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
