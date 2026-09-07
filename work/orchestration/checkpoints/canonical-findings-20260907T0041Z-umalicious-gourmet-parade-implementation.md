# Canonical finding implementation — Umalicious! Gourmet Parade

- Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260907T001306Z`
- Finding: `cf-3b73be2cd42ac2ac`
- JP source/song title: `ウマすぎ！グルメパレード`
- Canonical target under validation: `Umalicious! Gourmet Parade`
- Historical target: `Ngon tuyệt! Diễu hành ẩm thực`

## Evidence

The repository finding is an exact named-song occurrence in `text_data_dict.json`; historical review deferred it because a full verified Latin/English identity was missing. Fresh current English reference data from the Umamusume Wiki song page identifies Japanese `ウマすぎ！グルメパレード` and English `Umalicious! Gourmet Parade`. Japanese music catalog sources independently confirm the exact JP track identity on WINNING LIVE 20.

## Durable implementation

- `scripts/harden_umasugi_gourmet_parade_finding.py` adds an exact, item-scoped `text_data_dict.json` song-name rule preferring `Umalicious! Gourmet Parade`, forbidding the historical literal Vietnamese translation, and adds a matching terminology-review lock.
- `tests/test_umasugi_gourmet_parade_finding_hardening.py` verifies idempotence, canonical/review resolution, active-finding removal, wrong-path isolation, and exact-source isolation.
- Implementation commits: `dd9dfdf44208c17a7ec0abc342ad85d3996825d2`, `b251761c328593f6b03efb5ce59fd1165881c4e1`.
- Validate run `34070528847` and production Sync translation context run `34070528868` were triggered; acceptance remains pending successful completion and live generated-context confirmation.

No direct `localized_data/**` patch was made.
