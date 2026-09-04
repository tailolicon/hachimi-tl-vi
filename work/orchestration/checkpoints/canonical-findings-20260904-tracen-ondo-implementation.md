# Canonical finding implementation — Tracen Ondo

Finding: `cf-5c83fe60c17ea214`

- source title: `トレセン音頭`
- live item: `text_data_dict.json` category `16`, entry `1083`
- canonical target: `Tracen Ondo`

## Evidence basis

Official Lantis WINNING LIVE 13 lists `トレセン音頭` as the Uma Musume 2.5th-anniversary song. English-facing music catalogs for the same Lantis release identify the track as `Tracen Ondo`, and established Uma Musume discography references use the same Latin/Romanized identity. The current Vietnamese `Điệu ondo Tracen` is a semantic/localized rearrangement rather than the canonical song title.

## Implementation

- hardener: `scripts/harden_tracen_ondo_finding.py`
- regression: `tests/test_tracen_ondo_finding_hardening.py`
- community rule: `song.tracen_ondo`
- terminology decision: `audit.finding.song-tracen-ondo`
- source scope: exact match in `text_data_dict.json`
- forbidden targets include source-script leakage and historical `Điệu ondo Tracen`

Regression requires idempotence, community + review resolution of the exact live finding shape, removal from `active_findings`, and negative coverage proving the rule does not match longer prose or another source file.

## Acceptance complete

Accepted on 2026-09-04 using implementation commit `ee83cbaf80dc2354840d2c3e8adcb03a3f760666`, which contains both hardener and regression:

- Validate run `33821281944` completed successfully.
- Sync translation context run `33821281963` attempt 1 completed with a publish-only failure caused by concurrent `main` updates and repeated rebase conflict in generated `glossary/terminology_review_queue.json`; the pipeline itself passed 627 tests. The failed jobs were rerun and attempt 2 completed successfully.
- Sync translation review plan run `33821282002` completed successfully.
- live review plan `tr-p3-67f8551f7780-9a8edf935615-b5c0bcb3bd-224165957c`, item `text_data_dict.json` `16/1083`, embeds `song.tracen_ondo` with preferred `Tracen Ondo`.
- that live item has `canonical_findings: []`, so `cf-5c83fe60c17ea214` no longer blocks review.

Maintenance `completed_count` may advance from 65 to 66. `cf-b74bd0c4b24ab2af` / `ドロワダンスパート` remains evidence-blocked and must not be guessed. Positive research checkpoints now exist for later active findings `cf-b620a9b9adbb1efa` / `ソシテミンナノ` (`Soshite Minna no`) and `cf-786f492ee1495f8f` / `爆熱マイソウル` (`Bakunetsu My Soul`).