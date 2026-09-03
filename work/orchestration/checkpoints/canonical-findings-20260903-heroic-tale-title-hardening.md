# Canonical finding checkpoint — League of Heroes `英雄奇谭`

Finding: `cf-0533ace8b6cf1c16`

## Decision

Lock the League of Heroes event-limited title label `英雄奇谭` to `Anh Hùng Kỳ Đàm` in the proven `localize_dict.json` `Heroes511*` UI family.

Repository evidence already has multiple reviewed/generated regression targets using `Anh Hùng Kỳ Đàm`, while a later split cluster uses `Heroic Tale`. The phrase also occurs in unrelated narrative prose, so the canonical rule is intentionally scoped by `source_paths=[localize_dict.json]` and `key_prefixes=[Heroes511]` rather than globally matching the Chinese phrase.

## Durable changes

- `scripts/harden_heroic_tale_title_finding.py` added at main commit `4658bd5e682e30f72135a2f60fecb937347ffd99`.
- `tests/test_heroic_tale_title_finding_hardening.py` added at main commit `e950d0f1f841942036d00eaa6d5edea9b7851788`.
- Local execution backend has no pytest installed, but direct import/compile/idempotence assertions against the live hardener passed (`manual_hardener_check=pass`).
- A clean archive simulation from current `origin/main` ran the hardener followed by `scripts/canonical_findings.py --refresh`; finding `cf-0533ace8b6cf1c16` resolved exactly to `{layer: community, term_id: event.league_of_heroes.heroic_tale_title, target_vi: Anh Hùng Kỳ Đàm}`. This proves the hardener matches the repository resolver semantics without overmatching unrelated prose.
- Live repository search during acceptance verification found multiple durable translation and review artifacts already using `Anh Hùng Kỳ Đàm`, including `work/results/batch-00026/...` and retrospective review result `...b0073...`; this independently agrees with the scoped community-term resolution and does not broaden its matcher.

## Validation / production continuation

Push-triggered workflows for head `e950d0f1f841942036d00eaa6d5edea9b7851788`:

- Sync translation context: run `33769319161` — **completed successfully** on production.
- Sync translation review plan: run `33769319396` — **still pending with no jobs allocated** at the latest check during this worker lease.

Do not mark the finding resolved from this checkpoint alone. The sole remaining acceptance gate is production completion of review-plan Sync. Continue by verifying run `33769319396`; if it succeeds, confirm the generated canonical resolution on live `main`, record the completion evidence, increment maintenance completion count, and move to the next active finding under `scripts/canonical_findings.py::active_findings` semantics.
