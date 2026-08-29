# Training / Support canonical hardening checkpoint — 2026-08-29T14:12Z

Task: `canonical-training-support`
Stage: `domain_work`
Branch: `canonical-training-support-hardening`

## Continued scope

Resumed from the released 13:48Z checkpoint without restarting completed inventory.

## Durable progress in this run

1. Confirmed that the branch already contains the intended scoped Bond/Friendship correction in `scripts/harden_training_support_canon.py`: legacy global `progress.bond` is disabled as an enforcing bare-term lock, while `羁绊值` in `text_data_dict.json` category `155` is explicitly `Friendship Gauge`. This is the support-card gauge mechanic and does not generalize ordinary friendship/bond prose.
2. Confirmed the live production review context is stale relative to that branch: current Audit Round 1 batch `b0838` still shows `progress.bond -> Gắn kết` on category-155 support-effect descriptions such as `羁绊值在80以上时`.
3. Re-verified terminology against current established Global/community documentation: support-card descriptions use `Friendship Gauge`, `Friendship Bonus`, `Training Effectiveness`, `Mood Effect`, `Initial Friendship`, etc.; Friendship Training unlocks when the Friendship Gauge reaches 80%.
4. Materialized both permanent hardeners on the branch through GitHub Actions and persisted the generated glossary delta. Temporary workflow run `33256895192`, job `99112099929`, passed focused tests, full pytest, CLI validation/index, and committed the generated canonical glossary at branch head `58fe412646bc00d8fbe941e4b25ad7b4b2739a9d`.

No `localized_data/**` examples were patched.

## Remaining substantive domain work

Do not finalize yet. Continue the support-effect label inventory in category `155`, especially repeated labels/phrases corresponding to established player-facing terms such as `Training Effectiveness`, `Friendship Bonus`, `Mood Effect`, initial Friendship/Gauge wording, Hint Level/Frequency, and stat bonuses. Add only scoped canonical rules with negative tests; do not turn generic story prose into system labels.

After that inventory/coverage is complete, rerun full validation, remove temporary workflow artifacts, then transition to `ready_for_finalize`.
