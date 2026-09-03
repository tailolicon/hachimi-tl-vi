# Canonical finding implementation — Boukyaku Nite

Finding: `cf-851d6f50674f9adb`

- source title: `忘却にて`
- live item: `text_data_dict.json` category `16`, entry `1074`
- canonical target: `Boukyaku Nite`

## Evidence basis

Official Lantis `WINNING LIVE 08` identifies `忘却にて` as Aston Machan's named song. Established Uma Musume discography references render the same track as `Boukyaku Nite`. The historical Vietnamese `Trong lãng quên` is a semantic translation, not the requested Latin/Romanized proper-name identity.

## Implementation

- hardener: `scripts/harden_boukyaku_nite_finding.py`
- regression: `tests/test_boukyaku_nite_finding_hardening.py`
- community rule: `song.boukyaku_nite`
- terminology decision: `audit.finding.song-boukyaku-nite`
- source scope: exact match in `text_data_dict.json`
- forbidden targets include source-script leakage `忘却にて` and historical semantic calque `Trong lãng quên`

Regression requires idempotence, community + review resolution of the exact live finding shape, removal from `active_findings`, and negative coverage proving the rule does not match longer prose or another source file.

## Acceptance pending

Do not increment maintenance `completed_count` beyond 63 until a commit containing this hardener/test has successful Validate, production Sync translation context, and Sync translation review plan runs, and the newly generated live review context for `16/1074` embeds `song.boukyaku_nite` / `Boukyaku Nite` with `cf-851d6f50674f9adb` no longer present as a canonical blocker.
