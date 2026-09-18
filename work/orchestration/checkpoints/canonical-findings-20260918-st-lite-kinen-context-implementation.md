# Canonical finding implementation — St. Lite Kinen precedence (2026-09-18)

Finding: `cf-6b9b893796ef90b5` (`圣列特纪念`).

## Evidence and diagnosis

- The repository already locks the full race identity `圣列特纪念` / JP `セントライト記念` as `St. Lite Kinen` through `race.st_lite_kinen`.
- The current reviewed target for this finding is also `St. Lite Kinen`.
- The shorter locked character alias `圣列特` → `Saint Lite` still matched inside the full race source, so one review item simultaneously received contradictory character and race locks.
- Current English racing coverage continues to use the St Lite Kinen race identity; repository canonical evidence remains authoritative for the punctuated target.

## Permanent fix

- Add `圣列特纪念` to `character.saint_lite.exclude_source_contains`.
- Register `cf-6b9b893796ef90b5` in `scripts/resolve_context_guard_findings.py` so it resolves only after the character matcher no longer fires on the evidence row.
- Add `scripts/harden_saint_lite_race_context_finding.py`; Sync automatically executes `scripts/harden_*_finding.py`.
- Add `tests/test_st_lite_race_context_finding_hardening.py` covering:
  - positive standalone Saint Lite character matching;
  - negative Saint Lite matching inside `圣列特纪念`;
  - positive `race.st_lite_kinen` matching;
  - idempotent context-guard resolution.

## Validation

- Focused context tests: 8 passed.
- Full repository suite: 870 passed.
- Hardener second run: unchanged.
- Resolver second run: unchanged.
- Active canonical findings after local resolution: 84 (down from 85).
- Evidence `text_data_dict.json / 111 / 62` now matches only `race.st_lite_kinen`; standalone `圣列特` still matches `character.saint_lite`.

Production Sync/no-op verification is still required before incrementing maintenance `completed_count`.
