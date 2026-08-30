# Canonical findings maintenance checkpoint — generic hardener workflow fix

Claim: `canonical-findings-maintenance-gpt56sol-20260830T214700Z`

Confirmed baseline remains **31 resolved findings**.

Systemic workflow repair now durable on `main`:

- `.github/workflows/sync-context.yml` push paths now include `scripts/harden_*_finding.py` and `tests/test_*_finding_hardening.py`;
- production Sync now executes every matching `scripts/harden_*_finding.py` through one generic loop;
- the existing `tests/test_context_sync_auto_hardener.py` guard is satisfied by the loop syntax;
- `tests/test_context_sync_workflow_persistence.py` additionally guards generic trigger + execution wiring.

Relevant commits:

- `c3799c747ebdca9c15cd2d17cfec7ba0c8fecfec` — generic workflow wiring aligned with the pre-existing regression guard;
- `84143928700088fc4c2752a151826e5a61cbb11b` — persistence test aligned with the generic loop.

Do not increment the resolved-finding counter for the pending song-title hardeners until the resulting production Sync completes and live `glossary/canonical_findings.json` contains their canonical resolutions.
