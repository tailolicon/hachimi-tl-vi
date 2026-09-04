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

## Acceptance complete

Accepted on 2026-09-04 after production evidence for commit `2546c9849e0daaa44e07d1d07eb253e0270fe247`:

- Validate check `test` completed successfully.
- Sync translation context run `33819391935` completed successfully.
- Sync translation review plan run `33819391976` completed successfully.
- live review batch `tr-p3-67f8551f7780-838f16b962bc-b5c0bcb3bd-05f31b1d0f-b0175` item `text_data_dict.json` `16/1074` embeds `song.boukyaku_nite` with preferred `Boukyaku Nite`.
- the live item has `canonical_findings: []`, so `cf-851d6f50674f9adb` no longer blocks review.

Maintenance completed_count may advance from 63 to 64. Next priority must be re-read from live routing; research checkpoint `work/orchestration/checkpoints/canonical-findings-20260903-golshi-de-rap-research.md` is available for `cf-2a8fd2f0a0deb318` if it remains next.