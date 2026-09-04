# Canonical finding implementation — Hai no memoire

Finding: `cf-71ebad8d272930b0`

- live zh-CN title: `灰之memoire`
- JP title: `灰のmemoire`
- live item: `text_data_dict.json` category `16`, entry `1159`
- canonical target: `Hai no memoire`

## Evidence basis

The live zh-CN title maps directly to the Lantis `WINNING LIVE 27` song `灰のmemoire`, released in 2025. Established English-facing Uma Musume discography references render the title as `Hai no memoire`. Preserve that stable Latin/Romanized proper-name identity instead of the semantic Vietnamese rendering `Memoire màu tro`.

## Implementation

- regression: `tests/test_hai_no_memoire_finding_hardening.py`
- hardener: `scripts/harden_hai_no_memoire_finding.py`
- community rule: `song.hai_no_memoire`
- terminology decision: `audit.finding.song-hai-no-memoire`
- source scope: exact match in `text_data_dict.json`

Implementation commits on live `main`:

- regression commit `b17558679bb77899456c38a132d816212ac82ea0`
- hardener commit `4236ac588cb2a0a4f7980c609bb2f59ad63e8877`

## Acceptance status

Pending production acceptance. Do not advance the maintenance completed count until required Validate, Sync translation context, and Sync translation review plan workflows succeed and the then-live generated review item `text_data_dict.json` `16/1159` embeds `song.hai_no_memoire` / `Hai no memoire` with `canonical_findings: []`.
