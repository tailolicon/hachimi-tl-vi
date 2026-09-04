# Canonical findings maintenance checkpoint — Keisuke NPC item ignore accepted

Finding `cf-1edf7f36acfffbfb` (`圭介(NPC)`) is accepted as an item-scoped ignore rather than a reusable romanization lock.

## Durable implementation

- Hardener: `scripts/harden_keisuke_npc_finding.py`.
- Regression: `tests/test_keisuke_npc_finding_hardening.py`, regression head `4f0eef01d7bca1b9ab5e78871db9ec31016d32fa`.
- Scope is limited to exact `text_data_dict.json` category-152 item paths `3`, `37`, `71`, `105`, `139`, `173`.
- The resolution deliberately does not canonize `Keisuke` and does not broaden matching to category `152`.

## Acceptance evidence

All required production workflows on regression head `4f0eef01d7bca1b9ab5e78871db9ec31016d32fa` completed successfully:

- Validate run `33894181372`: success.
- Sync translation context run `33894181432`: success.
- Sync translation review plan run `33894181496`: success.

The current regenerated review artifact `b0135` shows `text_data_dict.json` path `152/105` for `圭介(NPC)` with `canonical_findings: []`, confirming the blocker is no longer attached to that item under the live plan.

Maintenance sequencing may advance `completed_count` from 114 to 115. Successor routing must re-read live main before selecting the next unresolved finding; ambiguous NPC names should continue to use exact item scope rather than guessed reusable romanizations.
