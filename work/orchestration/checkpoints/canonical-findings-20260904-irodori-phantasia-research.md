# Canonical finding implementation — Irodori Phantasia

Finding: `cf-6aa2093f21cdff5c`

- source title: `彩 Phantasia`
- live item: `text_data_dict.json` category `16`, entry `1095`
- current Vietnamese: `Sắc màu Phantasia`
- canonical target: `Irodori Phantasia`

## Evidence

Official Lantis `WINNING LIVE 02` lists `彩 Phantasia` as the exact named song title and identifies its credited performers and creators. Official Lantis event/remix discographies repeatedly preserve the same Japanese title, confirming named-track identity rather than generic prose.

Established English-facing Uma Musume discography references romanize the title as `Irodori Phantasia`. That stable Latin/Romanized identity is preferable for this finding's explicit proper-name requirement to the semantic Vietnamese calque `Sắc màu Phantasia`.

## Implementation

- hardener: `scripts/harden_irodori_phantasia_finding.py`
- regression: `tests/test_irodori_phantasia_finding_hardening.py`
- community rule: `song.irodori_phantasia`
- terminology decision: `audit.finding.song-irodori-phantasia`
- source scope: exact match in `text_data_dict.json`
- forbidden targets include source-script leakage and historical `Sắc màu Phantasia`
- exact matching prevents generic `彩` from leaking into unrelated prose.

Implementation commits observed on live `main`:

- hardener commit `ebcdc5a81d1ae5ab03fd6b1c17c49537705ce37e`
- regression commit `b76fc8f7b504a9fb0cd22ae628b6a4b29cb3fe3a`

## Acceptance status

Pending production acceptance. Do not advance the maintenance completed count until Validate, Sync translation context, and Sync translation review plan succeed and the live generated review item `text_data_dict.json` `16/1095` embeds `song.irodori_phantasia` / `Irodori Phantasia` with `canonical_findings: []`.
