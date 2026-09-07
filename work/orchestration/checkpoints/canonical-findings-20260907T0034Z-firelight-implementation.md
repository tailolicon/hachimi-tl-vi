# Canonical finding implementation — Firelight

- Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260907T001306Z`
- Finding: `cf-3a460c751596bfac`
- zh-CN bridge alias: `灯穗`
- JP identity: `灯穂`
- Skill ID: `110341`
- Canonical target: `Firelight`

## Evidence update

The earlier repository research checkpoint intentionally left this finding unresolved until stronger player-facing English evidence existed. That condition is now met: current independent English community references `umamusu.wiki` and `uma.guide` both render the `[Fields of Gold]` Inari One unique Skill `灯穂` as `Firelight`, while the current Global release window for `[Fields of Gold]` is active.

## Durable implementation

- `scripts/harden_firelight_finding.py` locks `灯穗 -> Firelight`, scoped to `text_data_dict.json`, item invalidation, contains matching; historical `Bông lúa ánh sáng` is forbidden.
- `tests/test_firelight_finding_hardening.py` covers idempotence, canonical/review resolution, active-finding removal, and wrong-source-path isolation.
- Implementation commits: `fef1181799397264382c8f5854db760f0adec9c5`, `9c991d1433c1e2e6aaf609959c52290cb555d1bb`.
- Fresh `origin/main` direct verification passed syntax, idempotence, canonical target `Firelight`, review lock, and isolated `active_findings() == []`.

Production Validate/Sync acceptance remains required before counting this finding complete.
