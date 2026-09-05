# Canonical finding checkpoint — Initial Friendship compound overmatch

Finding: `cf-375c57aaf697bbff` (`初始牵绊值`)

## Live diagnosis

The finding is source-path-wide (`text_data_dict.json`) with no JSON-path prefix, but all nine evidence rows are category `155` Support Effect strings. The repository already has the narrower community rule `support.initial_friendship.effect155` → `Initial Friendship`, scoped to category `155`, and the generic `Friendship Gauge` rule explicitly excludes `初始牵绊值` and related Initial Friendship compounds.

The normal canonical refresh cannot resolve this regenerated finding because `_rule_covers_finding` correctly refuses to let a category-scoped rule cover a source-path-wide finding. Broadening the Initial Friendship rule would weaken context safety.

## Durable fix

Registered `cf-375c57aaf697bbff` in `POSITIVE_EVIDENCE_GUARDS` inside `scripts/resolve_context_guard_findings.py`, targeting the existing scoped `support.initial_friendship.effect155` rule. The resolver therefore closes the finding only when every evidence row is actually covered by that rule.

Added `tests/test_initial_friendship_context_finding_resolution.py` with positive category-155 evidence and a negative category-163 case. A direct runtime check produced:

- category `155` evidence → canonical resolution `community / support.initial_friendship.effect155 / Initial Friendship`;
- category `163` evidence → no resolution.

Running canonical refresh followed by the context-guard resolver on the live checkout also resolved `cf-375c57aaf697bbff` to `Initial Friendship`. The generated ledger mutation was intentionally reverted before commit; production Context Sync remains responsible for materializing derived canonical-finding state after integration.
