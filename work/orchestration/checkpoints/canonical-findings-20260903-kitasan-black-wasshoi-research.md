# Canonical finding research: Kitasan Black / Wasshoi

- Finding: `cf-64aebd49fa203b6b`
- zh-CN source: `胜利呐喊Wasshoi！`
- Current Vietnamese: `Tiếng hô chiến thắng Wasshoi!`
- Skill ID: `100681`
- Character: Kitasan Black `[錦上・大判御輿]`

## Verified JP identity

Current Japanese Skill references consistently identify Skill ID `100681` as:

`勝ち鬨ワッショイ！`

The title combines `勝ち鬨` (a victory/battle cry) with the preserved cultural exclamation `ワッショイ / Wasshoi`. The zh-CN bridge already keeps `Wasshoi`; the current Vietnamese likewise preserves that distinctive element and naturally renders the victory-cry portion.

## Project canonical

`Tiếng hô chiến thắng Wasshoi!`

Rationale:
- preserves `Wasshoi` instead of translating away the culturally distinctive title element;
- naturally conveys `勝ち鬨` as a victory cry;
- matches the already-localized live string, so resolving this finding should stabilize identity rather than introduce churn;
- this is a project Vietnamese canonical title, not an asserted official Global localization.

A category/path-scoped canonical rule can safely lock this exact Skill title for `text_data_dict.json` category `147` without affecting generic uses of `胜利`, `呐喊`, or `Wasshoi` elsewhere.
