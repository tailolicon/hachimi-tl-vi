# Canonical findings maintenance checkpoint — Sota NPC item ignore accepted

Finding `cf-ad719284aacc4b7f` (`宗太(NPC)`) is accepted as an item-scoped ignore rather than a reusable romanization lock.

## Durable implementation

- Hardener: `scripts/harden_sota_npc_finding.py` at `3b270956`.
- Regression: `tests/test_sota_npc_finding_hardening.py` at `c9ebdb29d5348f04b4ac3b4d5294a0826b4257fa`.
- Scope is limited to exact `text_data_dict.json` category-152 item paths `6`, `40`, `74`, `108`, `142`, `176`.
- The resolution deliberately does not canonize `Sota` and does not broaden matching to category `152`.

## Acceptance evidence

All required production workflows on regression head `c9ebdb29d5348f04b4ac3b4d5294a0826b4257fa` completed successfully:

- Validate run `33894728379`: success.
- Sync translation context run `33894728431`: success.
- Sync translation review plan run `33894728359`: success.

Live regenerated review-plan evidence confirms the Sota item at `text_data_dict.json` path `152/6` has `canonical_findings: []`, while adjacent unrelated NPC findings remain present. This demonstrates the item-scoped ignore applied without broad category overmatch.

Maintenance sequencing may advance `completed_count` from 109 to 110. The next ordered finding remains `cf-2d11e8b41c5d8527` (`太郎(NPC)`), whose hardener/regression are already on main and require fresh successful production acceptance after the Taro regression head before advancing 110 to 111.
