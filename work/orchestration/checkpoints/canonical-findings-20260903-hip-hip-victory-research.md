# Canonical finding research — `どどっと優勝！大感謝祭！！！`

Finding: `cf-09acdcebbe013cfd`

## Live finding evidence

- `status: open`, `match_mode: exact`, source path `text_data_dict.json`.
- Sole retained evidence is `text_data_dict.json/16/1085` with current Vietnamese `Chiến thắng ào ạt! Đại lễ cảm ơn!!!`.
- The worker finding correctly refuses to lock that semantic Vietnamese calque without a verified proper-title identity.

## Identity research

- Cygames' official Japanese portal identifies `どどっと優勝！大感謝祭！！！` as the theme song of `ウマ娘 プリティーダービー 熱血ハチャメチャ大感謝祭！` and as a track on WINNING LIVE 21.
- The English digital distribution published by Lantis/Apple Music exposes the same August 30, 2024 single under the English title `Hip Hip Victory! It's the Fan Fest!`.
- English Party Dash credits independently expose the theme as `Hip Hip Victory! It's the Fan Fest`, reinforcing that this is a published English proper-title identity rather than a worker-authored translation.
- Community discography sources also map the Japanese title to Romanized `Dodo tto Yuushou! Dai Kanshasai!!!`, but repository canonical policy prefers a verified official English/Global identity when available.

## Canonical decision

Lock exact Japanese source `どどっと優勝！大感謝祭！！！` in `text_data_dict.json` category 16 to:

`Hip Hip Victory! It's the Fan Fest!`

Do not retain the semantic Vietnamese calque as the player-facing song title. Add an item-scoped song rule plus terminology-review lock. Because the worker finding omitted `json_path_prefixes` even though all retained evidence proves category 16, repair that finding scope to `[["16"]]` before resolution refresh, mirroring the proven Ichibanboshi song-finding pattern.

## Required regression

The permanent test must prove:

1. hardening is idempotent;
2. category-16 exact source matches the official English title;
3. longer prose containing the title does not overmatch;
4. the malformed live finding scope is repaired only when evidence proves category 16;
5. `refresh_canonical_resolutions()` resolves `cf-09acdcebbe013cfd` to the new song term and removes it from `active_findings()`.
