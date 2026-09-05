# Canonical finding checkpoint — Initial Friendship overmatch

Claim: `canonical-findings-maintenance-gpt56sol-20260905-0845-a11`
Finding: `cf-375c57aaf697bbff`
Source alias: `初始牵绊值`
Suggested/established target: `Initial Friendship`

## Live evidence

A fresh retrospective-review merge on live `main` introduced `cf-375c57aaf697bbff` because category-155 source strings such as `友情加成&初始牵绊值提升` simultaneously matched the generic `牵绊值 -> Friendship Gauge` rule and the narrower established `初始牵绊值 -> Initial Friendship` rule.

Repository evidence already establishes the narrower canonical concept:

- `glossary/ui_community_terms.json` contains `support.initial_friendship.effect155` with aliases `初始牵绊值`, `初始羁绊值`, and `初始羁绊槽上升`, preferred `Initial Friendship`.
- `scripts/harden_training_support_effect_labels.py` durably recreates that scoped support-effect term.
- `scripts/translation_review_common.py` already supports `exclude_source_contains` for both locked and community terminology matching.
- The generic gauge hardener `scripts/harden_friendship_gauge_variant_finding.py` previously used `contains` for `牵绊值` without excluding the narrower Initial Friendship compounds.

## Durable changes in this maintenance claim

1. Commit `5d6129c685faf46226bfdb06791e98c160533d82`
   - updates `scripts/harden_friendship_gauge_variant_finding.py`;
   - adds `INITIAL_FRIENDSHIP_COMPOUNDS = ["初始牵绊值", "初始羁绊值", "初始羁绊槽上升"]`;
   - adds those values to `exclude_source_contains` on both generic Friendship Gauge locked/community terms;
   - preserves category-155/item-scoped behavior for true bare `牵绊值`/`羁绊值` gauge contexts.

2. Commit `dcbf1b7086cc9a56f04d68b5cf7550f071f7d06e`
   - extends `tests/test_friendship_gauge_variant_finding_hardening.py`;
   - asserts all three Initial Friendship compounds no longer match the generic Friendship Gauge community term;
   - retains the existing positive gauge match, category-scope negative case, idempotence, and resolver evidence guard.

## Required continuation

The permanent hardener/test source is now patched, but the generated live glossary has not yet been regenerated and the new finding has not yet been resolved. Continue without redoing research:

1. run the relevant hardener/test suite (at minimum `tests/test_friendship_gauge_variant_finding_hardening.py` plus existing training-support-effect hardening tests);
2. execute the hardener against live repository state so `term_registry.json` and `ui_community_terms.json` receive the exclusion fields;
3. resolve `cf-375c57aaf697bbff` through the canonical-finding pipeline only after verifying its evidence is the narrower Initial Friendship compound in category 155;
4. run required validation / production Context Sync and Review Plan Sync;
5. run the second unchanged Sync/no-op proof if required by the live maintenance protocol;
6. verify a positive bare-gauge example still yields `Friendship Gauge`, while `友情加成&初始牵绊值提升` yields only `Friendship Bonus` + `Initial Friendship` and no contradictory generic gauge requirement;
7. then increment maintenance `completed_count`, checkpoint completion, and release/return to mass-work routing.

Do not patch localized translations to hide this conflict; the defect is canonical matcher precedence/overmatch.
