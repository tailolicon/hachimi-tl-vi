# Race finalizer checkpoint — 2026-08-29T10:10Z

Claim: `canonical-race-finalizer-20260829T1004Z-gpt56sol`.

## Concrete failure resolved

Diagnostic artifact from Race validator run `33245440234` exposed the remaining full-pytest failure as `tests/test_race_hardening.py::test_race_hardener_is_idempotent`.

Root cause: `_is_proper_race()` in `scripts/harden_race_canon.py` classified almost every `race.*` ID as a proper named race. The staging guard therefore applied proper-race `source_paths/json_path_prefixes/match_mode` to system records such as `race.class.*`, `race.grade.*`, `race.ui.*`, and `race.track_condition.*` on the second hardener run, causing semantic churn.

Bounded permanent fix: proper-race default guarding is now category-structured: only records whose `category == "race_name"` qualify. Verified RACES upserts normalize legacy proper-race records to that category before persistence, while system Race records retain their own explicit structured guards.

## Validation evidence

Race branch validation run `33247073656` completed successfully at 2026-08-29T10:09:11Z. All gates passed:

- staging permanent hardening outputs;
- bounded classifier fix;
- Python compile;
- full `pytest -q`;
- hardener idempotence;
- translation-review plan rebuild twice with unchanged no-op assertion;
- `git diff --check`;
- deterministic Race inventory build;
- staged permanent branch publication.

The workflow published Race branch commit `343c075928bb279d002e1949680cefeb83b5c502` (`Race hardening: stage canonical outputs`).

## Integration boundary

Live compare from `main` commit `3e8ea4a31d57335cec2c701d6f1e78028a7254ba` to Race head `343c075928bb279d002e1949680cefeb83b5c502` is diverged: Race is 27 commits ahead and 45 commits behind, merge-base `9e17356ed0702c2574646f9d563b51ec99318e55`.

Do NOT merge or overwrite the branch wholesale. Construct a clean selective integration from current live `main`, preserving concurrent main edits. Permanent candidates include the Race hardener, Race regressions, builder no-op/import fix, canonical glossary outputs, and production Sync wiring. TEMP-only artifacts must not land on main, including `.github/workflows/validate-race-hardening.yml`, `scripts/race_stage_tmp.py`, `scripts/race_finalizer_fix_tmp.py`, `scripts/race_inventory_tmp.py`, `scripts/race_inventory_compact_tmp.py`, and `work/tmp_race_*.json`.

After selective integration, rerun full acceptance on the integrated tree, then perform production Sync, inspect active plan/parallel-state agreement and representative positive/negative Race contexts, run a second unchanged Sync, and prove true no-op before marking Race complete and activating canonical-training-support.
