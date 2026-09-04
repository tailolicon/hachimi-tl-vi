# Canonical findings maintenance checkpoint — Yoshiko NPC item ignore accepted

Finding `cf-53209016ce00c5d2` (`佳子(NPC)`) is accepted as an item-scoped ignore rather than a reusable romanization lock.

## Durable implementation

- Hardener: `scripts/harden_yoshiko_npc_finding.py` at `dbe92a65a6f415875efab6d8f9db7518956023d4`.
- Regression: `tests/test_yoshiko_npc_finding_hardening.py` at `ba9c914e579fe281709eb7ce399190431e2dfffc`.
- Scope is limited to exact `text_data_dict.json` category-152 item paths `21`, `55`, `89`, `123`, `157`, `191`.
- The resolution deliberately does not canonize `Yoshiko` and does not broaden matching to category `152`.

## Acceptance evidence

All required production workflows on regression head `ba9c914e579fe281709eb7ce399190431e2dfffc` completed successfully:

- Validate run `33896054484`: success.
- Sync translation context run `33896054497`: success.
- Sync translation review plan run `33896054504`: success.

Live regenerated review artifact `b0137` shows `text_data_dict.json` path `152/191` for `佳子(NPC)` with `canonical_findings: []`. Live category-152 batches still retain unrelated open proper-name findings such as `光(NPC)`, `由加里(NPC)`, `兰(NPC)`, `理沙(NPC)`, and `和树(NPC)`, demonstrating that the item-scoped resolution did not broaden to the category.

Maintenance sequencing may advance `completed_count` from 112 to 113. Successor routing must re-read the live canonical-finding ordering from main before selecting the next finding.
