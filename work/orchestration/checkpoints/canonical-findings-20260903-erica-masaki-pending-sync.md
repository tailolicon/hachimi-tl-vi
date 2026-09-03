# Canonical finding: 真崎エリカ / Erica Masaki

- Live finding: `cf-88ef6b46bebcdb4d`
- Source alias: `真崎エリカ`
- Verified Latin spelling: `Erica Masaki`
- Scope: `text_data_dict.json`, category/path prefix `17`, `match_mode: contains`

## Evidence and rationale

Current retrospective-review batches contained repeated song/staff credits with `真崎エリカ` left in CJK and explicitly flagged the name as a proper-name canonical finding requiring a verified Latin/Roman spelling. External music-credit evidence consistently identifies the lyricist as `Erica Masaki`; MusicBrainz release credits pair `真崎エリカ` with `Erica Masaki` across multiple official releases. The rule is intentionally scoped to category 17 credit text so unrelated prose cannot inherit a person-name substitution.

## Durable implementation

- Hardener: `scripts/harden_erica_masaki_finding.py` (`edbd1a46072e28a4d548342609dd5963c37f9aab`)
- Regression tests: `tests/test_erica_masaki_finding_hardening.py` (`1732ed70117824acfcaf53e6f846fca78c4fc818`)
- Canonical target: `Erica Masaki`
- Rule requires accepted target, forbids the raw CJK name in this scoped player-facing credit context, and is item-scoped.
- Negative tests cover the same alias outside category 17 and outside `text_data_dict.json`.

## Production acceptance

- Validate run `33765716844`: success, including pytest, `tlvi validate`, and index generation.
- Production Sync translation context run `33765716883`: success, including all finding hardeners, canonical finding refresh, context pipeline tests, and generated-context commit step.
- The regenerated live review plan `tr-p3-67f8551f7780-68306370a21d-b5c0bcb3bd-34c0167cc5` materializes `proper_name.erica_masaki.credit17` with target `Erica Masaki`; matching category-17 entries now have `community_terms` and no `cf-88ef6b46bebcdb4d` blocker.

The finding is durably resolved and maintenance `completed_count` may advance from 24 to 25.
