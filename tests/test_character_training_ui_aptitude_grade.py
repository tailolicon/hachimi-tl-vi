from __future__ import annotations

from pathlib import Path

from scripts.translation_review_common import community_term_matches, load_community_terms


REPO_ROOT = Path(__file__).resolve().parents[1]


def _ids(matches: list[dict[str, object]]) -> set[str]:
    return {str(item.get("id")) for item in matches}


def test_aptitude_grade_placeholder_composes_with_distance_terms() -> None:
    community = load_community_terms(REPO_ROOT)
    cases = (
        ("TrainingChallenge4180925", "短距离适性{0}", "Sprint Aptitude {0}", "common.distance.sprint"),
        ("TrainingChallenge4180928", "长距离适性{0}", "Long Aptitude {0}", "common.distance.long"),
    )
    for key, source, target, distance_term in cases:
        matches = community_term_matches(
            key,
            source,
            target,
            community,
            source_path="localize_dict.json",
            json_path=[key],
        )
        ids = _ids(matches)
        assert "common.aptitude" in ids
        assert distance_term in ids
        assert "{0}" in source
        assert "{0}" in target
