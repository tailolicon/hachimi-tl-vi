# Canonical finding implementation — Make debut! (Morishi Remix)

Finding: `cf-5f39dad6eabba899`

- source title: `Make debut! (モリシー (Awesome City Club) Remix)`
- live item: `text_data_dict.json` category `16`, entry `1100`
- canonical target: `Make debut! (Morishi (Awesome City Club) Remix)`

## Evidence basis

Official Lantis WINNING LIVE Remix ALBUM `ぱか☆アゲ↑ミックス` Vol.1 lists the exact remix title with creator spelling `モリシー (Awesome City Club)`. Established English-facing Uma Musume discography references romanize the same creator name as `Morishi`, yielding the stable Latin title `Make debut! (Morishi (Awesome City Club) Remix)`. The current Vietnamese target already uses that Latin spelling; this hardening resolves the proper-name blocker rather than changing correct player-facing text.

## Implementation

- hardener: `scripts/harden_make_debut_morishi_remix_finding.py`
- regression: `tests/test_make_debut_morishi_remix_finding_hardening.py`
- community rule: `song.make_debut_morishi_remix`
- terminology decision: `audit.finding.song-make-debut-morishi-remix`
- source scope: exact match in `text_data_dict.json`
- exact matching is required because the finding source is the complete reviewed title and must not generalize creator-name matching into prose.

Implementation commits observed on live `main`:

- hardener commit `6a4d4190dbe6bfcd2d498eddc08704390c45e863`
- regression commit `d81b1c164884ce0d8d2faa50a951213b6df4f106`

## Acceptance status

Pending production acceptance. Do not advance the maintenance completed count until Validate, Sync translation context, and Sync translation review plan succeed and the live generated review item `text_data_dict.json` `16/1100` embeds `song.make_debut_morishi_remix` / `Make debut! (Morishi (Awesome City Club) Remix)` with `canonical_findings: []`.
