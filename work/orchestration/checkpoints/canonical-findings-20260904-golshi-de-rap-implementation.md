# Canonical finding implementation — Golshi de Rap -It's Muri Muri-

Finding: `cf-2a8fd2f0a0deb318`

- source title: `ゴルシでラップ -It's むりむり-`
- live item: `text_data_dict.json` category `16`, entry `1075`
- canonical target: `Golshi de Rap -It's Muri Muri-`

## Evidence basis

Official Lantis `WINNING LIVE 12` identifies the exact Japanese track title as a Gold Ship song. CDJapan/Neowing catalog Romanization gives `GOLSHI DE RAP - IT'S MURI MURI-`; established Uma Musume references use the same identity with ordinary title casing. The current Vietnamese `Rap cùng Golshi -It's không thể đâu-` semantically translates the title instead of preserving the named-song identity.

## Implementation

- hardener: `scripts/harden_golshi_de_rap_finding.py`
- regression: `tests/test_golshi_de_rap_finding_hardening.py`
- community rule: `song.golshi_de_rap_its_muri_muri`
- terminology decision: `audit.finding.song-golshi-de-rap-its-muri-muri`
- source scope: exact match in `text_data_dict.json`
- forbidden targets include source-script leakage and the historical mixed semantic target

Regression requires hardener idempotence, community + review resolution of the exact live finding shape, removal from `active_findings`, and negative coverage proving the rule does not match longer prose or another source file.

## Acceptance pending

Do not increment maintenance `completed_count` beyond 64 until a commit containing both the hardener and regression has successful Validate, production Sync translation context, and Sync translation review plan runs, and the generated live review context for `16/1075` embeds `song.golshi_de_rap_its_muri_muri` / `Golshi de Rap -It's Muri Muri-` with `cf-2a8fd2f0a0deb318` absent from canonical blockers.
