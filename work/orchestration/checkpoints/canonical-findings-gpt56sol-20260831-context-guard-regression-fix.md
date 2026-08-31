# Canonical maintenance checkpoint — context-guard regression repair

Claim: `canonical-findings-maintenance-gpt56sol-20260831T154738Z-a9f4`

The first sync-context run after adding the `不服输的傲娇少女` guard failed in pytest because two earlier context-guard regressions used synthetic finding IDs that the production resolver intentionally does not recognize.

Durable repair:
- `scripts/resolve_context_guard_findings.py` now includes production finding `cf-1db30364f26517a5` -> community `common.distance.long` / `Long`.
- `scripts/resolve_context_guard_findings.py` now includes production finding `cf-fbbcf5f4a79f6cf8` -> community `common.stat.wit` / `Wit`.
- `tests/test_super_long_distance_context_finding_hardening.py` now seeds production finding ID `cf-1db30364f26517a5`.
- `tests/test_wit_puzzle_context_finding_hardening.py` now seeds production finding ID `cf-fbbcf5f4a79f6cf8`.
- Production IDs were verified against the live canonical findings ledger.

Commits:
- resolver mappings: `7800632131f227273ea1395f82794922ea465273`
- super-long regression: `529c74832069fe2a63ce24c02ee56567df4fafc8`
- Wit regression: `9c35c439a39a4328c743c400fe78872cce12d949`

Sync-context run `33411608616` was triggered by the resolver mapping commit and was in progress when this checkpoint was written. Do not count the affected findings resolved until generated ledger state and validation are confirmed on live main.
