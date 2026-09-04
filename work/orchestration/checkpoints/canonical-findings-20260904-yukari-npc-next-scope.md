# Canonical findings maintenance checkpoint — next Yukari NPC scope

After production acceptance of `cf-903f94a51b0e869e` (`和树(NPC)`) and advancing maintenance completion to 114, live regenerated batch `b0138` exposes the next unresolved category-152 proper-name finding:

- finding: `cf-6d1975b18f24e5ca`
- source: `由加里(NPC)`
- current localized rendering: `Yukari (NPC)`
- live finding scope is still broad category `152`, so it must not be accepted as-is.

The stable repeated NPC layout plus live/historical review evidence identifies the six exact occurrences as:

- `152/32`
- `152/66`
- `152/100`
- `152/134`
- `152/168`
- `152/202`

`由加里` is not sufficient repository evidence to promote `Yukari` as a reusable canonical reading. The protocol-valid next step is to follow the established ambiguous-NPC pattern: exact item-scoped `ignore`, with an idempotence/scope regression and the full Validate + Sync translation context + Sync translation review plan acceptance gates. Do not broaden to category `152`, and do not increment `completed_count` until production acceptance succeeds.
