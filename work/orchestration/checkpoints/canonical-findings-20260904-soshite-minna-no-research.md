# Canonical finding research — ソシテミンナノ

Finding: `cf-b620a9b9adbb1efa`

- source title: `ソシテミンナノ`
- live item: `text_data_dict.json` category `16`, entry `1084`
- current Vietnamese: `Và rồi, của mọi người`
- candidate Latin/Romanized identity: `Soshite Minna no`

## Evidence checked

- Official Lantis `ANIMATION DERBY Season 3 vol.1「ソシテミンナノ」` (LACM-24452, released 2023-11-01) confirms the exact Japanese title and that it is the TV anime Season 3 opening theme.
- Established Uma Musume discography references romanize the release and track as `Soshite Minna no`, including the album title `ANIMATION DERBY Season 3 vol.1 "Soshite Minna no"` and track 1 `Soshite Minna no`.
- English-facing anime-song references independently map Japanese `ソシテミンナノ` to `Soshite Minna no`.
- One community wiki additionally supplies semantic English `Be Their Beloved`. That is useful explanatory translation, but it does not displace the established Latin/Romanized catalog identity requested by this canonical finding.

## Decision

Evidence is sufficient for a future exact song-title lock to `Soshite Minna no` if this finding remains active when routed. Do not use the current semantic Vietnamese `Và rồi, của mọi người` as the proper-name identity, and do not substitute the explanatory English `Be Their Beloved` where the repository asks specifically for verified Latin/Romanized identity.

Implementation should use an exact `text_data_dict.json` item-scoped community song rule plus terminology lock, with idempotent regression and negative coverage for longer prose/other source files. Acceptance requires normal Validate + production context/review sync gates and live generated-context verification.
