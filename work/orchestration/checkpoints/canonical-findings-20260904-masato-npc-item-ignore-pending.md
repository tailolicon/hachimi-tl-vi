# Canonical finding maintenance checkpoint — 正人(NPC) accepted

Finding `cf-1ed10dd6d18561b9` is production-accepted as an exact item-scoped `ignore`. The live retrospective plan contains four distinct occurrences of `正人(NPC)` in `text_data_dict.json`, at paths:

- `152/13`
- `152/115`
- `152/149`
- `152/183`

Because `正人` has multiple valid Japanese readings (including Masato and Masahito), no reusable romanization is canonized. `scripts/harden_masato_npc_finding.py` covers only those four exact paths; category `152` is not broadly ignored.

Implementation:
- four-path hardener correction: `073c64b7ca3ae13b29238e09b8d7b5d3a37b5f6d`
- regression test: `44fc84b07f4de411585b7c432dec4223ed8b4d76`
- production persistence: `f7c2a6b25514d186dac403a20824971c0f0a5c58` updated `glossary/terminology_reviews.json` from the prior single-path decision to all four exact paths.

Production acceptance:
- Validate run `33890219071`: success, including pytest and CLI validation.
- Sync translation review plan run `33890219096`: success; its generated-state commit persisted the four exact item scopes.
- Sync translation context run `33890219061`: success; all finding hardeners, canonical refresh/resolvers, context tests, and generated-context persistence step succeeded.
- Current worker-facing batches `b0135`, `b0136`, and `b0137` still contain the affected source items but no longer contain `cf-1ed10dd6d18561b9`; unrelated NPC canonical findings remain present, proving the ignore is scoped rather than broad.

Maintenance completion may advance from 103 to 104 for this accepted unit. Keep `灯穂` / Inari One deferred until authoritative Global evidence is available on or after 2026-09-06.
