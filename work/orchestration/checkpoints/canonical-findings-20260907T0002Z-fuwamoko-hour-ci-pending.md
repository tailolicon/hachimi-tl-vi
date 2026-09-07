# Canonical findings maintenance checkpoint — ふわもこアワー

- Claim: `canonical-findings-maintenance-gpt56sol-automation-20260906T235815Z`
- Finding: `cf-3236b7b35703be33`
- Source: `轻柔软绵时光`
- Verified JP identity / proposed target: `ふわもこアワー`
- Skill ID: `110871`
- Character: Aston Machan / `[溶けない砂糖菓子]`

## Evidence and implementation

Repository evidence had already pinned the zh-CN title to Skill 110871 but lacked the exact JP title. Fresh external identity lookup recovered `110871 = ふわもこアワー` and a dedicated skill page explicitly pairing `ふわもこアワー / 轻柔软绵时光`.

Following the existing JP-only proper-name policy, preserve the exact Japanese display title until an official Global title exists rather than keeping the historical zh-CN-derived Vietnamese calque `Khoảnh khắc mềm mại êm ái`.

Durable implementation on `main`:

- `scripts/harden_fuwamoko_hour_finding.py` adds an exact `text_data_dict.json` Skill rule and terminology-review lock, item-scoped, preferring `ふわもこアワー` and forbidding the historical calque.
- `tests/test_fuwamoko_hour_finding_hardening.py` verifies idempotence, canonical/review resolution, removal from `active_findings()`, and negative cases for wrong source path and prose containment.
- Implementation head: `0f64421b2e6d7c544a2cbcdd606a68188d6e335e`.
- Validate run `34068453168` and Sync translation context run `34068453178` were automatically triggered; acceptance remains pending their successful completion.

No direct `localized_data/**` edit was made.
