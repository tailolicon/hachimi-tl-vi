# Canonical finding implementation — Super Suki Shuki Rush

Finding: `cf-5fe21392eb60849a`

- live zh-CN title: `超级稀饭♡全力冲击！`
- JP title: `めにしゅき♡ラッシュっしゅ！`
- live item: `text_data_dict.json` category `16`, entry `1156`
- canonical target: `Super Suki Shuki Rush`

## Evidence basis

The live zh-CN title is independently mapped to the Uma Musume 4.5th Anniversary song `めにしゅき♡ラッシュっしゅ！`. Lantis-distributed English storefront metadata publishes that track as `Super Suki Shuki Rush` (digital single released 2025-08-28). Preserve that stable English-facing proper-name identity instead of the semantic Vietnamese rendering `Siêu mê♡Xung kích hết mình!`.

## Implementation

- regression: `tests/test_super_suki_shuki_rush_finding_hardening.py`
- hardener: `scripts/harden_super_suki_shuki_rush_finding.py`
- community rule: `song.super_suki_shuki_rush`
- terminology decision: `audit.finding.song-super-suki-shuki-rush`
- source scope: exact match in `text_data_dict.json`
- exact matching prevents title words from generalizing into ordinary prose.

Implementation commits on live `main`:

- regression commit `cc49d1f6519e9dfe530c5a124cac090af761ae41`
- hardener commit `a916a1f9f698ca1507893aa7cbf1ac41301d5420`

## Acceptance status

Accepted in production.

- Validation passed for the final replay-safe canonical surface.
- Production Sync translation context run `33825873073` succeeded.
- Production Sync translation review plan run `33825873089` succeeded.
- Published live plan `tr-p3-67f8551f7780-bdff91d1f88f-b5c0bcb3bd-3f3fefbe8d`, batch `b0176`, embeds `song.super_suki_shuki_rush` / `Super Suki Shuki Rush` for `text_data_dict.json` `16/1156` with `canonical_findings: []`.
