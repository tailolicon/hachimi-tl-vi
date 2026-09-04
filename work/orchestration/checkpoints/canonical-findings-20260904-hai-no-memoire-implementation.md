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

Accepted in production.

- Validation passed for the final replay-safe canonical surface.
- Production Sync translation context run `33825873073` succeeded.
- Production Sync translation review plan run `33825873089` succeeded.
- Published live plan `tr-p3-67f8551f7780-bdff91d1f88f-b5c0bcb3bd-3f3fefbe8d`, batch `b0176`, embeds `song.hai_no_memoire` / `Hai no memoire` for `text_data_dict.json` `16/1159` with `canonical_findings: []`.
