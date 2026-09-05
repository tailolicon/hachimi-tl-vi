# Canonical finding checkpoint — Initial Friendship overmatch

Claim: `canonical-findings-maintenance-gpt56sol-20260905-0930-a11`
Finding: `cf-375c57aaf697bbff`
Source alias: `初始牵绊值`
Suggested/established target: `Initial Friendship`

## Live evidence

A fresh retrospective-review merge on live `main` introduced `cf-375c57aaf697bbff` because category-155 source strings such as `友情加成&初始牵绊值提升` simultaneously matched the generic `牵绊值 -> Friendship Gauge` rule and the narrower established `初始牵绊值 -> Initial Friendship` rule.

Repository evidence establishes the narrower canonical concept:

- `glossary/ui_community_terms.json` contains `support.initial_friendship.effect155` with aliases `初始牵绊值`, `初始羁绊值`, and `初始羁绊槽上升`, preferred `Initial Friendship`.
- `scripts/harden_training_support_effect_labels.py` durably recreates that scoped support-effect term.
- `scripts/translation_review_common.py` supports `exclude_source_contains` for both locked and community terminology matching.

## Durable hardening

1. Commit `5d6129c685faf46226bfdb06791e98c160533d82`
   - updates `scripts/harden_friendship_gauge_variant_finding.py`;
   - adds `INITIAL_FRIENDSHIP_COMPOUNDS = ["初始牵绊值", "初始羁绊值", "初始羁绊槽上升"]`;
   - adds those values to `exclude_source_contains` on both generic Friendship Gauge locked/community terms;
   - preserves category-155/item-scoped behavior for true bare `牵绊值`/`羁绊值` gauge contexts.

2. Commit `dcbf1b7086cc9a56f04d68b5cf7550f071f7d06e`
   - extends `tests/test_friendship_gauge_variant_finding_hardening.py`;
   - asserts all three Initial Friendship compounds no longer match the generic Friendship Gauge community term;
   - retains the positive gauge match, category-scope negative case, idempotence, and resolver evidence guard.

## Validation progress

GitHub Actions run `33956175984` for live-main commit `dcbf1b7086cc9a56f04d68b5cf7550f071f7d06e` completed successfully. Its job logs provide the following acceptance evidence:

- `scripts/harden_friendship_gauge_variant_finding.py` ran successfully and reported `term_registry_changed=false` and `units_en_changed=false`, proving the generated registry state already contains the hardening and the hardener is idempotent on that head;
- the resolver step `resolve_regenerated_initial_friendship_finding` reported `changed=true` for the regenerated finding pipeline;
- the hardening regression tests passed;
- final generated Context Sync reported the generated context already current/no update required, providing unchanged/no-op evidence for that generated-context step.

## Still required before completion

Do not increment `completed_count` yet. Before marking this maintenance unit complete:

1. directly verify live `glossary/canonical_findings.json` no longer has active `cf-375c57aaf697bbff`;
2. directly spot-check the live glossary entries for `progress.friendship_gauge` and `progress.friendship_gauge.support_effects` retain the Initial Friendship exclusions while the scoped `support.initial_friendship.effect155` mapping remains `Initial Friendship`;
3. verify production Review Plan Sync for the exact accepted head, including the required unchanged/no-op proof where the live maintenance protocol requires it;
4. confirm a bare Friendship Gauge case remains positive while `友情加成&初始牵绊值提升` no longer receives the contradictory generic Friendship Gauge requirement;
5. only after all acceptance gates pass, increment maintenance `completed_count` from 135 to 136, persist completion evidence, release the maintenance claim, and immediately re-route through live `WORKER_START.md`.

Do not patch localized translations to hide this conflict; the defect is canonical matcher precedence/overmatch.
