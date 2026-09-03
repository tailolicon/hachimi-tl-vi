# Canonical finding checkpoint — League of Heroes `英雄奇谭`

Finding: `cf-0533ace8b6cf1c16`

## Decision

Lock the League of Heroes event-limited title label `英雄奇谭` to `Anh Hùng Kỳ Đàm` in the proven `localize_dict.json` `Heroes511*` UI family.

Repository evidence already has multiple reviewed/generated regression targets using `Anh Hùng Kỳ Đàm`, while a later split cluster uses `Heroic Tale`. The phrase also occurs in unrelated narrative prose, so the canonical rule is intentionally scoped by `source_paths=[localize_dict.json]` and `key_prefixes=[Heroes511]` rather than globally matching the Chinese phrase.

## Durable changes

- `scripts/harden_heroic_tale_title_finding.py` added at main commit `4658bd5e682e30f72135a2f60fecb937347ffd99`.
- `tests/test_heroic_tale_title_finding_hardening.py` added at main commit `e950d0f1f841942036d00eaa6d5edea9b7851788`.
- Local execution backend has no pytest installed, but direct import/compile/idempotence assertions against the live hardener passed (`manual_hardener_check=pass`).

## Validation / production continuation

Push-triggered workflows for head `e950d0f1f841942036d00eaa6d5edea9b7851788`:

- Sync translation context: run `33769319161` — pending at checkpoint time.
- Sync translation review plan: run `33769319396` — pending at checkpoint time.

Do not mark the finding resolved from this checkpoint alone. Continue by verifying workflow success and generated canonical resolution on live `main`; if successful, record the completion evidence and move to the next active finding under `scripts/canonical_findings.py::active_findings` semantics.
