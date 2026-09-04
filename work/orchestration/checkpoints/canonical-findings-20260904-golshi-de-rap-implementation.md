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

## Acceptance complete

Accepted on 2026-09-04 using implementation commit `2fb46c785986dfd5b186442a7f868e2f372ffa9f`, which contains both the hardener and regression:

- Validate run `33820656583` completed successfully.
- Sync translation context run `33820656579` completed successfully.
- Sync translation review plan run `33820656556` completed successfully.
- live review plan `tr-p3-67f8551f7780-afe3f6cc0a12-b5c0bcb3bd-48d2cc7839`, item `text_data_dict.json` `16/1075`, embeds `song.golshi_de_rap_its_muri_muri` with preferred `Golshi de Rap -It's Muri Muri-`.
- that live item has `canonical_findings: []`, so `cf-2a8fd2f0a0deb318` no longer blocks review.

Maintenance `completed_count` may advance from 64 to 65. The next live item `cf-b74bd0c4b24ab2af` / `ドロワダンスパート` has a durable research checkpoint at `work/orchestration/checkpoints/canonical-findings-20260904-drowa-dance-part-research.md`; evidence is currently insufficient for a non-guessed Latin lock. `cf-5c83fe60c17ea214` / `トレセン音頭` has a positive research checkpoint at `work/orchestration/checkpoints/canonical-findings-20260904-tracen-ondo-research.md` if routing proceeds past the unresolved Drowa title.