# Canonical maintenance checkpoint — スタホTV pending sync

Claim: `canonical-findings-maintenance-gpt56sol-auto10-20260831T1623Z`

Blocking finding `cf-56f201174e84a443` (`スタホTV`) is being hardened to preserve the official SEGA display form `スタホTV`.

Evidence:
- official StarHorse4 guide pages display the in-game news/reward program as `スタホTV`;
- current official StarHorse4 update notices continue to call the program `スタホTV`;
- no official Latin spelling was found, so inventing `StaHo TV` or `StarHorse TV` would be less authoritative than preserving the official display.

Durable changes:
- `scripts/harden_staho_tv_finding.py` commit `3c66076529a6fb3cbea8cf79be590a8ae9a4ffd2`;
- `tests/test_staho_tv_finding_hardening.py` commit `29c9e7b98b67d199edb429a358101237db34b985` verifies production finding resolution, idempotence, and that generic `TV` does not match.

Do not advance completed_count until CI and live generated ledger confirm resolution.
