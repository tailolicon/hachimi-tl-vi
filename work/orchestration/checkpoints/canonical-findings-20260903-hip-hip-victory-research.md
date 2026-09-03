# Canonical finding maintenance — `どどっと優勝！大感謝祭！！！`

Finding: `cf-09acdcebbe013cfd`

## Live finding evidence

- Original finding: `status: open`, `match_mode: exact`, source path `text_data_dict.json`.
- Sole retained evidence is `text_data_dict.json/16/1085` with current Vietnamese `Chiến thắng ào ạt! Đại lễ cảm ơn!!!`.
- The worker finding correctly refused to lock that semantic Vietnamese calque without a verified proper-title identity.

## Identity research

- Cygames' official Japanese portal identifies `どどっと優勝！大感謝祭！！！` as the theme song of `ウマ娘 プリティーダービー 熱血ハチャメチャ大感謝祭！` and as a track on WINNING LIVE 21.
- The English digital distribution published by Lantis/Apple Music exposes the same August 30, 2024 single under the English title `Hip Hip Victory! It's the Fan Fest!`.
- English Party Dash credits independently expose the theme as `Hip Hip Victory! It's the Fan Fest`, reinforcing that this is a published English proper-title identity rather than a worker-authored translation.
- Community discography sources also map the Japanese title to Romanized `Dodo tto Yuushou! Dai Kanshasai!!!`, but repository canonical policy prefers a verified official English/Global identity when available.

## Canonical decision

Lock exact Japanese source `どどっと優勝！大感謝祭！！！` in `text_data_dict.json` category 16 to:

`Hip Hip Victory! It's the Fan Fest!`

Do not retain the semantic Vietnamese calque as the player-facing song title. The hardener adds an item-scoped song rule plus terminology-review lock. Because the worker finding omitted `json_path_prefixes` even though all retained evidence proves category 16, it repairs that finding scope to `[["16"]]` before resolution refresh, mirroring the proven Ichibanboshi song-finding pattern.

## Durable implementation

- Research checkpoint: commit `34f1d979ebce4299e57a3955debd5734e1cca9fa`.
- Hardener `scripts/harden_hip_hip_victory_song_finding.py`: commit `270e323115db9c144bd5151946fdc6b85d6f5119`.
- Permanent regression `tests/test_hip_hip_victory_song_finding_hardening.py`: commit `b0020b18dfe7f9b5d2e5fc672277fe150051da44`.
- Regression proves hardening idempotence, category-16 exact matching, no longer-prose overmatch, evidence-backed malformed-scope repair, canonical resolution, and removal from `active_findings()`.

## Production acceptance

- Validate run `33774328334` succeeded, including pytest, `tlvi validate`, and `tlvi index`.
- Context Sync run `33774328388` succeeded; its full canonical pipeline ran all finding hardeners, refreshed worker findings, rebuilt context, tested the pipeline, and committed generated context.
- Review-plan Sync run `33774298504` from the hardener commit succeeded and published corrected retrospective review context.
- Review-plan Sync run `33774328361` from the regression head also succeeded, proving the regression-only follow-up remains production-compatible.
- Fresh live `main` shows the finding scope repaired to `[["16"]]` and `review_resolution` locked to `Hip Hip Victory! It's the Fan Fest!`.
- Fresh live `main` resolves the finding to locked term `reviewed.proper_name.b3eaaf4adc9f` with the same target. Production precedence therefore materializes the terminology-review lock rather than the parallel community-rule id, which is valid because both enforce the same verified proper-title identity.
- Fresh live retrospective review plan is `tr-p3-67f8551f7780-c47e7eb1fb1d-b5c0bcb3bd-4e85101d5e`, generated `2026-09-03T15:49:50.518009Z` with item-scoped policy hash `4e85101d5e3950bf88af9b78a5cba6ba4bff73a969c2757b694c9c838627cef3`.
- The finding is no longer returned by active-finding semantics. Live active blocker count observed after acceptance was 210; concurrent maintenance/review work may continue changing that count.

Production acceptance is complete. Maintenance completion count may advance from 31 to 32 for `cf-09acdcebbe013cfd`.
