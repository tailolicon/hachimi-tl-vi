# Canonical finding checkpoint — Sounds of Earth / Che Piacevole!

Finding: `cf-24e795c0befb0e4f`
Source zh-CN alias: `真是愉快！`
Verified JP identity: `ケ・ピアチェーヴォレ！` (Sounds of Earth unique Skill)
Canonical target: `Che Piacevole!`

## Diagnosis

The active generated finding is category-172 inheritance text where the zh-CN bridge embeds `真是愉快！` and historical review deferred because the JP identity was not yet verified. Live repository output already uses `Che Piacevole!` for the corresponding category-147 title keys `11020201`, `11020202`, and `11020203`, while category 172 still contains the literal bridge-derived `Thật vui quá!` inside Skill Hint descriptions.

The repair therefore preserves the repository-established Italian title instead of translating the zh-CN semantics literally.

## Durable repair

- Hardener: `scripts/harden_sounds_of_earth_che_piacevole_finding.py`
- Implementation commit: `ccceb5c01e591783f119fe2501d533548404c2d6`
- Regression test: `tests/test_sounds_of_earth_che_piacevole_finding_hardening.py`
- Regression commit: `45da5f9ee07850a43b6b6d27d2ec913ece3336da`
- Manual execution of both regression functions passed in the available repository Python environment. The environment did not have pytest installed locally.
- The hardener adds an exact category-147 title rule and a category-172 `contains` factor rule, both item-invalidated and scoped to `text_data_dict.json`.
- Historical literal target `Thật vui quá!` is forbidden for this Skill identity.

## Production gates

- Validate run `33927430643`: **success** on regression head `45da5f9ee07850a43b6b6d27d2ec913ece3336da`.
- Production context materialization commit: `cca87c95894d80d3a072d38932c1924526863756`.
  - `glossary/canonical_findings.json` now records `canonical_resolution.layer = locked`, term `reviewed.skill_name.611db75c6a35`, target `Che Piacevole!` for this finding.
  - `glossary/term_registry.json` contains the reviewed Skill lock with category-172 `contains` scope.
  - Generated terminology queue open canonical findings decreased `118 -> 117` in that sync commit.
- Context Sync run `33927430590`: **success**; completed at `2026-09-04T22:58:29Z`.
- Successor Translation Review Plan run `33927755539`: workflow-dispatch created after the production context materialization/checkpoint and currently pending. It is the acceptance candidate because it will rebuild from current `origin/main` after the new canonical context exists.
- Earlier Translation Review Plan run `33927430675` remains pending from the regression push and is not sufficient successor proof by itself.
- Do not increment maintenance `completed_count` until successor Translation Review Plan regeneration succeeds and confirms `cf-24e795c0befb0e4f` is no longer an active blocker in the regenerated worker-facing batch snapshot.
