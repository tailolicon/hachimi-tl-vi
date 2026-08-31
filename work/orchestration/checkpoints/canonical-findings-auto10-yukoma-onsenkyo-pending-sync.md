# Canonical maintenance checkpoint — Yukoma Onsenkyo pending sync

Claim: `canonical-findings-maintenance-gpt56sol-auto10-20260831T1623Z`

Blocking finding `cf-2bb0d562f4d904c4` (`汤驹温泉乡`, text_data category 120) is being hardened to `Yukoma Onsenkyo`.

Evidence:
- source description is the hot-springs training scenario setting;
- JP coverage for Cygames' scenario `ごくらく♪ゆこま温泉郷` identifies the named main setting as `ゆこま温泉郷`;
- current translation already uses `Yukoma Onsenkyo`, so the hardening preserves the named place rather than literalizing it as a generic hot-springs village.

Durable changes:
- `scripts/harden_yukoma_onsenkyo_finding.py` commit `e955fc8f81fe030249c528aaccfc9718744477bf`;
- `tests/test_yukoma_onsenkyo_finding_hardening.py` commit `4ecdf4438186bcfaacc6735bebfffb1a41b117f4` verifies production-finding resolution, idempotence, and category-120 scoping.

`Sync translation context` run `33414695274` was triggered from the test commit and was pending at checkpoint creation. Do not advance completed_count until live generated ledger confirms canonical resolution.
