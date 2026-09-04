# Canonical finding acceptance: Seirios

Finding `cf-1673a3660fd5050e` (`天骄`) is accepted as Sirius Symboli's JP unique Skill `セイリオス`, using the international spelling `Seirios`.

Durable hardening is live on `main` at `7982e7587676c5ec7cffc16740e353ba496eae2f` via `scripts/harden_seirios_skill_finding.py`, with permanent regression coverage in `tests/test_seirios_skill_finding_hardening.py`. Repository factor ID `10700101` maps this zh-CN title to `セイリオス`; external game/reference data independently confirms the same Sirius Symboli Skill identity and spelling.

Production acceptance:

- Validate `33861497580`: success.
- Sync translation context `33861497511`: success.
- Sync translation review plan `33861497448`: success.

Do not double-count this finding on later regenerated-state refreshes.
