# Canonical findings maintenance checkpoint — Spark/factor standalone "固有" label

Finding: `cf-55f8aa69cee34bce` (`固有`, exact `localize_dict.json`, no key scoping).

## Evidence and decision

Sole evidence row is `Character701065` in `localized_data/localize_dict.json`, sitting among
Spark/factor-selection UI keys (`Character701064` inheritance specialization, `Character701066`
priority Spark count). The repository already canonicalizes `固有因子` as `Spark độc nhất`
(`glossary/translation_regressions.generated.json` regressions `894dc6e636094a0a`,
`eb84f02c2f51b0eb`, `bbddba08a6903119`; `common.spark.localize_ui` in
`glossary/ui_community_terms.json`). The standalone modifier therefore locks to **`Độc nhất`**,
matching the existing (and already-live) target text at this key rather than the generic
`skill.unique` ("Unique Skill", kept in English) convention, which applies only to the distinct
`固有技能`/`固有スキル` skill-category label family.

## Durable implementation added

- `scripts/harden_spark_unique_label_finding.py`
  - adds `common.spark.unique_label` to `ui_community_terms.json` (exact match, scoped to
    `localize_dict.json`, no key restriction);
  - adds terminology review decision `audit.finding.spark-unique-label` (lock → `Độc nhất`).
- `tests/test_spark_unique_label_finding_hardening.py`
  - proves hardener idempotence;
  - proves the finding resolves to the scoped community term;
  - proves another source path and the unrelated `固有技能` compound do not inherit the rule.

## Sync performed

Ran the full local equivalent of `.github/workflows/sync-context.yml` (sync_context_registry,
extract_context_candidates, build_observed_term_memory, harden_*_finding loop x2 around
apply_terminology_reviews/harden_audit_findings/harden_training_support_effect_labels,
build_source_bridge_risk_registry, `canonical_findings.py --refresh`,
resolve_scoped_canonical_overrides, resolve_context_guard_findings,
resolve_running_style_narrative_finding, the regenerated-finding resolvers,
build_terminology_review_queue) against fresh live `main`, then ran it a second time and diffed
every touched glossary file byte-for-byte against the first run's output — confirmed semantic
no-op. `TranslationQualityGuard.validate` returns zero errors for the live target and correctly
flags a `Duy nhất` substitute as `community_required:common.spark.unique_label`. Full `pytest -q`
suite: 784 passed. `cf-55f8aa69cee34bce` now carries `canonical_resolution` (`layer: locked`,
`term_id: reviewed.system_label.79ccba4482c3`, `target_vi: Độc nhất`) and is no longer in
`scripts/canonical_findings.py::active_findings` (137 → 136).

## Continuation

No other `固有`-only findings remain in the ledger. Next maintainer should re-read live
`work/orchestration/maintenance_claim.json` and `glossary/canonical_findings.json`, pick the next
`active_findings()` entry in the 136-item backlog, and continue one finding at a time following
this same hardener + Sync + no-op-proof pattern. Do not broaden the `固有` → `Độc nhất` rule beyond
`localize_dict.json`; `固有技能`/`固有スキル` skill-category uses remain governed by the separate
`skill.unique` / `common.skill.unique` ("Unique Skill") rule.
