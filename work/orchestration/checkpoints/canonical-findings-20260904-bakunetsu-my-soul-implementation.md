# Canonical finding implementation — Bakunetsu My Soul

Finding: `cf-786f492ee1495f8f`

- source title: `爆熱マイソウル`
- live item: `text_data_dict.json` category `16`, entry `1088`
- canonical target: `Bakunetsu My Soul`

## Evidence basis

`爆熱マイソウル` is the named U.A.F. Ready GO! scenario theme released on WINNING LIVE 18. Established Uma Musume discography references consistently romanize the title as `Bakunetsu My Soul`. The current Vietnamese `My Soul bùng cháy` is a mixed semantic rendering and is not the stable Latin/Romanized proper-name identity requested by the finding.

## Implementation

- hardener: `scripts/harden_bakunetsu_my_soul_finding.py`
- regression: `tests/test_bakunetsu_my_soul_finding_hardening.py`
- community rule: `song.bakunetsu_my_soul`
- terminology decision: `audit.finding.song-bakunetsu-my-soul`
- source scope: exact match in `text_data_dict.json`
- forbidden targets include source-script leakage and historical `My Soul bùng cháy`
- regression covers idempotence, canonical/review resolution, active-finding removal, and negative longer-text/other-file matching.

Implementation commits observed on live `main`:

- hardener commit `759a3b51f5a6287faf79a098002f4bf3cf41e4fb`
- regression commit `d06261bd60b90bf51c8b6df7212533deb98126f0`

## Acceptance status

Accepted on live `main`.

- Validate run `33822327151`: success.
- Sync translation context run `33822327174`: success.
- Sync translation review plan run `33822327301`: success.
- Live generated review plan `tr-p3-67f8551f7780-467d9805a848-b5c0bcb3bd-0f8e2d4154` contains `text_data_dict.json` `16/1088` with community rule `song.bakunetsu_my_soul`, preferred target `Bakunetsu My Soul`, and `canonical_findings: []`.

This finding satisfies production acceptance and may advance the maintenance completed count.
