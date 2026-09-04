# Canonical finding implementation — PisuPisu☆SupiSupi Golshi-chan no Uta

Finding: `cf-7e18117a4f949bb6`

- source title: `ピスピス☆スピスピ ゴルシちゃんのうた`
- live item: `text_data_dict.json` category `16`, entry `1127`
- canonical target: `PisuPisu☆SupiSupi Golshi-chan no Uta`

## Evidence basis

Official Lantis WINNING LIVE 20 lists the exact Japanese title as track 5, sung by Gold Ship. Established English-facing Uma Musume discography references consistently render the title as `PisuPisu☆SupiSupi Golshi-chan no Uta`. Preserve that stable Latin/Romanized proper-name identity instead of the mixed semantic Vietnamese rendering `Bài ca Pisu Pisu☆Supi Supi của Golshi-chan`.

## Implementation

- hardener: `scripts/harden_pisupisu_supisupi_golshi_song_finding.py`
- regression: `tests/test_pisupisu_supisupi_golshi_song_finding_hardening.py`
- community rule: `song.pisupisu_supisupi_golshi_chan_no_uta`
- terminology decision: `audit.finding.song-pisupisu-supisupi-golshi-chan-no-uta`
- source scope: exact match in `text_data_dict.json`
- exact matching is required because the finding source is the complete reviewed title and must not generalize title fragments into prose.

Implementation commits on live `main`:

- hardener commit `ae7aa0460121fb2c17205b54ce5f494d12e2e507`
- regression commit `f53acc011d433b5759fbd3945abed355d925c390`

## Acceptance status

Pending production acceptance. Do not advance the maintenance completed count until Validate, Sync translation context, and Sync translation review plan succeed and the live generated review item `text_data_dict.json` `16/1127` embeds `song.pisupisu_supisupi_golshi_chan_no_uta` / `PisuPisu☆SupiSupi Golshi-chan no Uta` with `canonical_findings: []`.
