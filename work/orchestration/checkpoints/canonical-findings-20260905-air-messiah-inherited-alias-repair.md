# Canonical finding checkpoint — Air Messiah inherited alias repair

Finding: `cf-187722b45a122b68`
Source alias: `相依血脉 开花未来`
Verified JP identity: `辿る血脈、芽吹く未来` (Air Messiah unique Skill)
Canonical target: `Theo Dấu Huyết Mạch, Tương Lai Nảy Mầm`

## Live diagnosis

The earlier Air Messiah hardener covered the standalone zh-CN Skill title `相依血脉,开花未来`, but the current generated retrospective ledger also contains a distinct inheritance-factor finding whose alias uses a space separator: `相依血脉 开花未来`. That row is `status: open`, `match_mode: contains`, has no path-prefix restriction, and still had both `canonical_resolution: null` and `review_resolution: null`.

This is the same Skill identity, not a second translation standard. Repository evidence and JP references already establish `辿る血脈、芽吹く未来`; the accepted project title remains `Theo Dấu Huyết Mạch, Tương Lai Nảy Mầm` because it preserves JP `辿る` (following/tracing) and `芽吹く` (budding/sprouting), avoiding the zh-CN bridge's altered dependence/blooming imagery.

## Durable repair

- `scripts/harden_air_messiah_bloodline_future_finding.py` now includes both zh-CN punctuation aliases on the same canonical Skill identity and persists a dedicated review lock for the inheritance alias. Implementation commit: `1c06542738dbac5d5ed67c53812849b19c9677c1`.
- `tests/test_air_messiah_bloodline_future_finding_hardening.py` now exercises both the standalone and inherited generated finding shapes, idempotence, longer-source contains behavior, and source-path negative coverage. Regression commit: `38a7aa0f688ac2b0019c38f8bebd17ebd152a66a`.

## Acceptance status

Production acceptance is not claimed yet. Validate and generated-context/review-plan Sync triggered from the regression commit must pass, and the regenerated live canonical-findings ledger must show `cf-187722b45a122b68` resolved before `completed_count` advances from 120.
