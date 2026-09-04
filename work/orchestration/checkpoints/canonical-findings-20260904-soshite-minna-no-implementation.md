# Canonical finding implementation — Soshite Minna no

Finding: `cf-b620a9b9adbb1efa`

- source title: `ソシテミンナノ`
- live item: `text_data_dict.json` category `16`, entry `1084`
- canonical target: `Soshite Minna no`

## Evidence basis

Official Lantis `ANIMATION DERBY Season 3 vol.1「ソシテミンナノ」` identifies the exact Japanese title as the TV anime Season 3 opening theme. Established Uma Musume discography and English-facing anime-song references romanize the same release and track as `Soshite Minna no`. The current Vietnamese `Và rồi, của mọi người` is a semantic rendering rather than the established Latin/Romanized proper-name identity.

## Implementation

- hardener: `scripts/harden_soshite_minna_no_finding.py`
- regression: `tests/test_soshite_minna_no_finding_hardening.py`
- community rule: `song.soshite_minna_no`
- terminology decision: `audit.finding.song-soshite-minna-no`
- source scope: exact match in `text_data_dict.json`
- forbidden targets include source-script leakage and historical `Và rồi, của mọi người`

Implementation commits observed on live `main`:

- hardener commit `769a41dfe613295d6495374e63973438ca9dd89a`
- regression commit `8f9fd072f3509b8ed3a417caad7f2a2d508c6b05`

## Acceptance status

- Validate run `33821819685`: success.
- Sync translation context run `33821819713`: success; production sync published canonical/context changes to live `main`.
- Sync translation review plan run `33821819730`: still pending at the latest check.

Do **not** advance the maintenance completion count until review-plan sync succeeds and the live generated review item `text_data_dict.json` `16/1084` embeds `song.soshite_minna_no` / `Soshite Minna no` with `canonical_findings: []`. If the review-plan run remains pending, continue other protocol-valid maintenance research without claiming acceptance early.
