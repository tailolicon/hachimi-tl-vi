# Canonical finding hardening — Unique Single Path

Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260906T204445Z`

Finding: `cf-875a4950fbb079e9`

## Repository evidence

Pinned curation verifies Skill `101201` as Japanese `無二無三なる一条の路`. The live zh-CN title is `一线生路无二亦无三`, previously rendered `Một tia sinh lộ, không hai chẳng ba`. The older curation defer explicitly states that the title is stylized and needed a reviewed Vietnamese word choice/rhythm rather than a direct bridge calque.

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

## Validation / integration

- Validate run `34059057066` completed successfully.
- Production Sync translation context run `34059043594` completed successfully through all finding hardeners, terminology application, context-pipeline tests, and generated-context commit.
- Generated context commit: `3198d9c1192f456d72fa2e6e3230b7f45c6be61a`.
- Live `glossary/canonical_findings.json` now records for `cf-875a4950fbb079e9`:
  - `suggested_targets_vi: ["Con Đường Độc Nhất Vô Nhị"]`
  - `canonical_resolution.layer: locked`
  - `canonical_resolution.target_vi: "Con Đường Độc Nhất Vô Nhị"`
  - review decision `audit.finding.skill-unique-single-path`, action `lock`.
- Live term registry now carries JP `無二無三なる一条の路` and exact zh-CN `一线生路无二亦无三` for the reviewed locked term.
- Generated terminology queue reduced `open_canonical_findings` from 154 to 153.

## Status

Complete. This maintenance unit may increment the shared maintenance completed count from 154 to 155. Re-route from live `WORKER_START.md`; other canonical findings and retrospective review work remain.
