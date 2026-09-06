# Canonical finding hardening — Air Shakur `…found you.`

Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260906T205100Z`

Finding: `cf-2c4b6d109aaf229d`

## Identity evidence

The finding occurs in inheritance descriptions for trainee `103602`, `[Belphegor's Prime] Air Shakur`, and refers to unique Skill id `110361`.

The earlier evidence checkpoint correctly rejected promoting the zh-CN semantic calque without verified identity. Fresh verification now establishes that the Japanese-game Skill title itself is the English text `…found you.`. Multiple JP references list Air Shakur's unique skill using that exact title; therefore preserving `…found you.` is identity-preserving rather than importing an English fan translation.

## Hardening implemented

- `scripts/harden_air_shakur_found_you_finding.py`
  - zh-CN alias `...抓到你了。`
  - JP title `…found you.`
  - locked target `…found you.`
  - historical Vietnamese calque `...Bắt được bạn rồi.` forbidden
  - source path `text_data_dict.json`
  - narrow inheritance category prefix `172`
  - `match_mode: contains`, because the alias occurs inside a longer inheritance description
  - review decision `audit.finding.skill-air-shakur-found-you`.
- `tests/test_air_shakur_found_you_finding_hardening.py`
  - idempotence
  - canonical + review resolution
  - path/prefix non-overmatch
  - historical calque rejection.

Implementation commits:

- hardener: `2ee16863157ae394e53eafb6b995ac99db5359f4`
- regression test: `c8d99daff521c4c66079b401c888a9a706675eb3`

## Validation status

Repository Actions were triggered from the regression-test commit. `Sync translation context`, `Sync translation review plan`, and `Validate` must complete successfully before this finding is counted complete. The local Shiro checkout could not run pytest because that isolated runtime lacks the pytest module; this is a backend-local limitation, so GitHub Actions remains the acceptance path.

## Status

Hardening implemented; production acceptance pending. Do not increment the shared maintenance completed count until Validate + production Sync prove the generated finding resolves and the historical calque is rejected.
