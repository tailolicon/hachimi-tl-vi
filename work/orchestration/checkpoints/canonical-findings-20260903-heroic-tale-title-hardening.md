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

## Validation / production acceptance

Push-triggered workflows for head `e950d0f1f841942036d00eaa6d5edea9b7851788`:

- Sync translation context: run `33769319161` — **completed successfully** on production.
- Sync translation review plan: run `33769319396` / job `100697520449` — **completed successfully** on production.
- The production review-plan job ran every `scripts/harden_*_finding.py` hardener; `harden_heroic_tale_title_finding.py` reported `heroic_tale_title_hardening_changed=false`, confirming the durable rule was already present on the live checkout.
- The same job then ran `scripts/canonical_findings.py --refresh` followed by `scripts/resolve_context_guard_findings.py`; refresh reported `findings=442 active=251` before the guard pass and the guard pass reported `context_guard_resolutions_changed=true`.
- All production validation tests passed: `553 passed`.
- Review-plan generation remained on plan `tr-p3-67f8551f7780-4ecdb18e53c1-b5c0bcb3bd-b8b3910d6d` with `candidate_count=4210`; batch-finding refresh reported no stale batch changes. A live default-branch search of this plan for `cf-0533ace8b6cf1c16` returns no hits, while the hardener's exact resolver target remains `{layer: community, term_id: event.league_of_heroes.heroic_tale_title, target_vi: Anh Hùng Kỳ Đàm}`.

## Completion

Production acceptance is complete. `cf-0533ace8b6cf1c16` is resolved by the scoped canonical community rule and no longer needs to block retrospective translation review. Maintenance completion count may advance from 28 to 29.
