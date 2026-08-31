# Canonical maintenance checkpoint — Stamina achievement threshold complete

Claim: `canonical-findings-maintenance-gpt56sol-auto10-20260901T0328+07`

Finding `cf-cea396d277bd7301` is resolved on live `main` without weakening the generic `体力 -> Energy` policy.

## Resolution

- Source finding: `体力` inside text-data category `131`, evidence text `【体力】达到1200以上`.
- Category-131 canonical target: `Stamina`.
- Generic `体力` outside this proven achievement scope remains `Energy`/unaffected by the scoped exception.
- Scoped community rule: `stat.stamina.achievement_threshold`.
- Obsolete source-wide decision `audit.finding.stamina-achievement-threshold` was removed because a global `体力 -> Stamina` lock conflicts with the repository's generic Energy semantics.

## Durable implementation

- Scoped hardener/migration: `scripts/harden_stamina_threshold_finding.py` (`6510437f4bc9b2cc96c4813e9f7126c5624073b6`).
- Scoped canonical post-resolver: `scripts/resolve_scoped_canonical_overrides.py` (`4456c1a1e210c9147215cd938a04734e7350ced9`; direct-execution fix originated at `86a3d31be2690ffe9007914d04c5fbe18d5f76d4`).
- Resolver regression coverage: `tests/test_scoped_canonical_override_resolution.py` (`9f5350ec1aadc9526aa18544ac804852d8d36ae4`), including no-reviewed-target, scope mismatch, explicit defer protection, unscoped-rule rejection, and direct workflow entrypoint execution.
- Stamina-specific regression/migration coverage: `tests/test_stamina_threshold_finding_hardening.py` (`f47f63572ec45a900cbcd13f996f925503d322b8`).
- Context workflow migration/integration: `.github/workflows/sync-context.yml` (`6cb3ca2ea4133f8fc3746b86299c015d4e9569f5`).

## Validation

- Validate on executable resolver commit: check `99638562508` — success.
- Context sync run `33437854223`, check `99638558501` — success through migration, terminology apply, all finding hardeners, scoped override resolution, context guard, review-queue build, full pytest, and generated-context commit.
- Generated context commit: `c28f9dfbb4bbdd8c6418a8b6777fec726f366129`.
- That generated diff changes `cf-cea396d277bd7301` from `canonical_resolution: null` to:
  - layer: `community`
  - term_id: `stat.stamina.achievement_threshold`
  - target_vi: `Stamina`
- The same generated diff removes the obsolete global Stamina review decision and drops the `体力` canonical-finding-review row from the terminology review queue.

This checkpoint closes only the Stamina threshold unit. Continue immediately with the next live canonical-maintenance blocker.
