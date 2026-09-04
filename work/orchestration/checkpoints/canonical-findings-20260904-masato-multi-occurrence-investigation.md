# Canonical findings maintenance checkpoint — Masato NPC multi-occurrence investigation

Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260904T150548Z`

## Accepted work before this checkpoint

- `彻(NPC)` / JP `徹` was production-accepted as an exact item-scoped ignore; maintenance count advanced to 102.
- `望(NPC)` / JP `望` was production-accepted as an exact item-scoped ignore; maintenance count advanced to 103.

## Next unresolved identity investigated

`正人(NPC)` is still an unresolved/deferred proper-name finding, `cf-1ed10dd6d18561b9`. The maintained defer source explicitly records that 正人 has multiple established Japanese readings, including Masato and Masahito, so the current `Masato (NPC)` rendering must not be promoted to reusable canonical terminology without stronger identity evidence.

Unlike the just-resolved Toru and Nozomi cases, the active review plan contains multiple occurrences of `正人(NPC)` across several batches/items. Repository search shows multiple distinct exact text-data paths for this same source identity (historical/current review evidence includes path tails such as 13, 115, and 149). Therefore a single exact item ignore would be incomplete, while a broad `152` prefix must not be introduced without enumerating and validating the intended occurrences.

## Continuation

1. Re-read live `WORKER_START.md`, orchestration state, parallel state, and maintenance claim.
2. If resuming this investigation, enumerate all live active-plan `正人(NPC)` occurrences and their exact `text_data_dict.json` paths.
3. Prefer explicit per-item scoped ignore decisions (or another repository-supported narrow representation) that cover all intended occurrences without affecting unrelated category-152 names.
4. Add an idempotence/regression test proving no `canonical_resolution` is created and that the relevant finding is removed only for the covered items.
5. Run/observe Validate, Context Sync, and review-plan Sync before incrementing `completed_count` beyond 103.
6. Keep `cf-3a460c751596bfac` (`灯穂` / Inari One) deferred until authoritative Global evidence is available on/after 2026-09-06; do not guess it.
