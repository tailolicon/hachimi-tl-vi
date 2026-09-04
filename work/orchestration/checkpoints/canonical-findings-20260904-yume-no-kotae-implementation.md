# Canonical finding implementation — Yume no Kotae

Finding: `cf-73f7016990538048`

- source title: `夢のこたえ`
- live item: `text_data_dict.json` category `16`, entry `1129`
- canonical target: `Yume no Kotae`

## Evidence basis

Official Lantis ANIMATION DERBY Season 3 vol.3 lists `夢のこたえ` as Satono Diamond's named track. Established English-facing Uma Musume discography references romanize the same title as `Yume no Kotae`. Preserve that stable Latin/Romanized proper-name identity instead of the semantic Vietnamese rendering `Lời đáp của giấc mơ`.

## Implementation

- hardener: `scripts/harden_yume_no_kotae_finding.py`
- regression: `tests/test_yume_no_kotae_finding_hardening.py`
- community rule: `song.yume_no_kotae`
- terminology decision: `audit.finding.song-yume-no-kotae`
- source scope: exact match in `text_data_dict.json`
- exact matching is required because the finding source is the complete reviewed song title and must not generalize generic dream/answer prose.

Implementation commits on live `main`:

- hardener commit `59935817163b13dfa96e69c5c4f3f4dcacc394cc`
- regression commit `f0d2c5e394121f36ea7df0c1ed11184e08a8b9e2`

## Acceptance status

Pending production acceptance. Do not advance the maintenance completed count until Validate, Sync translation context, and Sync translation review plan succeed and the live generated review item `text_data_dict.json` `16/1129` embeds `song.yume_no_kotae` / `Yume no Kotae` with `canonical_findings: []`.
