# Canonical finding evidence — Symboli Rudolf Divine Might

Finding: `cf-331266d60d876889`

## Verified identity

The zh-CN title `汝等,瞻仰皇帝之神威吧` appears at category 147 keys `10170101`–`10170103`, identifying Symboli Rudolf trainee/card id `101701`.

Current JP references identify unique Skill id `100171` as `汝、皇帝の神威を見よ`. Current Global-oriented references consistently render the player-facing title as `Behold Thine Emperor's Divine Might` and tie it to Symboli Rudolf. This is substantially stronger evidence than the existing semantic zh-CN-derived target `Hỡi các ngươi, hãy chiêm ngưỡng thần uy của Hoàng đế`.

## Bounded resolution

Lock exact source `汝等,瞻仰皇帝之神威吧` to `Behold Thine Emperor's Divine Might` for `text_data_dict.json` only. The hardener deliberately uses exact matching so the mapping cannot bleed into unrelated emperor/divine-power prose.

Implementation:
- `scripts/harden_symboli_rudolf_divine_might_finding.py`
- `tests/test_symboli_rudolf_divine_might_finding_hardening.py`

Do not edit `localized_data/**` directly. Context Sync must materialize the canonical and review resolutions before this finding is counted complete.
