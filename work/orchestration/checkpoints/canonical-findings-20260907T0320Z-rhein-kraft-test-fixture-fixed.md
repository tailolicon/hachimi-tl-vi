# Canonical finding checkpoint — Rhein Kraft / Power CI fixture corrected

Finding: `cf-47c737cc38fc1f48`
Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260907T0256Z`
Completed count remains: `175`

The first regression run (`Validate` 34079195899) failed only because the isolated test fixture omitted the canonical locked `stat.power` registry row required by `scripts/harden_power_context_finding.py`; repository production data does contain that locked row. The failure was therefore in the new test fixture, not the context hardener.

Commit `37ddcd6467091f6770b4df40e8860bec9c3fb199` fixes the fixture by providing the same minimal locked `stat.power` row used by the established Power-hardening regression setup. No production canonical rule was weakened.

Require a fresh successful Validate run for this corrected head plus successful production Sync acceptance before completing the finding.