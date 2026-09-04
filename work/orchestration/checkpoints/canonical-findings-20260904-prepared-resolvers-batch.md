# Canonical finding checkpoint — apply already-prepared resolver scripts

## What happened

The active-findings ledger (153 open blockers at claim time) had four findings for which a
prior worker had already authored a ready resolver script under `scripts/` that matched the
finding to an existing locked/community term, but the script had not yet been executed/committed:

- `cf-13f41d397ec5e6ad` (初始羁绊槽上升 / Support initial Friendship gauge) via
  `scripts/resolve_regenerated_initial_friendship_finding.py` → `support.initial_friendship.effect155`
  → `Initial Friendship`.
- `cf-7894d0578d8c8a02` (Aoharu Ignition skill family) via
  `scripts/resolve_regenerated_aoharu_ignition_finding.py` → `skill.aoharu_ignition.family`
  → `Thắp lửa thanh xuân`.
- `cf-9f625a03a4f08c41` (Super Long distance context) via
  `scripts/resolve_regenerated_super_long_distance_context_finding.py` → `common.distance.long`
  → `Long`.
- `cf-b17becec58edec45` (Running style narrative) via
  `scripts/resolve_running_style_narrative_finding.py` → `common.style` → `Style`.

Each script only writes `canonical_resolution` when its own evidence-matching check passes
against the finding's live evidence and the already-existing locked/community term; none of them
invented a new mapping. Ran all four, confirmed `glossary/canonical_findings.json` diff only sets
`canonical_resolution` on those four findings, and reran
`uv run --with pytest pytest tests/test_canonical_findings.py
tests/test_canonical_findings_skill_resolution.py tests/test_canonical_finding_rule_exclusions.py`
(7 passed).

`active_findings()` count dropped from 153 to 149.

## Continuation

No other open finding currently has a matching prepared-but-unexecuted resolver script (checked
by grepping every remaining `finding_id` against `scripts/`). Remaining open findings require
fresh JP/canonical research (skill titles, NPC display names, named Room Match/event labels, etc.)
before a lock/ignore decision can be recorded in `glossary/terminology_reviews.json`.

`completed_count` incremented by 4 (88 → 92) to reflect four newly resolved findings in this pass.
