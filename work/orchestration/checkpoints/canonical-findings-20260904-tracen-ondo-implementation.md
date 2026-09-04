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

## Acceptance pending

Do not increment maintenance `completed_count` beyond 65 until Validate, Sync translation context, and Sync translation review plan all succeed on commit `ee83cbaf80dc2354840d2c3e8adcb03a3f760666` (or a later commit containing both hardener and regression), then verify live `16/1083` embeds `song.tracen_ondo` / `Tracen Ondo` with `cf-5c83fe60c17ea214` absent from canonical blockers.
