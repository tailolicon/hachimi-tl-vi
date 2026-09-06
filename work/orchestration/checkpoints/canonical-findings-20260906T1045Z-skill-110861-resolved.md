# Canonical finding — Skill 110861 resolved

Resolved active finding `cf-03735d8f77de39a1` for zh-CN `至死不渝的爱`.

- Existing curation identified the source as Skill `47/110861` but deferred it because the Japanese canonical title had not been verified.
- Independent verification identifies numeric Skill ID `110861` as Mejiro Ramonu [Untouchable Eden]'s unique Skill `解けぬ結い目`; Biligame explicitly pairs the zh-CN title `至死不渝的爱` with Japanese `解けぬ結い目`.
- Added reviewed lock `audit.finding.mejiro-ramonu-tokenu-yuime` with `target_vi: 解けぬ結い目` and JP alias `解けぬ結い目`.
- Applied reviewed terminology and ran the repository canonical refresh/hardener/resolver sequence plus terminology-review queue rebuild.
- `cf-03735d8f77de39a1` now resolves through locked term `reviewed.proper_name.70e0b5af92f1` with matching lock review resolution.
- Active-finding semantics decreased from 149 blockers before this unit to 148 after the full resolver sequence.
- Regression validation after rebasing over concurrent Context Sync / review-plan updates: `UV_CACHE_DIR=.uv-cache uv run --with pytest pytest -q tests/test_apply_terminology_reviews.py tests/test_audit_finding_hardening.py tests/test_context_guard_finding_resolution.py tests/test_scoped_canonical_override_resolution.py` -> `28 passed`.

Canonical artifacts were integrated to live `main` at commit `21af04b5ce41f71914e6b5c958ccf7b1b4cab5de` via a non-forced fast-forward ref update.
