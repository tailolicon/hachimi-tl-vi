# Canonical maintenance checkpoint — Trainee text-data pending sync

Claim: `canonical-findings-maintenance-gpt56sol-auto10-20260831T1623Z`

Blocking finding `cf-338ec3f0de1ad2e9` (`育成赛马娘`) is being extended to the already-established canonical target `Trainee` in `text_data_dict.json`.

Repository evidence already defines the full compound 育成赛马娘 / 育成ウマ娘 as Trainee in Career UI and explicitly separates it from bare 育成 (Career) and generic 赛马娘/Umamusume. The new rule therefore matches only the full compound across text_data and does not promote either ambiguous component alone.

Durable changes:
- `scripts/harden_trainee_text_data_finding.py` commit `dd63cac407d633477ad14fcee307db5b464d9ca4`;
- `tests/test_trainee_text_data_finding_hardening.py` commit `dc7a24ef432ed920397119f0ba1dcc1d4bf2b857` verifies production finding resolution, idempotence, and negative behavior for bare `育成` and `赛马娘`.

`Sync translation context` run `33415032619` was triggered from the test commit and was pending at checkpoint creation. Do not advance completed_count until CI and the live generated ledger confirm resolution.
