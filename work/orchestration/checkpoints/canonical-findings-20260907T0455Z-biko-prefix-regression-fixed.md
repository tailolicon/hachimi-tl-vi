# Canonical finding checkpoint — Biko Unyielding prefix regression corrected

- Finding: `cf-5026b367a0d84413` (`不可动摇的热血誓言`).
- Initial Validate run `34084724053` failed only in the newly added negative regression: the test incorrectly assumed `review_resolution` itself is filtered by a finding's `source_paths`.
- Inspection of live `scripts/canonical_findings.py` confirms `_latest_review_decisions()` indexes review decisions by exact `source_zh_cn`, and `refresh_canonical_resolutions()` attaches that decision before canonical-rule path coverage is evaluated. Therefore the original negative-path assertion did not reflect repository semantics.
- Corrected `tests/test_biko_pegasus_unyielding_prefix_finding_hardening.py` at commit `9127bc87d00547ea64d8221d7c597b5cf587600c`: the negative case now verifies that the distinct full source `不可动摇的热血誓言・短距离` does not receive the prefix's ignore decision, while the exact Unyielding Vow Sprint/Mile locks remain asserted.
- New Validate run `34084857217` and production Sync run `34084857240` are running/pending from the corrected commit.
- Do not increment maintenance completion until Validate + production Sync pass, live finding is non-active via ignore, exact full-label locks remain intact, and a second unchanged production Sync succeeds.
