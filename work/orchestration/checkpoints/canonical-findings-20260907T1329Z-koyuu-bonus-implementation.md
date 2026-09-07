# Canonical finding implementation checkpoint — 固有加成

Finding: `cf-5cc239af1c9d7710` (`固有加成`), with companion exact finding `cf-823a42e63df66f92`.

Fresh identity checkpoint `canonical-findings-20260907T1325Z-koyuu-bonus-identity.md` establishes the canonical Vietnamese label `Hiệu ứng riêng` for the generic Support-card Unique Effect UI label.

Implementation is durable on branch `auto11-unique-bonus-20260907` at commit `38ee977b1ef9a4b275200e9ee029fddb0f6cba9c`:

- `scripts/harden_unique_bonus_finding.py` adds an idempotent `localize_dict.json`-scoped contains rule `固有加成 -> Hiệu ứng riêng` and matching lock review decision.
- The rule deliberately does not apply to `text_data_dict.json`, so category-150 unique-effect proper/display names remain outside its scope.
- `tests/test_unique_bonus_finding_hardening.py` verifies idempotence, exact + reusable-alias resolution, and negative coverage for another source path / another `固有...` alias.
- Targeted test suite with `tests/test_canonical_findings.py`: **6 passed**.

Do not increment `completed_count` yet. Next: integrate the implementation onto fresh live `main`, apply the hardener/resolver through the repository-supported pipeline, then obtain Validate + production Context Sync + second unchanged no-op Sync acceptance before counting the finding complete.
