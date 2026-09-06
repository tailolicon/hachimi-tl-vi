# Canonical finding hardening — Unique Single Path

Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260906T204445Z`

Finding: `cf-875a4950fbb079e9`

## Repository evidence

Pinned curation verifies Skill `101201` as Japanese `無二無三なる一条の路`. The live zh-CN title is `一线生路无二亦无三`, currently rendered `Một tia sinh lộ, không hai chẳng ba`. The older curation defer explicitly states that the title is stylized and needed a reviewed Vietnamese word choice/rhythm rather than a direct bridge calque.

The selected title is `Con Đường Độc Nhất Vô Nhị`. It follows the Japanese identity: `一条の路` as one path and `無二無三` as incomparable/unique, while avoiding the separate zh-CN 'one lifeline / no two, no three' wordplay.

## Hardening implemented

- `scripts/harden_unique_single_path_finding.py`
  - exact source alias `一线生路无二亦无三`
  - JP `無二無三なる一条の路`
  - target `Con Đường Độc Nhất Vô Nhị`
  - historical bridge calque forbidden
  - source-path coverage `text_data_dict.json`
  - supported `invalidation_scope: item`
  - review decision `audit.finding.skill-unique-single-path`.
- `tests/test_unique_single_path_finding_hardening.py`
  - idempotence
  - canonical + review resolution
  - exact source/path non-overmatch
  - asserts the historical zh-CN wordplay rendering is not reused.

Implementation commits:

- hardener: `92fee3f09ebd56c965e291dd6c6207360054cd26`
- regression test: `dcd7a4c34f5aec01b73815106d1e9a21f6b0d4f5`

## Completion gate

Do not increment maintenance `completed_count` yet. Require Validate plus a successful production context Sync; then verify live `glossary/canonical_findings.json` records a non-null canonical resolution for `cf-875a4950fbb079e9` and the generated review context no longer carries this blocker.
