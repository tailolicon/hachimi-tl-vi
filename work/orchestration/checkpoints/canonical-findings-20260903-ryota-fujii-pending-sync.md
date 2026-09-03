# Canonical finding: 藤井亮太 / Ryota Fujii

- Live finding: `cf-71b93369404bbe81`
- Source alias: `藤井亮太`
- Verified Latin spelling: `Ryota Fujii`
- Scope: `text_data_dict.json`, category/path prefix `17`, `match_mode: contains`

## Evidence and rationale

Retrospective-review credit text contains `藤井亮太` as composer/arranger and flagged the CJK name as a proper-name canonical finding. Commercial music-credit sources including VGMdb pair `藤井亮太` with `Ryota Fujii` for composition/arrangement credits; independent catalogs use the same Latin identity. The canonical mapping is intentionally constrained to category 17 credit text.

## Durable implementation

- Hardener: `scripts/harden_ryota_fujii_finding.py` (`93d421486f5055f6a0db6bbc7268b30f57fcdeaa`)
- Regression tests: `tests/test_ryota_fujii_finding_hardening.py` (`74e538af9dc6d4fb5e1d3e9c92b338d7b7d32907`)
- Canonical target: `Ryota Fujii`
- Negative coverage checks another text-data category and another source file.

## Production acceptance

- Validate run `33765923203`: success, including pytest, `tlvi validate`, and index generation.
- Production Sync translation context run `33765923287`: success. Its hardener sweep reports `ryota_fujii_hardening_changed=true`, canonical-finding refresh completed, the context test suite passed `544 passed`, and generated context was safely rebased/pushed to `main`.
- Live generated `glossary/canonical_findings.json` at the production-sync result contains `cf-71b93369404bbe81` with canonical resolution `layer=community`, `term_id=proper_name.ryota_fujii.credit17`, `target_vi=Ryota Fujii`, plus review lock `audit.finding.ryota-fujii-credit`.

The finding is durably resolved and maintenance `completed_count` may advance from 25 to 26.
