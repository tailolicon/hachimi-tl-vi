# Trainee localize canonical finding — pending validation

Finding `cf-d4d7f252ccfed57f` is an active localize_dict.json contains-scope blocker for the full compound `育成赛马娘`, with reviewed target `Trainee`.

Repository evidence already establishes the complete compound as the player-facing Trainee concept while keeping bare `育成` and bare `赛马娘` semantically separate. Existing `scripts/harden_trainee_text_data_finding.py` covered text_data only, while this finding is unkeyed `localize_dict.json` scope.

Durable implementation:
- `9fa8ecf45d5b8d5765cde520d5acf6038925442a` extends the permanent hardener with `career.ui.trainee.localize`, source alias `育成赛马娘`, target `Trainee`, item invalidation, and localize-only scope.
- `0e69ee41ac4c4a7200a2c002203d42a56e35c315` extends regression coverage to prove `cf-d4d7f252ccfed57f` resolves through the new community rule while bare `育成` and `赛马娘` remain unresolved.

Acceptance evidence currently running from the test commit:
- Validate run `34098570963` — in progress at checkpoint time.
- Sync translation context run `34098570944` — queued/pending at checkpoint time.

Do not mark the finding complete until Validate succeeds, production Sync succeeds and persists refreshed canonical context/findings, and an unchanged second Sync proves semantic no-op. If the first Sync fails because the hardener is not included by production orchestration, inspect the Sync job logs and wire the permanent hardener into the existing production hardener sequence rather than patching generated glossary output manually.
