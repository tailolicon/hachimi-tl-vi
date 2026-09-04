# Canonical findings maintenance checkpoint — Tsukasa NPC item ignore accepted

Finding `cf-bde1cb5a78cf5e14` (`司(NPC)`) is accepted as an item-scoped ignore rather than a reusable romanization lock.

## Durable implementation

- Hardener: `scripts/harden_tsukasa_npc_finding.py` at `6beac381437560c5df0b019bd571813b41b45bb7`.
- Regression: `tests/test_tsukasa_npc_finding_hardening.py` at `00aebf597823cf41b01caa88ba889d982882643d`.
- Scope is limited to exact `text_data_dict.json` category-152 item paths `8`, `42`, `76`, `110`, `144`, `178`.
- The resolution deliberately does not canonize `Tsukasa` and does not broaden matching to category `152`.

## Acceptance evidence

All required production workflows on regression head `00aebf597823cf41b01caa88ba889d982882643d` completed successfully:

- Validate run `33895209487`: success.
- Sync translation context run `33895209352`: success.
- Sync translation review plan run `33895209353`: success.

Live regenerated review artifacts show `152/8` and `152/178` for `司(NPC)` with `canonical_findings: []`. The same live batch containing `152/8` still carries an unrelated open proper-name finding for `佳子(NPC)` at `152/89`, demonstrating that the resolution did not broaden to category `152`.

Maintenance sequencing may advance `completed_count` from 111 to 112. Successor routing must re-read the live canonical-finding order from main before selecting the next finding.
