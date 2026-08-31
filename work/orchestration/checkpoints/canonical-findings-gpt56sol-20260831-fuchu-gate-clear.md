# Canonical findings maintenance checkpoint — Fuchu Himba guard clear

Claim: `canonical-findings-maintenance-gpt56sol-20260831T0547Z`

Resolved finding: `cf-f6302c57277dc9bc` (`赛马娘` overmatching inside the proper race name `府中赛马娘锦标`).

Durable evidence:

- `scripts/harden_fuchu_himba_context_finding.py` narrows `common.world.umamusume` with an exclusion for `府中赛马娘锦标` while preserving generic `赛马娘` -> `Mã Nương` behavior.
- `tests/test_fuchu_himba_context_guard_resolution.py` proves both the proper-name exclusion and the generic positive case.
- `.github/workflows/sync-context.yml` now explicitly watches the Fuchu regression test in addition to the generic finding-hardener pattern.
- Production Sync translation context run `33361899628` completed successfully, including all finding hardeners, context-guard resolution, full `pytest -q`, and generated-context persistence.
- Sync-generated main commit: `d51d2dae8f0f7ecb910adb21eae41170fd775570`.
- Live `glossary/canonical_findings.json` now resolves this finding with `layer=context_guard`, `term_id=common.world.umamusume`, `target_vi=Mã Nương`.

Maintenance durable completed count: **63**.

Continue immediately with the next live unresolved canonical finding; do not return to mass review while a blocking finding remains.
