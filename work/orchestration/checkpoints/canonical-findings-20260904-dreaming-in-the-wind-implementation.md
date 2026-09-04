# Canonical finding implementation — Dreaming in the Wind

Finding: `cf-29762b18682213f5c888aacf`

- live zh-CN title: `梦疾风`
- JP title: `夢疾風`
- live item: `text_data_dict.json` category `16`, entry `1166`
- canonical target: `Dreaming in the Wind`

## Evidence basis

The live zh-CN title maps directly to Mr. C.B.'s `WINNING LIVE 24` solo song `夢疾風`. Lantis-distributed English storefront metadata publishes the track as `Dreaming in the Wind`. Preserve that stable English-facing proper-name identity instead of the semantic Vietnamese rendering `Cuồng phong giấc mơ`.

## Implementation

- regression: `tests/test_dreaming_in_the_wind_finding_hardening.py`
- hardener: `scripts/harden_dreaming_in_the_wind_finding.py`
- community rule: `song.dreaming_in_the_wind`
- terminology decision: `audit.finding.song-dreaming-in-the-wind`
- source scope: exact match in `text_data_dict.json`

Implementation commits on live `main`:

- regression commit `9b5acbad8440adc7323e543e6099c2bc8c69a833`
- original hardener commit `9cba679795238ca5b6795abc1b3fa94fc76ae8a8`
- replay-safety fix `221961d01455b6c06fcde0632f589fb777709b49`

## Acceptance status

Accepted in production.

- Replay-safety fix passed Validate/pytest.
- Production Sync translation context run `33825873073` succeeded, including all finding hardeners and context-pipeline tests.
- Production Sync translation review plan run `33825873089` succeeded.
- Published live plan `tr-p3-67f8551f7780-bdff91d1f88f-b5c0bcb3bd-3f3fefbe8d`, batch `b0176`, embeds `song.dreaming_in_the_wind` / `Dreaming in the Wind` for `text_data_dict.json` `16/1166` with `canonical_findings: []`.
