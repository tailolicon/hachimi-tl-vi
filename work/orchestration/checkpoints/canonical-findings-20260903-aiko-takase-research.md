# Canonical finding research — `高瀬愛虹`

Finding: `cf-0c148b50fe9cd57f`

## Live finding evidence

- `status: open`, `match_mode: contains`, source path `text_data_dict.json`, scope `[["17"]]`.
- Retained evidence is song/staff credit `text_data_dict.json/17/1050`, where current Vietnamese still leaves `高瀬愛虹` in CJK.
- The finding explicitly requires a verified Latin/Roman spelling rather than a guessed local transliteration.

## Identity evidence

- The lyricist's own website is titled `TAKASE AIKO WEB SITE` and gives the identity `高瀬愛虹（たかせあいこ）`, directly verifying surname Takase and given name Aiko.
- The Heart Company work page for Uma Musume 1st Anniversary `We are DREAMERS!!` credits `作詞：高瀬愛虹`, independently tying this exact Japanese identity to an Uma Musume lyric credit.
- English-language music metadata/catalog sources render `高瀬愛虹` as `Aiko Takase`, consistent with the self-published reading and Western-order Latin credit style already used by this repository for creator names.

## Canonical decision

Lock `高瀬愛虹` to `Aiko Takase` for `text_data_dict.json` category 17 credit text only. Use `match_mode: contains`, item-scoped invalidation, and a terminology-review lock so the name can be replaced inside a complete multi-credit line without broadening to unrelated text.

## Required regression

The permanent test must prove idempotence, category-17 contained-name matching, no match outside category 17, terminology-review target `Aiko Takase`, finding canonical resolution, and removal from `active_findings()`.
