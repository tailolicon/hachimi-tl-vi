from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_grand_live_performance_stats_finding import STATS, harden
from scripts.resolve_regenerated_grand_live_performance_stats_findings import FINDINGS, resolve
from scripts.translation_review_common import community_term_matches, load_community_terms


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _seed(root: Path) -> None:
    _write(root / "glossary/ui_community_terms.json", {"schema_version": 1, "terms": []})


def test_hardener_adds_scoped_grand_live_stats_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    before = (tmp_path / "glossary/ui_community_terms.json").read_text(encoding="utf-8")
    assert harden(tmp_path) is False
    assert (tmp_path / "glossary/ui_community_terms.json").read_text(encoding="utf-8") == before
    terms = load_community_terms(tmp_path)
    for slug, source, target, forbidden in STATS:
        matches = community_term_matches(
            None,
            f"获得300点{source}",
            f"Earn 300 {target}",
            terms,
            source_path="text_data_dict.json",
            json_path=["131", "1"],
        )
        rule = next(match for match in matches if match["id"] == f"scenario.grand_live.performance.{slug}.text_data")
        assert rule["accepted_present"] is True
        assert community_term_matches(
            None, source, target, terms, source_path="story.json", json_path=["1"]
        ) == []


def test_regenerated_resolver_closes_all_three_findings(tmp_path: Path) -> None:
    _seed(tmp_path)
    harden(tmp_path)
    findings = []
    for (finding_id, (term_id, target)), (_, source, _, _) in zip(FINDINGS.items(), STATS):
        findings.append(
            {
                "finding_id": finding_id,
                "status": "open",
                "source_zh_cn": source,
                "suggested_targets_vi": [target],
                "canonical_resolution": None,
                "evidence": [
                    {
                        "source_path": "text_data_dict.json",
                        "json_path": ["131", "1"],
                        "source_text": f"获得300点{source}",
                        "current_text": "legacy translation",
                    }
                ],
            }
        )
    _write(tmp_path / "glossary/canonical_findings.json", {"schema_version": 1, "findings": findings})
    assert resolve(tmp_path) == 3
    assert resolve(tmp_path) == 0
    payload = json.loads((tmp_path / "glossary/canonical_findings.json").read_text(encoding="utf-8"))
    assert [finding["canonical_resolution"]["target_vi"] for finding in payload["findings"]] == [
        "Visual",
        "Vocal",
        "Passion",
    ]


def test_regenerated_resolver_rejects_out_of_scope_evidence(tmp_path: Path) -> None:
    _seed(tmp_path)
    harden(tmp_path)
    finding_id, (term_id, target) = next(iter(FINDINGS.items()))
    source = STATS[0][1]
    _write(
        tmp_path / "glossary/canonical_findings.json",
        {
            "findings": [
                {
                    "finding_id": finding_id,
                    "status": "open",
                    "source_zh_cn": source,
                    "suggested_targets_vi": [target],
                    "canonical_resolution": None,
                    "evidence": [
                        {
                            "source_path": "story.json",
                            "json_path": ["1"],
                            "source_text": source,
                            "current_text": "legacy",
                        }
                    ],
                }
            ]
        },
    )
    assert resolve(tmp_path) == 0
