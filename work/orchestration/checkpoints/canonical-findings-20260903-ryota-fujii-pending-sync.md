# Canonical finding: 藤井亮太 / Ryota Fujii

- Live finding: `cf-71b93369404bbe81`
- Source alias: `藤井亮太`
- Verified Latin spelling: `Ryota Fujii`
- Scope: `text_data_dict.json`, category/path prefix `17`, `match_mode: contains`

## Evidence and rationale

Current retrospective-review credit text contains `藤井亮太` as composer/arranger and flags the CJK name as a proper-name canonical finding. Commercial music-credit sources including VGMdb pair `藤井亮太` with `Ryota Fujii` for composition/arrangement credits; other music-credit catalogs independently use the same Latin identity. The canonical mapping is intentionally constrained to category 17 credit text.

## Durable implementation

- Hardener: `scripts/harden_ryota_fujii_finding.py` (`93d421486f5055f6a0db6bbc7268b30f57fcdeaa`)
- Regression tests: `tests/test_ryota_fujii_finding_hardening.py` (`74e538af9dc6d4fb5e1d3e9c92b338d7b7d32907`)
- Canonical target: `Ryota Fujii`
- Negative coverage checks another text-data category and another source file.

## Production acceptance state

Push-triggered workflows from the test commit include:
- Validate run `33765923203`
- Sync translation context run `33765923287`

Do not increment maintenance `completed_count` or call this finding resolved until validation succeeds and production Sync materializes `cf-71b93369404bbe81` with a non-null canonical resolution on live `main`.
