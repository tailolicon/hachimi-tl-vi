# Canonical finding research — 彩 Phantasia

Finding: `cf-6aa2093f21cdff5c`

- source title: `彩 Phantasia`
- live item: `text_data_dict.json` category `16`, entry `1095`
- current Vietnamese: `Sắc màu Phantasia`
- proposed canonical target: `Irodori Phantasia`

## Evidence

Official Lantis `WINNING LIVE 02` lists `彩 Phantasia` as the exact named song title and identifies its credited performers and creators. Official Lantis event/remix discographies repeatedly preserve the same Japanese title, confirming named-track identity rather than generic prose.

Established English-facing Uma Musume discography references romanize the title as `Irodori Phantasia`. That stable Latin/Romanized identity is preferable for this finding's explicit proper-name requirement to the semantic Vietnamese calque `Sắc màu Phantasia`.

## Scope decision

The finding source equals the complete reviewed source text, so use `match_mode: exact`, `source_paths: [text_data_dict.json]`, and item-scoped invalidation. Do not create a reusable rule for the generic character `彩`; the canonical lock must apply only to the complete named song.

## Next step

Implement a permanent hardener + regression using canonical target `Irodori Phantasia`, reject the historical calque and source-script leakage, then require Validate + production context Sync + production review-plan Sync and a live generated-item spot check before acceptance.
