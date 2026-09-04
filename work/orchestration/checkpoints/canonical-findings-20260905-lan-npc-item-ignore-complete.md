# Canonical findings maintenance checkpoint — Lan NPC item ignore complete

Finding `cf-d4452115173b9c65` (`兰(NPC)`) is production-accepted as an exact item-scoped ignore for `text_data_dict.json` paths `152/33`, `152/67`, `152/101`, `152/135`, `152/169`, and `152/203`. This intentionally does not canonize `Ran` or any other reading from repository evidence alone.

Implementation evidence:
- hardener commit `93cde92d7d14a2f7510d3654d504c7de452f7a4e`
- regression head `aa786d8969a3eb33c57a683e4b5338786320103c`

Acceptance evidence for `aa786d8969a3eb33c57a683e4b5338786320103c`:
- Validate run `33898760629`: success
- Sync translation context run `33898760603`: success
- Sync translation review plan run `33898760613`: success
- regenerated active-plan batch `b0138` shows exact item `text_data_dict.json` path `152/33`, source `兰(NPC)`, with `canonical_findings: []`
- the immediately adjacent `152/34` `理沙(NPC)` still carries active finding `cf-310693893cdc8eef`, proving the ignore did not suppress unrelated category-152 blockers.

Maintenance completed count may advance from 115 to 116 for this accepted finding.
