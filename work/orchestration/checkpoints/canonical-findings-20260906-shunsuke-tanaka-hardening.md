# Canonical finding hardening — Shunsuke Tanaka

Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260906T205900Z`

Finding: `cf-2d359ed052159dea`

## Verified identity

The live finding is a category-17 creator credit containing `田中俊亮`. The creator's official Smile Company profile identifies him as `SHUNSUKE TANAKA`; independent music credits also use `Shunsuke Tanaka` for the same composer/arranger. The canonical Vietnamese release credit should therefore use `Shunsuke Tanaka` rather than leave the CJK name unresolved.

## Hardening implemented

- `scripts/harden_shunsuke_tanaka_finding.py`
  - source alias `田中俊亮`
  - target `Shunsuke Tanaka`
  - CJK source form forbidden in accepted Vietnamese output
  - source-path coverage `text_data_dict.json`
  - `match_mode: contains`, because the creator name occurs inside a longer credit line
  - supported `invalidation_scope: item`
  - review decision `audit.finding.shunsuke-tanaka-credit`.
- `tests/test_shunsuke_tanaka_finding_hardening.py`
  - idempotence
  - canonical + review resolution
  - active-finding clearance
  - wrong-source-path non-overmatch.

Implementation commits:

- hardener: `d308bd0467a118b1f252c43d2953e30ce207b34c`
- regression test: `246f8f0505aaa156e0607b88c93f1b31f2fee049`

## Validation status

Repository Validate and production Sync triggered by the regression-test commit must succeed before this finding is counted complete.

## Status

Hardening implemented; production acceptance pending. Shared maintenance completed count remains 156 until generated live context resolves `cf-2d359ed052159dea` to `Shunsuke Tanaka`.
