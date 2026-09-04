# Canonical findings maintenance checkpoint — Taro NPC item ignore accepted

Finding `cf-2d11e8b41c5d8527` (`太郎(NPC)`) is accepted as an item-scoped ignore rather than a reusable romanization lock.

## Durable implementation

- Hardener: `scripts/harden_taro_npc_finding.py` at `2afbc44b`.
- Regression: `tests/test_taro_npc_finding_hardening.py` at `5b47f414ab807a5420944d078c38d1c7944dc55a`.
- Scope is limited to exact `text_data_dict.json` category-152 item paths `7`, `41`, `75`, `109`, `143`, `177`.
- The resolution deliberately does not canonize `Taro` and does not broaden matching to category `152`.

## Acceptance evidence

- Validate run `33895032735` on the Taro regression head completed successfully.
- Sync translation review plan run `33895032754` on the Taro regression head completed successfully.
- The Taro-head context Sync was cancelled by workflow concurrency, but later production Context Sync run `33895192639` completed successfully on head `6beac381437560c5df0b019bd571813b41b45bb7`, which contains the Taro hardener and regression unchanged.
- Live regenerated review artifacts show both sampled endpoints `152/7` and `152/177` for `太郎(NPC)` with `canonical_findings: []`, while unrelated category-152 proper-name findings remain open elsewhere. This demonstrates that the item-scoped ignore applied without broad category overmatch.

Maintenance sequencing may advance `completed_count` from 110 to 111. The next ordered finding remains `cf-bde1cb5a78cf5e14` (`司(NPC)` / current rendering `Tsukasa (NPC)`), whose exact-item hardener and regression are already on main and require successful production acceptance before advancing 111 to 112.
