# Canonical finding: 松井洋平 / Yohei Matsui

- Live finding: `cf-ff1b53486e8bf6a1`
- Source alias: `松井洋平`
- Verified Latin spelling: `Yohei Matsui`
- Source scope: `text_data_dict.json`, `match_mode: contains`

## Evidence and rationale

HAOKK's official creator page identifies `松井洋平` as `Yohei Matsui`; independent release-credit catalogs use the same creator identity. The official company spelling is used for Vietnamese release credits.

## Durable implementation

- Hardener: `scripts/harden_yohei_matsui_finding.py` (`577a23ec0d5a556357ab9d831fac8c37dab10117`)
- Regression tests: `tests/test_yohei_matsui_finding_hardening.py` (`ed6f4e918de621f37f01d5f2495e1126e7f1b763`)
- Review decision: `audit.finding.yohei-matsui-credit`
- Target: `Yohei Matsui`

## Production acceptance

- Test/Validate check for `ed6f4e918de621f37f01d5f2495e1126e7f1b763`: success (`33766588352`).
- Production Sync translation context run `33766588393`: success; the pipeline reported `548 passed` and pushed generated context commit `c248552616` to `main`.
- Generated `glossary/canonical_findings.json` at `c248552616` contains the finding resolved to `target_vi=Yohei Matsui` and `review_resolution=lock` from `audit.finding.yohei-matsui-credit` (materialized as locked term `reviewed.proper_name.8d10406b6aa1`).

This finding is durably resolved and maintenance `completed_count` may advance by one.
