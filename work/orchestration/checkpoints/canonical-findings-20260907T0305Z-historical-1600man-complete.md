# Canonical findings maintenance checkpoint — historical 1600万下 complete

- task: `canonical-findings-maintenance`
- claim: `canonical-findings-maintenance-gpt56sol-auto11-20260907T0256Z`
- finding: `cf-493004166ae49fae`
- source zh-CN: `1600万下`
- canonical target: `Hạng dưới 16 triệu yên`
- previous_completed_count: `171`
- completed_count: `172`

## Durable implementation

- hardener commit: `8905663d5752d060ea372ad8ae36d7e5d1ebb7ac`
- regression commit: `3dee078f5a0770433a0564e0d9cb1794fbdaaaf1`
- hardener: `scripts/harden_historical_1600man_race_class_finding.py`
- regression: `tests/test_historical_1600man_race_class_finding_hardening.py`

The canonical rule is exact-match and scoped to `localize_dict.json`. It preserves the historical earnings-class label, makes the omitted yen unit explicit, and rejects the legacy `Dưới 16 triệu` form.

## Production validation

- Validate run `34078135058`: success.
- Sync translation context run `34078125077`: success.
- Production hardener pass first added the 1600万下 rule, then the second pass reported `historical_1600man_race_class_hardening_changed=false`, demonstrating idempotence in the live workflow.
- Production context test suite: `787 passed`.
- Generated context commit after safe rebase/push: `5b8778760ef7fcd0d4b4878f95ee36295666fc89`.
- That generated commit gives finding `cf-493004166ae49fae` a locked canonical resolution and review resolution targeting `Hạng dưới 16 triệu yên`, adds locked registry term `reviewed.system_label.55c13f93009d`, and removes `1600万下` from the open canonical-finding review queue.
- Queue summary moved open canonical findings from 135 to 134.

This bounded finding unit has passed production acceptance and is complete.