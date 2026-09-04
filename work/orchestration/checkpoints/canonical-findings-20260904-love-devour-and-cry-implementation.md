# Canonical finding implementation — Love, Devour, and Cry

Finding: `cf-74981ec2af840898`

- live zh-CN title: `爱舞之，欲噬之。`
- JP title: `愛舞い、喰らい。`
- live item: `text_data_dict.json` category `16`, entry `1164`
- canonical target: `Love, Devour, and Cry`

## Evidence basis

The live zh-CN title maps to Still in Love's `WINNING LIVE 21` solo song `愛舞い、喰らい。`. Lantis-distributed English storefront metadata publishes the track as `Love, Devour, and Cry`. Preserve that stable English-facing proper-name identity instead of the semantic Vietnamese rendering `Múa vì yêu, muốn nuốt trọn.`.

## Implementation

- regression: `tests/test_love_devour_and_cry_finding_hardening.py`
- hardener: `scripts/harden_love_devour_and_cry_finding.py`
- community rule: `song.love_devour_and_cry`
- terminology decision: `audit.finding.song-love-devour-and-cry`
- source scope: exact match in `text_data_dict.json`

Implementation commits on live `main`:

- regression commit `66e7f728744b47b7ce8afbf98566cd4ae48f4767`
- hardener commit `e0dae62f73fa471409e9955a01d10792adf96991`

## Acceptance status

Accepted in production.

- Validation passed for the final replay-safe canonical surface.
- Production Sync translation context run `33825873073` succeeded.
- Production Sync translation review plan run `33825873089` succeeded.
- Published live plan `tr-p3-67f8551f7780-bdff91d1f88f-b5c0bcb3bd-3f3fefbe8d`, batch `b0176`, embeds `song.love_devour_and_cry` / `Love, Devour, and Cry` for `text_data_dict.json` `16/1164` with `canonical_findings: []`.
