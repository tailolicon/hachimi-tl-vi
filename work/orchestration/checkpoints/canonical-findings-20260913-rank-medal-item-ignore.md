# Canonical findings maintenance — 等级奖牌 exact-item ignore

## Finding

- finding_id: `cf-55f0e8a1d70264a2`
- source: `等级奖牌`
- evidence UID: `zhcn:6e7d42dbf885145a98b9cc48`
- exact source item: `text_data_dict.json` → JSON path `['133', '3']`

## Disposition

Resolved the canonical-maintenance blocker with an **item-scoped `ignore` review disposition**, not with a guessed reusable canonical identity.

Live hardening uses decision `audit.finding.rank-medal-unverified-identity-ignore`, `action=ignore`, `invalidation_scope=item`, `source_paths=['text_data_dict.json']`, `json_path_prefixes=[['133','3']]`, and exact matching.

This disposition deliberately does **not** identify `等级奖牌` as Trainer Medal / トレーナーメダル, Rank Medal, Grade Medal, Class Medal, or any other reusable player-facing term. The ordinary current rendering `Huy chương cấp` is not promoted to canonical identity.

## Validation evidence

Validated from a clean worktree based on fetched `origin/main` rather than the dirty local main checkout.

- `python scripts/harden_rank_medal_finding.py` → exit 0, `rank_medal_ignore_changed=false` (the durable ignore disposition was already materialized and the hardener was idempotent).
- `python scripts/canonical_findings.py --repo-root . --refresh` → exit 0, `findings=542 active=119`.
- Inspected the refreshed `glossary/canonical_findings.json` entry for `cf-55f0e8a1d70264a2`:
  - `status=open`
  - `canonical_resolution=null`
  - `review_resolution.decision_id=audit.finding.rank-medal-unverified-identity-ignore`
  - `review_resolution.action=ignore`
  - evidence path remains `text_data_dict.json` / `['133','3']`
- Live `scripts/canonical_findings.py::active_findings` excludes findings whose `review_resolution.action == 'ignore'`; therefore this finding is no longer a canonical-maintenance blocker while remaining intentionally non-canonical.
- Regression test `tests/test_rank_medal_finding_hardening.py` was corrected on main to pass a proper findings payload into `active_findings`, preventing a false-positive nonblocking assertion.

Full pytest was **not** claimed as executed in this validation environment because pytest is not installed there. The repository sync workflow remains responsible for the full suite when that runner is available; targeted production-script validation above succeeded.

## Continuation

Future workers should preserve this exact-item ignore unless new authoritative source-identity evidence appears. If such evidence appears, review the exact item and only then consider replacing the ignore with a canonical identity. Do not infer identity from the Simplified Chinese label alone.
