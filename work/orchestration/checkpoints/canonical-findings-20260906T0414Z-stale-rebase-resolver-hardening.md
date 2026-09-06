# Canonical findings maintenance checkpoint — stale-rebase and Initial Friendship hardening

Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260906T035816Z`

Durable work completed in this run:

- Fixed `Sync translation review plan` so a generated canonical/review-plan commit is not blindly rebased across concurrent changes to canonical generation inputs. The workflow now detects canonical/resolver/hardener changes after generation and rebuilds from fresh `main` instead. Commit: `5e39034b1a3d0bbe1ff24bab36f3cff6339d2f10`.
- Verified workflow run `34010618228` completed successfully against the race-guarded workflow.
- Verified live `cf-375c57aaf697bbff` (`初始牵绊值`) is resolved as `context_guard / common.friendship_gauge.support_effects / Friendship Gauge`; the live evidence is category 155 and current text uses `Initial Friendship` while the generic Friendship Gauge term excludes the narrower compound.
- Strengthened `scripts/resolve_regenerated_initial_friendship_finding.py` so future canonical refresh/rematerialization of `cf-375c57aaf697bbff` is resolved only when every evidence row is positively covered by the scoped `support.initial_friendship.effect155` term and none is still matched by the generic Friendship Gauge term. Commit: `319ffe1221fcfa5c1ff1d16d342fd0a7cc2bc1da`.

No direct edits were made to `localized_data/**`. No other worker claims or automations were modified.
