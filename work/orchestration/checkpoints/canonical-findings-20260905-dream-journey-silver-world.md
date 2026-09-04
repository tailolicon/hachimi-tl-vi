# Canonical finding checkpoint — Dream Journey silver world unique Skill

Finding: `cf-1900e9e9aa8bd7ec`
Source zh-CN alias: `梦寐中的银色世界`
Verified JP identity: `夢寐に見る銀世界`
Canonical target: `Cõi Bạc Trong Mộng`

## Live diagnosis

The live finding is an active proper-name blocker under `scripts/canonical_findings.py::active_findings`: status `open`, no canonical resolution, and a historical `defer` review decision. Its three evidence rows are inheritance-factor keys `text_data_dict.json` `172/11190201`, `172/11190202`, and `172/11190203`.

Repository evidence ties locator family `111902` to Dream Journey. Independent JP references identify Skill `111191` and inherited Skill `911191` as `夢寐に見る銀世界`, the unique Skill of `[雪白の夢路] ドリームジャーニー` (Dream Journey Christmas). This establishes identity without relying on the zh-CN semantic bridge.

`夢寐に見る` is the world seen in dreams; `銀世界` is the poetic silver/white world of a snowy landscape. The project target is therefore `Cõi Bạc Trong Mộng`, replacing the stiff historical calque `Thế giới bạc trong giấc mơ` while retaining the Japanese title's imagery.

## Durable repair

- `scripts/harden_dream_journey_silver_world_finding.py` adds one source-path-scoped community Skill identity and a reviewed lock for `梦寐中的银色世界`.
- Implementation commit: `2c99fe4b9aa5c50f2d729c8b1037ac24afd34ab1`.
- `tests/test_dream_journey_silver_world_finding_hardening.py` covers idempotence, replacement of the historical defer, canonical resolution of the live finding shape, and negative source-path coverage.
- Regression commit: `15c01007297be040f885936d424f06ab65c1ebf0`.
- The regression logic was also executed directly in the local repository environment because the host interpreter does not have pytest installed; both test functions passed. Production acceptance still requires repository Validate + Context Sync + Review-plan Sync.

## Acceptance status

Do not increment maintenance `completed_count` yet. Wait for the production workflows triggered by the durable commits, then verify the regenerated live canonical finding is resolved and the review plan no longer exposes this canonical blocker. Continue from this checkpoint if acceptance is still pending.
