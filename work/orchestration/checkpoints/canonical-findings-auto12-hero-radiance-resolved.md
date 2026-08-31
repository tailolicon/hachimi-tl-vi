# Canonical findings maintenance checkpoint — Hero's Radiance resolved

Claim: `canonical-findings-maintenance-gpt56sol-auto12-20260831T1858Z`

Resolved finding: `cf-754c7bc46e60b69e` (`英雄的光辉`).

## Evidence and decision

- Live review evidence places `英雄的光辉` at `text_data_dict.json` category `142`, the named Condition table.
- Japanese Uma Musume references identify Zenno Rob Roy's special Career Condition as `英雄の光輝`, obtained for her final Arima Kinen after the relevant autumn wins.
- No official Global Condition label was established by the evidence used in this maintenance pass, so the canonical player-facing target is the direct English rendering `Hero's Radiance` rather than the previous Vietnamese calque.
- Permanent hardener: `scripts/harden_hero_radiance_finding.py`.
- Positive/negative regression: `tests/test_hero_radiance_finding_hardening.py`; same source text outside category `142` must not resolve through this rule.

## Validation

- Validate workflow run `33428258775`: success, including pytest and `tlvi validate/index`.
- Sync translation context run `33428258884`: success, including all finding hardeners, canonical-finding refresh, context tests, and generated-context persistence.
- Live `glossary/canonical_findings.json` now resolves `cf-754c7bc46e60b69e` to `Hero's Radiance` through reviewed Condition lock `reviewed.condition.166b882d5100`.

Maintenance completed count advances from **102** to **103**. Continue with the next unresolved canonical identity; do not restart inventory.
