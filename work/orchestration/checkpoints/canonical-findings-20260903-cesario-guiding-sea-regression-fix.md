# Cesario / Guiding Sea regression correction

Initial Validate run `33817275485` failed with exactly one test failure after `618 passed`:

`test_scope_prevents_generic_idiom_outside_inheritance_category` incorrectly expected `review_resolution` to be absent for a category-163 synthetic finding.

Diagnosis: `scripts/canonical_findings.py` intentionally indexes terminology-review decisions by `source_zh_cn`; `review_resolution` is therefore source-keyed metadata and is not the scope-aware blocking gate. Scope-aware canonical coverage is represented by `canonical_resolution`, and `active_findings()` only clears a blocking finding when canonical resolution exists (or an explicit review `ignore` exists).

The production safety requirement is unchanged: the category-163 synthetic finding must have `canonical_resolution: null` and remain in `active_findings()` even if the source-keyed review lock is displayed.

Regression commit `62e7f946b37cabeb01f99dbb1a1794dca0bdddae` updates the test to assert that actual contract. No canonical rule scope was broadened and no production target changed.

Acceptance remains pending new successful Validate plus production context/review-plan Sync on a descendant containing this fix.
