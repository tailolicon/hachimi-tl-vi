# Canonical finding checkpoint — 脚色十分

Finding: `cf-642f6b7fcbe6af58`
Source: `脚色十分`
Key: `localize_dict.json` / `Race9467001`
Observed current target: `Dư lực dồi dào`
Target: `Fully Charged`

## Diagnosis

`脚色十分` is the named race mechanic/state whose English/Global terminology is `Fully Charged`. The source finding is exact and belongs to the dedicated `Race9467001` localize key, so the canonical rule is deliberately key-scoped rather than generalized to prose.

## Durable implementation

- `scripts/harden_fully_charged_finding.py` adds exact item-scoped community rule `race_state.fully_charged` and terminology decision `audit.finding.race-state-fully-charged`, both restricted to `localize_dict.json` key `Race9467001`.
- Hardener commit: `d698be10b27bc242631c2d5b0a2969a5e6673bf5`.
- `tests/test_fully_charged_finding_hardening.py` proves positive canonical resolution on `Race9467001`, idempotence, and negative non-resolution on a neighboring localize key.
- Regression commit: `d575c97fb7d2de51e95903ffbc6664e4059ad014`.

## Acceptance pending

Maintenance remains at 129. Require production Validate, Context Sync, Translation Review Plan, live canonical materialization, terminology-queue removal, and worker-facing blocker removal before incrementing 129 -> 130.
