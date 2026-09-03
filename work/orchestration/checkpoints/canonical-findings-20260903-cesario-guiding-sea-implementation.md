# Canonical finding implementation — Cesario / Guiding Sea

Finding: `cf-a7a33a0b139e1f56`

- zh-CN Skill alias: `海纳百川`
- character: Cesario / `シーザリオ`, game ID `1110`
- affected Skill IDs in live finding evidence: `11100101` / `11100102` / `11100103`
- canonical Skill identity: `Guiding Sea`
- historical Vietnamese calques include `Biển dung trăm sông` and `Biển ôm trọn trăm sông`

## Scope correction

The historical finding used global `contains` matching in `text_data_dict.json`, but all live evidence is category `172` Spark/inheritance text. Because `海纳百川` is also an ordinary Chinese idiom, globally locking every occurrence would be unsafe.

The hardener therefore narrows the finding itself to `json_path_prefixes: [["172"]]` and installs the canonical rule with the same category scope. `contains` matching is retained inside that scope so the Skill title resolves when embedded in inheritance/Spark prose.

## Implementation

- hardener: `scripts/harden_cesario_guiding_sea_finding.py`, commit `f15f9b2a6640db81905c80b2b4218e20956dd120`
- regression: `tests/test_cesario_guiding_sea_finding_hardening.py`, commit `525cc563615ad75d22713381f636bd5dd0c98bf0`
- community rule: `skill.cesario.guiding_sea`
- terminology decision: `audit.finding.skill-cesario-guiding-sea`

Regression requires production-shape resolution after the scope correction, idempotence, and a negative category-163 finding that must remain unresolved.

## Acceptance pending

Do not increment maintenance `completed_count` beyond 61 until Validate, production Sync translation context, and Sync translation review plan succeed on a descendant containing the regression commit, and live generated context shows `cf-a7a33a0b139e1f56` resolved to `Guiding Sea` with category-172 scope.
