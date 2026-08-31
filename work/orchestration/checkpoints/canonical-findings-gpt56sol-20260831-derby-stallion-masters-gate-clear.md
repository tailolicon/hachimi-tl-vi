# Canonical findings maintenance checkpoint — Derby Stallion Masters gate clear

Claim: `canonical-findings-maintenance-gpt56sol-20260831T0547Z`

Resolved finding: `cf-c443cdb477c9c443` (`ダービースタリオン マスターズ`).

Durable evidence:

- `scripts/harden_derby_stallion_masters_finding.py` locks the official publisher English product name `Derby Stallion Masters` in `text_data_dict.json` collaboration descriptions.
- `tests/test_derby_stallion_masters_finding_hardening.py` proves resolution and negative source-path scope.
- The initial over-narrow category-prefix assumption was caught by validation; the durable resolver-compatible source-path-only fix is committed.
- Current combined-main Validate is green after that fix.
- Live `glossary/canonical_findings.json` now resolves the finding to `Derby Stallion Masters` and records review decision `audit.finding.derby-stallion-masters`.

Maintenance durable completed count: **68**.
