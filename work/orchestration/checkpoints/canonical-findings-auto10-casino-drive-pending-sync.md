# Canonical maintenance checkpoint — Casino Drive identity

Claim: `canonical-findings-maintenance-gpt56sol-auto10-20260831T1623Z`

Resolved the identity evidence for blocking finding `cf-096e09d8c05dcc89` (`夺金旅途`) in `text_data_dict.json` category `120`.

Evidence:
- live curation had deferred the alias because game ID 1139 was unresolved and observed memory suggested Casino Drive;
- current official Cygames character page identifies `カジノドライヴ` as `Casino Drive` and explicitly describes her as the founder of the Breeders' Cup expedition project `DREAMS`;
- current external game-data evidence identifies character ID 1139 as Casino Drive;
- therefore the existing `Stay Gold` rendering in the reviewed category-120 scenario text is not the correct character identity.

Durable changes:
- `scripts/harden_casino_drive_finding.py` commit `407552c1d1de0fda39f8485abd3f72184c675899` adds scoped canonical rule `proper_name.casino_drive.scenario120`, `夺金旅途` -> `Casino Drive`, category 120 only, with `Stay Gold` forbidden in that scope;
- `tests/test_casino_drive_finding_hardening.py` commit `c97c4be03129d5831f232256e8d9f922313934ca` verifies idempotence, positive canonical resolution for the production finding, and no resolution outside category 120.

Validation and sync-context are triggered from the test commit. Do not count the finding complete until both CI and generated live ledger confirm `canonical_resolution`.
