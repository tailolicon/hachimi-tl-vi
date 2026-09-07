from __future__ import annotations

"""Keep full Kyoto Himba Stakes identity ahead of the shared Uma Musume Stakes component rule."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-528fb1894e2fccc1"
SOURCE = "京都赛马娘锦标"
TARGET = "Kyoto Himba Stakes"
FULL_TERM_ID = "race.kyoto_himba_stakes"
COMPONENT_TERM_ID = "race.uma_musume_stakes.component131"
COMPONENT_DECISION_ID = "audit.finding.uma-musume-stakes-component"


def _load(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return dict(default)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def _append_exact_exclusion(record: dict[str, Any]) -> None:
    values = [str(v) for v in record.get("exclude_source_exact", []) if str(v)]
    record["exclude_source_exact"] = list(dict.fromkeys([*values, SOURCE]))


def harden(repo_root: Path = ROOT) -> bool:
    changed = False

    community_path = repo_root / "glossary" / "ui_community_terms.json"
    community = _load(community_path, {"schema_version": 1, "terms": []})
    before = json.dumps(community, ensure_ascii=False, sort_keys=True)
    component = next(
        (x for x in community.setdefault("terms", []) if isinstance(x, dict) and x.get("id") == COMPONENT_TERM_ID),
        None,
    )
    if component is None:
        raise ValueError(f"missing component term {COMPONENT_TERM_ID}")
    _append_exact_exclusion(component)
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    decision = next(
        (x for x in reviews.setdefault("decisions", []) if isinstance(x, dict) and x.get("decision_id") == COMPONENT_DECISION_ID),
        None,
    )
    if decision is None:
        raise ValueError(f"missing component decision {COMPONENT_DECISION_ID}")
    _append_exact_exclusion(decision)
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"kyoto_himba_precedence_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
