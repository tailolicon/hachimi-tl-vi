# Canonical findings maintenance checkpoint — St. Lite Kinen guard clear

Claim: `canonical-findings-maintenance-gpt56sol-relay-a6bda3fa-20260918T025625Z`

Resolved finding: `cf-6b9b893796ef90b5` (`圣列特纪念`, St. Lite Kinen precedence over nested Saint Lite character alias).

Durable evidence:

- `scripts/harden_saint_lite_race_context_finding.py` excludes full race `圣列特纪念` from `character.saint_lite` while preserving standalone `圣列特 → Saint Lite`.
- `scripts/resolve_context_guard_findings.py` now resolves this finding only after the conflicting character matcher no longer fires on its evidence.
- `tests/test_st_lite_race_context_finding_hardening.py` proves standalone character matching, race exclusion, positive `race.st_lite_kinen` matching, and idempotent finding resolution.
- Focused context tests: 8 passed.
- Full repository suite: 870 passed.
- Implementation main commit: `356c37a09bda5d5b682b9adcbb597459124767c6`.
- Production Sync translation context run `35302604863` completed successfully.
- Sync-generated main commit: `1284f467a88d5ba1fa28b66dbbda44172e846304`.
- Live `glossary/canonical_findings.json` resolves the finding with `layer=context_guard`, `term_id=character.saint_lite`, `target_vi=St. Lite Kinen`.
- Live evidence `text_data_dict.json / 111 / 62` matches the race lock without the character lock.

Maintenance durable completed count after this finding: **219**.

Continue immediately with `cf-6e9ce1ab478d60de`; earlier JP-only/evidence-insufficient findings remain explicitly deferred and active.
