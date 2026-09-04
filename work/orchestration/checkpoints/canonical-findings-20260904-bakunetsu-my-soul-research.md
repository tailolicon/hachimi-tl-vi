# Canonical finding research — 爆熱マイソウル

Finding: `cf-786f492ee1495f8f`

- source title: `爆熱マイソウル`
- live item: `text_data_dict.json` category `16`, entry `1088`
- current Vietnamese: `My Soul bùng cháy`
- candidate Latin/Romanized identity: `Bakunetsu My Soul`

## Evidence checked

- The title is a named Uma Musume song and the U.A.F. Ready GO! scenario theme, released on `WINNING LIVE 18` on 2024-04-17.
- Established Uma Musume discography references consistently romanize `爆熱マイソウル` as `Bakunetsu My Soul`, including WINNING LIVE 18 and later solo-vocal listings.
- An English semantic gloss `Big Bang! My Soul` appears in community metadata, but the canonical finding asks for a verified Latin/Romanized identity. The stable catalog/discography Romanization is `Bakunetsu My Soul`.

## Decision

Evidence is sufficient for a future exact song-title lock to `Bakunetsu My Soul` if this finding remains active when routed. Do not preserve the mixed semantic Vietnamese `My Soul bùng cháy`, and do not substitute a semantic English gloss where the repository requires the Latin/Romanized proper-name identity.

Implementation should use an exact `text_data_dict.json` item-scoped community song rule plus terminology lock, with idempotent regression and negative coverage for longer prose/other source files. Acceptance requires normal Validate + production context/review sync gates and live generated-context verification.
