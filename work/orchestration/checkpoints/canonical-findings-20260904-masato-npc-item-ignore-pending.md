# Canonical finding maintenance checkpoint — 正人(NPC)

Finding `cf-1ed10dd6d18561b9` remains under production acceptance. The live retrospective plan `tr-p3-67f8551f7780-7ce4dfb45ab6-b5c0bcb3bd-734a4f22c0` contains four distinct exact occurrences of `正人(NPC)` in `text_data_dict.json`, at paths:

- `152/13`
- `152/115`
- `152/149`
- `152/183`

Because `正人` has multiple valid Japanese readings (including Masato and Masahito), no reusable romanization is being canonized. `scripts/harden_masato_npc_finding.py` now creates an exact item-scoped `ignore` covering only those four paths. This replaces an incomplete concurrent version that covered only `152/183`.

Implementation commits:
- four-path hardener correction: `073c64b7ca3ae13b29238e09b8d7b5d3a37b5f6d`
- regression test: `44fc84b07f4de411585b7c432dec4223ed8b4d76`

Acceptance status:
- Validate run `33890219071`: success.
- Sync translation context run `33890219061`: queued/pending behind the workflow concurrency group at last check.
- Sync translation review plan run `33890219096`: queued/pending at last check.

Do not increment maintenance completion until context sync has persisted the review decision and a regenerated live plan proves `cf-1ed10dd6d18561b9` is no longer an actionable canonical blocker. Do not broaden this to the whole category-152 prefix.
